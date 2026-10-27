import sys
from pathlib import Path
import faulthandler
import multiprocessing

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from core.settings_manager import Settings
from gui.loading_window import MyLoadingWindow
from gui.main_window import MainWindow
from gui.utils.windows_animations import AnimationsManager
from utils.output_rich import Rich


def start_with_loading_window() -> None:
    """
    Функция-связка для показа загрузочного и основного окон приложения.
    Запускает показа загрузочного окна приложения и про его закрытии показывает
    основное окно приложения.

    :return: None
    """

    Rich.debug_log("Запуск приложения с загрузочным окном")

    LoadingWindow = MyLoadingWindow()

    LoadingWindow.setWindowOpacity(0.0)
    LoadingWindow.show()
    LoadingWindow.fade_in_anim = AnimationsManager.window_appearance_animation(
        LoadingWindow, 320)


    MainWin = MainWindow()

    Rich.print_spacer()
    MainWin.load_cached_data()


    def on_loading_closed() -> None:
        """
        Функция для показа основного окна приложения.
        Скрывает загрузочное окно при показе основного окна приложения.

        :return: None
        """

        Rich.print_spacer()
        LoadingWindow.hide()
        Rich.exit_log("Загрузочное окно скрыто")
        Rich.enter_log("Показ главного окна")
        MainWin.setWindowOpacity(0.0)
        MainWin.show()
        MainWin.fade_in_anim = AnimationsManager.window_appearance_animation(MainWin,320)

    LoadingWindow.closed.connect(on_loading_closed)


def start_without_loading_window() -> None:
    """
    Функция для запуска приложения буз загрузочного окна

    :return: None
    """

    Rich.debug_log("Запуск приложения без загрузочного окна")
    MainWin = MainWindow()

    MainWin.load_cached_data()

    Rich.enter_log("Показ главного окна")
    MainWin.setWindowOpacity(0.0)
    MainWin.show()
    MainWin.fade_in_anim = AnimationsManager.window_appearance_animation(MainWin,320)


if __name__ == "__main__":

    multiprocessing.freeze_support() # нужна для корректной работы мультипроцессинга
    # в exe сборке - чтобы exe понимал запущен ли дочерний процесс или нет

    faulthandler.enable() # перехватывает сигнал ошибки от C и печатает
    # Python-стек в stderr — traceback

    Settings.print_settings()
    Rich.print_spacer()

    App = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    App.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    if Settings.get_flag_show_loading_window():
        Rich.debug_log("Показ загрузочного окна разрешён")
        Rich.print_spacer()
        start_with_loading_window()
    else:
        Rich.debug_log("Показ загрузочного окна запрещен")
        Rich.print_spacer()
        start_without_loading_window()

    sys.exit(App.exec())
