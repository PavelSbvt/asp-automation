import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from utils.output_rich import success_log, log_error


def choose_parsing_save_folder(self) -> None:
    """
    выбор папки сохранения для собранных пдф по напарсенным данным

    :return: None
    """

    folder_path = QFileDialog.getExistingDirectory(
        self,
        "Выберите папку для сохранения PDF (парсинг)",
        self.parsing_save_folder_path
    )
    if folder_path:
        self.parsing_save_folder_path = folder_path
        self.save_path_label.setText(folder_path)

def choose_save_folder_second_tab(self) -> None:
    """
    выбор папки сохранения для собранных пдф по таблице с собранным БД

    :return: None
    """

    folder_path = QFileDialog.getExistingDirectory(
        self,
        "Выберите папку для сохранения PDF (парсинг)",
        self.save_folder_second_tab_path
    )
    if folder_path:
        self.save_folder_second_tab_path = folder_path
        self.current_save_path_label.setText(folder_path)

def open_parsing_pdf_folder(self) -> None:
    """
    Открывает папку с созданными по напарсенным данным PDF

    :return: None
    """

    folder_path = self.parsing_save_folder_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            self,
                "Папка не найдена",
                f"Папка '{folder_path}' не существует.\n\n"
                f"Сначала создайте PDF файлы, нажав кнопку "
                f"запуска процесса на первой вкладке."
        )
        log_error("[E] ошибка с открытием папки с пдф")
        return
    os.startfile(folder_path)

def open_pdf_folder(self) -> None:
    """
    Открывает папку с созданными по готовым данным PDF

    :return: None
    """

    folder_path = self.save_folder_second_tab_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            self,
            "Папка не найдена",
            f"Папка '{folder_path}' не существует.\n\n"
            f"Сначала создайте PDF файлы, нажав кнопку "
            f"запуска процесса на первой вкладке."
        )
        log_error("[E] ошибка с открытием папки с пдф")
        return
    os.startfile(folder_path)

def choose_universal_excel(self) -> None:
    """
    Функция для выбора файла "универсальной" таблицы и сохранения его
    пути в атрибут класса главного окна

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )

    if file_path:
        self.universal_file_path = file_path

        self.universal_excel_label.setText(f"{file_path}")

        success_log(f"Выбран файл универсальной таблицы: {file_path}")

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

        self.history_xl_choused_label.setText(file_path)

        success_log(f"Выбран файл комиссии по истории: {file_path}")

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

        self.foreign_xl_choosed_label.setText(file_path)

        success_log(f"Выбран файл комиссии по иностранному: {file_path}")

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

        self.specialization_xl_choosed_lb.setText(file_path)

        success_log(f"Выбран файл комиссии по специальности: {file_path}")

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
        success_log(f"Выбран файл комиссии по специальности: {file_path}")
