import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.loading_window import MyLoadingWindow
from gui.main_window.main_window import MainWindow
from utils.output_rich import enter_log, exit_log, debug_log
from utils.functions_for_window_gui import load_cached_data
from core.settings_manager import settings


def start_with_loading_window() -> None:
    """
    Функция-связка для показа загрузочного и основного окон приложения.
    Запускает показа загрузочного окна приложения и про его закрытии показывает
    основное окно приложения.

    :return: None
    """

    debug_log("Запуск приложения с загрузочным окном")
    loading_win = MyLoadingWindow()

    loading_win.show()

    main_win = MainWindow()

    load_cached_data(main_win)

    def on_loading_closed() -> None:
        """
        Функция для показа основного окна приложения.
        Скрывает загрузочное окно при показе основного окна приложения.

        :return: None
        """

        loading_win.hide()
        exit_log("Загрузочное окно скрыто")
        main_win.show()
        enter_log("Показ главного окна")

    loading_win.closed.connect(on_loading_closed)

def start_without_loading_window() -> None:
    """
    Функция для запуска приложения буз загрузочного окна

    :return: None
    """

    debug_log("Запуск приложения без загрузочного окна")
    main_win = MainWindow()

    load_cached_data(main_win)

    enter_log("Показ главного окна")
    main_win.show()

if __name__ == "__main__":
    settings.print_settings()

    app = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    app.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    if settings.get_flag_show_loading_window():
        start_with_loading_window()
    else:
        start_without_loading_window()

    sys.exit(app.exec())
