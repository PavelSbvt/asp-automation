import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from core.pdf_render import render_one_student
from parser.parsing_functions import parsing_commissions
from core.fill_db_sheet import fill_database_sheet
from utils.output_rich import Rich


class PdfParseAndGenerateWorker(QObject):
    """
    Воркер для парсинга данных и генерации PDF (первая вкладка).

    Живёт в отдельном QThread, общается с UI через сигналы.
    Внутри — две фазы:
        1) парсинг (Excel + doc-файлы комиссии + сборка БД);
        2) генерация PDF по каждому студенту.

    ВАЖНО: если render_one_student использует Excel/VBScript —
    параллелизм через ProcessPoolExecutor НЕ РАБОТАЕТ, ставим
    USE_PROCESS_POOL = False. Если рендер на чистом Python —
    можно включить True и получить ускорение.
    """

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    file_done = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(int, str)

    # Флаг: использовать ли реальный параллелизм при генерации.
    # Включи True, если render_one_student — чистый Python (без Excel).
    USE_PROCESS_POOL = False

    def __init__(
        self,
        universal_excel_file_path: str,
        doc_file_with_commission_path: str,
        output_folder_path: str,
        commission_text: str,
        selected_semester: int):
        """
        :param universal_excel_file_path: путь к универсальной таблице
        :param doc_file_with_commission_path: путь к doc-файлу с комиссией
        :param output_folder_path: папка для сохранения PDF
        :param commission_text: текст приказа из поля на первой вкладке
        :param selected_semester: выбранный семестр
        """

        super().__init__()

        self.universal_excel_file = universal_excel_file_path
        self.doc_file_with_commission = doc_file_with_commission_path
        self.output_folder = output_folder_path
        self.commission_text = commission_text
        self.selected_semester = selected_semester

        self.stop_requested = False


    def request_stop(self) -> None:
        """
        Ставит флаг остановки. Вызывается из UI-потока.
        """

        self.stop_requested = True


    # Основной метод, выполняется в отдельном QThread
    def run(self) -> None:
        processed = 0
        try:
            self.status.emit("НАЧАЛО ПАРСИНГА")
            Rich.simple_log("НАЧАЛО ПАРСИНГА")

            # парсинг
            self.status.emit("Парсинг универсальной таблицы...")
            students_data = self.parse_universal_table()

            if self.stop_requested:
                self.status.emit("Остановлено пользователем")
                return

            if not students_data:
                self.error.emit("Не удалось загрузить данные из универсальной таблицы")
                return

            self.status.emit(f"Загружено {len(students_data)} студентов")

            # Парсинг doc-файла комиссии
            self.status.emit("Парсинг комиссии...")
            commission_members = self.parse_commission()

            if self.stop_requested:
                self.status.emit("Остановлено пользователем")
                return

            if not commission_members:
                self.error.emit("Не удалось найти членов комиссии")
                return

            self.status.emit(f"Найдено комиссий: {len(commission_members)}")

            # Заполнение БД
            self.status.emit("Заполнение БД...")
            db_file = fill_database_sheet(
                students_data,
                self.commission_text,
                commission_members,
                self.selected_semester,
            )

            if self.stop_requested:
                self.cleanup_temp_file(db_file)
                self.status.emit("Остановлено пользователем")
                return

            if not db_file:
                self.error.emit("Не удалось сохранить файл БД")
                return

            self.status.emit(f"БД сохранена: {db_file}")

            # генерация пдф
            self.status.emit("Генерация PDF...")
            processed = self.generate_pdfs(db_file)

            self.status.emit(f"Готово. Создано PDF: {processed}")

        except BaseException as e:
            traceback.print_exc()
            Rich.log_error(f"Критическая ошибка: {e}")
            self.error.emit(f"Непредвиденная ошибка: {e}")

        finally:
            # Гарантирует, что UI узнает о завершении — даже если была ошибка
            self.finished.emit(processed, self.output_folder)


    # парсинг универсальной таблицы
    def parse_universal_table(self) -> list[dict]:
        """
        Читает универсальную таблицу, возвращает список студентов.
        """

        Rich.debug_log("Чтение универсальной таблицы.")

        df = pd.read_excel(
            self.universal_excel_file,
            dtype=str,
            engine="openpyxl",
        )
        Rich.simple_log(f"Загружено {len(df)} строк")

        columns = list(df.columns)
        fio_idx = profile_idx = citizenship_idx = None

        for i, col in enumerate(columns):
            col_lower = col.lower()
            if "фио" in col_lower:
                fio_idx = i
            if "профиль" in col_lower:
                profile_idx = i
            if "гражданство" in col_lower:
                citizenship_idx = i

        fio_idx = fio_idx if fio_idx is not None else 2
        profile_idx = profile_idx if profile_idx is not None else 22
        citizenship_idx = citizenship_idx if citizenship_idx is not None else 40

        Rich.debug_log(
            f"Индексы: ФИО={fio_idx}, Профиль={profile_idx}, "
            f"Гражданство={citizenship_idx}"
        )

        students = []
        for index, row in df.iterrows():
            if self.stop_requested:
                Rich.debug_log(f"Остановка на строке {index}")
                return students

            try:
                fio = str(row.iloc[fio_idx]).strip() if len(row) > fio_idx else ""
                profile = (
                    str(row.iloc[profile_idx]).strip()
                    if len(row) > profile_idx else ""
                )
                citizenship = (
                    str(row.iloc[citizenship_idx]).strip()
                    if len(row) > citizenship_idx else ""
                )

                if fio and fio.lower() != "nan":
                    if profile.lower() == "nan":
                        profile = ""
                    if not citizenship or citizenship.lower() == "nan":
                        citizenship = "РФ"

                    students.append({
                        "fio": fio,
                        "profile": profile,
                        "citizenship": citizenship,
                    })

            except Exception as e:
                Rich.log_error(f"Ошибка строки {index}: {e}")
                continue

        Rich.success_log(f"Всего студентов: {len(students)}")
        return students


    # парсинг комиссии
    def parse_commission(self):
        """
        Парсит doc-файл комиссии. Возвращает словарь с комиссиями
        или None, если что-то пошло не так.
        """

        Rich.debug_log("Начало парсинга doc-файла комиссии")

        # parsing_commissions(self) ожидает объект с атрибутами radio_button_*
        # и *_commission_path.
        fake_self = CommissionContext(
            doc_path=self.doc_file_with_commission,
            selected_semester=self.selected_semester,
        )

        members = parsing_commissions(fake_self)

        if not members:
            Rich.warning_log("Члены комиссии не найдены!")
            return None

        Rich.success_log(f"Комиссия загружена. Найдено комиссий: {len(members)}")
        return members


    # генерация PDF
    def generate_pdfs(self, db_file: str) -> int:
        """
        Генерирует PDF по каждому студенту из БД.

        :param db_file: путь к xlsx-файлу с листом «БД»

        :return: количество успешно созданных PDF
        """

        try:
            df = pd.read_excel(db_file, sheet_name="БД", dtype=str)
        except Exception as e:
            self.error.emit(f"Ошибка чтения БД: {e}")
            return 0

        if df is None or len(df) == 0:
            self.error.emit("Нет данных для генерации PDF")
            return 0

        os.makedirs(self.output_folder, exist_ok=True)

        total = len(df)
        tasks = self.prepare_tasks(df)

        if not tasks:
            self.error.emit("Нет валидных задач для генерации")
            return 0

        if self.USE_PROCESS_POOL:
            return self.generate_with_pool(db_file, tasks, total)
        else:
            return self.generate_sequential(db_file, tasks, total)


    def prepare_tasks(self, df: pd.DataFrame) -> list[dict]:
        """
        Готовит список словарей-задач для render_one_student.
        """

        tasks = []
        for i in range(len(df)):
            surname_genitive = str(df.iloc[i, 0]).strip()
            surname_nominative = str(df.iloc[i, 9]).strip()
            direction = str(df.iloc[i, 10]).strip()

            if (
                surname_genitive.lower() == "nan"
                or surname_nominative.lower() == "nan"
                or not surname_nominative
            ):
                continue

            code = (
                direction.split()[0]
                if direction and direction.lower() != "nan"
                else "unknown"
            )

            tasks.append({
                "code": code,
                "surname_name": surname_nominative,
                "surname_name_p": surname_nominative,
                "surname_datelnyi_p": surname_genitive,
                "direction": direction,
                "discipline": str(df.iloc[i, 1]),
                "commission_text": str(df.iloc[i, 2]),
                "comm1_text": str(df.iloc[i, 3]),
                "comm1_fio": str(df.iloc[i, 4]),
                "comm2_text": str(df.iloc[i, 5]),
                "comm2_fio": str(df.iloc[i, 6]),
                "comm3_text": str(df.iloc[i, 7]),
                "comm3_fio": str(df.iloc[i, 8]),
            })

        return tasks


    def generate_sequential(
        self, db_file: str, tasks: list[dict], total: int) -> int:
        """
        Последовательная генерация. Используется, если Excel внутри.
        """

        processed = 0
        for idx, data in enumerate(tasks, 1):
            if self.stop_requested:
                self.status.emit("Сборка остановлена пользователем")
                break

            self.status.emit(f"Подготовка PDF: {data['surname_name']}")

            try:
                pdf_path = render_one_student(
                    db_file, data, self.output_folder,
                )
            except Exception as e:
                Rich.log_error(f"Ошибка для '{data['surname_name']}': {e}")
                self.error.emit(f"Ошибка для '{data['surname_name']}': {e}")
                continue

            processed += 1
            self.progress.emit(int(processed / total * 100))
            self.file_done.emit(os.path.basename(pdf_path))

        return processed


    def generate_with_pool(self, db_file: str, tasks: list[dict], total: int) -> int:
        """
        Параллельная генерация. Работает ТОЛЬКО если render_one_student
        на чистом Python (без Excel/VBScript).
        """

        processed = 0
        max_workers = os.cpu_count() or 1

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    render_one_student, db_file, data, self.output_folder,
                ): data
                for data in tasks
            }

            for idx, future in enumerate(as_completed(futures), 1):
                if self.stop_requested:
                    executor.shutdown(cancel_futures=True)
                    self.status.emit("Сборка остановлена пользователем")
                    break

                data = futures[future]
                try:
                    pdf_path = future.result()
                    processed += 1
                    self.file_done.emit(os.path.basename(pdf_path))
                except Exception as e:
                    Rich.log_error(f"Ошибка для '{data['surname_name']}': {e}")
                    self.error.emit(f"Ошибка для '{data['surname_name']}': {e}")

                self.progress.emit(int(idx / total * 100))

        return processed


    @staticmethod
    def cleanup_temp_file(path: str) -> None:
        """
        Удаляет временный файл БД, если пользователь остановил процесс.
        """

        if path and os.path.exists(path):
            try:
                os.remove(path)
                Rich.debug_log(f"Удален временный файл: {path}")
            except OSError:
                pass


class CommissionContext:
    """
    Минимальная обёртка для parsing_commissions(self), у которой
    есть только то, что нужно: путь к doc-файлу и семестр.

    parsing_commissions использует:
        - self.radio_button_1/2/3.isChecked()
        - self.history_commission_path / foreign_commission_path /
          specialization_commission_path
    """

    def __init__(self, doc_path: str, selected_semester: int):
        self.history_commission_path = None
        self.foreign_commission_path = None
        self.specialization_commission_path = None

        if selected_semester == 1:
            self.history_commission_path = doc_path
        elif selected_semester == 2:
            self.foreign_commission_path = doc_path
        else:
            self.specialization_commission_path = doc_path

        self._selected = selected_semester
        self.radio_button_1 = FakeRadio(selected_semester == 1)
        self.radio_button_2 = FakeRadio(selected_semester == 2)
        self.radio_button_3 = FakeRadio(selected_semester == 3)


class FakeRadio:
    """
    Заглушка QRadioButton для parsing_commissions.
    """

    def __init__(self, checked: bool):
        self._checked = checked

    def isChecked(self) -> bool:
        return self._checked
