import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from core.settings_manager import Settings
from gui.loading_window import MyLoadingWindow
from gui.main_window import MainWindow
from gui.utils.windows_functions import load_cached_data
from gui.utils.windows_animations import AnimateManager
from utils.output_rich import Rich
from utils.create_shortcut import check_build


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

    Rich.print_spacer()
    load_cached_data(MainWin)

    def on_loading_closed() -> None:
        """
        Функция для показа основного окна приложения.
        Скрывает загрузочное окно при показе основного окна приложения.

        :return: None
        """

        Rich.print_spacer()
        LoadingWindow.hide()
        Rich.exit_log("Загрузочное окно скрыто")
        MainWin.show()
        Rich.enter_log("Показ главного окна")
        AnimateManager.animation_appearance_window(MainWin, duration=1000)

    LoadingWindow.closed.connect(on_loading_closed)

def start_without_loading_window() -> None:
    """
    Функция для запуска приложения буз загрузочного окна

    :return: None
    """

    Rich.debug_log("Запуск приложения без загрузочного окна")
    MainWin = MainWindow()

    load_cached_data(MainWin)

    Rich.enter_log("Показ главного окна")
    MainWin.show()
    AnimateManager.animation_appearance_window(MainWin, duration=1000)

if __name__ == "__main__":

    check_build()

    Settings.print_settings()
    Rich.print_spacer()

    App = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    App.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    if Settings.get_flag_show_loading_window():
        Rich.print_spacer()
        start_with_loading_window()
    else:
        Rich.print_spacer()
        start_without_loading_window()

    sys.exit(App.exec())
