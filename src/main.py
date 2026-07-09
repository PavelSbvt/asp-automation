import sys

from PyQt6.QtWidgets import QApplication

from loading_window_pyqt import MyLoadingWindow # Импорт класса для загрузочного окна
from pyqt6_code import MyWindow # Импорт класса для визуального интерфейса на pyqt6


def main() -> None:
    """
    Функция, запускающая загрузочное окно, которое по прошествии 3 секунд закроется,
     после чего откроется основное окно программы. Функция-связка.
    """

    app = QApplication(sys.argv) # Один qapplication на два py файла с окнами
    # - один окно загрузки, другой основная программы. В их коде qapplication
    # соответственно нет. Их qapplication один и находится здесь

    loading_win = MyLoadingWindow() # Создаётся объект класса загрузочного окна
    loading_win.show() # Показ окна загрузки программы

    def on_loading_closed() -> None:
        """
        Функция, которая показывает основное окно,
         а загрузочное окно скрывает при показе основного окна программы.
        """

        main_win = MyWindow()
        main_win.show()
        loading_win.hide() # скрывает загрузочное окно

    loading_win.closed.connect(on_loading_closed)
    # при срабатывании сигнале выполнит функцию, которая закроет загрузочное окно

    sys.exit(app.exec()) # завершает выполнение основного цикла обработки событий

if __name__ == "__main__":
    main()