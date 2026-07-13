import sys

from PyQt6.QtWidgets import QApplication

from loading_window_pyqt import MyLoadingWindow
from pyqt6_code import MyWindow


def main() -> None:
    """
    Функция, запускающая загрузочное окно, которое по прошествии 3 секунд закроется,
     после чего откроется основное окно программы. Функция-связка.
    """

    app = QApplication(sys.argv)
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