import os
import re
import shutil # встроенная библиотека Python для работы с файлами и папками
import subprocess
import traceback
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import aspose.words as aw
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, Side
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox


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

def open_pdf_folder(self) -> None:
    """
    Функция для открытия папки сохранения пдф.
    :param self:
    :return: None
    """

    folder_path = self.save_folder_path
    if not Path(folder_path).exists():
        QMessageBox.warning(
            self,
            "Папка не найдена",
            f"Папка '{folder_path}' не существует.\n\n"
            f"Сначала создайте PDF файлы, нажав кнопку "
            f"'Запустить' на первой вкладке."
        )
        print(f"[E] Папка не найдена. Папка '{folder_path}' не существует."
        f" Сначала создайте PDF файлы, нажав кнопку 'Запустить' на первой вкладке.")
        return
    os.startfile(folder_path)

def choose_save_folder(self) -> None:
    """
    Функция для выбора папки сохранения для пдф
    :param self:
    :return: None
    """

    folder_path = QFileDialog.getExistingDirectory(
        self,
        "Выберите папку для сохранения PDF",
        self.save_folder_path
    )
    if folder_path:
        self.save_folder_path = folder_path
        short_path = self.save_folder_path
        if len(short_path) > 15:
            short_path = "..." + short_path[-12:]
        self.path_value_label.setText(short_path)
        self.path_value_label.setToolTip(self.save_folder_path)
        print_out_string(f"[I] Папка для сохранения изменена: {folder_path}")
        string_save_way = f"[I] Папка для сохранения изменена: {folder_path}"
        self.output_text.append(string_save_way)
        QApplication.processEvents()

