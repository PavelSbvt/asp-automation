import re
from typing import Dict, List

import pandas as pd


def print_out_string(text: str) -> None:
    """
    Функция для красивого вывода строки логгирования в консоль
    :param text: str
    :return: None
    """
    out_string_size = 150
    if len(text) % 2 != 0:
        text += " "

    output_string = ("|" + " " * int((out_string_size - len(text) - 2) / 2) +
                     text + " " * int((out_string_size - len(text) - 2) / 2) + "|")
    print(output_string)

def print_separator() -> None:
    """
    Функция для вывода разделителя - для читаемости консоли.
    Строка из нижних подчёркиваний.
    :return: None
    """

    print("|" + "_" * 148 + "|")

def print_separator_points() -> None:
    """
    Функция для вывода разделителя - для читаемости консоли.
    Строка из точек.
    :return: None
    """

    print("|" + "." * 148 + "|")

def print_big_separator() -> None:
    """
    Функция для вывода разделителя - для читаемости консоли.
    Строка из нижних знаков равно.
    :return: None
    """

    print("|" + "=" * 148 + "|")

def extract_code_number(text: str) -> str:
    """
    Извлекает код специальности вида 1.2.3 из строки.
    :return: string
    """

    if not isinstance(text, str):
        return ""
    match = re.search(r'\d{1,2}\.\d{1,2}\.\d{1,2}', text)
    return match.group(0) if match else text.strip()

def _extract_commission_members(text: str, members_by_specialty: List[Dict],
                                row=None, code_col=None) -> None:
    """
    Извлечение членов комиссии из текста одной строки таблицы
    :return: None
    """

    # Получаем шифр специальности
    code = ""
    if row is not None and code_col is not None and code_col in row:
        raw_code = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""
        code = extract_code_number(raw_code)

    # Разбиваем текст по точкам с запятой
    parts = re.split(r'[;]', text)

    members = []

    for part in parts:
        part = part.strip()
        if not part or len(part) < 5:
            continue

        fio_match = re.search(
            r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.?|'
            r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)',
            part
        )

        if not fio_match:
            continue

        fio = fio_match.group(1)

        role = "член"
        part_lower = part.lower()
        if "председатель" in part_lower:
            role = "председатель"
        elif "заместитель" in part_lower:
            role = "заместитель"
        elif "член" in part_lower:
            role = "член"

        if not any(m['fio'] == fio for m in members):
            members.append({
                'fio': fio,
                'role': role,
                'full_text': part
            })

    if members:
        members_by_specialty.append({
            'code': code,
            'members': members
        })
