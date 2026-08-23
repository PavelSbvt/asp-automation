import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.loading_window import MyLoadingWindow
from gui.pyqt6_code import MainWindow
from utils.output_rich import enter_log, exit_log
from utils.functions_for_window_gui import load_cached_data
from core.settings_manager import settings


def main() -> None:
    """
    Функция-связка для показа загрузочного и основного окон приложения.
    Запускает показа загрузочного окна приложения и про его закрытии показывает
    основное окно приложения.

    :return: None
    """

    app = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    app.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))
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
        exit_log("[Exit] загрузочное окно скрыто")
        main_win.show()
        enter_log("[Enter] Показ главного окна")

    loading_win.closed.connect(on_loading_closed)
    sys.exit(app.exec())

if __name__ == "__main__":
    settings.print_settings()
    main()