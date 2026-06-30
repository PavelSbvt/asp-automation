import sys
from PyQt6.QtWidgets import QApplication
from src.loading_window_pyqt import My_loading_window
from src.pyqt6_code import MyWindow

def main():
    app = QApplication(sys.argv)

    loading_win = My_loading_window()
    loading_win.show()

    def on_loading_closed():
        main_win = MyWindow()
        main_win.show()
        loading_win.hide()

    loading_win.closed.connect(on_loading_closed)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()