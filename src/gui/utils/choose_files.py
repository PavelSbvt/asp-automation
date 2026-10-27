import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from utils.output_rich import Rich


def choose_parsing_save_folder(widget) -> None:
    """
    выбор папки сохранения для собранных пдф по напарсенным данным

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    folder_path = QFileDialog.getExistingDirectory(
        widget,
        "Выберите папку для сохранения PDF (парсинг)",
        widget.parsing_save_folder_path
    )
    if folder_path:
        widget.parsing_save_folder_path = folder_path
        widget.save_path_label.setText(folder_path)


def choose_save_folder_second_tab(widget) -> None:
    """
    выбор папки сохранения для собранных пдф по таблице с собранным БД

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    folder_path = QFileDialog.getExistingDirectory(
        widget,
        "Выберите папку для сохранения PDF (сборка)",
        widget.save_folder_second_tab_path
    )
    if folder_path:
        widget.save_folder_second_tab_path = folder_path
        widget.current_save_path_label.setText(folder_path)


def open_parsing_pdf_folder(widget) -> None:
    """
    Открывает папку с созданными по напарсенным данным PDF

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    folder_path = widget.parsing_save_folder_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            widget,
                "Папка не найдена",
                f"Папка '{folder_path}' не существует.\n\n"
                f"Сначала создайте PDF файлы, нажав кнопку "
                f"запуска процесса на первой вкладке."
        )
        Rich.log_error("[E] ошибка с открытием папки с пдф")
        return
    os.startfile(folder_path)


def open_pdf_folder(widget) -> None:
    """
    Открывает папку с созданными по готовым данным PDF

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    folder_path = widget.save_folder_second_tab_path
    if not os.path.exists(folder_path):
        QMessageBox.warning(
            widget,
            "Папка не найдена",
            f"Папка '{folder_path}' не существует.\n\n"
            f"Сначала создайте PDF файлы, нажав кнопку "
            f"запуска процесса на первой вкладке."
        )
        Rich.log_error("[E] ошибка с открытием папки с пдф")
        return
    os.startfile(folder_path)


def choose_universal_excel(widget) -> None:
    """
    Функция для выбора файла "универсальной" таблицы и сохранения его
    пути в атрибут класса главного окна

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        widget,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )

    if file_path:
        widget.universal_file_path = file_path

        widget.universal_excel_label.setText(f"{file_path}")

        Rich.success_log(f"Выбран файл универсальной таблицы: {file_path}")


def choose_history_excel(widget) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по истории

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        widget,
        "Выберите файл комиссии по истории",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        widget.history_commission_path = file_path

        widget.history_xl_choused_label.setText(file_path)

        Rich.success_log(f"Выбран файл комиссии по истории: {file_path}")


def choose_foreign_excel(widget) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по иностранному

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        widget,
        "Выберите файл комиссии по иностранному",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        widget.foreign_commission_path = file_path

        widget.foreign_xl_choosed_label.setText(file_path)

        Rich.success_log(f"Выбран файл комиссии по иностранному: {file_path}")


def choose_specialization_excel(widget) -> None:
    """
    выбор doc файла с таблицей, содержащей информацию и комиссии по специальности

    :param widget: Принимает имя родительского класса-виджета

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        widget,
        "Выберите файл комиссии по специальности",
        "",
        "Word files (*.doc *.docx);;All files (*.*)"
    )
    if file_path:
        widget.specialization_commission_path = file_path

        widget.specialization_xl_choosed_lb.setText(file_path)

        Rich.success_log(f"Выбран файл комиссии по специальности: {file_path}")