def choose_file(self) -> None:
    """
    Функция для выбора файла обрабатываемой таблицы для генерации пдф.
    :param self:
    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName( #
        self,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )

    if file_path:
        self.excel_file_path = file_path
        string = f"[I] Выбран файл: {file_path}"
        print_out_string(string)
        self.output_text.append(string)
        QApplication.processEvents()

def get_pdf(self) -> None:
    """
    Функция, собирающая PDF по таблицу, которую выбирает пользователь
    :return: None
    """

    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    if not self.excel_file_path:
        print_big_separator()
        string_1 = "[E] ОШИБКА: Сначала выберите файл с данными!"
        print_out_string(string_1)
        self.output_text.append(string_1)
        QApplication.processEvents()
        print_big_separator()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return

    try:
        df = pd.read_excel(self.excel_file_path, sheet_name="БД", dtype=str)
    except Exception as e:
        print_big_separator()
        print_out_string(f"[E] ОШИБКА при чтении файла: {e}")
        self.output_text.append(f"[E] ОШИБКА при чтении файла: {e}")
        QApplication.processEvents()
        print_big_separator()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return

    EXCEL_FILE = self.excel_file_path
    print_big_separator()
    self.output_text.append("=" * 80)

    count_peoples_in_work = f"[I] Найдено {len(df)} человек"
    print_out_string(count_peoples_in_work)
    self.output_text.append(count_peoples_in_work)
    QApplication.processEvents()

    # прогресс бар
    self.progress_bar.setValue(0)
    self.progress_bar.setMaximum(100)

    print_big_separator()
    self.output_text.append("=" * 80)

    output_pdf_name = self.save_folder_path

    os.makedirs(f"{output_pdf_name}", exist_ok=True)

    processed_count = 0

    for string_number in range(len(df)):
        surname_datelnyi_p = str(df.iloc[string_number, 0]).strip()
        surname_name_p = str(df.iloc[string_number, 9]).strip()
        direction = str(df.iloc[string_number, 10]).strip()
        discipline = str(df.iloc[string_number, 1]).strip()

        processed_count += 1
        self.update_progress(processed_count, len(df))

        if surname_datelnyi_p == "nan" or surname_name_p == "nan" or surname_name_p =="":
            continue

        code = direction.split()[0] if direction and direction != "nan" else "unknown"

        msg = f"[I] Делаю PDF для: {surname_name_p}"
        print_out_string(msg)
        self.output_text.append(msg)
        QApplication.processEvents()

        print_separator_points()
        self.output_text.append("." * 80)

        wb = load_workbook(EXCEL_FILE)
        ws = wb["Протокол"]

        strings_with_data = [29, 39, 23, 14, 42, 17, 45, 19, 47]

        for row_num in range(1, 60):
            if row_num in strings_with_data:
                ws.row_dimensions[row_num].height = 15
            else:
                ws.row_dimensions[row_num].height = 15

        ws.row_dimensions[14].height = 35
        ws.row_dimensions[17].height = 35
        ws.row_dimensions[19].height = 35

        thin_border = Border(
            bottom=Side(border_style='thin', color='000000'))

        cell = ws['A1']
        text = (
            "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
"Федеральное государственное бюджетное образовательное учреждение высшего образования\n"
            "«Тамбовский государственный технический университет»"
        )
        cell.value = text
        cell.alignment = Alignment(horizontal='center',
                                   vertical='center', wrap_text=True)
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[1].height = 42

        cell = ws['A8']
        text_pr = (
            "ПРОТОКОЛ №___________"
        )
        cell.value = text_pr
        cell.alignment = Alignment(horizontal='center',
                                   vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=14, bold=True)
        ws.row_dimensions[8].height = 20

        cell = ws['A10']
        text_hc = (
            "от  «___»__________________20___г."
        )
        cell.value = text_hc
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[10].height = 15

        cell = ws['I5']
        text_M = (
            "___________Д.Ю. Муромцев"
        )
        cell.value = text_M
        cell.alignment = Alignment(horizontal='left',
                                   vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[5].height = 15

        cell = ws['I6']
        text_d = (
            "«___»______________20___г."
        )
        cell.value = text_d
        cell.alignment = Alignment(horizontal='left',
                                   vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[6].height = 15

        cell = ws.cell(row=29, column=3, value=surname_datelnyi_p)
        cell.alignment = Alignment(wrap_text=False,
                                   vertical='center', horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=39, column=4, value=surname_name_p)
        cell.alignment = Alignment(wrap_text=False,
                                   vertical='center', horizontal='center')

        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws['J39']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left',
                                   vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[21].height = 5
        ws.row_dimensions[25].height = 5
        ws.row_dimensions[28].height = 5

        cell = ws.cell(row=26, column=4, value=str(df.iloc[string_number, 1]))
        cell.alignment = Alignment(wrap_text=True,
                                   vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[26].height = 30

        cell = ws.cell(row=23, column=1, value=direction)
        cell.alignment = Alignment(wrap_text=True,
                                   vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[23].height = 30

        cell = ws.cell(row=14, column=1, value=str(df.iloc[string_number, 3]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=42, column=9, value=str(df.iloc[string_number, 4]))
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws.cell(row=17, column=1, value=str(df.iloc[string_number, 5]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=45, column=9, value=str(df.iloc[string_number, 6]))
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws.cell(row=19, column=1, value=str(df.iloc[string_number, 7]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=47, column=9, value=str(df.iloc[string_number, 8]))
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[44].height = 10

        ws.row_dimensions[33].height = 18
        ws.row_dimensions[34].height = 18
        ws.row_dimensions[35].height = 18
        ws.row_dimensions[36].height = 18
        ws.row_dimensions[37].height = 18

        ws.row_dimensions[2].height = 20
        ws.row_dimensions[7].height = 5

        cell = ws['A32']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['A33']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['A34']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['A35']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['A36']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['A37']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['E42']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['E45']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws['E47']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        if len(surname_name_p) > 35:
            ws.cell(row=39, column=4).font = Font(name='Times New Roman',
                                                  size=8, italic=True)
        else:
            ws.cell(row=39, column=4).font = Font(name='Times New Roman',
                                                  size=12, italic=True)

        file_name = f"{code} {surname_name_p}.xlsx"
        file_name = file_name.replace("/", "_").replace(
            "\\", "_").replace(":", "_").replace("*", "_")
        wb.save(file_name)

        excel_path = os.path.abspath(file_name)
        pdf_path = os.path.abspath(f"{output_pdf_name}/{code} {surname_name_p}.pdf")

        vba_script = f'''
               Dim xlApp
               Dim xlBook
               Set xlApp = CreateObject("Excel.Application")
               xlApp.Visible = False
               Set xlBook = xlApp.Workbooks.Open("{excel_path}")
               xlBook.Sheets(1).ExportAsFixedFormat 0, "{pdf_path}"
               xlBook.Close False
               xlApp.Quit
               '''

        with open("temp_convert.vbs", "w", encoding="windows-1251") as f:
            f.write(vba_script)

        subprocess.run(["cscript", "//Nologo", "temp_convert.vbs"], shell=True)

        os.remove("temp_convert.vbs")
        os.remove(file_name)

        msg = f"[S] Готов: {code} {surname_name_p}.pdf"

        print_out_string(msg)
        self.output_text.append(msg)
        QApplication.processEvents()

        print_separator()
        self.output_text.append("-" * 80)

    msg = (f"[S] Программа завершила работу. "
           f"Документы PDF сохранены в папке '{output_pdf_name}'")
    print_big_separator()
    print_out_string(msg)
    self.output_text.append(msg)
    print_big_separator()
    self.output_text.append("=" * 80)
    QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    self.progress_bar.setValue(100)


    QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
    QMessageBox.information(
        self,
        "Готово!",
        f"Создано PDF документов: {len(df)}\n\n"
        f"Папка сохранения: {output_pdf_name}",
        QMessageBox.StandardButton.Ok
    )
    print(f"[S] Готово! Создано PDF документов: {len(df)}. "
          f"Создано PDF документов: {len(df)}. Папка сохранения: {output_pdf_name}")

def choose_universal_excel(self) -> None:
    """
    выбор универсальной таблицы
    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )
    # если пользователь выбрал файл
    if file_path:
        # Сохраняем путь в атрибут класса
        self.universal_file_path = file_path
        selected_file = file_path

        # Обновляем label (показываем имя файла)
        if len(f"{os.path.basename(file_path)}") > 30:
            self.universal_excel_label.setStyleSheet(
                "font-size: 12px; color: white; background-color: rgb(105,208,73);")
            self.universal_excel_label.setText(f"{os.path.basename(file_path)}")
        else:
            self.universal_excel_label.setText(f"{os.path.basename(file_path)}")
            self.universal_excel_label.setStyleSheet(
                "font-size: 14px; color: white; background-color: rgb(105,208,73);")

        # return selected_file

        # Выводим в лог
        print(f"[I] Выбран файл: {file_path}")

