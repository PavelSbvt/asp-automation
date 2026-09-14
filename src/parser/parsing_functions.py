import os
import traceback
import re
from typing import Dict, Optional, Tuple

import aspose.words as aw
import pandas as pd
from openpyxl import load_workbook
from PyQt6.QtWidgets import QApplication, QMessageBox

from utils.basic_functions import extract_commission_members, normalize_initials
from utils.output_rich import Rich


def normalize_name_for_comparison(name: str) -> str:
    """
    Нормализует имя для сравнения (удаляет лишние пробелы)

    :param name: Str - Принимает фио, которое нужно нормализовать
    """

    if not name or name == "nan":
        return ""

    name = ' '.join(name.split())

    name = normalize_initials(name)

    return name

def parsing_universal_excel(self) -> None:
    """
    Парсит универсальную таблицу Excel

    :return: None
    """

    try:
        Rich.print_spacer()
        Rich.simple_log("НАЧАЛО parsing_universal_excel")

        Rich.debug_log(f"Путь к файлу: {self.universal_file_path}")

        # Проверяем существование файла
        if not os.path.exists(self.universal_file_path):
            Rich.success_log(f"Файл не существует: {self.universal_file_path}")
            QMessageBox.critical(self, "Ошибка",
                                 f"Файл не существует:\n{self.universal_file_path}")

            return

        Rich.debug_log("Файл существует")

        # Проверяем размер файла
        file_size = os.path.getsize(self.universal_file_path)
        Rich.debug_log(f"Размер файла: {file_size} байт")

        if file_size == 0:
            Rich.warning_log("Файл пустой!")
            QMessageBox.critical(self, "Ошибка", "Файл пустой!")
            return

        Rich.debug_log("Начало чтения файла")

        try:
            Rich.debug_log("Через openpyxl.")
            wb = load_workbook(self.universal_file_path, read_only=True, data_only=True)
            ws = wb.active
            Rich.debug_log(f"Активный лист: {ws.title}")
            QApplication.processEvents()

            data = []
            for row in ws.iter_rows(values_only=True):
                row_data = []
                for cell in row:
                    row_data.append(str(cell) if cell is not None else "")
                data.append(row_data)
                if len(data) > 100:  # ограничиваем для теста
                    break

            wb.close()
            Rich.debug_log(f"Прочитано строк: {len(data)} ")

            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                df = pd.DataFrame()

        except Exception as e:
            Rich.warning_log(f"openpyxl не сработал: {e}")

            # Пробуем через pandas
            try:
                Rich.debug_log("Через pandas.")
                df = pd.read_excel(
                    self.universal_file_path,
                    dtype=str,
                    engine='openpyxl'
                )
                Rich.debug_log(f"pandas прочитал {len(df)} строк")
            except Exception as e2:
                Rich.warning_log(f"pandas не сработал: {e2}")
                raise

        if df is None or len(df) == 0:
            Rich.log_error("Нет данных в файле!")
            QMessageBox.warning(self, "Ошибка", "Файл пуст или не содержит данных!")
            Rich.warning_log("Ошибка. Файл пуст или не содержит данных!")
            return

        Rich.success_log(f"Загружено {len(df)} строк, колонок: {len(df.columns)}")

        students_data = []
        for index, row in df.iterrows():
            try:
                if len(row) > 2:
                    fio = str(row.iloc[2]).strip()
                else:
                    fio = ""

                if len(row) > 22:
                    profile = str(row.iloc[22]).strip()
                else:
                    profile = ""

                if len(row) > 7:
                    citizenship = str(row.iloc[7]).strip()
                else:
                    citizenship = ""

                if fio and fio != "nan" and fio != "":
                    fio = normalize_initials(fio)
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
                Rich.log_error(f"Ошибка строки {index}: {e}")
                continue

        self.students_data = students_data
        Rich.simple_log(f"Всего студентов: {len(students_data)}")
        QApplication.processEvents()

        for i, student in enumerate(students_data[:5], 1):
            Rich.debug_log(f"   {i}. {student['fio']}")

        QMessageBox.information(
            self,
            "Готово!",
            f"Данные успешно загружены!\n\n"
            f"Найдено записей: {len(students_data)}"
        )
        Rich.success_log(f"Данные успешно загружены! Найдено записей: {len(students_data)}")

    except Exception as e:
        Rich.log_error(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        QApplication.processEvents()
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось прочитать файл:\n{str(e)}"
        )


