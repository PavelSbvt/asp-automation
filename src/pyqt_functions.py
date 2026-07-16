import os
import re
import shutil
import traceback
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from PyQt6.QtWidgets import QMessageBox

from parsing_functions import parsing_commissions, site_parce_main, site_parce_dn
from generate_pdf_from_db import generate_pdf_from_db
from general_functions import extract_code_number, remove_trailing_dot


def get_specialty_code(profile: str) -> str:
    """
    Возвращает код специальности по названию профиля из данных сайта.
    :return: str
    """

    try:
        # пробуем основной сайт
        specialties = site_parce_main()
        if not specialties:
            specialties = site_parce_dn()
        for code, name in specialties:
            if profile.lower() in name.lower():
                return code
        return ""   # не найдено соответствие
    except Exception:
        # Любая ошибка (сеть, таймаут) - возвращаем пустую строку
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
        direction_code = get_specialty_code(student['profile'])
        if not direction_code:
            direction_code = student['profile']

        clean_code = extract_code_number(direction_code)
        if not clean_code:
            clean_code = direction_code.strip()

        # ===== ИЩЕМ КОМИССИЮ =====
        student_comm = None

        # 1. Пробуем найти по точному коду
        if clean_code in commission_dict:
            student_comm = commission_dict[clean_code]
            print(f"[I] Найдена комиссия по точному коду: {clean_code}")

        # 2. Если не нашли - пробуем найти по части кода
        if not student_comm:
            for key, comm in commission_dict.items():
                # Пропускаем "ALL" пока
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

        # Используем full_text или fio, если full_text нет
        pred_text = remove_trailing_dot(clean_excel_string(pred.get('full_text',
                                                pred.get('fio', '')))) if pred else ''
        pred_fio = remove_trailing_dot(clean_excel_string(pred.get(
            'fio', ''))) if pred else ''
        zam_text = remove_trailing_dot(clean_excel_string(zam.get('full_text',
                                                zam.get('fio', '')))) if zam else ''
        zam_fio = remove_trailing_dot(clean_excel_string(zam.get(''
                                                    'fio', ''))) if zam else ''
        chlen_text = remove_trailing_dot(
            clean_excel_string(chlen.get('full_text', chlen.get('fio',
                                                    '')))) if chlen else ''
        chlen_fio = remove_trailing_dot(clean_excel_string(chlen.get('fio',
                                                        ''))) if chlen else ''

        fio_clean = clean_excel_string(student['fio'])
        profile_clean = clean_excel_string(student['profile'])
        direction_clean = clean_excel_string(clean_code)

        if hasattr(self, 'selected_semester'):
            if self.selected_semester == 1:
                discipline_text = "История и философия науки"
            elif self.selected_semester == 2:
                discipline_text = "Иностранный язык (английский)"
            else:
                discipline_text = profile_clean
        else:
            discipline_text = profile_clean

        row = [
            _get_fio_genitive(student['fio'], student.get('citizenship', 'РФ')).upper(),
            discipline_text,
            self.commission_text,
            pred_text,
            _get_fio_initials(pred_fio) if pred else '',
            zam_text,
            _get_fio_initials(zam_fio) if zam else '',
            chlen_text,
            _get_fio_initials(chlen_fio) if chlen else '',
            fio_clean,
            direction_clean + " " + profile_clean
        ]
        data_rows.append(row)

    df = pd.DataFrame(data_rows, columns=columns)

    # Путь к выходному файлу
    output_path = Path('resources/docs/temporary_protocol_db_sheet.xlsx')
    output_path = str(output_path.absolute())

    # Определяем путь к файлу-шаблону (корень проекта)
    template_file = Path('resources/docs/Protocol_template.xlsx')
    template_file = str(template_file.absolute())

    if not os.path.exists(template_file):
        print(f"[E] Файл шаблона не найден: {template_file}")
        return None

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy(template_file, output_path)
        print(f"[I] Шаблон скопирован в {output_path}")
    except Exception as e:
        print(f"[E] Ошибка при копировании шаблона: {e}")
        return None

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

