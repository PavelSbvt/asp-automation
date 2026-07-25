import re
from typing import Dict

import pandas as pd


def remove_trailing_dot(text) -> str:
    """
    Убирает точку в конце строки, если она там есть.
    Также обрабатывает None, nan и пустые строки.
    """
    if text is None or pd.isna(text):
        return ""
    text = str(text).strip()
    if text.endswith('.'):
        return text[:-1]
    return text

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

def extract_code_from_row(row, code_col) -> str:
    """
    Извлекает шифр из строки таблицы комиссий.
    Если написано "Все" — возвращает "ALL".
    Если есть шифр формата 2.2.12. — возвращает его.
    """
    if code_col is None:
        return "UNKNOWN"

    code = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""

    # Если написано "Все" — это значит, что комиссия для всех шифров
    if code.lower() == "все" or "все" in code.lower():
        return "ALL"

    # Пробуем извлечь шифр формата 2.2.12.
    match = re.search(r'(\d+\.\d+\.\d+\.?)', code)
    if match:
        return match.group(1)

    return code

def extract_fio_from_text(text: str) -> str:
    """Извлекает ФИО из текста (фамилия + инициалы)"""
    if not text:
        return ""
    # Ищем фамилию с инициалами в начале строки
    match = re.search(r'^([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.?)?)', text)
    if match:
        return match.group(1).strip()
    # Если не нашло, пробуем найти фамилию с именем и отчеством
    match = re.search(r'^([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)', text)
    if match:
        return match.group(1).strip()
    return text[:30].strip()

def extract_initials_from_text(text: str) -> str:
    """Извлекает инициалы из текста"""
    return extract_fio_from_text(text)

def _extract_commission_members(text: str, commissions_dict: Dict, row, code_col: str) -> None:
    """
    Извлекает членов комиссии из текста и сохраняет в словарь commissions_dict
    по ключу-шифру.
    """
    if not text or len(text) < 10:
        return

    # ===== ИЗВЛЕКАЕМ ШИФР И НАУКУ ИЗ ВТОРОЙ КОЛОНКИ =====
    code = None
    science_branch = ""

    if code_col is not None:
        code_value = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""

        # Ищем код формата 2.2.8, 2.2.11, 4.3.1
        code_match = re.search(r'(\d+\.\d+\.\d+)', code_value)
        if code_match:
            code = code_match.group(1)

        # Ищем текст в скобках (науку)
        science_match = re.search(r'\(([^)]+)\)', code_value)
        if science_match:
            science_branch = science_match.group(1).strip()
            print(f"[I] Найдена наука: '{science_branch}' для шифра {code}")

    # Если код не нашёлся — пробуем извлечь из текста
    if not code:
        code_match = re.search(r'(\d+\.\d+\.\d+)', text)
        if code_match:
            code = code_match.group(1)

    if not code:
        print(f"[W] Не удалось извлечь шифр из строки: {text[:50]}...")
        return

    if code not in commissions_dict:
        commissions_dict[code] = {
            'code': code,
            'members': [],
            'science_branch': science_branch  # ← СОХРАНЯЕМ НАУКУ
        }

    # Разбиваем текст по ";" на части
    parts = [p.strip() for p in text.split(';') if p.strip()]

    # Если не разбилось по ";", пробуем по ". "
    if len(parts) <= 1:
        parts = [p.strip() for p in re.split(r'\.\s*[А-ЯЁ]', text) if p.strip()]

    # Проходим по частям и ищем роли
    for part in parts:
        part_lower = part.lower()
        role = None
        if 'председатель' in part_lower:
            role = 'председатель'
        elif 'заместитель' in part_lower:
            role = 'заместитель'
        elif 'член' in part_lower:
            role = 'член'

        if role:
            fio = extract_fio_from_text(part)
            if fio:
                commissions_dict[code]['members'].append({
                    'fio': fio,
                    'role': role,
                    'full_text': part,
                    'initials': fio
                })

    # Если не нашли по ролям — распределяем по порядку
    if len(commissions_dict[code]['members']) == 0 and len(parts) >= 3:
        roles = ['председатель', 'заместитель', 'член']
        for i, part in enumerate(parts[:3]):
            fio = extract_fio_from_text(part)
            if fio:
                commissions_dict[code]['members'].append({
                    'fio': fio,
                    'role': roles[i] if i < len(roles) else 'член',
                    'full_text': part,
                    'initials': fio
                })

def extract_code_number(raw_code: str) -> str:
    """
    Извлекает код специальности из строки.
    Пример: "2.2.12." -> "2.2.12."
    """
    if not raw_code:
        return ""
    match = re.search(r'(\d+\.\d+\.\d+\.?)', raw_code)
    if match:
        return match.group(1)
    return raw_code.strip()