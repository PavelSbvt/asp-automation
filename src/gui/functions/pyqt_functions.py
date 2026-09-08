import traceback
import os

import pandas as pd
from PyQt6.QtWidgets import QMessageBox

from parser.parsing_functions import parsing_commissions
from core.generate_pdf_from_db import generate_pdf_from_db
from core.fill_db_sheet import fill_database_sheet
from utils.output_rich import (debug_log, success_log,
    simple_log, log_error, warning_log)


def parsing(self) -> None:
    """
    Функция парсинга данных и сбора ПДФ

    :return: None
    """

    simple_log("НАЧАЛО ПАРСИНГА")

    self.stop_generation = False
    self.stop_parsing_button.setVisible(True)
    self.stop_parsing_button.setEnabled(True)
    self.run_button.setVisible(False)
    self.run_button.setEnabled(False)
    self.progress_bar_parsing.setVisible(True)

    try:
        debug_log("Проверяю наличие файлов...")
        if (not hasattr(self, 'universal_file_path')
                or not self.universal_file_path):
            QMessageBox.warning(self, "Ошибка", "Сначала выберите универсальную таблицу!")
            warning_log("Не выбрана универсальная таблица")
            return

        debug_log("Универсальный файл есть")

        if (not self.radio_button_1.isChecked() and not self.radio_button_2.isChecked()
                and not self.radio_button_3.isChecked()):
            QMessageBox.warning(self, "Ошибка", "Выберите семестр!")
            warning_log("Не выбран семестр")
            return

        debug_log("Семестр выбран")

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            return

        # Сохраняем текст приказа
        debug_log("Сохранение текста приказа")
        self.commission_text = self.input_commission.text().strip()
        simple_log(f"Текст приказа: {self.commission_text[:30]}...")

        # Определяем семестр
        debug_log("Определение семестра.")
        if self.radio_button_1.isChecked():
            self.selected_semester = 1
            self.semester_name = "Первый семестр"
        elif self.radio_button_2.isChecked():
            self.selected_semester = 2
            self.semester_name = "Второй семестр"
        else:
            self.selected_semester = 3
            self.semester_name = "Третий семестр"

        simple_log(f"Семестр: {self.semester_name}")

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            return

        debug_log("Чтение универсальной таблицы.")
        df = pd.read_excel(
            self.universal_file_path,
            dtype=str,
            engine='openpyxl'
        )
        simple_log(f"Загружено {len(df)} строк")

        columns = list(df.columns)
        debug_log(f"Колонки: {columns[:5]}...")

        fio_idx = None
        profile_idx = None
        citizenship_idx = None

        for i, col in enumerate(columns):
            col_lower = col.lower()
            if 'фио' in col_lower:
                fio_idx = i
            if 'профиль' in col_lower:
                profile_idx = i
            if 'гражданство' in col_lower:
                citizenship_idx = i

        if fio_idx is None:
            fio_idx = 2
        if profile_idx is None:
            profile_idx = 22
        if citizenship_idx is None:
            citizenship_idx = 40

        debug_log(f"Индексы: ФИО={fio_idx}, Профиль={profile_idx}, "
              f"Гражданство={citizenship_idx}")

        students_data = []
        for index, row in df.iterrows():
            if self.stop_generation:
                debug_log(f"Остановка на строке {index}")
                return
            try:
                fio = str(row.iloc[fio_idx]).strip() if len(row) > fio_idx else ""
                profile = str(row.iloc[profile_idx]).strip() \
                    if len(row) > profile_idx else ""
                citizenship = str(row.iloc[citizenship_idx]).strip() \
                    if len(row) > citizenship_idx else ""

                if fio and fio != "nan" and fio != "":
                    if profile == "nan":
                        profile = ""
                    if citizenship == "nan" or citizenship == "":
                        citizenship = "РФ"

                    students_data.append({
                        'fio': fio,
                        'profile': profile,
                        'citizenship': citizenship
                    })
            except Exception as e:
                log_error(f"Ошибка строки {index}: {e}")
                continue

        self.students_data = students_data
        simple_log(f"Всего студентов: {len(students_data)}")

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            return

        debug_log("Начало парсинга doc-ов комиссии")
        commission_members = parsing_commissions(self)

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            return

        if commission_members:
            self.commission_members = commission_members
            simple_log(f"Найдено комиссий: {len(commission_members)}")
        else:
            warning_log("Члены комиссии не найдены!")
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось найти членов комиссии"
            )
            return

        success_log("Завершение парсинга doc-ов комиссии")

        for i, student in enumerate(students_data, 1):
            debug_log(f"    {i}. {student['fio']}")

        success_log("Парсинг таблицы завершён")

        debug_log("Проверка данные студентов.")
        if not hasattr(self, 'students_data') or not self.students_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные из универсальной таблицы!")
            return
        simple_log(f"Загружено {len(self.students_data)} студентов")

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            return

        simple_log("Заполнение БД.")
        db_file = fill_database_sheet(self)

        if self.stop_generation:
            simple_log("Генерация отменена пользователем")
            if db_file and os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    debug_log(f"Удален временный файл БД: {db_file}")
                except:
                    pass
            return

        if db_file:
            self.generated_db_path = db_file
            simple_log(f"БД сохранена: {db_file}")

            if self.stop_generation:
                simple_log("Генерация отменена пользователем")
                if os.path.exists(db_file):
                    try:
                        os.remove(db_file)
                        debug_log(f"Удален временный файл БД: {db_file}")
                    except:
                        pass
                return

            generate_pdf_from_db(self, self.generated_db_path)
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл БД!")
            warning_log("Ошибка. Не удалось сохранить файл БД!")
            return

        success_log("КОНЕЦ ПАРСИНГА")

    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        traceback.print_exc()
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")

    finally:
        debug_log("Восстановление состояния кнопок...")
        self.stop_generation = False
        self.stop_parsing_button.setVisible(False)
        self.stop_parsing_button.setEnabled(False)
        self.progress_bar_parsing.setVisible(False)
        self.run_button.setVisible(True)
        self.run_button.setEnabled(True)
        debug_log("Состояние кнопок восстановлено")