def _get_fio_genitive(fio: str, citizenship: str = "РФ") -> str:
    """
    функция для склонения ФИО из И.п. в Р.п. - слушали.
    :return: string
    """

    # Преобразует ФИО в родительный падеж
    # Для граждан РФ - склоняем, для иностранцев - нет
    if citizenship != "Россия":
        return fio

    parts = fio.split()
    if len(parts) < 3:
        return fio

    surname = parts[0]
    name = parts[1]
    patronymic = parts[2]

    # Склоняем фамилию
    if surname.endswith('ов'):
        surname_gen = surname[:-2] + 'ова'
    elif surname.endswith('ев'):
        surname_gen = surname[:-2] + 'ева'
    elif surname.endswith('ин'):
        surname_gen = surname[:-2] + 'ина'
    elif surname.endswith('ий'):
        surname_gen = surname[:-2] + 'ого'
    elif surname.endswith('ова'):
        surname_gen = surname[:-1] + 'у'
    elif surname.endswith('ева'):
        surname_gen = surname[:-1] + 'у'
    else:
        surname_gen = surname + 'а'

    # Склоняем имя
    if name.endswith('й'):
        name_gen = name[:-1] + 'я'
    elif name.endswith('а'):
        name_gen = name[:-1] + 'у'
    else:
        name_gen = name + 'а'

    # Склоняем отчество
    if patronymic.endswith('ич'):
        patronymic_gen = patronymic[:-2] + 'ича'
    elif patronymic.endswith('на'):
        patronymic_gen = patronymic[:-1] + 'у'
    else:
        patronymic_gen = patronymic + 'а'
    return f"{surname_gen} {name_gen} {patronymic_gen}"

def _get_fio_initials(fio: str) -> str:
    """
    Преобразует ФИО в формат / И.О. Фамилия /
    :return: string
    """
    parts = fio.split()
    if len(parts) < 2:
        return fio
    surname = parts[0]
    # Все части после фамилии объединяем в одну строку, оставляем только буквы
    letters = [c for c in ''.join(parts[1:]) if c.isalpha()]
    if not letters:
        return fio
    initials = '.'.join(letters) + '.'
    result = f"/ {initials} {surname} /"
    # ← Убираем точку в конце, если она есть
    if result.endswith(' . /'):
        result = result[:-3] + ' /'
    return result

