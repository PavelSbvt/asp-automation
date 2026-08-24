import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QPoint, QTimer, Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QTransform
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton, QTextEdit,
QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QMessageBox)
from PyQt6.QtMultimedia import QSoundEffect

from gui.functions.func_change_themes import change_theme
from gui.functions.pyqt_functions import parsing
from core.generate_pdf import (open_pdf_folder,
choose_save_folder, choose_file, get_pdf)
from gui.functions.choose_files import (choose_foreign_excel, choose_history_excel,
choose_specialization_excel, choose_universal_excel, open_parsing_pdf_folder,
choose_parsing_save_folder)
from parser.sait_parsing import update_data
from utils.output_rich import exit_log, debug_log, simple_log, warning_log

# Убирает из консоли лог Qt вида: "qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg
# version 7.1.3 LGPL version 2.1 or later"
os.environ["QT_LOGGING_RULES"] = "qt.multimedia.*=false"

class MainWindow(QWidget):
    """
    Главное окно приложения для генерации PDF и парсинга данных.

    Включает функции обработки данных, парсинга, анимаций и пр.

    Обеспечивает выбор файлов, смену тем оформления, вывод логов
    и координацию процессов генерации PDF-документов.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("main_window")

        self.stop_generation: bool = False  # булевый флаг остановки сборки пдф и парсинга

        # устанавливаю дефолтные пути к файлам пустыми
        self.excel_file_path: Optional[str] = None # путь к файлу - шаблон для ЛР
        self.universal_file_path: Optional[str] = None # путь к универсальной таблице
        self.students_data: Optional[List[Dict[str, Any]]] = None # данные студентов
        self.commission_members: Optional[List[str]] = None # члены комиссии

        # Пути к файлам комиссий
        self.history_commission_path: Optional[str] = None
        self.foreign_commission_path: Optional[str] = None
        self.specialization_commission_path: Optional[str] = None

        # стандартная папка сохранения пдф фалов в результате работы функций
        self.save_folder_path: str = str(Path.home() / "Desktop" / "results_folder")

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_sound()  # Инициализация звука
        self.play_open_sound()  # Воспроизведение звука при открытии

        # блок для фона программы
        self.background_block = QWidget(self)
        self.background_block.setFixedSize(1200, 800)
        back_path = Path("resources/images/color_themes/standard_theme/DSC_5174_1.jpg") # pathlib
        self.background_block.setStyleSheet(f'background-image:url({back_path.as_posix()});')
        self.background_block.move(0, 0)

        self.tab_widget = QTabWidget(self) # виджет вкладок

        self.tab_widget.setFixedSize(1200, 800)  # Размер виджета вкладок

        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West) # позиция вкладок слева

        self.tab_widget.setIconSize(QSize(65, 65)) # Размер иконок на вкладках

        self.tab_widget.setTabBarAutoHide(False) # Вкладки всегда видны

        # стиль вкладок через qss
        self.tab_widget.setStyleSheet(""" 
                QTabWidget::pane {
                    border: none;
                    background: transparent;
                }
                QTabBar::tab {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(76, 110, 50, 230),    
                        stop: 1 rgba(45, 75, 30, 230));   
                    color: rgba(220, 240, 180, 220);   
                    border: 1px solid rgba(100, 140, 65, 200);
                    border-radius: 8px;
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(120, 180, 80, 250),   
                        stop: 1 rgba(80, 130, 50, 250)); 
                    color: white;
                    border: 1px solid rgba(160, 220, 110, 230);
                }
                QTabBar::tab:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(100, 150, 65, 245),
                        stop: 1 rgba(60, 100, 40, 245));
                    border: 1px solid rgba(130, 180, 85, 220);
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                }
                QTabBar::tab:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(60, 90, 35, 250),
                        stop: 1 rgba(35, 60, 20, 250));
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                }
            """)

        # создание виджетов для вкладок
        tab_1 = QWidget()

        tab_2 = QWidget()

        tab_3 = QWidget()

        # кнопка открытия папки с пдф (первая вкладка)
        self.open_folder_button = QPushButton("Открыть папку с PDF", tab_1)
        self.open_folder_button.setFixedSize(300, 50)
        self.open_folder_button.move(370, 730)
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(60, 85, 45, 230),
                        stop: 1 rgba(40, 65, 30, 230));
                    color: white;
                    border: 1px solid rgba(80, 110, 60, 200);
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
                }
            """)
        self.open_folder_button.clicked.connect(lambda: open_pdf_folder(self))
        # чтобы передать аргумент self к функции использую лямбда функцию

        # добавление вкладок
        self.tab_widget.addTab(tab_3, "")  # кладка 1
        self.tab_widget.addTab(tab_1, "") # кладка 2
        self.tab_widget.addTab(tab_2, "") # кладка 3
        # порядок добавления определяет их положение среди вкладок

        # Функция для поворота иконок на 90 градусов по пути файла и размер у всех 65
        def rotate_icon(icon_path: str, size: int =65, angle: int =90) -> QIcon:
            """
            Функция для поворота иконок(изображений на 90 против часовой стрелки)

            :param icon_path: путь к файлу иконки
            :param size: размер иконки в пикселях
            :param angle: угол поворота в градусах
            :return: повёрнутая иконка
            """
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(size, size)
            transform = QTransform().rotate(angle)
            rotated_pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            return QIcon(rotated_pixmap)

        # вызов функций поворота иконок, потому что изначально иконки находятся в неправильном положении

        icon1_path = Path("resources/images/icons/pdf.png")
        icon2_path = Path("resources/images/icons/settings.png")
        icon3_path = Path("resources/images/icons/parsing_ill.png")

        icon1 = rotate_icon(icon1_path.as_posix())
        icon2 = rotate_icon(icon2_path.as_posix())
        icon3 = rotate_icon(icon3_path.as_posix())

        # устанавливаю иконки на вкладки
        self.tab_widget.setTabIcon(0, icon1)
        self.tab_widget.setTabIcon(1, icon3)
        self.tab_widget.setTabIcon(2, icon2)

        # кнопка закрытия основного окна приложения.
        button_close = QPushButton(self) # создание кастомной кнопки закрытия окна
        button_close.setFixedSize(45, 45)
        button_close.move(1150, 5)
        button_close.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button_path = Path("resources/images/icons/close_icon.png")
        button_close.setStyleSheet(f"""
            background-image:url({close_button_path.as_posix()});
            background-color: transparent;
            border: none;
            background-repeat: no-repeat;
            background-position: center;
            """)
        button_close.clicked.connect(self.close)

        # блок для логгирования процесса работы программы
        self.block_for_print_process = QWidget(tab_1) # Виджет-контейнер для текстового поля
        self.block_for_print_process.setFixedSize(1020, 620)
        self.block_for_print_process.setStyleSheet(
        "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,"
        " stop: 0 rgba(60, 85, 45, 230),stop: 1 rgba(40, 65, 30, 230));"
        "border-radius: 10px;")
        self.block_for_print_process.move(10, 100)

        self.output_text = QTextEdit(self.block_for_print_process)
        # Поле для вывода лога (self — чтобы использовать в других методах)
        self.output_text.setGeometry(5, 35, 1010, 580)
        self.output_text.setStyleSheet(
        "background: qlineargradient(x1: 0, y1: 0, x2: 0,"
        " y2: 1,stop: 0 rgba(60, 95, 45, 0.2),stop: 1 rgba(45, 75, 35, 0.25));"
        "border-radius: 10px;; color: white; font-family; font: bold; font-size: 12px;")
        self.output_text.setReadOnly(True)

        # кнопка выбора файла эксель
        self.button_to_find_file_tabel = QPushButton(tab_1)
        self.button_to_find_file_tabel.setFixedSize(180, 50)
        self.button_to_find_file_tabel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_find_file_tabel.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(70, 110, 50, 240),
                        stop: 1 rgba(50, 85, 35, 240));
                    color: white;
                    border: 1px solid rgba(100, 140, 70, 200);
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
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
        self.button_to_find_file_tabel.move(10, 25)
        self.button_to_find_file_tabel.setText("Выберите файл")
        self.button_to_find_file_tabel.clicked.connect(lambda: choose_file(self))
        # При клике открывает диалог выбора файла.
        # Чтобы передать аргумент self к функции использовал лямбда функцию

        # кнопка изменения пути сохранения
        self.button_to_find_where_save = QPushButton(tab_1)
        self.button_to_find_where_save.setFixedSize(250, 50)
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
                    padding: 5px;
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
        self.button_to_find_where_save.move(200, 25)
        self.button_to_find_where_save.setText("Изменить путь для сохранения")
        self.button_to_find_where_save.clicked.connect(lambda: choose_save_folder(self))

        # блок сообщения пути отображения пути сохранения пдф файлов
        self.block_where_save_pdfs_now = QWidget(tab_1)
        self.block_where_save_pdfs_now.setFixedSize(160, 50)
        self.block_where_save_pdfs_now.setStyleSheet("""              
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(70, 110, 50, 240),
                                stop: 1 rgba(50, 85, 35, 240));
                            color: white;
                            border: 1px solid rgba(100, 140, 70, 200);
                            border-radius: 12px;
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px;

                    """)
        self.block_where_save_pdfs_now.move(460, 25)

        # указатель на текущий путь сохранения файлов (готовых пдф протоколов).
        block_where_save_pdfs_now_label = QLabel(self.block_where_save_pdfs_now)
        block_where_save_pdfs_now_label.setText("Путь сохранения:")
        block_where_save_pdfs_now_label.setGeometry(0, 0, 160, 50)
        block_where_save_pdfs_now_label.setStyleSheet(
            "color:white; font: bold; font-size: 14px;")
        block_where_save_pdfs_now_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # отображение текущего пути сохранения файлов
        self.block_way_save = QWidget(tab_1)
        self.block_way_save.setFixedSize(340, 50)
        self.block_way_save.setStyleSheet("""
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 70, 35, 0.7),
                    stop: 1 rgba(35, 55, 25, 0.8));
                border: 1px solid rgba(80, 120, 55, 150);
                border-radius: 10px;
            """)
        self.block_way_save.move(630, 25)

        # лейбл для отображения пути сохранения готовых пдф документов.
        self.path_value_label = QLabel(self.block_way_save)
        short_path = self.save_folder_path
        if len(short_path) > 150:
            short_path = "..." + short_path[-150:]
        else:
            short_path = self.save_folder_path
        self.path_value_label.setText(short_path)
        self.path_value_label.setGeometry(5, 5, 330, 40)
        self.path_value_label.setStyleSheet(
            "color: white; font-size: 10px; font-weight: bold;")
        self.path_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path_value_label.setWordWrap(True)

        self.block_way_save.setToolTip(self.save_folder_path)

        # кнопка запуска сборки пдф документов
        button_do_operation = QPushButton(tab_1)
        button_do_operation.setFixedSize(50, 50)
        button_do_operation.setCursor(Qt.CursorShape.ClosedHandCursor)
        do_operation_button_path = Path("resources/images/icons/do_op_new.png")
        button_do_operation.setStyleSheet(
            f"background-image: url({do_operation_button_path.as_posix()});"
            f" color: white; font-size: 14px; font:bold; border-radius: 10px;")
        button_do_operation.move(980, 25)
        button_do_operation.clicked.connect(lambda: get_pdf(self))

        # виджет-указатель на то, что можно менять темы
        self.widget_for_styles = QWidget(tab_2)
        self.widget_for_styles.setFixedSize(300, 45)
        self.widget_for_styles.setStyleSheet(
            "border-radius:10px; background-color: rgba(45, 75, 30, 240)")
        self.widget_for_styles.move(10, 27)
        label_for_styles = QLabel(self.widget_for_styles)
        label_for_styles.setStyleSheet("color:white; font: bold; font-size: 18px;")
        label_for_styles.setText("Выберите стиль оформления")
        label_for_styles.setGeometry(0, 0, 300, 45)
        label_for_styles.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # фоновый блок для кнопок выбора темы цветового оформления.
        self.window_for_choosing_styles = QWidget(tab_2)
        self.window_for_choosing_styles.setFixedSize(795, 275)
        self.window_for_choosing_styles.setStyleSheet(
            "border-radius: 10px; background-color: rgba(45, 64, 30, 240)")
        self.window_for_choosing_styles.move(10, 100)

        # кнопка смены цветового оформления на тёмный стиль
        button_from_choose_dark_theme = QPushButton(tab_2)
        btn_from_dark_thm_path = Path(
            "resources/images/color_themes/dark_theme/dark_theme_icon.png")
        button_from_choose_dark_theme.setStyleSheet(
            f"background-image: url({btn_from_dark_thm_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_dark_theme.setFixedSize(250, 250)
        button_from_choose_dark_theme.move(20, 110)

        button_from_choose_dark_theme.clicked.connect(
            lambda: change_theme(self, "dark", button_from_choose_dark_theme)
        )

        # кнопка смены текущего цветового оформления на фиолетовую тему
        button_from_choose_violet_theme = QPushButton(tab_2)
        button_violet_theme_path = Path(
            "resources/images/color_themes/violet_theme/violet_theme_icon.png")
        button_from_choose_violet_theme.setStyleSheet(
            f"background-image: url({button_violet_theme_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_violet_theme.setFixedSize(250, 250)
        button_from_choose_violet_theme.move(280, 110)

        button_from_choose_violet_theme.clicked.connect(
            lambda: change_theme(self, "violet", button_from_choose_violet_theme))

        # кнопка для смены темы цветового оформления на стандартную тему
        button_from_choose_standard_theme = QPushButton(tab_2)
        button_standard_path = Path(
            "resources/images/color_themes/standard_theme/standard_theme_icon.png")
        button_from_choose_standard_theme.setStyleSheet(
            f"background-image: url({button_standard_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_standard_theme.setFixedSize(250, 250)
        button_from_choose_standard_theme.move(540, 110)

        button_from_choose_standard_theme.clicked.connect(
            lambda: change_theme(self, "standard", button_from_choose_standard_theme)
        )

        QTimer.singleShot(1, self.center_window) # запуск центрирования главного окна.

        self.progress_bar = QProgressBar(tab_1)
        self.progress_bar.setFixedSize(980, 25)
        self.progress_bar.move(20, 110)
        self.progress_bar.setRange(0, 100)  # диапазон от 0 до 100
        self.progress_bar.setValue(0)  # Начальное значение
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                color: white;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
                border: 2px solid rgba(100, 140, 65, 200);
                border-radius: 10px;
                background: rgba(45, 70, 35, 150);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(60, 150, 40, 200),
                    stop: 0.5 rgba(100, 200, 70, 220),
                    stop: 1 rgba(60, 150, 40, 200));
                border-radius: 8px;
            }
        """)

        # виджет, используемый для фона для ралиокнопок выбора семестра и лейбла
        background_widget_for_choosing_term = QWidget(tab_3)
        background_widget_for_choosing_term.setFixedSize(300, 200)
        background_widget_for_choosing_term.setStyleSheet(
            "background-color: white; border-radius: 10px;")
        background_widget_for_choosing_term.move(10,10)

        # виджет с лейблом, предлагающим пользователю выбрать семестр
        self.choose_the_term = QWidget(tab_3)
        self.choose_the_term.setFixedSize(200, 50)
        self.choose_the_term.setStyleSheet(
        "background-color: rgba(100, 140, 65, 200); border-radius: 10px; color: white;")
        self.choose_the_term.move(60, 20)
        label_choose_the_term = QLabel(self.choose_the_term)
        label_choose_the_term.setText("Выберите семестр:")
        label_choose_the_term.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_choose_the_term.setStyleSheet("font: bold; font-size: 18px; color: white;")
        label_choose_the_term.setGeometry(0, 0, 200, 50)

        # активирует работу с doc файлом комиссии по истории
        self.radio_button_1 = QRadioButton("Первый семестр", tab_3)
        # активирует работу с файлом «Комиссии - История.doc»
        self.radio_button_1.setStyleSheet("color: black; font-size: 18px; font: bold;")
        self.radio_button_1.move(65, 90)
        self.radio_button_1.setStyleSheet("""
            QRadioButton {
                color: black;
                font-size: 18px;
                font-weight: bold;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 10px;
                height: 10px;
                border-radius: 3px;
                border: 2px solid rgb(211,211,211);
                background: white;
            }
            QRadioButton::indicator:checked {
                background-color: rgb(105,208,73);
                border: 2px solid #27ae60;
            }
            QRadioButton::indicator:hover {
                border: 2px solid green;
            }
        """)

        # активирует работу с doc файлом комиссии по иностранному
        self.radio_button_2 = QRadioButton("Второй семестр", tab_3)
        # активирует работу с файлом «Комиссии - Иностранный.doc»
        self.radio_button_2.setStyleSheet("color: black; font-size: 18px; font: bold;")
        self.radio_button_2.move(65, 120)
        self.radio_button_2.setStyleSheet("""
                    QRadioButton {
                        color: black;
                        font-size: 18px;
                        font-weight: bold;
                        spacing: 10px;
                    }
                    QRadioButton::indicator {
                        width: 10px;
                        height: 10px;
                        border-radius: 3px;
                        border: 2px solid rgb(211,211,211);
                        background: white;
                    }
                    QRadioButton::indicator:checked {
                        background-color: rgb(105,208,73);
                        border: 2px solid #27ae60;
                    }
                    QRadioButton::indicator:hover {
                        border: 2px solid green;
                    }
                """)
        # активирует работу с doc файлом комиссии по специальности
        self.radio_button_3 = QRadioButton("Третий семестр", tab_3)
        # активирует работу с файлом «Комиссии - Специальность.doc»
        self.radio_button_3.setStyleSheet("color: black; font-size: 18px; font: bold;")
        self.radio_button_3.move(65, 150)
        self.radio_button_3.setStyleSheet("""
                    QRadioButton {
                        color: black;
                        font-size: 18px;
                        font-weight: bold;
                        spacing: 10px;
                    }
                    QRadioButton::indicator {
                        width: 10px;
                        height: 10px;
                        border-radius: 3px;
                        border: 2px solid rgb(211,211,211);
                        background: white;
                    }
                    QRadioButton::indicator:checked {
                        background-color: rgb(105,208,73);
                        border: 2px solid #27ae60;
                    }
                    QRadioButton::indicator:hover {
                        border: 2px solid green;
                    }
                """)

        # Группируем (чтобы работало как "только один выбор")
        self.button_group = QButtonGroup(tab_3)
        self.button_group.addButton(self.radio_button_1)
        self.button_group.addButton(self.radio_button_2)
        self.button_group.addButton(self.radio_button_3)

        # Добавить input с label: «Приказ о комиссиях»
        self.widget_for_label = QWidget(tab_3)
        self.widget_for_label.setFixedSize(730,80)
        self.widget_for_label.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.widget_for_label.move(320,10)

        # label для приказа о комиссиях.
        label_commission = QLabel(self.widget_for_label)
        label_commission.setGeometry(10,5,700,30)
        label_commission.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_commission.setText("Приказ о комиссиях")
        label_commission.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 18px;
        """)

        # поле ввода для приказа о комиссиях
        self.input_commission = QLineEdit(self.widget_for_label)
        self.input_commission.setGeometry(10, 40, 700, 30)
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

        # Главная кнопка, запускающая парсинг и сбор данных в пдф.
        self.parsing_button = QPushButton("Начать парсинг и генерацию PDF", tab_3)
        self.parsing_button.setStyleSheet("""
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
        self.parsing_button.setFixedSize(280,40)
        self.parsing_button.move(370,740)
        self.parsing_button.clicked.connect(lambda: parsing(self))

        # Кнопка, останавливающая парсинг и сбор данных в пдф.
        self.stop_parsing_button = QPushButton("Остановить парсинг и генерацию PDF", tab_3)
        self.stop_parsing_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 80, 80, 180),
                    stop: 0.3 rgba(220, 50, 50, 200),
                    stop: 0.7 rgba(180, 30, 30, 220),
                    stop: 1 rgba(140, 15, 15, 240));
                color: white;
                border: 1px solid rgba(255, 150, 150, 100);
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 100, 100, 200),
                    stop: 0.3 rgba(240, 70, 70, 220),
                    stop: 0.7 rgba(200, 40, 40, 240),
                    stop: 1 rgba(160, 20, 20, 255));
                border: 1px solid rgba(255, 200, 200, 150);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(120, 10, 10, 255),
                    stop: 1 rgba(80, 5, 5, 255));
                padding-top: 6px;
                padding-bottom: 4px;
            }
            QPushButton:disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(100, 50, 50, 120),
                    stop: 1 rgba(70, 35, 35, 160));
                color: rgba(200, 200, 200, 120);
                border: 1px solid rgba(100, 50, 50, 80);
            }
        """)
        self.stop_parsing_button.setFixedSize(280, 40)
        self.stop_parsing_button.move(370, 740)
        self.stop_parsing_button.clicked.connect(self.stop_generation_process)
        self.stop_parsing_button.setVisible(False)

        self.blc_for_stop = QWidget(tab_3)
        self.blc_for_stop.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        self.blc_for_stop.setFixedSize(200,100)
        self.blc_for_stop.move(670,680)

        self.label_stop = QLabel(self.blc_for_stop)
        self.label_stop.setText("Для остановки процесса нажмите клавишу 'ESC' или 'Пробел'")
        self.label_stop.setStyleSheet("color: red; font-size: 14px; font: bold;")
        self.label_stop.setGeometry(0,0,200,100)
        self.label_stop.setWordWrap(True)

        # self.blc_for_stop.setVisible(False)

        # background блок для выбора файлов - doc файлов и универсальной таблицы
        background_widget_for_choose_files = QWidget(tab_3)
        background_widget_for_choose_files.setFixedSize(730,310)
        background_widget_for_choose_files.move(320,100)
        background_widget_for_choose_files.setStyleSheet(
            "background-color: white; border-radius: 10px;")

        # предложение для пользователя о выборе фалов.
        self.widget_for_label_choosing_files = QWidget(tab_3)
        self.widget_for_label_choosing_files.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.widget_for_label_choosing_files.setFixedSize(300, 50)
        self.widget_for_label_choosing_files.move(525, 110)
        self.label_for_choozing_files = QLabel(self.widget_for_label_choosing_files)
        self.label_for_choozing_files.setStyleSheet(
            "color: white; font: bold; font-size: 14px;")
        self.label_for_choozing_files.setGeometry(0,0,300,50)
        self.label_for_choozing_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_choozing_files.setText("Пожалуйста, выберите файлы")

        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        self.btn_choose_universal_xl = QPushButton(
            "Выберите таблицу для парсинга",tab_3)
        self.btn_choose_universal_xl.setFixedSize(360,50)
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
        self.btn_choose_universal_xl.move(680,290)
        self.btn_choose_universal_xl.clicked.connect(lambda: choose_universal_excel(self))

        # виджет сменит свой стандартный текст на имя выбранной таблицы
        self.universal_excel_label_widget = QWidget(tab_3)
        self.universal_excel_label_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.universal_excel_label_widget.setFixedSize(360,50)
        self.universal_excel_label_widget.move(680, 350)
        self.universal_excel_label = QLabel(self.universal_excel_label_widget)
        self.universal_excel_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setText("Здесь будет имя выбранного файла...")
        self.universal_excel_label.setGeometry(0,0,360,50)

        # кнопка для выбора doc файла с данными комиссии по истории
        self.btn_choose_history_commission = QPushButton(
            "Выберите таблицу 'Комиссия - история.doc'",tab_3)
        self.btn_choose_history_commission.setFixedSize(330,50)
        self.btn_choose_history_commission.setStyleSheet("""
        QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(60, 85, 45, 230),
                    stop: 1 rgba(40, 65, 30, 230));
                color: white;
                border: 2px solid rgba(100, 140, 65, 200);
                border-radius: 10px;
                font-size: 12px;
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
        self.btn_choose_history_commission.move(330, 170)
        self.btn_choose_history_commission.clicked.connect(lambda: choose_history_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        self.history_excel_choosed_widget = QWidget(tab_3)
        self.history_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.history_excel_choosed_widget.setFixedSize(330, 50)
        self.history_excel_choosed_widget.move(330, 230)
        self.history_xl_choused_label = QLabel(self.history_excel_choosed_widget)
        self.history_xl_choused_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.history_xl_choused_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_xl_choused_label.setText(
            "Здесь будет имя выбранного файла...")
        self.history_xl_choused_label.setGeometry(0, 0, 330, 50)

        # кнопка для выбора doc файла с данными комиссии по иностранному
        self.btn_choose_foreign_commission = QPushButton(
            "Выберите таблицу 'Комиссия - иностранный.doc'", tab_3)
        self.btn_choose_foreign_commission.setFixedSize(360, 50)
        self.btn_choose_foreign_commission.setStyleSheet("""
                QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(60, 85, 45, 230),
                            stop: 1 rgba(40, 65, 30, 230));
                        color: white;
                        border: 2px solid rgba(100, 140, 65, 200);
                        border-radius: 10px;
                        font-size: 12px;
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
        self.btn_choose_foreign_commission.move(680, 170)
        self.btn_choose_foreign_commission.clicked.connect(lambda: choose_foreign_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        self.foreign_excel_choosed_widget = QWidget(tab_3)
        self.foreign_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.foreign_excel_choosed_widget.setFixedSize(360, 50)
        self.foreign_excel_choosed_widget.move(680, 230)
        self.foreign_xl_choosed_label = QLabel(self.foreign_excel_choosed_widget)
        self.foreign_xl_choosed_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.foreign_xl_choosed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreign_xl_choosed_label.setText(
            "Здесь будет имя выбранного файла...")
        self.foreign_xl_choosed_label.setGeometry(0, 0, 360, 50)

        # кнопка для выбора doc файла с данными комиссии по специальности
        self.btn_choose_specialization_commission = QPushButton(
            "Выберите таблицу 'Комиссия - специальность.doc'", tab_3)
        self.btn_choose_specialization_commission.setFixedSize(330, 50)
        self.btn_choose_specialization_commission.setStyleSheet("""
                        QPushButton {
                                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 rgba(60, 85, 45, 230),
                                    stop: 1 rgba(40, 65, 30, 230));
                                color: white;
                                border: 2px solid rgba(100, 140, 65, 200);
                                border-radius: 10px;
                                font-size: 12px;
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
        self.btn_choose_specialization_commission.move(330, 290)
        self.btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        self.specialization_excel_choosed_widget = QWidget(tab_3)
        self.specialization_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.specialization_excel_choosed_widget.setFixedSize(330, 50)
        self.specialization_excel_choosed_widget.move(330, 350)
        self.specialization_xl_choosed_lb = QLabel(self.specialization_excel_choosed_widget)
        self.specialization_xl_choosed_lb.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.specialization_xl_choosed_lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.specialization_xl_choosed_lb.setText(
            "Здесь будет имя выбранного файла...")
        self.specialization_xl_choosed_lb.setGeometry(0, 0, 330, 50)

        # фон для кнопки выбора пути сохранения готовых пдф документов
        widget_for_choose_save_way_for_parsed_pdf = QWidget(tab_3)
        widget_for_choose_save_way_for_parsed_pdf.setFixedSize(300, 190)
        widget_for_choose_save_way_for_parsed_pdf.setStyleSheet(
            "background-color: white; border-radius: 10px;")
        widget_for_choose_save_way_for_parsed_pdf.move(10, 220)

        # label с предложением пользователю выбрать папку сохранения для пдф
        self.widget_for_label_choosing_way = QWidget(tab_3)
        self.widget_for_label_choosing_way.setFixedSize(280,50)
        self.widget_for_label_choosing_way.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.widget_for_label_choosing_way.move(20, 230)
        self.lb_choosing_way_save_parsing_pdf = QLabel(self.widget_for_label_choosing_way)
        self.lb_choosing_way_save_parsing_pdf.setStyleSheet(
            "color: white; font: bold; font-size: 14px;")
        self.lb_choosing_way_save_parsing_pdf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_choosing_way_save_parsing_pdf.setText(
            "Выберите путь сохранения для PDF")
        self.lb_choosing_way_save_parsing_pdf.setGeometry(0,0,280,50)

        # Кнопка выбора пути сохранения
        self.button_choose_save_path = QPushButton("Выбрать папку", tab_3)
        self.button_choose_save_path.setFixedSize(250, 40)
        self.button_choose_save_path.move(35, 290)
        self.button_choose_save_path.setStyleSheet("""
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

        # Путь для сохранения PDF после парсинга (по умолчанию как основной)
        self.parsing_save_folder_path = self.save_folder_path

        # лейбл отображает текущий путь к папке сохранения пдф.
        self.save_path_label = QLabel("Папка не выбрана", tab_3)
        self.save_path_label.setGeometry(35, 335, 250, 40)
        self.save_path_label.setStyleSheet("""
            color: white;
            font-size: 11px;
            background: rgba(45, 70, 35, 150);
            border: 1px solid rgba(100, 140, 65, 150);
            border-radius: 8px;
            padding: 5px;
        """)
        self.save_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_path_label.setText(f"{self.parsing_save_folder_path}")

        self.button_choose_save_path.clicked.connect(lambda: choose_parsing_save_folder(self))

        # блок для пояснения к прогресс бару
        self.widget_for_progress_bar = QWidget(tab_3)
        self.widget_for_progress_bar.setFixedSize(1040,75)
        self.widget_for_progress_bar.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        self.widget_for_progress_bar.move(10,420)
        self.label_for_progress = QLabel(self.widget_for_progress_bar)
        self.label_for_progress.setText("Прогресс сборки PDF")
        self.label_for_progress.setStyleSheet(
            "color: white; font-size: 18px; font: bold;")
        self.label_for_progress.setGeometry(0,0,1040,50)
        self.label_for_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # прогресс бар для второй вкладки (с парсингом)
        self.progress_bar_parsing = QProgressBar(tab_3)
        self.progress_bar_parsing.setFixedSize(1020, 25)
        self.progress_bar_parsing.move(20, 465)
        self.progress_bar_parsing.setRange(0, 100)
        self.progress_bar_parsing.setValue(0)
        self.progress_bar_parsing.setStyleSheet("""
            QProgressBar {
                color: white;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
                border: 2px solid rgba(100, 140, 65, 200);
                border-radius: 10px;
                background: rgba(45, 70, 35, 150);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(60, 150, 40, 200),
                    stop: 0.5 rgba(100, 200, 70, 220),
                    stop: 1 rgba(60, 150, 40, 200));
                border-radius: 8px;
            }
        """)

        # кнопка, которая открывает выбранную папку с готовыми пдф
        self.button_to_open_folder_with_done_pdf = QPushButton("Открыть папку с PDF", tab_3)
        self.button_to_open_folder_with_done_pdf.setFixedSize(280,50)
        self.button_to_open_folder_with_done_pdf.setStyleSheet("""
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
        self.button_to_open_folder_with_done_pdf.move(370,680)
        self.button_to_open_folder_with_done_pdf.clicked.connect(
            lambda: open_parsing_pdf_folder(self))

        self.widget_for_update_data_site_parsing = QWidget(tab_3)
        self.widget_for_update_data_site_parsing.setStyleSheet(
            "border-radius:10px; background-color: rgba(45, 75, 30, 1)")
        self.widget_for_update_data_site_parsing.setFixedSize(400, 50)
        self.widget_for_update_data_site_parsing.move(10, 500)
        self.label_for_info_update_site_paring = QLabel(
            self.widget_for_update_data_site_parsing)
        self.label_for_info_update_site_paring.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_info_update_site_paring.setStyleSheet("color: white; font: bold;"
                                                             " font-size: 14px;")
        self.label_for_info_update_site_paring.setText(
            "Последнее обновление данных (парсинг сайтов):")
        self.label_for_info_update_site_paring.setGeometry(0, 0, 400, 50)

        widget_time_of_update = QWidget(tab_3)
        widget_time_of_update.setStyleSheet(
            "border-radius:10px; background-color: rgba(255, 255, 255, 0.9)")
        widget_time_of_update.setFixedSize(320, 50)
        widget_time_of_update.move(420, 500)
        self.time_update_label = QLabel(widget_time_of_update)
        self.time_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_update_label.setStyleSheet("color: black;"
                                             " font-size: 14px;")
        self.time_update_label.setText("время последнего обновления")
        self.time_update_label.setGeometry(0, 0, 320, 50)

        self.button_to_update_date = QPushButton(tab_3)
        self.button_to_update_date.setText("Обновить данные")
        self.button_to_update_date.setFixedSize(300,50)
        self.button_to_update_date.move(750, 500)
        self.button_to_update_date.setStyleSheet("""
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
        self.button_to_update_date.clicked.connect(lambda: update_data(self))

        # self.load_cached_data()

    def close(self) -> None:
        """
        Закрытие приложения с выводом лога
        """

        debug_log("Нажата кнопка выхода из приложения.")
        exit_log("Выход из приложения")

        super().close()

    def keyPressEvent(self, event) -> None:
        """
        Обработка нажатий клавиш для остановки процесса
        """

        # Пробел - обычная остановка
        if (event.key() == Qt.Key.Key_Space and
                self.stop_parsing_button.isVisible() and
                self.stop_parsing_button.isEnabled()):
            self.stop_generation_process()
            event.accept()
            return

        # ESC - аварийная остановка (работает даже если кнопка скрыта)
        if event.key() == Qt.Key.Key_Escape:
            if hasattr(self, 'stop_generation') and not self.stop_generation:
                # Если процесс идет
                if self.stop_parsing_button.isVisible():
                    print("[W] Аварийная остановка по ESC")
                    self.stop_generation = True
                    QMessageBox.warning(
                        self,
                        "Аварийная остановка",
                        "Процесс остановлен по клавише ESC"
                    )
                    event.accept()
                    return

        # Передаем событие дальше
        super().keyPressEvent(event)

    def stop_generation_process(self) -> None:
        """
        Останавливает процесс генерации
        """

        simple_log("Остановка процесса по запросу пользователя")
        self.stop_generation = True
        # self.blc_for_stop.setVisible(True)


        # Делаем кнопку неактивной, чтобы нельзя было нажать дважды
        self.stop_parsing_button.setEnabled(False)

        QMessageBox.information(
            self,
            "Остановка",
            "Процесс остановки запущен...\n\n"
            "Программа завершит текущую операцию и остановится."
        )

    def update_progress(self, current: int, total: int) -> None:
        """
        функция обновления прогресса progressbar.
        """

        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            QApplication.processEvents()


    def center_window(self) -> None:
        """
        функция для центрирования главного окна, чтобы оно появлялось
        по центру экрана пользователя после исчезновения загрузочного окна
        """

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_sound(self) -> None:
        """
        Настройка звукового эффекта
        """

        self.sound_effect = QSoundEffect()
        sound_path = Path('resources/sounds/guitar_sound.wav')

        # Проверяем существование файла
        if Path(sound_path.as_posix()).exists():
            self.sound_effect.setSource(QUrl.fromLocalFile(sound_path.as_posix()))
            self.sound_effect.setVolume(0.13)  # Громкость от 0.0 до 1.0
        else:
            warning_log(f"Звуковой файл не найден: {sound_path.as_posix()}")

    def play_open_sound(self) -> None:
        """
        Воспроизведение звука при открытии окна
        """

        if hasattr(self, 'sound_effect') and self.sound_effect.source().isValid():
            self.sound_effect.play()
        else:
            warning_log( "Звук не воспроизведён - файл не найден или не загружен")

    def mousePressEvent(self, event) -> None:
        """
        функция, отслеживающая точку, где пользователь зажал ЛКМ
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """
        функция для вычисления смещения по изменения позиции зажатой ЛКМ.
         Перемещает окно при движении мыши с зажатой ЛКМ.
        """

        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()
