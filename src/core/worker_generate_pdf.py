import traceback
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from core.pdf_render import render_one_student


class PdfBuilderWorker(QObject):
    """
    Класс для работы с сигналами и потоками процесса сборки пдф с второй вкладки
    """

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    file_done = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(int, str)

    def __init__(self, excel_file: str, output_folder: str):
        super().__init__()
        self.excel_file = excel_file
        self.output_folder = output_folder
        self.stop_requested = False


    def request_stop(self) -> None:
        self.stop_requested = True


    def run(self) -> None:
        processed = 0
        try:
            self.status.emit("Запущен процесс сборки ПДФ")

            # Чтение Excel в главном процессе worker'а
            try:
                df = pd.read_excel(self.excel_file, sheet_name="БД", dtype=str)
            except Exception as e:
                self.error.emit(f"Ошибка чтения файла: {e}")
                return

            if df is None or len(df) == 0:
                self.error.emit("Нет данных для обработки")
                return

            self.status.emit(f"Найдено {len(df)} человек")
            os.makedirs(self.output_folder, exist_ok=True)

            total = len(df)
            tasks = []

            # подготовка списка задач
            for i in range(total):
                surname_datelnyi_p = str(df.iloc[i, 0]).strip()
                surname_name_p = str(df.iloc[i, 9]).strip()
                direction = str(df.iloc[i, 10]).strip()

                if (surname_datelnyi_p == "nan"
                        or surname_name_p == "nan"
                        or not surname_name_p):
                    continue

                code = direction.split()[0] if direction and direction != "nan" else "unknown"

                data = {
                    "code": code,
                    "surname_name": surname_name_p,
                    "surname_name_p": surname_name_p,
                    "surname_datelnyi_p": surname_datelnyi_p,
                    "direction": direction,
                    "discipline": str(df.iloc[i, 1]),
                    "comm1_text": str(df.iloc[i, 3]),
                    "comm1_fio": str(df.iloc[i, 4]),
                    "comm2_text": str(df.iloc[i, 5]),
                    "comm2_fio": str(df.iloc[i, 6]),
                    "comm3_text": str(df.iloc[i, 7]),
                    "comm3_fio": str(df.iloc[i, 8]),
                }
                tasks.append(data)

            # Запуск обработки в пуле процессов
            self.status.emit(f"Запуск пула процессов ({len(tasks)} задач)")

            with ProcessPoolExecutor(max_workers=1) as executor:
                for idx, data in enumerate(tasks):
                    if self.stop_requested:
                        self.status.emit("Сборка остановлена пользователем")
                        break

                    self.status.emit(f"Подготовка ПДФ для '{data['surname_name']}'")

                    try:
                        future = executor.submit(
                            render_one_student,
                            self.excel_file,
                            data,
                            self.output_folder,
                        )
                        pdf_path = future.result()

                    except Exception as e:
                        self.error.emit(f"Ошибка для '{data['surname_name']}': {e}")
                        continue

                    processed += 1
                    self.progress.emit(int(processed / len(tasks) * 100))
                    self.file_done.emit(os.path.basename(pdf_path))

        except BaseException as e:
            traceback.print_exc()
            self.error.emit(f"Непредвиденная ошибка: {e}")
        finally:
            self.finished.emit(processed, self.output_folder)