def generate_pdf_from_db(self, excel_file_path: str) -> None:
    """
    Генерация PDF-протоколов на основе сгенерированного Excel-файла,
    содержащего листы «БД» и «Протокол».
    Для конвертации используется Microsoft Excel (через VBScript ExportAsFixedFormat).
    :return: None
    """

    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    if not excel_file_path:
        print_big_separator()
        print("[E] ОШИБКА: Не указан путь к файлу с данными!")
        print_big_separator()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return

    try:
        # Читаем лист «БД», все поля как строки
        df = pd.read_excel(excel_file_path, sheet_name="БД", dtype=str)
    except Exception as e:
        print_big_separator()
        print(f"[E] ОШИБКА при чтении файла: {e}")
        print_big_separator()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return

    print_big_separator()

    print(f"[I] Найдено {len(df)} человек")

    print_big_separator()

    output_pdf_name = self.parsing_save_folder_path
    os.makedirs(output_pdf_name, exist_ok=True)

    EXCEL_FILE = excel_file_path

    processed_count = 0

    for string_number in range(len(df)):
        # ------------------------------------------------------------
        # Данные из новой структуры «БД» (колонки 0..10)
        # 0  = СЛУШАЛИ (фамилия в родительном падеже)
        # 1  = Прием кандидатского экзамена по дисциплине
        # 2  = Направление (текст приказа)
        # 3  = Председатель комиссии (full_text)
        # 4  = ФИО (инициалы председателя)
        # 5  = Члены комиссии №1: (full_text зама)
        # 6  = ФИО (инициалы зама)
        # 7  = Члены комиссии №2: (full_text члена)
        # 8  = ФИО (инициалы члена)
        # 9  = ПОСТАНОВИЛИ (ФИО в именительном падеже)
        # 10 = НАПРАВЛЕНИЕ (шифр + профиль)
        # ------------------------------------------------------------
        surname_genitive = str(df.iloc[string_number, 0]).strip()   # родительный
        discipline       = str(df.iloc[string_number, 1]).strip()
        commission_text  = str(df.iloc[string_number, 2]).strip()   # текст приказа
        chair_full       = str(df.iloc[string_number, 3]).strip()
        chair_initials   = str(df.iloc[string_number, 4]).strip()
        deputy_full      = str(df.iloc[string_number, 5]).strip()
        deputy_initials  = str(df.iloc[string_number, 6]).strip()
        member_full      = str(df.iloc[string_number, 7]).strip()
        member_initials  = str(df.iloc[string_number, 8]).strip()
        surname_nominative = str(df.iloc[string_number, 9]).strip() # именительный
        direction_raw    = str(df.iloc[string_number, 10]).strip()

        processed_count += 1

        progress = int((processed_count / len(df)) * 100)
        self.progress_bar_parsing.setValue(progress)
        QApplication.processEvents()

        # Пропускаем пустые строки
        if (surname_genitive == "nan" or surname_nominative == "nan"
                or surname_nominative == ""):
            continue

        # Из направления берём первую часть (шифр) для имени файла
        code = direction_raw.split()[0] if direction_raw and direction_raw != "nan" \
            else "unknown"

        print(f"[I] Делаю PDF для: {surname_nominative}")

        print_separator_points()

        # Загружаем шаблон (лист «Протокол») из того же файла
        wb = load_workbook(EXCEL_FILE)
        ws = wb["Протокол"]

        # === Статические надписи (одинаковы для всех протоколов) ===

        cell = ws['A1']
        text = (
            "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
"Федеральное государственное бюджетное образовательное учреждение высшего образования\n"
            "«Тамбовский государственный технический университет»"
        )
        cell.value = text
        cell.alignment = Alignment(horizontal='center', vertical='center',
                                   wrap_text=True)
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[1].height = 42

        ws['A8'].value = "ПРОТОКОЛ №___________"
        ws['A8'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A8'].font = Font(name='Times New Roman', size=14, bold=True)
        ws.row_dimensions[8].height = 20

        ws['A10'].value = "от  «___»__________________20___г."
        ws['A10'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A10'].font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[10].height = 15

        ws['I5'].value = "___________Д.Ю. Муромцев"
        ws['I5'].alignment = Alignment(horizontal='left', vertical='center')
        ws['I5'].font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[5].height = 15

        ws['I6'].value = "«___»______________20___г."
        ws['I6'].alignment = Alignment(horizontal='left', vertical='center')
        ws['I6'].font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[6].height = 15

        # === Запись текста приказа в A12 ===
        ws['A12'] = commission_text
        ws['A12'].alignment = Alignment(horizontal='left', vertical='center',
                                        wrap_text=True)
        ws['A12'].font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[12].height = 45

        # === Настройка высоты строк и границ ===
        thin_border = Border(bottom=Side(border_style='thin', color='000000'))

        strings_with_data = [29, 39, 23, 14, 42, 17, 45, 19, 47]
        for row_num in range(2, 60):
            if row_num in strings_with_data:
                ws.row_dimensions[row_num].height = 15
            else:
                ws.row_dimensions[row_num].height = 15
        ws.row_dimensions[14].height = 35
        ws.row_dimensions[17].height = 35
        ws.row_dimensions[19].height = 35
        ws.row_dimensions[21].height = 5
        ws.row_dimensions[25].height = 5
        ws.row_dimensions[28].height = 5
        ws.row_dimensions[44].height = 10
        ws.row_dimensions[33].height = 18
        ws.row_dimensions[34].height = 18
        ws.row_dimensions[35].height = 18
        ws.row_dimensions[36].height = 18
        ws.row_dimensions[37].height = 18
        ws.row_dimensions[2].height = 20
        ws.row_dimensions[7].height = 5

        # === Заполнение переменных данных ===
        # Фамилия в родительном падеже (СЛУШАЛИ)
        cell = ws.cell(row=29, column=3, value=surname_genitive)
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        # ФИО в именительном падеже (ПОСТАНОВИЛИ)
        cell = ws.cell(row=39, column=4, value=surname_nominative)
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        # Дисциплина
        cell = ws.cell(row=26, column=4, value=discipline)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[26].height = 30

        # Направление (шифр + профиль)
        cell = ws.cell(row=23, column=1, value=direction_raw)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[23].height = 30

        # Председатель (full_text)
        cell = ws.cell(row=14, column=1, value=chair_full)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        # Инициалы председателя
        cell = ws.cell(row=42, column=9, value=chair_initials)
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        # Заместитель (full_text)
        cell = ws.cell(row=17, column=1, value=deputy_full)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        # Инициалы зама
        cell = ws.cell(row=45, column=9, value=deputy_initials)
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        # Член комиссии (full_text)
        cell = ws.cell(row=19, column=1, value=member_full)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        # Инициалы члена
        cell = ws.cell(row=47, column=9, value=member_initials)
        cell.alignment = Alignment(wrap_text=False, vertical='center',
                                   horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        # Очистка пустых строк таблицы комиссии
        for row_num in [32, 33, 34, 35, 36, 37]:
            cell = ws.cell(row=row_num, column=1)
            cell.value = ""
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='center')
            cell.font = Font(name='Times New Roman', size=12)
        for col in ['E42', 'E45', 'E47']:
            ws[col].value = ""
            ws[col].border = thin_border
            ws[col].alignment = Alignment(horizontal='left', vertical='center')
            ws[col].font = Font(name='Times New Roman', size=12)

        # Если фамилия слишком длинная, уменьшаем шрифт
        if len(surname_nominative) > 35:
            ws.cell(row=39, column=4).font = Font(name='Times New Roman',
                                                  size=8, italic=True)
        else:
            ws.cell(row=39, column=4).font = Font(name='Times New Roman',
                                                  size=12, italic=True)

        # Сохраняем временный xlsx
        file_name = f"{code} {surname_nominative}.xlsx"
        file_name = file_name.replace("/", "_").replace(
            "\\", "_").replace(":", "_").replace("*", "_")
        wb.save(file_name)
        excel_path = os.path.abspath(file_name)

        # === Конвертация в PDF через Excel (ExportAsFixedFormat) ===
        pdf_path = os.path.abspath(f"{output_pdf_name}/{code} {surname_nominative}.pdf")

        vba_script = f'''
                    Dim xlApp
                    Dim xlBook
                    Set xlApp = CreateObject("Excel.Application")
                    xlApp.Visible = False
                    Set xlBook = xlApp.Workbooks.Open("{excel_path}")
                    xlBook.Sheets(1).ExportAsFixedFormat 0, "{pdf_path}"
                    xlBook.Close False
                    xlApp.Quit
                    '''

        with open("temp_convert.vbs", "w", encoding="windows-1251") as f:
            f.write(vba_script)

        try:
            subprocess.run(["cscript", "//Nologo", "temp_convert.vbs"],
                           shell=True, check=True, timeout=30)
        except subprocess.CalledProcessError as e:
            print(f"[E] Ошибка конвертации Excel: {e}")
            os.remove("temp_convert.vbs")
            os.remove(file_name)
            continue
        except FileNotFoundError:
            print("[E] Не удалось запустить cscript (Windows Script Host). "
                  "Проверьте установку.")
            os.remove("temp_convert.vbs")
            os.remove(file_name)
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(self, "Ошибка", f"Ошибка конвертации Excel: {e}")
            return

        os.remove("temp_convert.vbs")
        os.remove(file_name)

        print(f"[S] Готов: {code} {surname_nominative}.pdf")

        print_separator()

    print(f"[S] Программа завершила работу. Документы PDF сохранены в папке "
          f"'{output_pdf_name}'")

    print_big_separator()
    QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    QMessageBox.information(
        self,
        "Готово!",
        f"Создано PDF документов: {len(df)}\n\n"
        f"Папка сохранения: {output_pdf_name}",
        QMessageBox.StandardButton.Ok
    )
    self.progress_bar_parsing.setValue(100)
    print(f"[S] Готово! Создано PDF документов: {len(df)}. Папка сохранения: "
          f"{output_pdf_name}")


def parsing_universal_excel(self) -> None:
    """
    Парсит универсальную таблицу Excel
    :return: None
    """

    try:
        print("[I] НАЧАЛО parsing_universal_excel")

        print(f"[I] Путь к файлу: {self.universal_file_path}")

        # Проверяем существование файла
        if not os.path.exists(self.universal_file_path):
            print(f"[E] Файл не существует: {self.universal_file_path}")
            QMessageBox.critical(self, "Ошибка",
                                 f"Файл не существует:\n{self.universal_file_path}")

            return

        print("[I] Файл существует")

        # Проверяем размер файла
        file_size = os.path.getsize(self.universal_file_path)
        print(f"[I] Размер файла: {file_size} байт")

        if file_size == 0:
            print("[E] Файл пустой!")
            QMessageBox.critical(self, "Ошибка", "Файл пустой!")
            return

        print("[I] Начало чтения файла")

        try:
            print("[I] Через openpyxl...")
            wb = load_workbook(self.universal_file_path, read_only=True, data_only=True)
            ws = wb.active
            print(f"[I] Активный лист: {ws.title}")
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
            print(f"[I] Прочитано {len(data)} строк")

            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                df = pd.DataFrame()

        except Exception as e:
            print(f"[E] openpyxl не сработал: {e}")

            # Пробуем через pandas
            try:
                print("[I] Через pandas...")
                df = pd.read_excel(
                    self.universal_file_path,
                    dtype=str,
                    engine='openpyxl'
                )
                print(f"[I] pandas прочитал {len(df)} строк")
            except Exception as e2:
                print(f"[E] pandas не сработал: {e2}")
                raise
                # ключевое слово для генерации (выброса) исключений.

        if df is None or len(df) == 0:
            print("[E] Нет данных в файле!")
            QMessageBox.warning(self, "Ошибка", "Файл пуст или не содержит данных!")
            print("[E] Ошибка. Файл пуст или не содержит данных!")
            return

        print(f"[I] Загружено {len(df)} строк, колонок: {len(df.columns)}")

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
        QApplication.processEvents()

        for i, student in enumerate(students_data[:5], 1):
            print(f"[I]   {i}. {student['fio']}")

        QMessageBox.information(
            self,
            "Готово!",
            f"Данные успешно загружены!\n\n"
            f"Найдено записей: {len(students_data)}"
        )
        print(f"[S] Данные успешно загружены! Найдено записей: {len(students_data)}")

    except Exception as e:
        print(f"[E] КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        QApplication.processEvents()
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось прочитать файл:\n{str(e)}"
        )

def parse_doc_with_tables(path: str) -> Tuple[pd.DataFrame, str]:
    """
    Извлекает все таблицы из документа word .doc и возвращает
    их как один DataFrame с текстом.
    :return: None
    """

    doc = aw.Document(path)
    text = doc.get_text()

    tables_data = []
    # Получаем все таблицы в документе
    for idx, node in enumerate(doc.get_child_nodes(aw.NodeType.TABLE, True)):
        table = node.as_table()
        rows = []
        for row_node in table.rows:
            # Получаем объект Row через as_row()
            row = row_node.as_row()
            cells = []
            for cell_node in row.cells:
                cell = cell_node.as_cell()
                cells.append(cell.get_text().strip())
            rows.append(cells)

        if not rows:
            continue

        # Если есть заголовок — делаем его колонками, иначе просто нумеруем
        if len(rows) > 1 and all(len(r) == len(rows[0]) for r in rows):
            df = pd.DataFrame(rows[1:], columns=rows[0])
        else:
            df = pd.DataFrame(rows)

        df['source_file'] = path
        df['table_index'] = idx
        tables_data.append(df)

    tables_df = pd.concat(tables_data, ignore_index=True)\
        if tables_data else pd.DataFrame()
    return tables_df, text


def parsing_commissions(self) -> Optional[List[Dict]]:
    """
    Парсит файл комиссии и извлекает членов комиссии с ролями для каждой специальности
    :return: None
    """

    print("[I] Парсинг комиссии...")

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

    # Проверяем, что файл выбран
    if not path:
        QMessageBox.warning(self, "Ошибка",
                            f"Сначала выберите файл комиссии '{commission_name}'!")
        print("[E] Ошибка. сначала выберите файл комиссии")
        return None

    if not os.path.exists(path):
        QMessageBox.warning(self, "Ошибка", f"Файл не существует: {path}")
        print("[E] ошибка. файл не существует")
        return None

    try:
        # Парсим документ через Aspose.Words
        tables_df, full_text = parse_doc_with_tables(path)

        members_by_specialty = []  # Список для хранения комиссий по специальностям

        # Если есть таблицы
        if tables_df is not None and not tables_df.empty:
            print(
                f"[I] Найдено таблиц: {len(tables_df['table_index'].unique())
                if 'table_index' in tables_df.columns else 1}")

            # Получаем колонки
            cols = list(tables_df.columns)
            print(f"[I] Колонки: {cols}")

            # Находим колонку с ФИО и колонку с шифром
            fio_col = None
            code_col = None

            for col in cols:
                if col not in ['source_file', 'table_index']:
                    col_lower = col.lower()
                    if 'фамил' in col_lower or 'инициал' in col_lower:
                        fio_col = col
                    elif ('шифр' in col_lower or 'наименование'
                          in col_lower or 'специальност' in col_lower):
                        code_col = col

            print(f"[I] Колонка ФИО: {fio_col}")
            print(f"[I] Колонка шифра: {code_col}")

            # Проходим по каждой строке таблицы
            for idx, row in tables_df.iterrows():
                if fio_col is None:
                    # Если не нашли специальную колонку - берём все колонки
                    for col in cols:
                        if col not in ['source_file', 'table_index']:
                            value = str(row[col]).strip() if pd.notna(row[col]) else ""
                            if value and len(value) > 10:
                                _extract_commission_members(value,
                                                    members_by_specialty, row, code_col)
                else:
                    # Берём значение из колонки с ФИО
                    value = str(row[fio_col]).strip() if pd.notna(row[fio_col]) else ""
                    if value and len(value) > 10:
                        _extract_commission_members(value, members_by_specialty,
                                                    row, code_col)

        # Если не нашли в таблицах - ищем в тексте документа
        if not members_by_specialty and full_text:
            print("[I] поиск комиссии в тексте документа...")
            # Ищем блоки с комиссиями по паттерну
            patterns = [
                r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.?.*?председатель.*?;)',
                r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.?.*?заместитель.*?;)',
            ]

        # Сохраняем в атрибут класса
        self.commission_members = members_by_specialty

        # Выводим результат
        if members_by_specialty:
            print(f"[I] Найдено {len(members_by_specialty)} комиссий:")
            for i, item in enumerate(members_by_specialty, 1):
                code = item.get('code', 'Без шифра')
                members = item.get('members', [])
                print(f"[I]  {i}. Шифр: {code}")
                for member in members:
                    print(f"[I]     - {member['fio']} ({member['role']})")

            print(
                f"[S] Готово. комиссия успешно загружена. Найдено комиссий: "
                f"{len(members_by_specialty)}. Семестр: {semester_name}."
                f" Файл: {os.path.basename(path)}.")
        else:
            print("[E] Члены комиссии не найдены!")
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось найти членов комиссии в файле:\n{os.path.basename(path)}"
            )

        return members_by_specialty

    except Exception as e:
        print(f"[E] Ошибка при парсинге комиссии: {e}")
        traceback.print_exc()
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось прочитать файл комиссии:\n{str(e)}"
        )
        return None


