import os
import re
import shutil
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from general_functions import extract_code_number, remove_trailing_dot
from declension_full_name import _get_fio_accusative, _get_fio_initials
from sait_parsing import load_specialties_from_cache


def get_specialty_code(profile: str) -> str:
    """
    Возвращает код специальности по названию профиля.
    Данные берутся ТОЛЬКО из локального файла кэша.
    Интернет НЕ используется.
    :return: str
    """
    try:
        # Загружаем данные из кэша
        specialties = load_specialties_from_cache()

        # Если файла нет - возвращаем пустую строку
        if specialties is None:
            print("[E] Файл кэша не найден! Данные не загружены.")
            return ""

        # Ищем совпадение с профилем
        for code, name in specialties:
            if profile.lower() in name.lower():
                return code

        # Если не нашли - возвращаем пустую строку
        return ""

    except Exception as e:
        print(f"[E] Ошибка в get_specialty_code: {e}")
        return ""

def clean_excel_string(s: str) -> str:
    """
    очистить строку от непечатаемых управляющих символов
    :return: string
    """

    if not isinstance(s, str):
        return s
    # Удаляем все управляющие символы, кроме \t, \n, \r
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    return cleaned

def fill_database_sheet(self) -> Optional[str]:
    """
    функция заполнения листа БД таблицы-шаблона
    :return: None
    """

    print("[I] fill_database_sheet через pandas")

    if not hasattr(self, 'students_data') or not self.students_data:
        print("[E] Нет студентов!")
        return None

    # Столбцы итоговой таблицы
    columns = [
        'СЛУШАЛИ',  # 0
        'Прием кандидатского экзамена по дисциплине',  # 1
        'Направление',  # 2
        'Председатель комиссии',  # full_text
        'ФИО',  # инициалы председателя
        'Члены комиссии №1:',  # full_text зама
        'ФИО',  # инициалы зама
        'Члены комиссии №2:',  # full_text члена
        'ФИО',  # инициалы члена
        'ПОСТАНОВИЛИ',  # 9
        'НАПРАВЛЕНИЕ'  # 10
    ]

    # ===== Строим словарь комиссий по коду специальности =====
    commission_dict = {}
    commission_members = getattr(self, 'commission_members', {})

    # Переменная для хранения комиссии "Все"
    all_commission = None

    if isinstance(commission_members, dict):
        for code, comm in commission_members.items():
            # Очищаем код от мусорных символов
            clean_key = re.sub(r'[\x00-\x1f\x7f]', '', code).strip()

            # Проверяем, есть ли в ключе слово "Все"
            if 'Все' in clean_key:
                all_commission = comm
                commission_dict["ALL"] = comm
                print(f"[I] Найдена комиссия 'Все'")
            else:
                raw_code = comm.get('code', '')
                clean_code = extract_code_number(raw_code)
                if clean_code:
                    commission_dict[clean_code] = comm
                elif clean_key:
                    commission_dict[clean_key] = comm
    else:
        # Если это список (старый формат)
        for comm in commission_members:
            raw_code = comm.get('code', '')
            clean_code = extract_code_number(raw_code)
            if clean_code:
                commission_dict[clean_code] = comm
            else:
                # Если нет кода - считаем это комиссией "Все"
                all_commission = comm
                commission_dict["ALL"] = comm

    # Если явно не нашли "Все" - ищем в ключах
    if not all_commission:
        for key in commission_dict.keys():
            if 'Все' in key or 'ALL' in key:
                all_commission = commission_dict[key]
                break

    print("[I] Ключи словаря комиссий:", list(commission_dict.keys()))

    def get_member_by_role(comm: Optional[Dict], role: str) -> Optional[Dict]:
        if not comm:
            return None
        for m in comm.get('members', []):
            if m.get('role', '').lower() == role:
                return m
        return None

    data_rows = []
    for student in self.students_data:
        # Получаем код направления
        direction_code = get_specialty_code(student['profile'])
        if not direction_code:
            direction_code = student['profile']

        # Очищаем код
        clean_code = extract_code_number(direction_code)
        if not clean_code:
            clean_code = direction_code.strip()

        # Сохраняем очищенный код для использования
        direction_clean = clean_excel_string(clean_code)

        # ===== ИЩЕМ КОМИССИЮ =====
        student_comm = None

        # 1. Пробуем найти по точному коду
        if clean_code in commission_dict:
            student_comm = commission_dict[clean_code]
            print(f"[I] Найдена комиссия по точному коду: {clean_code}")

        # 2. Если не нашли - пробуем найти по части кода
        if not student_comm:
            for key, comm in commission_dict.items():
                # Пропускаем "ALL"
                if key == "ALL":
                    continue
                # Очищаем ключ от мусора
                clean_key = re.sub(r'[\x00-\x1f\x7f]', '', key).strip()
                # Проверяем, начинается ли ключ с первых двух цифр
                key_parts = clean_key.split('.')
                code_parts = clean_code.split('.')
                if len(key_parts) >= 2 and len(code_parts) >= 2:
                    if key_parts[0] == code_parts[0] and key_parts[1] == code_parts[1]:
                        student_comm = comm
                        print(f"[I] Найдена комиссия по части кода: {clean_key}")
                        break

        # 3. Если всё ещё не нашли - берём комиссию "Все"
        if not student_comm and all_commission:
            student_comm = all_commission
            print(f"[I] Использую комиссию 'Все' для {student['fio']}")

        # 4. Если и "Все" нет - берём первую попавшуюся
        if not student_comm and commission_dict:
            student_comm = list(commission_dict.values())[0]
            print(f"[I] Использую первую попавшуюся комиссию для {student['fio']}")

        # Получаем членов комиссии
        pred = get_member_by_role(student_comm, 'председатель')
        zam = get_member_by_role(student_comm, 'заместитель')
        chlen = get_member_by_role(student_comm, 'член')

        # Извлекаем науку из комиссии
        science_branch = student_comm.get('science_branch', '') if student_comm else ''

        # Используем full_text или fio, если full_text нет
        pred_text = remove_trailing_dot(clean_excel_string(pred.get('full_text', pred.get('fio', '')))) if pred else ''
        pred_fio = remove_trailing_dot(clean_excel_string(pred.get('fio', ''))) if pred else ''
        zam_text = remove_trailing_dot(clean_excel_string(zam.get('full_text', zam.get('fio', '')))) if zam else ''
        zam_fio = remove_trailing_dot(clean_excel_string(zam.get('fio', ''))) if zam else ''
        chlen_text = remove_trailing_dot(
            clean_excel_string(chlen.get('full_text', chlen.get('fio', '')))) if chlen else ''
        chlen_fio = remove_trailing_dot(clean_excel_string(chlen.get('fio', ''))) if chlen else ''

        fio_clean = clean_excel_string(student['fio'])
        profile_clean = clean_excel_string(student['profile'])

        # Формируем полное направление (код + название)
        full_direction = direction_clean + " " + profile_clean

        # Добавляем науку в конец, если она есть
        if science_branch:
            full_direction += f", {science_branch}"
            print(f"[I] Добавлена наука '{science_branch}' для {student['fio']}")

        # Определяем дисциплину в зависимости от семестра
        if hasattr(self, 'selected_semester'):
            if self.selected_semester == 1:
                discipline_text = "История и философия науки"
            elif self.selected_semester == 2:
                discipline_text = "Иностранный язык (английский)"
            else:
                discipline_text = profile_clean
        else:
            discipline_text = profile_clean

        # Формируем строку для БД
        row = [
            _get_fio_accusative(student['fio'], student.get('citizenship', 'РФ')).upper(),
            discipline_text,
            self.commission_text,
            pred_text,
            _get_fio_initials(pred_fio) if pred else '',
            zam_text,
            _get_fio_initials(zam_fio) if zam else '',
            chlen_text,
            _get_fio_initials(chlen_fio) if chlen else '',
            fio_clean,
            full_direction
        ]
        data_rows.append(row)

    # Создаем DataFrame
    df = pd.DataFrame(data_rows, columns=columns)

    # Путь к выходному файлу
    output_path = (Path(__file__).parent.parent / "resources" /
                   "docs" / "temporary_protocol_db_sheet.xlsx")
    output_path = str(output_path.absolute())

    # Определяем путь к файлу-шаблону (корень проекта)
    template_file = (Path(__file__).parent.parent / "resources" /
                     "docs" / "Protocol_template.xlsx")
    template_file = str(template_file.absolute())

    if not os.path.exists(template_file):
        print(f"[E] Файл шаблона не найден: {template_file}")
        return None

    # Копируем шаблон в целевой файл
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy(template_file, output_path)
        print(f"[I] Шаблон скопирован в {output_path}")
    except Exception as e:
        print(f"[E] Ошибка при копировании шаблона: {e}")
        return None

    # Добавляем лист «БД» в скопированный файл
    try:
        with pd.ExcelWriter(
                output_path,
                engine='openpyxl',
                mode='a',
                if_sheet_exists='replace'
        ) as writer:
            print("[I] [debag] ПРОВЕРКА ДАННЫХ БД ")
            for i, row in enumerate(data_rows[:3]):  # выводим первые 3 строки
                print(f"  Строка {i + 1}:")
                print(f"  СЛУШАЛИ: {row[0]}")
                print(f"  Дисциплина: {row[1]}")
                print(f"  Направление: {row[2]}")
                print(f"  Председатель (full_text): {row[3]}")
                print(f"  Председатель (ФИО): {row[4]}")
                print(f"  Зам (full_text): {row[5]}")
                print(f"  Зам (ФИО): {row[6]}")
                print(f"  Член (full_text): {row[7]}")
                print(f"  Член (ФИО): {row[8]}")
                print(f"  ПОСТАНОВИЛИ: {row[9]}")
                print(f"  НАПРАВЛЕНИЕ: {row[10]}")
                print("-" * 40)
            df.to_excel(writer, sheet_name='БД', index=False)
        print(f"[S] Лист 'БД' успешно добавлен в {output_path}")
    except Exception as e:
        print(f"[E] Ошибка при записи листа БД: {e}")
        return None

    return output_path