def parse_doc_with_tables(path: str) -> Tuple[pd.DataFrame, str]:
    """
    Извлекает все таблицы из документа .doc и возвращает
    их как один DataFrame с текстом.

    :param path: Принимает путь к файлу, из которого нужно извлечь данные комиссии

    :return: Tuple[pd.DataFrame, str] - возвращает DataFrame с текстом комиссии
    """

    doc = aw.Document(path)
    text = doc.get_text()

    tables_data = []

    # Получаем все таблицы в документе
    for idx, node in enumerate(doc.get_child_nodes(aw.NodeType.TABLE, True)):
        table = node.as_table()
        rows = []

        for row_node in table.rows:
            row = row_node.as_row()
            cells = []
            for cell_node in row.cells:
                cell = cell_node.as_cell()
                # Получаем текст ячейки и очищаем от лишних пробелов
                cell_text = cell.get_text().strip()
                # Убираем управляющие символы
                cell_text = re.sub(r'[\x00-\x1f\x7f]', '', cell_text)
                cells.append(cell_text)
            rows.append(cells)

        if not rows:
            continue

        # Если есть заголовок — делаем его колонками
        if len(rows) > 1 and all(len(r) == len(rows[0]) for r in rows):
            # Проверяем, что первая строка — это заголовок
            header = rows[0]
            # Очищаем заголовки от мусора
            clean_header = []
            for h in header:
                h_clean = re.sub(r'[\x00-\x1f\x7f]', '', h).strip()
                clean_header.append(h_clean)
            df = pd.DataFrame(rows[1:], columns=clean_header)
        else:
            df = pd.DataFrame(rows)

        df['source_file'] = path
        df['table_index'] = idx
        tables_data.append(df)

    tables_df = pd.concat(tables_data, ignore_index=True)\
        if tables_data else pd.DataFrame()
    return tables_df, text


def parsing_commissions(self) -> Optional[Dict[str, Dict]]:
    """
    Парсит файл комиссии и возвращает словарь:
    { "шифр": {"members": [...], "code": "шифр"} }

    :return: Optional[Dict[str, Dict]] - возвращает словарь с данными комиссии
    """

    Rich.print_spacer()
    Rich.simple_log("Парсинг комиссии.")

    # Определяем файл в зависимости от семестра
    if self.radio_button_1.isChecked():
        path = getattr(self, "history_commission_path", None)
        commission_name = "История"
        semester_name = "Первый семестр"
    elif self.radio_button_2.isChecked():
        path = getattr(self, "foreign_commission_path", None)
        commission_name = "Иностранный"
        semester_name = "Второй семестр"
    else:
        path = getattr(self, "specialization_commission_path", None)
        commission_name = "Специальность"
        semester_name = "Третий семестр"

    if not path:
        QMessageBox.warning(self, "Ошибка",
                            f"Сначала выберите файл комиссии '{commission_name}'!")
        Rich.log_error("Ошибка. сначала выберите файл комиссии")
        return None

    if not os.path.exists(path):
        QMessageBox.warning(self, "Ошибка", f"Файл не существует: {path}")
        Rich.log_error("ошибка. файл не существует")
        return None

    try:
        tables_df, full_text = parse_doc_with_tables(path)
        commissions_by_code = {}

        Rich.debug_log("данные таблицы")
        for idx, row in tables_df.iterrows():
            Rich.debug_log(f"Строка {idx}:")
            for col in tables_df.columns:
                val = str(row[col])[:100] if pd.notna(row[col]) else ""
                Rich.debug_log(f"    {col}: {val}")
            Rich.print_spacer_points()

        if tables_df is not None and not tables_df.empty:
            cols = list(tables_df.columns)
            Rich.debug_log(f"Колонки: {cols}")

            # Находим колонки
            fio_col = None
            code_col = None

            for col in cols:
                if col not in ['source_file', 'table_index']:
                    col_lower = col.lower()
                    if 'фамил' in col_lower or 'инициал' in col_lower:
                        fio_col = col
                    if ('шифр' in col_lower or 'наименование'
                            in col_lower or 'специальност' in col_lower):
                        code_col = col

            # Если не нашли — берём по индексам
            if code_col is None and len(cols) >= 3:
                code_col = cols[1]
            if fio_col is None and len(cols) >= 2:
                fio_col = cols[0]

            Rich.debug_log(f"Колонка ФИО: {fio_col}")
            Rich.debug_log(f"Колонка шифра: {code_col}")

            # Проходим по строкам
            for idx, row in tables_df.iterrows():
                if fio_col is None:
                    for col in cols:
                        if col not in ['source_file', 'table_index']:
                            value = str(row[col]).strip() \
                                if pd.notna(row[col]) else ""
                            if value and len(value) > 10:
                                value = normalize_initials(value)
                                extract_commission_members(value,
                                            commissions_by_code, row, code_col)
                else:
                    value = str(row[fio_col]).strip() \
                        if pd.notna(row[fio_col]) else ""
                    if value and len(value) > 10:
                        value = normalize_initials(value)
                        extract_commission_members(value,
                                            commissions_by_code, row, code_col)

        self.commissions_by_code = commissions_by_code

        if commissions_by_code:
            Rich.simple_log(f"Найдено комиссий для шифров: {len(commissions_by_code)}")
            for code, comm in commissions_by_code.items():
                members = comm.get('members', [])
                Rich.debug_log(f"   Шифр: {code} -> {len(members)} членов")
                for member in members:
                    Rich.debug_log(f"  - {member.get('fio', '')} ({member.get('role', '')})")

            Rich.success_log(f"Готово. Комиссия успешно загружена. Найдено комиссий: "
                  f"{len(commissions_by_code)}. Семестр: {semester_name}.")
        else:
            Rich.log_error("Члены комиссии не найдены!")

            # Вывод ошибки на пустоту данных о комиссии
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось найти членов комиссии в файле:\n{path}\n\n"
            )

            return

        return commissions_by_code

    except Exception as e:
        Rich.log_error(f"Ошибка при парсинге комиссии: {e}")
        traceback.print_exc()
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось прочитать файл комиссии:\n{str(e)}"
        )
        return None
