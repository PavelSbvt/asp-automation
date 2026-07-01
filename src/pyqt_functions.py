from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side
import subprocess
from docx import Document
import re

def print_out_string(text):
    out_string_size = 150
    if len(text) % 2 != 0:
        text += " "

    output_string = "|" + " " * int((out_string_size - len(text) - 2) / 2) + text + " " * int(
        (out_string_size - len(text) - 2) / 2) + "|"
    print(output_string)

def print_separator():
    print("|" + "_" * 148 + "|")

def print_separator_points():
    print("|" + "." * 148 + "|")

def print_big_separator():
    print("|" + "=" * 148 + "|")

def open_pdf_folder(self):
    folder_path = self.save_folder_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            self,
            "Папка не найдена",
            f"Папка '{folder_path}' не существует.\n\n"
            f"Сначала создайте PDF файлы, нажав кнопку 'Запустить' на первой вкладке."
        )
        return
    os.startfile(folder_path)

def choose_save_folder(self):
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
        print_out_string(f"Папка для сохранения изменена: {folder_path}")
        string_save_way = f"Папка для сохранения изменена: {folder_path}"
        self.output_text.append(string_save_way)
        QApplication.processEvents()

def choose_file(self):
    file_path, _ = QFileDialog.getOpenFileName( #
        self,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )

    if file_path:
        self.excel_file_path = file_path
        string = f"Выбран файл: {file_path}"
        print_out_string(string)
        self.output_text.append(string)
        QApplication.processEvents()

