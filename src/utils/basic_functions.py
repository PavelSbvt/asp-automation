import re

import pandas as pd

from utils.output_rich import Rich


def remove_trailing_dot(text: str) -> str:
    """
    Убирает точку в конце строки, если она там есть.
    Также обрабатывает None, nan и пустые строки.

    :param text: Принимает текст, в котором нужно ужалить точку в конце

    :return: Str - возвращает строку без точки в конце.
    """

    if text is None or pd.isna(text):
        return ""
    text = str(text).strip()
    if text.endswith('.'):
        return text[:-1]
    return text


def normalize_initials(name: str) -> str:
    """
    Нормализует инициалы: приводит к формату с пробелом между инициалами.

    :param name: Принимает строку с ФИО

    :return: str - нормализованная строка с пробелом между инициалами
    """

    if not name or name == "nan":
        return name

    # Паттерн: буква, точка, буква, точка (без пробела)
    pattern = r'([А-ЯЁ]\.)([А-ЯЁ]\.)'
    result = re.sub(pattern, r'\1 \2', name)

    return result


def extract_code_from_row(row, code_col) -> str:
    """
    Извлекает шифр из строки таблицы комиссий.
    Если написано "Все" — возвращает "ALL".
    Если есть шифр формата 2.2.12. — возвращает его.

    :param row:

    :param code_col:

    :return: str - если находит подходящий шифр, возвращает содержимое ячейки
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
    """
    Извлекает ФИО из текста (фамилия + инициалы)

    :param text: Str - принимает текст, в котором нужно найти ФИО.

    :return: Str - возвращает строку с найденным ФИО (если не найдёт ФИО,
    вернёт пустую строку)
    """

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
    """
    Извлекает инициалы из текста

    :param text: Str - принимает текст и передаёт его функции поиска ФИО в тексте.

    :return: Str - строку с найденным ФИО
    """

    return extract_fio_from_text(text)


def extract_commission_members(text: str,
    commissions_dict: dict, row, code_col: str) -> None:
    """
    Извлекает членов комиссии из текста и сохраняет в словарь commissions_dict
    по ключу-шифру.

    :param row: Строка таблицы с данными о специальности

    :param text: Str - текст строки таблицы с ФИО и ролями членов комиссии.

    :param commissions_dict: Dict - словарь, в который сохраняются
        данные о комиссиях по шифрам

    :param code_col: Str - имя колонки с шифром специальности

    :return: None
    """

    if not text or len(text) < 10:
        return

    code = None
    science_branch = ""

    if code_col is not None:
        code_value = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""

        code_match = re.search(r'(\d+\.\d+\.\d+)', code_value)
        if code_match:
            code = code_match.group(1)

        science_match = re.search(r'\(([^)]+)\)', code_value)
        if science_match:
            science_branch = science_match.group(1).strip()
            Rich.debug_log(f"Найдена наука: '{science_branch}' для шифра {code}")

    if not code:
        code_match = re.search(r'(\d+\.\d+\.\d+)', text)
        if code_match:
            code = code_match.group(1)

    if not code:
        Rich.warning_log(f"Не удалось извлечь шифр из строки: {text[:50]}...")
        return

    if code not in commissions_dict:
        commissions_dict[code] = {
            'code': code,
            'members': [],
            'science_branch': science_branch
        }

    split_text = re.sub(r',?\s*член\s+комиссии\s*', '', text, flags=re.IGNORECASE)
    split_text = split_text.rstrip(',').strip()

    if not split_text:
        return

    parts = []

    if not parts:
        parts = [p.strip() for p in split_text.split(';') if p.strip()]

    if len(parts) <= 1:
        parts = [p.strip() for p in split_text.split(',') if p.strip()]

    if len(parts) <= 1:
        parts = [p.strip() for p in re.split(r'\.\s+', split_text) if p.strip()]

    if len(parts) <= 1:
        parts = [p.strip() for p in split_text.split('.') if p.strip()]

    if not parts:
        parts = [split_text]

    for part in parts:
        if not part:
            continue

        part_lower = part.lower()

        role = 'член'  # По умолчанию

        if 'председатель' in part_lower:
            role = 'председатель'
        elif 'заместитель' in part_lower or 'зам.' in part_lower:
            role = 'заместитель'
        elif 'секретарь' in part_lower:
            role = 'секретарь'
        elif 'член' in part_lower:
            role = 'член'

        clean_part = re.sub(
            r',?\s*член\s+комиссии\s*', '', part, flags=re.IGNORECASE)
        clean_part = re.sub(
            r',?\s*председатель\s+комиссии\s*', '', clean_part, flags=re.IGNORECASE)
        clean_part = clean_part.rstrip(',').strip()

        if not clean_part:
            continue

        fio = extract_fio_from_text(clean_part)

        if not fio and clean_part:
            fio = clean_part

        if fio:
            fio = normalize_initials(fio)

            if re.search(
                    r'[А-ЯЁ][а-яё]+',
                    fio) and re.search(r'[А-ЯЁ]\.', fio):
                commissions_dict[code]['members'].append({
                    'fio': fio,
                    'role': role,
                    'full_text': clean_part,
                    'initials': fio
                })

    if len(commissions_dict[code]['members']) == 0 and len(parts) >= 3:
        roles = ['председатель', 'заместитель', 'член']
        for i, part in enumerate(parts[:3]):
            if not part:
                continue
            fio = extract_fio_from_text(part)
            if not fio:
                fio = part
            if fio:
                fio = normalize_initials(fio)

                clean_part = re.sub(
                    r',?\s*член\s+комиссии\s*',
                    '', part, flags=re.IGNORECASE)
                clean_part = re.sub(
                    r',?\s*председатель\s+комиссии\s*',
                    '', clean_part, flags=re.IGNORECASE)
                clean_part = clean_part.rstrip(',').strip()

                commissions_dict[code]['members'].append({
                    'fio': fio,
                    'role': roles[i] if i < len(roles) else 'член',
                    'full_text': clean_part,
                    'initials': fio
                })


def extract_code_number(raw_code: str) -> str:
    """
    Извлекает код специальности из строки.
    Пример: "2.2.12." -> "2.2.12."

    :param raw_code: Str - строка, из которой нужно извлечь код

    :return: Str - код специальности или исходная строка, если код не найден.
    """

    if not raw_code:
        return ""
    match = re.search(r'(\d+\.\d+\.\d+\.?)', raw_code)
    if match:
        return match.group(1)
    return raw_code.strip()
