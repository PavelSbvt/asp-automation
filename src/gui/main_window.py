import sys
import random
from pathlib import Path
from typing import Optional, List, Dict, Any
import webbrowser

from PyQt6.QtCore import QPoint, QTimer, Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QTransform, QCursor
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton, QTextEdit,
QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QMessageBox,
QMainWindow, QVBoxLayout, QHBoxLayout)

from core.settings_manager import settings
from utils.output_rich import debug_log, warning_log
from utils.functions_for_window_gui import get_random_image_from_folder
from utils.fonts import fonts


class MainWindow(QMainWindow):
    """
    Класс для нового главного окна
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.setMinimumSize(900, 650)

        self.setWindowTitle(settings.get_app_name())

        self.width_now = 0
        self.height_now = 0

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
        self.main_back_widget.setStyleSheet("background-color: #2b2b2b; border-radius: 0px;")
        self.setCentralWidget(self.main_back_widget)

        # Главный вертикальный layout
        self.main_v_layout = QVBoxLayout()
        self.main_back_widget.setLayout(self.main_v_layout)

        # Работа с вкладками
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(fonts.get_qfont("Inter", 10))
        self.tab_widget.setStyleSheet("color: rgba(253,251,212, 1);")

        # Вкладки
        tab_main_widget = QWidget()
        tab_second_widget = QWidget()
        tab_settings_widget = QWidget()

        self.tab_widget.addTab(tab_main_widget, "Главная")
        self.tab_widget.addTab(tab_second_widget, "ЛР по формированию PDF")
        self.tab_widget.addTab(tab_settings_widget, "Настройки")

        self.tab_widget.setTabVisible(2, False)

        # Шапка
        self.cap_widget = QWidget(self)

        self.cap = QHBoxLayout()

        self.cap_widget.setLayout(self.cap)
        self.cap_widget.setFixedHeight(48)
        # self.cap_widget.setMaximumWidth(1400)

        self.cap.setContentsMargins(12,0,12,0)

        self.app_name_button = QPushButton()
        self.app_name_button.setText(settings.get_app_name())
        self.app_name_button.setFont(fonts.get_qfont("Playfair_Display", 14))
        self.app_name_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(253,251,212, 1);
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #4a4a4a;
                color: #6C5CE7;
            }
            QPushButton:pressed {
                background: #3a3a3a;
            }
        """)
        self.app_name_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.app_name_button.clicked.connect(self.app_name_clicked)

        self.cap.addWidget(self.app_name_button)
        self.cap.addStretch()

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #bbbbbb;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background: #3a3a3a;
            }
        """)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(self.open_settings_tab)

        self.run_button = QPushButton(">")
        self.run_button.setStyleSheet("""
            QPushButton {
                background: #3c8d4a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #4ca85a;
            }
            QPushButton:pressed {
                background: #2d6e38;
            }
        """)

        self.what_tab_is_show_now()
        self.tab_widget.currentChanged.connect(self.what_tab_is_show_now)

        self.cap.addWidget(self.run_button)
        self.cap.addWidget(self.settings_button)

        self.main_v_layout.addWidget(self.cap_widget)

        self.main_v_layout.addWidget(self.tab_widget)

        # Виджет для фона основной вкладки приложения
        self.widget_bg_main_tab = QWidget(tab_main_widget)

        self.widget_bg_main_tab.setMinimumHeight(200)
        self.widget_bg_main_tab.setMaximumWidth(1400)

        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

        # Лейбл для того, чтобы показался виджет с фоном (без текста)
        label = QLabel(self.widget_bg_main_tab)
        label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout для виджета, чтобы расположить текст лейбла
        bg_layout = QVBoxLayout()
        bg_layout.addWidget(label)
        self.widget_bg_main_tab.setLayout(bg_layout)

        # Установка лейаута для главной вкладки и загрузка в неё виджета фона
        tab_main_layout = QVBoxLayout()

        bg_main_tab_layout = QHBoxLayout()
        bg_main_tab_layout.addWidget(self.widget_bg_main_tab)

        tab_main_layout.addLayout(bg_main_tab_layout)
        # tab_main_layout.addStretch()

        tab_main_widget.setLayout(tab_main_layout)

        # =======================================================

        # Специальный лейаут для кнопок и остального на главной вкладке
        widgets_horizontal_main_tab_layout = QHBoxLayout()

        widgets_horizontal_main_tab_layout.addStretch()

        widgets_vertical_main_tab_layout = QVBoxLayout()
        widgets_horizontal_main_tab_layout.addLayout(widgets_vertical_main_tab_layout)

        widgets_horizontal_main_tab_layout.addStretch()

        # кнопка открытия папки с пдф (главная вкладка
        self.open_folder_button = QPushButton("Открыть папку с PDF", tab_main_widget)
        self.open_folder_button.setMaximumWidth(400)
        self.open_folder_button.setFixedHeight(30)
        self.open_folder_button.setFont(fonts.get_qfont("Inter", 14))
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(60, 85, 45, 230),
                                stop: 1 rgba(40, 65, 30, 230));
                            color: rgba(253,251,212, 1);
                            border: 1px solid rgba(80, 110, 60, 200);
                            border-radius: 10px;
                            font-size: 14px;
                            font-weight: bold;
                            padding: 0px 10px 0px 10px;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(100, 140, 70, 250),
                                stop: 1 rgba(70, 110, 45, 250));
                            border: 1px solid rgba(140, 190, 100, 230);
                        }
                        QPushButton:pressed {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(40, 65, 30, 230),
                                stop: 1 rgba(30, 50, 20, 230));
                        }
                    """)
        # self.open_folder_button.clicked.connect(lambda: open_pdf_folder(self))

        # кнопка изменения пути сохранения
        self.button_to_find_where_save = QPushButton(tab_main_widget)
        self.button_to_find_where_save.setMaximumWidth(400)
        self.button_to_find_where_save.setFixedHeight(30)
        self.button_to_find_where_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_find_where_save.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(70, 110, 50, 240),
                                stop: 1 rgba(50, 85, 35, 240));
                            color: white;
                            border: 1px solid rgba(100, 140, 70, 200);
                            border-radius: 12px;
                            font-size: 14px;
                            font-weight: bold;
                            padding: 0px 10px 0px 10px;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(100, 150, 70, 250),
                                stop: 1 rgba(70, 110, 45, 250));
                            border: 1px solid rgba(140, 190, 100, 230);
                        }
                        QPushButton:pressed {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(45, 75, 30, 240),
                                stop: 1 rgba(35, 60, 25, 240));
                            padding-top: 6px;
                            padding-bottom: 4px;
                        }
                    """)
        self.button_to_find_where_save.setText("Изменить путь для сохранения")

        # self.button_to_find_where_save.clicked.connect(lambda: choose_save_folder(self))

        # ================================================================

        self.radio_buttons_background = QWidget(tab_main_widget)
        self.radio_buttons_background.setFixedHeight(200)
        self.radio_buttons_background.setMaximumWidth(350)
        self.radio_buttons_background.setStyleSheet(
            "background-color: gray; border-radius: 10px;"
            )

        radio_buttons_vertical_layout = QVBoxLayout()
        self.radio_buttons_background.setLayout(radio_buttons_vertical_layout)

        self.label_for_radio_buttons = QLabel()
        self.label_for_radio_buttons.setText("Выберите семестр:")
        self.label_for_radio_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_radio_buttons.setStyleSheet("color: rgba(253,251,212, 1); margin: 10px; font-weight: bold;")
        self.label_for_radio_buttons.setFont(fonts.get_qfont("Inter", 14))

        radio_buttons_vertical_layout.addWidget(self.label_for_radio_buttons)

        # tab_main_layout.addLayout(radio_buttons_vertical_layout)

        horizontal_layout_for_radio_buttons_and_button = QHBoxLayout()
        horizontal_layout_for_radio_buttons_and_button.addWidget(self.radio_buttons_background)

        widgets_vertical_main_tab_layout.addWidget(self.button_to_find_where_save)
        widgets_vertical_main_tab_layout.addWidget(self.open_folder_button)

        # tab_main_layout.addLayout(horizontal_layout_for_radio_buttons_and_button)

        radio_buttons_vertical_layout.addStretch()

        # Радиокнопки
        # активирует работу с doc файлом комиссии по истории
        self.radio_button_1 = QRadioButton("Первый семестр - история", tab_main_widget)
        # активирует работу с файлом «Комиссии - История.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_1)
        self.radio_button_1.setFont(fonts.get_qfont("Inter", 12))
        self.radio_button_1.setStyleSheet("""
                    QRadioButton {
                        color: rgba(253,251,212, 1);
                        font-weight: bold;
                        spacing: 10px;
                    }
                    QRadioButton:checked{
                        color: rgb(105,208,73);
                    }
                    QRadioButton::indicator {
                        width: 10px;
                        height: 10px;
                        border-radius: 3px;
                        border: 2px solid rgb(211,211,211);
                        background: white;
                    }
                    QRadioButton::indicator:checked {
                        width: 15px;
                        height: 15px;
                        background-color: rgb(105,208,73);
                        border: 2px solid #27ae60;
                    }
                    QRadioButton::indicator:hover {
                        border: 2px solid green;
                    }
                """)

        # активирует работу с doc файлом комиссии по иностранному
        self.radio_button_2 = QRadioButton("Второй семестр - иностранный", tab_main_widget)
        # активирует работу с файлом «Комиссии - Иностранный.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_2)
        self.radio_button_2.setFont(fonts.get_qfont("Inter", 12))
        self.radio_button_2.setStyleSheet("""
                            QRadioButton {
                                color: rgba(253,251,212, 1);
                                font-weight: bold;
                                spacing: 10px;
                            }
                            QRadioButton:checked{
                                color: rgb(105,208,73);
                            }
                            QRadioButton::indicator {
                                width: 10px;
                                height: 10px;
                                border-radius: 3px;
                                border: 2px solid rgb(211,211,211);
                                background: white;
                            }
                            QRadioButton::indicator:checked {
                                width: 15px;
                                height: 15px;
                                background-color: rgb(105,208,73);
                                border: 2px solid #27ae60;
                            }
                            QRadioButton::indicator:hover {
                                border: 2px solid green;
                            }
                        """)
        # активирует работу с doc файлом комиссии по специальности
        self.radio_button_3 = QRadioButton("Третий семестр - специальность", tab_main_widget)
        # активирует работу с файлом «Комиссии - Специальность.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_3)
        self.radio_button_3.setFont(fonts.get_qfont("Inter", 12))
        self.radio_button_3.setStyleSheet("""
                            QRadioButton {
                                color: rgba(253,251,212, 1);
                                font-weight: bold;
                                spacing: 10px;
                            }
                            QRadioButton:checked{
                                color: rgb(105,208,73);
                            }
                            QRadioButton::indicator {
                                width: 10px;
                                height: 10px;
                                border-radius: 3px;
                                border: 2px solid rgb(211,211,211);
                                background: white;
                            }
                            QRadioButton::indicator:checked {
                                width: 15px;
                                height: 15px;
                                background-color: rgb(105,208,73);
                                border: 2px solid #27ae60;
                            }
                            QRadioButton::indicator:hover {
                                border: 2px solid green;
                            }
                        """)

        # Группируем (чтобы работало как "только один выбор")
        self.button_group = QButtonGroup(tab_main_widget)
        self.button_group.addButton(self.radio_button_1)
        self.button_group.addButton(self.radio_button_2)
        self.button_group.addButton(self.radio_button_3)

        radio_buttons_vertical_layout.addStretch()

        # =============================================

        # поле ввода для приказа о комиссиях
        self.input_commission = QLineEdit()
        self.input_commission.setMaximumWidth(1000)
        self.input_commission.setPlaceholderText(
            "Введите текст приказа"
        )
        self.input_commission.setStyleSheet("""
                   QLineEdit {
                       background: rgba(45, 70, 35, 180);
                       color: white;
                       border: 2px solid rgba(100, 140, 65, 200);
                       border-radius: 8px;
                       padding: 5px 10px;
                       font-size: 14px;
                   }
                   QLineEdit:focus {
                       border: 2px solid rgba(100, 200, 70, 220);
                       background: rgba(55, 80, 45, 200);
                   }
                   QLineEdit::placeholder {
                       color: rgba(200, 220, 180, 150);
                       font-style: italic;
                   }
               """)

        horizontal_widget_for_input_commission = QHBoxLayout()
        horizontal_widget_for_input_commission.addWidget(self.input_commission)

        # ===========================================================

        self.widget_for_choose_files_commission = QWidget()
        self.widget_for_choose_files_commission.setStyleSheet("background-color: gray; border-radius: 10px;")
        self.widget_for_choose_files_commission.setFixedHeight(200)
        self.widget_for_choose_files_commission.setMaximumWidth(350)

        horizontal_layout_for_radio_buttons_and_button.addWidget(self.widget_for_choose_files_commission)

        horizontal_layout_for_radio_buttons_and_button.setContentsMargins(50, 20, 50, 20)

        vertical_layout_for_choosing_files = QVBoxLayout()
        self.widget_for_choose_files_commission.setLayout(vertical_layout_for_choosing_files)

        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        self.btn_choose_universal_xl = QPushButton(
            "Выберите таблицу для парсинга")
        self.btn_choose_universal_xl.setFixedHeight(35)
        self.btn_choose_universal_xl.setMaximumWidth(330)
        self.btn_choose_universal_xl.setStyleSheet("""
                QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(60, 85, 45, 230),
                            stop: 1 rgba(40, 65, 30, 230));
                        color: white;
                        border: 2px solid rgba(100, 140, 65, 200);
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(100, 140, 70, 250),
                            stop: 1 rgba(70, 110, 45, 250));
                        border: 1px solid rgba(140, 190, 100, 230);
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(40, 65, 30, 230),
                            stop: 1 rgba(30, 50, 20, 230));
                        padding-top: 6px;
                        padding-bottom: 4px;
                    }
                """)
        # self.btn_choose_universal_xl.clicked.connect(lambda: choose_universal_excel(self))

        vertical_layout_for_choosing_files.addWidget(self.btn_choose_universal_xl)

        if self.radio_button_1.isChecked():
            pass
        elif self.radio_button_2.isChecked():
            pass
        elif self.radio_button_3.isChecked():
            pass
        else:
            pass

        tab_main_layout.addLayout(horizontal_widget_for_input_commission)

        # tab_main_layout.addStretch()

        tab_main_layout.addLayout(horizontal_layout_for_radio_buttons_and_button)

        tab_main_layout.addStretch()

        tab_main_layout.addLayout(widgets_horizontal_main_tab_layout)

    def app_name_clicked(self):
        """
        Функция для перехода по ссылке на Гит с репозиторием проекта. Просто попробовать.

        :return: None
        """

        webbrowser.open("https://lab.vr-pro.ru:8514/SAPR/asp-automation/src/branch/"
                        "development")

    def resizeEvent(self, event):
        """
        Вызывается при изменении размера окна.

        :param event: QResizeEvent — содержит новую информацию о размере
        """

        width = self.width()
        height = self.height()

        self.width_now = width
        self.height_now = height

        if self.height_now <= 800:
            self.widget_bg_main_tab.setMinimumHeight(200)
        else:
            self.widget_bg_main_tab.setMinimumHeight(350)

        super().resizeEvent(event)

    def get_bg_for_main_tab_widget(self, folder_path: str) -> None:
        """

        :param folder_path:
        :return:
        """

        img_path = get_random_image_from_folder(folder_path)
        path_bg_widget = Path(f'{img_path}')

        self.widget_bg_main_tab.setStyleSheet(
            f"background-image: url({path_bg_widget.as_posix()});"
            f" background-position: center;"
            f" background-repeat: no-repeat;"
            f"border-radius: 10px;"
        )

    def what_tab_is_show_now(self) -> int:
        """
        Функция для получения индекса текущей вкладки

        :return: int
        """

        tabs_name = ["Главная", "ЛР по формированию PDF", "Настройки"]

        current_index = self.tab_widget.currentIndex()

        tab_name = ""

        if current_index == 0:
            tab_name = tabs_name[0]
        elif current_index == 1:
            tab_name = tabs_name[1]
        elif current_index == 2:
            tab_name = tabs_name[2]
        else:
            tab_name = "неизвестно"

        debug_log(f"Открыта вкладка: {current_index} ({tab_name})")

        return current_index

    def open_settings_tab(self) -> None:
        """
        Функция для открытия вкладки с настройками

        :return: None
        """

        self.tab_widget.setCurrentIndex(2)

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