def extract_code_number(text: str) -> str:
    """
    Извлекает код специальности вида 1.2.3 из строки.
    :return: str
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

def choose_history_excel(self) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по истории
    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл комиссии по истории",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        self.history_commission_path = file_path
        # Обновляем label
        short_name = os.path.basename(file_path)
        if len(short_name) > 30:
            self.history_xl_choused_label.setStyleSheet(
                "font-size: 11px; color: white; background-color: rgb(105,208,73);")
            self.history_xl_choused_label.setText(short_name)
        else:
            self.history_xl_choused_label.setText(short_name)
            self.history_xl_choused_label.setStyleSheet(
                "font-size: 13px; color: white; background-color: rgb(105,208,73);")
        print(f"[I] Выбран файл комиссии по истории: {file_path}")

def choose_foreign_excel(self) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по иностранному
    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл комиссии по иностранному",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        self.foreign_commission_path = file_path
        short_name = os.path.basename(file_path)
        if len(short_name) > 30:
            self.foreign_xl_choosed_label.setStyleSheet(
                "font-size: 11px; color: white; background-color: rgb(105,208,73);")
            self.foreign_xl_choosed_label.setText(short_name)
        else:
            self.foreign_xl_choosed_label.setText(short_name)
            self.foreign_xl_choosed_label.setStyleSheet(
                "font-size: 13px; color: white; background-color: rgb(105,208,73);")
        print(f"[I] Выбран файл комиссии по иностранному: {file_path}")

def choose_specialization_excel(self) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по специальности
    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл комиссии по специальности",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        self.specialization_commission_path = file_path
        short_name = os.path.basename(file_path)
        if len(short_name) > 30:
            self.specialization_xl_choosed_lb.setStyleSheet(
                "font-size: 11px; color: white; background-color: rgb(105,208,73);")
            self.specialization_xl_choosed_lb.setText(short_name)
        else:
            self.specialization_xl_choosed_lb.setText(short_name)
            self.specialization_xl_choosed_lb.setStyleSheet(
                "font-size: 13px; color: white; background-color: rgb(105,208,73);")
        print(f"[I] Выбран файл комиссии по специальности: {file_path}")

def choose_save_folder_path(self) -> None:
    """
    выбор папки сохранения готовых пдф
    :return: None
    """

    file_path, _ = QFileDialog.getExistingDirectory(
        self,
        "Выберите папку сохранения для PDF",

    )
    if file_path:
        self.lb_choosing_way_save_parsing_pdf = file_path
        short_name = os.path.basename(file_path)
        if len(short_name) > 30:
            self.lb_choosing_way_save_parsing_pdf.setStyleSheet(
                "font-size: 11px; color: white; background-color: rgb(105,208,73);")
            self.lb_choosing_way_save_parsing_pdf.setText(short_name)
        else:
            self.lb_choosing_way_save_parsing_pdf.setText(short_name)
            self.lb_choosing_way_save_parsing_pdf.setStyleSheet(
                "font-size: 13px; color: white; background-color: rgb(105,208,73);")
        print(f"[I] Выбран файл комиссии по специальности: {file_path}")

def site_parce_dn() -> List[Tuple[str, str]]:
    """
    парсинг данных профилей и их кодов аспирантов с сайта магистратуры
    :return: :return: List[Tuple[str, str]]
    """

    url = 'http://dn.tstu.ru/index.php/specialties'
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    target_table = None
    for table in soup.find_all('table'): #Цикл по всем таблицам на сайте
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'Шифр и наименование научной специальности' in headers: #Поиск нужной таблицы
            target_table = table
            break
    if target_table is None:
        return []

    specialties = []
    for row in target_table.find_all('tr'): #Добавление кода, профиль в список как кортеж
        cols = row.find_all('td')
        if not cols:
            continue

        #Проверяем сколько яйчеек в строке
        if len(cols) == 3: #Если 3, то берём код и специальность из 2 и 3
            code = cols[1].get_text(strip=True)
            name = cols[2].get_text(strip=True)
            if code and code.endswith('.') and ' ' not in code:
                specialties.append((code, name))
        elif len(cols) == 2: #Если 2, то код и специальность из 1 и 2
            code = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            if code and code.endswith('.') and ' ' not in code:
                specialties.append((code, name))
    return specialties

def site_parce_main() -> List[Tuple[str, str]]:
    """
    парсинг данных (аспирантов) профилей и их кодов с сайта ТГТУ
    :return: List[Tuple[str, str]]
    """

    url = 'https://www.tstu.ru/r.php?r=postup.abitur.na_sp'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,'
                'application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    } #Имитируем браузер
    response = requests.get(url, headers=headers, timeout=10)
    #Пытаемся получить ответ от сайта
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    target_table = None
    for header in soup.find_all(['h4', 'font'], class_='head4'):
        # цикл по всем элементам, чтобы найти таблицу с заголовком "Аспирантура"
        if header.get_text(strip=True) == 'Аспирантура':
            target_table = header.find_next('table')
            break

    if target_table is None: #Поиск по якорю, если не нашлось по тегам
        anchor = soup.find('a', attrs={'name': '4'})
        if anchor:
            next_tag = anchor.find_next()
            while next_tag and next_tag.name != 'table':
                next_tag = next_tag.find_next()
            target_table = next_tag

    specialties = []
    for row in target_table.find_all('tr'):
        # Добавляем каждый код и каждый профиль в список как кортеж
        cols = row.find_all('td')
        if not cols:
            continue
        if len(cols) >= 2: #Проверяем сколько яйчеек в строке
            code = cols[-2].get_text(strip=True) #Код профиля из предпоследней ячейки
            name = cols[-1].get_text(strip=True) #Название профиля из последней ячейки
            if code and '.' in code and ' ' not in code:
                specialties.append((code, name))

    return specialties


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
        'СЛУШАЛИ',                                    # 0
        'Прием кандидатского экзамена по дисциплине', # 1
        'Направление',                                # 2
        'Председатель комиссии',                      # full_text
        'ФИО',                                        # инициалы председателя
        'Члены комиссии №1:',                         # full_text зама
        'ФИО',                                        # инициалы зама
        'Члены комиссии №2:',                         # full_text члена
        'ФИО',                                        # инициалы члена
        'ПОСТАНОВИЛИ',                                # 9
        'НАПРАВЛЕНИЕ'                                 # 10
    ]

    # ===== Строим словарь комиссий по коду специальности =====
    commission_dict = {}
    for comm in getattr(self, 'commission_members', []):
        raw_code = comm.get('code', '')
        code = extract_code_number(raw_code)
        if code:
            commission_dict[code] = comm

    print("[I] Ключи словаря комиссий:", list(commission_dict.keys()))

    def get_member_by_role(comm: Optional[Dict], role: str) -> Optional[Dict]:
        """
        поиск в комиссии члена по роли
        :return: Optional[Dict]
        """

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

        student_comm = commission_dict.get(clean_code)
        if not student_comm:
            for key, comm in commission_dict.items():
                if key.startswith('.'.join(clean_code.split('.')[:2])):
                    student_comm = comm
                    break

        if not student_comm and self.commission_members:
            student_comm = self.commission_members[0]

        pred = get_member_by_role(student_comm, 'председатель')
        zam  = get_member_by_role(student_comm, 'заместитель')
        chlen = get_member_by_role(student_comm, 'член')

        pred_text = clean_excel_string(pred['full_text']) if pred else ''
        pred_fio  = clean_excel_string(pred['fio']) if pred else ''
        zam_text  = clean_excel_string(zam['full_text']) if zam else ''
        zam_fio   = clean_excel_string(zam['fio']) if zam else ''
        chlen_text = clean_excel_string(chlen['full_text']) if chlen else ''
        chlen_fio = clean_excel_string(chlen['fio']) if chlen else ''

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

    # 2. Копируем шаблон в целевой файл (теперь в нём есть лист «Протокол»)
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy(template_file, output_path)
        print(f"[I] Шаблон скопирован в {output_path}")
    except Exception as e:
        print(f"[E] Ошибка при копировании шаблона: {e}")
        return None

    # 3. Добавляем лист «БД» в скопированный файл, заменяя старый, если был
    try:
        with pd.ExcelWriter(
            output_path,
            engine='openpyxl',
            mode='a',                       # открыть существующий файл
            if_sheet_exists='replace'       # заменить лист, если уже есть
        ) as writer:
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
    return f"/ {initials} {surname} /"

def test_excel() -> None:
    """
    тестовая функция, созданная для поиска ошибки в коде.
    не используется в программе. только для отладки
    :return: None
    """

    file_path = \
    (r"C:/Users/Maini/Desktop/ПР по формированию протоколов/Разнообразные документы"
     r"/Универсальный список.xlsx")

    print(f"[I] Тест: читаю файл {file_path}")
    print(f"[I] Файл существует: {os.path.exists(file_path)}") # вернёт булево
    print(f"[I] Размер: {os.path.getsize(file_path)} байт")

    try:
        df = pd.read_excel(file_path, dtype=str, engine='openpyxl')
        # read_excel - функция, которая читает Excel файл и превращает его в DataFrame,
        # все данные читает как текст
        print(f"[S] Успешно! Загружено {len(df)} строк")
        print(f"[I] Колонки: {list(df.columns)}")
    except Exception as e:
        print(f"[E] Ошибка: {e}")
        traceback.print_exc()


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

def open_parsing_pdf_folder(self) -> None:
    """
    Открывает папку с созданными по напарсенным данным PDF
    :param self:
    :return: None
    """

    folder_path = self.parsing_save_folder_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            self,
                "Папка не найдена",
                f"Папка '{folder_path}' не существует.\n\n"
                f"Сначала создайте PDF файлы, нажав кнопку "
                f"'Начать парсинг и генерацию PDF' на второй вкладке."
        )
        print("[E] ошибка с открытием папки с пдф")
        return
    os.startfile(folder_path)
