import sys
from PyQt6.QtWidgets import QApplication # так как qapplication должен быть один пришлось создать его в отдельном файле,
# чтобы окно загрузки программы и основное окно работали правильно и запускались оба
from loading_window_pyqt import My_loading_window # Импорт класса для загрузочного окна, которое запускается до основного окна
from pyqt6_code import MyWindow # Импорт класса для визуального интерфейса на pyqt6

def main():
    app = QApplication(sys.argv) # Как раз один qapplication на два py файла с окнами - один окно загрузки, другой основная программы. в их коде qapplication соответственно нет. их qapplication один и находится здесь

    loading_win = My_loading_window() # Создаётся объект класса загрузочного окна
    loading_win.show() # Показ окна загрузки программы

    def on_loading_closed(): # Объявление функции, которая будет вызывать основное окно после закрытия загрузочного окна
        main_win = MyWindow() # Создаётся объект класса основного окна
        main_win.show() # показ основного окна
        loading_win.hide() # скрывает загрузочное окно

    loading_win.closed.connect(on_loading_closed) # экземпляр класса загрузочного окна при срабатывании сигнале выполнит функцию, которая  закроет загрузочное окно

    sys.exit(app.exec()) # завершает выполнение основного цикла обработки событий

if __name__ == "__main__":
    main()