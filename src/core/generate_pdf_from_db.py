import os
import re
import subprocess

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, Side
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from utils.basic_functions import (print_separator,
                                   print_big_separator, print_separator_points, remove_trailing_dot)


def extract_science_from_brackets(text: str) -> str:
    """
    Убирает скобки из строки и заменяет их на запятую.
    Например: "название (технические науки)" -> "название, технические науки"
    """
    if text is None or pd.isna(text):
        return ""

    text = str(text).strip()
    match = re.search(r'\(([^)]+)\)', text)
    if match:
        science_text = match.group(1)
        result = re.sub(r'\s*\([^)]*\)', '', text).strip()
        result = result.rstrip(',') + f", {science_text}"
        return result
    return text


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
        # проверка остановки процесса пользователем
        if hasattr(self, 'stop_generation') and self.stop_generation:
            print(f"[I] ОСТАНОВКА генерации. Обработано {processed_count} из {len(df)}")
            # Удаляем временные файлы, если есть
            if os.path.exists("temp_convert.vbs"):
                try:
                    os.remove("temp_convert.vbs")
                except:
                    pass
            # Показываем сообщение
            QMessageBox.information(
                self,
                "Остановка",
                f"Генерация остановлена.\nОбработано: {processed_count} из {len(df)}"
            )
            self.stop_generation = False
            self.stop_parsing_button.setVisible(False)
            self.run_button.setVisible(True)
            self.progress_bar_parsing.setValue(processed_count)
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
            return

        # ------------------------------------------------------------
        # Данные из БД (колонки 0..10)
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
        surname_genitive = str(df.iloc[string_number, 0]).strip()  # родительный
        discipline = str(df.iloc[string_number, 1]).strip()
        commission_text = str(df.iloc[string_number, 2]).strip()  # текст приказа

        # ===== ДАННЫЕ КОМИССИИ ИЗ EXCEL (уже заполнены fill_database_sheet) =====
        chair_full = str(df.iloc[string_number, 3]).strip()
        chair_initials = remove_trailing_dot(str(df.iloc[string_number, 4]).strip())
        deputy_full = str(df.iloc[string_number, 5]).strip()
        deputy_initials = remove_trailing_dot(str(df.iloc[string_number, 6]).strip())
        member_full = str(df.iloc[string_number, 7]).strip()
        member_initials = remove_trailing_dot(str(df.iloc[string_number, 8]).strip())

        surname_nominative = str(df.iloc[string_number, 9]).strip()  # именительный
        direction_raw = extract_science_from_brackets(str(df.iloc[string_number, 10]).strip())

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