def parsing(self) -> None:
    """
    Функция парсинга данных
    :param self:
    :return: None
    """

    print("[I] НАЧАЛО ПАРСИНГА")

    # Проверки
    print("[I] Проверяю наличие файлов...")
    if (not hasattr(self, 'universal_file_path')
            or not self.universal_file_path):
        # Если у объекта self нет атрибута с именем
        # 'universal_file_path' или атрибут существует, но он пустой
        QMessageBox.warning(self, "Ошибка",
                    "Сначала выберите универсальную таблицу!")
        # Выскочит короткий QMessageBox с предупреждением
        print("[E] Не выбрана универсальная таблица")
        return

    print("[I] Универсальный файл есть")

    if (not self.radio_button_1.isChecked() and not self.radio_button_2.isChecked()
            and not self.radio_button_3.isChecked()):
        # Если ни одна кнопка QRadioButton не выбрана
        QMessageBox.warning(self, "Ошибка", "Выберите семестр!")
        # Тоже появится предупреждение, о том что не выбран семестр
        print("[E] Не выбран семестр")
        return

    print("[I] Семестр выбран")

    # Сохраняем текст приказа
    print("[I] Сохраняю текст приказа") # лог для отладки
    self.commission_text = self.input_commission.text().strip()
    print(f"[I] Текст приказа: {self.commission_text[:30]}...")
    # для отладки - вывод кусочка вписанного в поле приказа

    # Определяем семестр
    print("[I] Определение семестра.")
    if self.radio_button_1.isChecked(): # если радиокнопка нажата, то вернёт True
        self.selected_semester = 1
        self.semester_name = "Первый семестр"
    elif self.radio_button_2.isChecked(): ## ели вторая нажата, то вернёт True
        self.selected_semester = 2
        self.semester_name = "Второй семестр"
    else: # иначе приравняет вспомогательные переменные к 3 семестру.
        self.selected_semester = 3
        self.semester_name = "Третий семестр"

    print(f"[I] Семестр: {self.semester_name}")
    # соответственно после предыдущего блока кода переменная имя
    # семестра будет вмещать имя текущего выбранного семестра и выведет в лог

    # Читаем Excel файл
    print("[I] Чтение универсальной таблицы.")
    try:
        df = pd.read_excel(
            # df - сокращение от dataframe - таблицы в пандас,
            # обращаемся к библиотеке пандас, методу чтения таблиц, присваивая таблицу,
            # которую возвращает метод чтения переменной
            self.universal_file_path,
            # путь к таблице. он принадлежит классу и прописан ранее в коде
            dtype=str,
            # читать данные как текст
            engine='openpyxl'
            # использовать библиотеку openpyxl для чтения файла. движок
        )
        print(f"[I] Загружено {len(df)} строк")

        # Ищем нужные колонки по названиям
        columns = list(df.columns)
        print(f"[I] Колонки: {columns[:5]}...")

        # Находим индексы нужных колонок
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

        # Если не нашли по названиям - используем индексы из теста
        if fio_idx is None:
            fio_idx = 2  # ФИО
        if profile_idx is None:
            profile_idx = 22  # ПРОФИЛЬ
        if citizenship_idx is None:
            citizenship_idx = 40  # ГРАЖДАНСТВО

        print(f"[I] Индексы: ФИО={fio_idx}, Профиль={profile_idx}, "
              f"Гражданство={citizenship_idx}")

        # Извлекаем данные
        students_data = []
        for index, row in df.iterrows():
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
                print(f"[E] Ошибка строки {index}: {e}")
                continue

        self.students_data = students_data
        print(f"[I] Всего студентов: {len(students_data)}")

        print("[I]Начало парсинга doc-ов комиссии")
        commission_members = parsing_commissions(self)
        if commission_members:
            self.commission_members = commission_members
            print(f"[I] Найдено комиссий: {len(commission_members)}")
        else:
            print("[E] Члены комиссии не найдены!")
            self.commission_members = []  # чтобы не упало в fill_database_sheet
        print("[I] Завершение парсинга doc-ов комиссии")

        for i, student in enumerate(students_data, 1):
            print(f"[I]      {i}. {student['fio']}")

    except Exception as e:
        print(f"[E] Ошибка: {e}")
        # traceback.print_exc()
        QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл:\n{str(e)}")
        return

    print("[S] Парсинг таблицы завершён")

    # Проверяем данные
    print("[I] Проверяю данные студентов...")
    if not hasattr(self, 'students_data') or not self.students_data:
        QMessageBox.warning(self, "Ошибка",
                            "Не удалось загрузить данные из универсальной таблицы!")
        return
    print(f"[I] Загружено {len(self.students_data)} студентов")

    # Заполняем БД
    print("[I] Заполняю БД...")
    try:
        db_file = fill_database_sheet(self)
        if db_file:
            self.generated_db_path = db_file
            print(f"[I] БД сохранена: {db_file}")
            # Теперь генерация PDF
            generate_pdf_from_db(self, self.generated_db_path)
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл БД!")
            print("[E] Ошибка. Не удалось сохранить файл БД!")
            return
    except Exception as e:
        traceback.print_exc()
        QMessageBox.critical(self,"Ошибка", f"Ошибка при создании БД или PDF:\n{str(e)}")
        print(f"[E] Ошибка. Ошибка при создании БД или PDF:{str(e)}")
        return
    print("[I] КОНЕЦ ПАРСИНГА")
