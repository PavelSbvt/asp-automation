import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from gui.loading_window import MyLoadingWindow
from gui.pyqt6_code import MainWindow


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

    def on_loading_closed() -> None:
        """
        Функция для показа основного окна приложения.
        Скрывает загрузочное окно при показе основного окна приложения.

        :return: None
        """

        main_win = MainWindow()
        main_win.show()
        loading_win.hide()

    loading_win.closed.connect(on_loading_closed)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()