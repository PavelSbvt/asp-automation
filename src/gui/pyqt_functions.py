import traceback

import pandas as pd
from PyQt6.QtWidgets import QMessageBox

from src.core.parsing.parsing_functions import parsing_commissions
from src.core.generate_pdf_from_db import generate_pdf_from_db
from src.core.fill_db_sheet import fill_database_sheet


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
