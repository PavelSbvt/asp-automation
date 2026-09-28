import textwrap

from PyQt6.QtWidgets import QApplication, QFileDialog, QProgressBar

from utils.output_rich import Rich


def wrap_text(text: str, width: int = 50) -> str:
    """
    Переносит длинный текст по словам с заданной шириной

    :param text: Принимает текст, который нужно обработать и вернуть с переносами.
    :param width: Принимает желаемую ширину строки (для переноса лишнего)

    :return: str - Возвращает отредактированную строку с переносами по ширине
    """

    return "\n".join(textwrap.wrap(text, width=width))


def choose_file(self) -> None:
    """
    Функция для выбора файла обрабатываемой таблицы для генерации пдф.

    :return: None
    """

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите файл Excel с данными",
        "",
        "Excel files (*.xlsx *.xls);;All files (*.*)"
    )

    if file_path:
        self.excel_file_path = file_path
        self.label_current_tabel.setText(self.excel_file_path)
        Rich.success_log(f"Выбрана таблица  с данными для сборки ПДФ: {file_path}")


def update_progress(progress_bar: QProgressBar, current: int, total: int) -> None:
    """
    функция обновления прогресса progressbar на вкладке со сборкой (без парсинга).
    Переводит текущий индекс в процент от максимального индекса и
    устанавливает значение прогресс бару.

    :param progress_bar: Имя объекта QProgressBar,
     для которого будет обновляться прогресс
    :param current: принимает int - индекс текущей операции. Например, 4 из 8.
    :param total: Принимает максимальный индекс операций
    (сколько всего будет шагов до заполнения)

    :return: None
    """

    if total > 0:
        progress = int((current / total) * 100)
        progress_bar.setValue(progress)
        QApplication.processEvents()
        Rich.print_spacer_points()
        Rich.debug_log(f"Прогресс сборки ПДФ: {progress}%")
        Rich.print_spacer_points()
