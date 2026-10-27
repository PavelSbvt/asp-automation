import os
import re
import traceback
from typing import Dict, Optional, Tuple

import aspose.words as aw
import pandas as pd
from PyQt6.QtWidgets import QMessageBox

from utils.basic_functions import extract_commission_members, normalize_initials
from utils.output_rich import Rich


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


def parsing_commissions(class_name) -> Optional[Dict[str, Dict]]:
    """
    Парсит файл комиссии и возвращает словарь:
    { "шифр": {"members": [...], "code": "шифр"} }

    :param class_name: Принимает имя класса, в котором будет атрибут для
     хранения возвращаемых значений

    :return: Optional[Dict[str, Dict]] - возвращает словарь с данными комиссии
    """

    Rich.print_spacer()
    Rich.simple_log("Парсинг комиссии.")

    # Определяем файл в зависимости от семестра
    if class_name.radio_button_1.isChecked():
        path = getattr(class_name, "history_commission_path", None)
        commission_name = "История"
        semester_name = "Первый семестр"
    elif class_name.radio_button_2.isChecked():
        path = getattr(class_name, "foreign_commission_path", None)
        commission_name = "Иностранный"
        semester_name = "Второй семестр"
    else:
        path = getattr(class_name, "specialization_commission_path", None)
        commission_name = "Специальность"
        semester_name = "Третий семестр"

    if not path:
        QMessageBox.warning(class_name, "Ошибка",
                            f"Сначала выберите файл комиссии '{commission_name}'!")
        Rich.log_error("Ошибка. сначала выберите файл комиссии")
        return None

    if not os.path.exists(path):
        QMessageBox.warning(class_name, "Ошибка", f"Файл не существует: {path}")
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

        class_name.commissions_by_code = commissions_by_code

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
                class_name,
                "Ошибка",
                f"Не удалось найти членов комиссии в файле:\n{path}\n\n"
            )

            return

        return commissions_by_code

    except Exception as e:
        Rich.log_error(f"Ошибка при парсинге комиссии: {e}")
        traceback.print_exc()
        QMessageBox.critical(
            class_name,
            "Ошибка",
            f"Не удалось прочитать файл комиссии:\n{str(e)}"
        )
        return None
