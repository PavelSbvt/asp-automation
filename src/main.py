import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.gui.loading_window import MyLoadingWindow
from src.gui.pyqt6_code import MyWindow


def main() -> None:
    """
    Функция, запускающая загрузочное окно, которое по прошествии 3 секунд закроется,
     после чего откроется основное окно программы. Функция-связка.
    """

    app = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    app.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))
    loading_win = MyLoadingWindow()
    loading_win.show()

    def on_loading_closed() -> None:
        """
        Функция, которая показывает основное окно,
         а загрузочное окно скрывает при показе основного окна программы.
        """

        main_win = MyWindow()
        main_win.show()
        loading_win.hide()

    loading_win.closed.connect(on_loading_closed)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()