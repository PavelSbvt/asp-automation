import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QPoint, QTimer, Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QTransform
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton, QTextEdit,
QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QMessageBox,
QMainWindow, QVBoxLayout, QHBoxLayout)

from core.settings_manager import settings


class MainWindow(QMainWindow):
    """
    Класс для нового главного окна
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.setMinimumSize(600, 400)

        self.stop_generation: bool = False  # булевый флаг остановки сборки пдф и парсинга

        # устанавливаю дефолтные пути к файлам пустыми
        self.excel_file_path: Optional[str] = None  # путь к файлу - шаблон для ЛР
        self.universal_file_path: Optional[str] = None  # путь к универсальной таблице
        self.students_data: Optional[List[Dict[str, Any]]] = None  # данные студентов
        self.commission_members: Optional[List[str]] = None  # члены комиссии

        # Пути к файлам комиссий
        self.history_commission_path: Optional[str] = None
        self.foreign_commission_path: Optional[str] = None
        self.specialization_commission_path: Optional[str] = None

        # стандартная папка сохранения пдф фалов в результате работы функций
        self.save_folder_path: str = str(Path.home() / "Desktop" / "results_folder")

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        # # Скрываю стандартную кнопку закрытия окна (и сворачивания)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Главный виджет
        self.main_back_widget = QWidget(self)
        self.main_back_widget.setStyleSheet("background-color: gray; border-radius: 10px;")
        self.setCentralWidget(self.main_back_widget)

        # Главный вертикальный layout
        self.main_v_layout = QVBoxLayout()
        self.main_back_widget.setLayout(self.main_v_layout)

        self.test = QLabel("test")
        self.test2 = QLabel("Test2")
        self.test3 = QLabel("TesT3")

        # Шапка
        self.cap = QHBoxLayout()

        self.cap.addWidget(self.test)
        self.cap.addWidget(self.test2)

        self.main_v_layout.addLayout(self.cap)
        self.main_v_layout.addWidget(self.test3)

        self.main_v_layout.addStretch()
        self.cap.addStretch()

    def mousePressEvent(self, event) -> None:
        """
        Обработчик события нажатия кнопки мыши.

        :param event: Принимает event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).

        :return: None
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()


    def mouseMoveEvent(self, event) -> None:
        """
        Обработчик события движения мыши.

        :param event: Принимает event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).

        :return: None
        """

        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()



if __name__ == "__main__":
    # Тест
    settings.print_settings()

    app = QApplication(sys.argv)
    icon_path = Path('resources/images/icons/icon_pdf_maker_255_size.ico')
    app.setWindowIcon(QIcon(f"{icon_path.as_posix()}"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