def get_pdf(self):
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    if not self.excel_file_path:
        print_big_separator()
        string_1 = "ОШИБКА: Сначала выберите файл с данными!"
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
        print_out_string(f"ОШИБКА при чтении файла: {e}")
        self.output_text.append(f"ОШИБКА при чтении файла: {e}")
        QApplication.processEvents()
        print_big_separator()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return

    EXCEL_FILE = self.excel_file_path
    print_big_separator()
    self.output_text.append("=" * 80)

    count_peoples_in_work = f"Найдено {len(df)} человек"
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

        if surname_datelnyi_p == "nan" or surname_name_p == "nan" or surname_name_p == "":
            continue

        code = direction.split()[0] if direction and direction != "nan" else "unknown"

        msg = f"* Делаю PDF для: {surname_name_p}"
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
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[1].height = 42

        cell = ws['A8']
        text_pr = (
            "ПРОТОКОЛ №___________"
        )
        cell.value = text_pr
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
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
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[5].height = 15

        cell = ws['I6']
        text_d = (
            "«___»______________20___г."
        )
        cell.value = text_d
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)
        ws.row_dimensions[6].height = 15

        cell = ws.cell(row=29, column=3, value=surname_datelnyi_p)
        cell.alignment = Alignment(wrap_text=False, vertical='center', horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=39, column=4, value=surname_name_p)
        cell.alignment = Alignment(wrap_text=False, vertical='center', horizontal='center')

        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws['J39']
        cell.value = ""
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=False)
        cell.font = Font(name='Times New Roman', size=12)

        ws.row_dimensions[21].height = 5
        ws.row_dimensions[25].height = 5
        ws.row_dimensions[28].height = 5

        cell = ws.cell(row=26, column=4, value=str(df.iloc[string_number, 1]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[26].height = 30

        cell = ws.cell(row=23, column=1, value=direction)
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)
        ws.row_dimensions[23].height = 30

        cell = ws.cell(row=14, column=1, value=str(df.iloc[string_number, 3]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=42, column=9, value=str(df.iloc[string_number, 4]))
        cell.alignment = Alignment(wrap_text=False, vertical='center', horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws.cell(row=17, column=1, value=str(df.iloc[string_number, 5]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=45, column=9, value=str(df.iloc[string_number, 6]))
        cell.alignment = Alignment(wrap_text=False, vertical='center', horizontal='center')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12)

        cell = ws.cell(row=19, column=1, value=str(df.iloc[string_number, 7]))
        cell.alignment = Alignment(wrap_text=True, vertical='bottom')
        cell.border = thin_border
        cell.font = Font(name='Times New Roman', size=12, italic=True)

        cell = ws.cell(row=47, column=9, value=str(df.iloc[string_number, 8]))
        cell.alignment = Alignment(wrap_text=False, vertical='center', horizontal='center')
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
            ws.cell(row=39, column=4).font = Font(name='Times New Roman', size=8, italic=True)
        else:
            ws.cell(row=39, column=4).font = Font(name='Times New Roman', size=12, italic=True)

        file_name = f"{code} {surname_name_p}.xlsx"
        file_name = file_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_")
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

        msg = f"+ Готов: {code} {surname_name_p}.pdf"

        print_out_string(msg)
        self.output_text.append(msg)
        QApplication.processEvents()

        print_separator()
        self.output_text.append("-" * 80)

    msg = f"Программа завершила работу. Документы PDF сохранены в папке '{output_pdf_name}'"
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

def choose_universal_excel(self):
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
            self.universal_excel_label.setStyleSheet("font-size: 12px; color: white")
            self.universal_excel_label.setText(f"{os.path.basename(file_path)}")
        else:
            self.universal_excel_label.setText(f"{os.path.basename(file_path)}")
            self.universal_excel_label.setStyleSheet("font-size: 14px; color: white")

        # return selected_file

        # Выводим в лог
        print(f"Выбран файл: {file_path}")

def parsing_universal_excel(self):
    # парсинг
    try:
        # Читаем Excel файл
        print(f"Читаю файл: {self.universal_file_path}")
        df = pd.read_excel(self.universal_file_path, dtype=str)

        print(f"Загружено {len(df)} строк")
        QApplication.processEvents()

        # Проверяем, что есть данные
        if len(df) == 0:
            print("Файл пуст!")
            QApplication.processEvents()
            return

        students_data = []

        for index, row in df.iterrows():
            # Получаем данные по индексам колонок
            fio = str(row.iloc[2]).strip() if len(row) > 0 else ""
            profile = str(row.iloc[22]).strip() if len(row) > 1 else ""
            citizenship = str(row.iloc[7]).strip() if len(row) > 2 else ""

            # Пропускаем пустые строки
            if fio == "nan" or not fio:
                continue

            # Очищаем данные от "nan"
            if profile == "nan":
                profile = ""
            if citizenship == "nan":
                citizenship = "РФ"

            students_data.append({
                'fio': fio,
                'profile': profile,
                'citizenship': citizenship
            })

        # Сохраняем данные в атрибут класса
        self.students_data = students_data

        for i, student in enumerate(students_data, 1):
            print(f"{i}. ФИО: {student['fio']}")
            print(f"   Профиль: {student['profile']}")
            print(f"   Гражданство: {student['citizenship']}")
            print("-" * 40)
            QApplication.processEvents()

        print(f"Всего записей: {len(students_data)}")
        self.output_text.append("=" * 80)
        QApplication.processEvents()

        # Показываем сообщение об успехе
        QMessageBox.information(
            self,
            "Готово!",
            f"Данные успешно загружены!\n\n"
            f"Найдено записей: {len(students_data)}\n"
        )

        print(f"Загружено {len(students_data)} записей")

    except Exception as e:
        self.output_text.append(f"Ошибка при чтении файла: {e}")
        QApplication.processEvents()
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось прочитать файл:\n{str(e)}"
        )
        print(f"Ошибка: {e}")

def parsing_commissions(self):
    print("Парсинг комиссии")
    # Определяем выбранный семестр
    if self.radio_button_1.isChecked():
        selected_semester = 1
        semester_name = "Первый семестр"
        print("Выбран 1 семестр")
        # работаю с Комиссии - История.doc


    elif self.radio_button_2.isChecked():
        selected_semester = 2
        semester_name = "Второй семестр"
        print("Выбран 2 семестр")
        # работаю с Комиссии - Иностранный.doc

    else:
        selected_semester = 3
        semester_name = "Третий семестр"
        print("Выбран 3 семестр")
        # работаю с Комиссии - Специальность.doc

def choose_history_excel(self):
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
            self.history_excel_choosed_widget_label.setStyleSheet("font-size: 11px; color: white")
            self.history_excel_choosed_widget_label.setText(short_name)
        else:
            self.history_excel_choosed_widget_label.setText(short_name)
            self.history_excel_choosed_widget_label.setStyleSheet("font-size: 13px; color: white")
        print(f"Выбран файл истории: {file_path}")

def choose_foreign_excel(self):
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
            self.foreign_excel_choosed_widget_label.setStyleSheet("font-size: 11px; color: white")
            self.foreign_excel_choosed_widget_label.setText(short_name)
        else:
            self.foreign_excel_choosed_widget_label.setText(short_name)
            self.foreign_excel_choosed_widget_label.setStyleSheet("font-size: 13px; color: white")
        print(f"Выбран файл иностранного: {file_path}")

def parsing(self):
    print("Начало парсинга.")
    # 1. Проверяем, что выбран файл
    if not hasattr(self, 'universal_file_path') or not self.universal_file_path:
        QMessageBox.warning(
            self,
            "Предупреждение",
            "Сначала выберите универсальную таблицу!\n"
            "Нажмите кнопку 'Выбрать универсальную таблицу'."
        )
        print("таблица не выбрана")
        return

    # 2. Проверяем, что выбран семестр
    if not self.radio_button_1.isChecked() and not self.radio_button_2.isChecked() and not self.radio_button_3.isChecked():
        QMessageBox.warning(
            self,
            "Предупреждение",
            "Пожалуйста, выберите семестр!"
        )
        print("не выбран семестр")
        return

    # 3. Проверяем, что введён текст приказа
    commission_text = self.input_commission.text().strip()
    if not commission_text:
        QMessageBox.warning(
            self,
            "Предупреждение",
            "Пожалуйста, введите текст приказа о комиссиях!"
        )
        print("Не введён текст приказа о комиссиях")
        return

    # 4. Определяем выбранный семестр
    if self.radio_button_1.isChecked():
        selected_semester = 1
        semester_name = "Первый семестр"
        print("Выбран 1 семестр")
    elif self.radio_button_2.isChecked():
        selected_semester = 2
        semester_name = "Второй семестр"
        print("Выбран 2 семестр")
    else:
        selected_semester = 3
        semester_name = "Третий семестр"
        print("Выбран 3 семестр")

    self.parsing_universal_excel()





if __name__ == "__main__":
    print("Пожалуйста, запустите программу через pyqt_general_file.py")
    print(f"Сейчас запущен файл {os.path.basename(__file__)}")