import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.loading_window import MyLoadingWindow
from gui.main_window.main_window import MainWindow
from utils.output_rich import Rich
from utils.functions_for_window_gui import load_cached_data
from core.settings_manager import Settings


def start_with_loading_window() -> None:
    """
    Функция-связка для показа загрузочного и основного окон приложения.
    Запускает показа загрузочного окна приложения и про его закрытии показывает
    основное окно приложения.

    :return: None
    """

    Rich.debug_log("Запуск приложения с загрузочным окном")

    LoadingWindow = MyLoadingWindow()

    LoadingWindow.show()

    MainWin = MainWindow()

    load_cached_data(MainWin)

    def on_loading_closed() -> None:
        """
        Функция для показа основного окна приложения.
        Скрывает загрузочное окно при показе основного окна приложения.

        :return: None
        """

        LoadingWindow.hide()
        Rich.exit_log("Загрузочное окно скрыто")
        MainWin.show()
        Rich.enter_log("Показ главного окна")

    LoadingWindow.closed.connect(on_loading_closed)

def start_without_loading_window() -> None:
    """
    Функция для запуска приложения буз загрузочного окна

    :return: None
    """

    Rich.debug_log("Запуск приложения без загрузочного окна")
    main_win = MainWindow()

    load_cached_data(main_win)

    Rich.enter_log("Показ главного окна")
    main_win.show()

if __name__ == "__main__":
    Settings.print_settings()

    App = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    App.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    if Settings.get_flag_show_loading_window():
        start_with_loading_window()
    else:
        start_without_loading_window()

    sys.exit(App.exec())
