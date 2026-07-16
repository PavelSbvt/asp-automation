from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QPoint, QTimer, Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QTransform # QIcon — иконки, QTransform — поворот иконок
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton, QTextEdit,
QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QFileDialog)
from PyQt6.QtMultimedia import QSoundEffect

from pyqt_functions import parsing
from functions_from_generate_pdf_first_part_of_task import (open_pdf_folder,
choose_save_folder, choose_file, get_pdf)
from functions_from_choose_files import (choose_foreign_excel, choose_history_excel,
    choose_specialization_excel, choose_universal_excel, open_parsing_pdf_folder)


class MyWindow(QWidget):
    """
    Главное окно приложения для генерации PDF и парсинга данных.

    Включает функции обработки данных, парсинга, анимаций и пр.

    Обеспечивает выбор файлов, смену тем оформления, вывод логов
    и координацию процессов генерации PDF-документов.
    """

    def __init__(self) -> None:
        super().__init__()

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
        background_block = QWidget(self)
        background_block.setFixedSize(1200, 800)
        back_path = Path("resources/images/background_images/DSC_5174_1.jpg") # pathlib
        background_block.setStyleSheet(f'background-image:url({back_path.as_posix()});')
        background_block.move(0, 0)

        tab_widget = QTabWidget(self) # виджет вкладок

        tab_widget.setFixedSize(1200, 800)  # Размер виджета вкладок

        tab_widget.setTabPosition(QTabWidget.TabPosition.West) # позиция вкладок слева

        tab_widget.setIconSize(QSize(65, 65)) # Размер иконок на вкладках

        tab_widget.setTabBarAutoHide(False) # Вкладки всегда видны

        # стиль вкладок через qss
        tab_widget.setStyleSheet(""" 
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
        tab_widget.addTab(tab_1, "") # кладка 1
        tab_widget.addTab(tab_3, "") # кладка 2
        tab_widget.addTab(tab_2, "") # кладка 3
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
        tab_widget.setTabIcon(0, icon1)
        tab_widget.setTabIcon(1, icon3)
        tab_widget.setTabIcon(2, icon2)

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
        block_for_print_process = QWidget(tab_1) # Виджет-контейнер для текстового поля
        block_for_print_process.setFixedSize(1020, 620)
        block_for_print_process.setStyleSheet(
        "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,"
        " stop: 0 rgba(60, 85, 45, 230),stop: 1 rgba(40, 65, 30, 230));"
        "border-radius: 10px;")
        block_for_print_process.move(10, 100)

        self.output_text = QTextEdit(block_for_print_process)
        # Поле для вывода лога (self — чтобы использовать в других методах)
        self.output_text.setGeometry(5, 35, 1010, 580)
        self.output_text.setStyleSheet(
        "background: qlineargradient(x1: 0, y1: 0, x2: 0,"
        " y2: 1,stop: 0 rgba(60, 95, 45, 0.2),stop: 1 rgba(45, 75, 35, 0.25));"
        "border-radius: 10px;; color: white; font-family; font: bold; font-size: 12px;")
        self.output_text.setReadOnly(True)

        # кнопка выбора файла эксель
        button_to_find_file_tabel = QPushButton(tab_1)
        button_to_find_file_tabel.setFixedSize(180, 50)
        button_to_find_file_tabel.setCursor(Qt.CursorShape.PointingHandCursor)
        button_to_find_file_tabel.setStyleSheet("""
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
        button_to_find_file_tabel.move(10, 25)
        button_to_find_file_tabel.setText("Выберите файл")
        button_to_find_file_tabel.clicked.connect(lambda: choose_file(self))
        # При клике открывает диалог выбора файла.
        # Чтобы передать аргумент self к функции использовал лямбда функцию

        # кнопка изменения пути сохранения
        button_to_find_where_save = QPushButton(tab_1)
        button_to_find_where_save.setFixedSize(250, 50)
        button_to_find_where_save.setCursor(Qt.CursorShape.PointingHandCursor)
        button_to_find_where_save.setStyleSheet("""
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
        button_to_find_where_save.move(200, 25)
        button_to_find_where_save.setText("Изменить путь для сохранения")
        button_to_find_where_save.clicked.connect(lambda: choose_save_folder(self))

        # блок сообщения пути отображения пути сохранения пдф файлов
        block_where_save_pdfs_now = QWidget(tab_1)
        block_where_save_pdfs_now.setFixedSize(160, 50)
        block_where_save_pdfs_now.setStyleSheet("""              
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
        block_where_save_pdfs_now.move(460, 25)

        # указатель на текущий путь сохранения файлов (готовых пдф протоколов).
        block_where_save_pdfs_now_label = QLabel(block_where_save_pdfs_now)
        block_where_save_pdfs_now_label.setText("Путь сохранения:")
        block_where_save_pdfs_now_label.setGeometry(0, 0, 160, 50)
        block_where_save_pdfs_now_label.setStyleSheet(
            "color:white; font: bold; font-size: 14px;")
        block_where_save_pdfs_now_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # отображение текущего пути сохранения файлов
        block_way_save = QWidget(tab_1)
        block_way_save.setFixedSize(340, 50)
        block_way_save.setStyleSheet("""
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 70, 35, 0.7),
                    stop: 1 rgba(35, 55, 25, 0.8));
                border: 1px solid rgba(80, 120, 55, 150);
                border-radius: 10px;
            """)
        block_way_save.move(630, 25)

        # лейбл для отображения пути сохранения готовых пдф документов.
        self.path_value_label = QLabel(block_way_save)
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

        block_way_save.setToolTip(self.save_folder_path)

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
        widget_for_styles = QWidget(tab_2)
        widget_for_styles.setFixedSize(300, 45)
        widget_for_styles.setStyleSheet(
            "border-radius:10px; background-color: rgba(45, 75, 30, 240)")
        widget_for_styles.move(10, 27)
        label_for_styles = QLabel(widget_for_styles)
        label_for_styles.setStyleSheet("color:white; font: bold; font-size: 18px;")
        label_for_styles.setText("Выберите стиль оформления")
        label_for_styles.setGeometry(0, 0, 300, 45)
        label_for_styles.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # фоновый блок для кнопок выбора темы цветового оформления.
        window_for_choosing_styles = QWidget(tab_2)
        window_for_choosing_styles.setFixedSize(795, 275)
        window_for_choosing_styles.setStyleSheet(
            "border-radius: 10px; background-color: rgba(45, 64, 30, 240)")
        window_for_choosing_styles.move(10, 100)

        # кнопка смены цветового оформления на тёмный стиль
        button_from_choose_dark_theme = QPushButton(tab_2)
        btn_from_dark_thm_path = Path(
            "resources/images/color_themes/dark_theme/dark_theme_icon.png")
        button_from_choose_dark_theme.setStyleSheet(
            f"background-image: url({btn_from_dark_thm_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_dark_theme.setFixedSize(250, 250)
        button_from_choose_dark_theme.move(20, 110)

        btn_from_dark_thm_path = Path(
            "resources/images/color_themes/dark_theme/dark_theme_icon.png")
        btn_from_dark_med_thm_path = Path(
            "resources/images/color_themes/dark_theme/dark_theme_icon_medium.png")
        btn_from_dark_mini_thm_path = Path(
            "resources/images/color_themes/dark_theme/dark_theme_icon_mini.png")


        def change_theme_to_dark() -> None:
            """
            Функция смены темы цветового оформления на тёмную.
            :return: None
            """
            QTimer.singleShot(10, lambda: (
                button_from_choose_dark_theme.setFixedSize(245, 245),
                button_from_choose_dark_theme.setStyleSheet(
                f"background-image: url({btn_from_dark_med_thm_path.as_posix()});"
                f" border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(22, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_dark_theme.setFixedSize(240, 240),
                button_from_choose_dark_theme.setStyleSheet(
                    f"background-image: url({btn_from_dark_mini_thm_path.as_posix()}); border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(25, 115)
            ))

            QTimer.singleShot(125, lambda: (
                button_from_choose_dark_theme.setFixedSize(245, 245),
                button_from_choose_dark_theme.setStyleSheet(
                    f"background-image: url({btn_from_dark_med_thm_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(22, 112)
            ))

            QTimer.singleShot(160, lambda: (
                button_from_choose_dark_theme.setFixedSize(250, 250),
                button_from_choose_dark_theme.setStyleSheet(
                    f"background-image: url({btn_from_dark_thm_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(20, 110)
            ))
            back_dark_path = Path(
                "resources/images/color_themes/dark_theme/image_from_dark_theme.JPG")
            background_block.setStyleSheet(
                f"background-image: url({back_dark_path.as_posix()});")
            self.progress_bar.setStyleSheet("""
                            QProgressBar {
                                color: rgb(255, 255, 255);
                                font-weight: bold;
                                font-size: 13px;
                                text-align: center;
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                background: rgb(30, 30, 30);
                            }
                            QProgressBar::chunk {
                                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                    stop: 0 rgb(100, 100, 100),
                                    stop: 0.5 rgb(180, 180, 180),
                                    stop: 1 rgb(100, 100, 100));
                                border-radius: 8px;
                            }
                        """)

            self.progress_bar_parsing.setStyleSheet("""
                            QProgressBar {
                                color: rgb(255, 255, 255);
                                font-weight: bold;
                                font-size: 13px;
                                text-align: center;
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                background: rgb(30, 30, 30);
                            }
                            QProgressBar::chunk {
                                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                    stop: 0 rgb(100, 100, 100),
                                    stop: 0.5 rgb(180, 180, 180),
                                    stop: 1 rgb(100, 100, 100));
                                border-radius: 8px;
                            }
                        """)

            choose_the_term.setStyleSheet(
                "background-color: rgb(60, 60, 60); "
                "border-radius: 10px; color: rgb(255, 255, 255);")

            radio_style_dark = """
                            QRadioButton {
                                color: rgb(56, 53, 53);
                                font-size: 18px;
                                font-weight: bold;
                                spacing: 10px;
                            }
                            QRadioButton::indicator {
                                width: 10px;
                                height: 10px;
                                border-radius: 3px;
                                border: 2px solid rgb(145, 145, 145);
                                background: rgb(128, 128, 128);
                            }
                            QRadioButton::indicator:checked {
                                background-color: rgb(18, 18, 18);
                                border: 2px solid rgb(0, 0, 0);
                            }
                            QRadioButton::indicator:hover {
                                border: 2px solid rgb(200, 200, 200);
                            }
                        """
            self.radio_button_1.setStyleSheet(radio_style_dark)
            self.radio_button_2.setStyleSheet(radio_style_dark)
            self.radio_button_3.setStyleSheet(radio_style_dark)

            widget_for_label.setStyleSheet("background-color: rgb(60, 60, 60);"
                                           " border-radius: 10px;")

            self.input_commission.setStyleSheet("""
                            QLineEdit {
                                background: rgb(30, 30, 30);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(60, 60, 60);
                                border-radius: 8px;
                                padding: 5px 10px;
                                font-size: 14px;
                            }
                            QLineEdit:focus {
                                border: 2px solid rgb(120, 120, 120);
                                background: rgb(45, 45, 45);
                            }
                            QLineEdit::placeholder {
                                color: rgb(100, 100, 100);
                                font-style: italic;
                            }
                        """)

            parsing_button.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            widget_for_label_choosing_files.setStyleSheet(
                "background-color: rgb(60, 60, 60); border-radius: 10px;")

            self.open_folder_button.setStyleSheet("""
                            QPushButton {
                                background: rgb(50, 50, 50);
                                color: rgb(255, 255, 255);
                                border: 1px solid rgb(70, 70, 70);
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(70, 70, 70);
                                border: 1px solid rgb(100, 100, 100);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                            }
                        """)

            button_to_find_file_tabel.setStyleSheet("""
                            QPushButton {
                                background: rgb(50, 50, 50);
                                color: rgb(255, 255, 255);
                                border: 1px solid rgb(70, 70, 70);
                                border-radius: 12px;
                                font-size: 14px;
                                font-weight: bold;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background: rgb(70, 70, 70);
                                border: 1px solid rgb(100, 100, 100);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            button_to_find_where_save.setStyleSheet("""
                            QPushButton {
                                background: rgb(50, 50, 50);
                                color: rgb(255, 255, 255);
                                border: 1px solid rgb(70, 70, 70);
                                border-radius: 12px;
                                font-size: 14px;
                                font-weight: bold;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background: rgb(70, 70, 70);
                                border: 1px solid rgb(100, 100, 100);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            block_where_save_pdfs_now.setStyleSheet("""              
                            background: rgb(50, 50, 50);
                            color: rgb(255, 255, 255);
                            border: 1px solid rgb(70, 70, 70);
                            border-radius: 12px;
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px;
                        """)

            tab_widget.setStyleSheet(""" 
                            QTabWidget::pane {
                                border: none;
                                background: transparent;
                            }
                            QTabBar::tab {
                                background: rgb(45, 45, 45);
                                color: rgb(170, 170, 170);
                                border: 1px solid rgb(60, 60, 60);
                                border-radius: 8px;
                                padding: 5px;
                                padding-top: -10px;
                                padding-bottom: 7px;
                                margin: 4px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QTabBar::tab:selected {
                                background: rgb(70, 70, 70);
                                color: rgb(255, 255, 255);
                                border: 1px solid rgb(120, 120, 120);
                            }
                            QTabBar::tab:hover {
                                background: rgb(60, 60, 60);
                                border: 1px solid rgb(100, 100, 100);
                                padding: 5px;
                                padding-top: -10px;
                                padding-bottom: 7px;
                                margin: 4px;
                            }
                            QTabBar::tab:pressed {
                                background: rgb(30, 30, 30);
                                padding: 5px;
                                padding-top: -10px;
                                padding-bottom: 7px;
                            }
                        """)

            btn_choose_universal_xl.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            btn_choose_history_commission.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            btn_chouse_foreign_commission.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            btn_choose_specialization_commission.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            button_choose_save_path.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)
            self.save_path_label.setStyleSheet("""
                color: rgb(224, 224, 224);
                font-size: 11px;
                background: rgb(26, 26, 26);
                border: 1px solid rgb(61, 61, 61);
                border-radius: 8px;
                padding: 5px;
            """)

            button_to_open_folder_with_done_pdf.setStyleSheet("""
                            QPushButton {
                                background: rgb(60, 60, 60);
                                color: rgb(255, 255, 255);
                                border: 2px solid rgb(80, 80, 80);
                                border-radius: 10px;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: rgb(80, 80, 80);
                                border: 2px solid rgb(120, 120, 120);
                            }
                            QPushButton:pressed {
                                background: rgb(30, 30, 30);
                                padding-top: 6px;
                                padding-bottom: 4px;
                            }
                        """)

            block_for_print_process.setStyleSheet("""
                            background: rgb(26, 26, 26);
                            border-radius: 10px;
                            border: 1px solid rgb(50, 50, 50);
                        """)

            widget_for_label_choosing_way.setStyleSheet(
                "background-color: rgb(60, 60, 60); border-radius: 10px;")
            widget_for_styles.setStyleSheet(
                "border-radius:10px; background-color: rgba(60, 60, 60, 240)")

            universal_excel_label_widget.setStyleSheet(
                "background-color: rgb(100, 100, 100); border-radius: 10px;")
            history_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 100, 100); border-radius: 10px;")
            foreign_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 100, 100); border-radius: 10px;")
            specialization_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 100, 100); border-radius: 10px;")
            widget_for_progress_bar.setStyleSheet(
                "background-color: rgb(60, 60, 60); border-radius: 10px;")
            self.output_text.setStyleSheet("""
                background: rgb(13, 13, 13);
                border-radius: 10px;
                color: rgb(224, 224, 224);
                font-family: 'Courier New';
                font: bold;
                font-size: 12px;
                border: 1px solid rgb(50, 50, 50);
            """)
            block_way_save.setStyleSheet("""
                background: rgb(30, 30, 30);
                border: 1px solid rgb(60, 60, 60);
                border-radius: 10px;
            """)
            window_for_choosing_styles.setStyleSheet(
                "border-radius: 10px; background-color: rgb(60, 60, 60);")

            print("[I] [style] Применена тёмная тема")


        button_from_choose_dark_theme.clicked.connect(change_theme_to_dark)

        # кнопка смены текущего цветового оформления на фиолетовую тему
        button_from_choose_violet_theme = QPushButton(tab_2)
        button_violet_theme_path = Path(
            "resources/images/color_themes/violet_theme/violet_theme_icon.png")
        button_from_choose_violet_theme.setStyleSheet(
            f"background-image: url({button_violet_theme_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_violet_theme.setFixedSize(250, 250)
        button_from_choose_violet_theme.move(280, 110)

        button_violet_theme_path = Path(
            "resources/images/color_themes/violet_theme/violet_theme_icon.png")
        button_violet_theme_medium_path = Path(
            "resources/images/color_themes/violet_theme/violet_theme_icon_medium.png")
        button_violet_theme_mini_path = Path(
            "resources/images/color_themes/violet_theme/violet_theme_icon_mini.png")


        def change_theme_to_violet() -> None:
            """
            Функция для смены темы цветового оформления на фиолетовый.
            :return: None
            """
            QTimer.singleShot(10, lambda: (
                button_from_choose_violet_theme.setFixedSize(245, 245),
                button_from_choose_violet_theme.setStyleSheet(
                f"background-image: url({button_violet_theme_medium_path.as_posix()});"
                f" border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(282, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_violet_theme.setFixedSize(240, 240),
                button_from_choose_violet_theme.setStyleSheet(
                f"background-image: url({button_violet_theme_mini_path.as_posix()});"
                f" border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(285, 115)
            ))
            QTimer.singleShot(125, lambda: (
                button_from_choose_violet_theme.setFixedSize(245, 245),
                button_from_choose_violet_theme.setStyleSheet(
                f"background-image: url({button_violet_theme_medium_path.as_posix()});"
                f" border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(282, 112)
            ))
            QTimer.singleShot(160, lambda: (
                button_from_choose_violet_theme.setFixedSize(250, 250),
                button_from_choose_violet_theme.setStyleSheet(
                f"background-image: url({button_violet_theme_path.as_posix()});"
                f" border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(280, 110)
            ))
            back_violet_path = Path(
            "resources/images/color_themes/violet_theme/image_from_violet_theme.jpg")
            background_block.setStyleSheet(
                f"background-image: url({back_violet_path.as_posix()});")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    color: rgb(255, 255, 255);
                    font-weight: bold;
                    font-size: 13px;
                    text-align: center;
                    border: 2px solid rgb(100, 70, 120);
                    border-radius: 10px;
                    background: rgb(30, 20, 40);
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgb(120, 80, 150),
                        stop: 0.5 rgb(180, 140, 200),
                        stop: 1 rgb(120, 80, 150));
                    border-radius: 8px;
                }
            """)

            self.progress_bar_parsing.setStyleSheet("""
                QProgressBar {
                    color: rgb(255, 255, 255);
                    font-weight: bold;
                    font-size: 13px;
                    text-align: center;
                    border: 2px solid rgb(100, 70, 120);
                    border-radius: 10px;
                    background: rgb(30, 20, 40);
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgb(120, 80, 150),
                        stop: 0.5 rgb(180, 140, 200),
                        stop: 1 rgb(120, 80, 150));
                    border-radius: 8px;
                }
            """)

            choose_the_term.setStyleSheet(
                "background-color: rgb(60, 40, 80);"
                " border-radius: 10px; color: rgb(255, 255, 255);")

            radio_style_violet = """
                QRadioButton {
                    color: rgb(60, 43, 77);
                    font-size: 18px;
                    font-weight: bold;
                    spacing: 10px;
                }
                QRadioButton::indicator {
                    width: 10px;
                    height: 10px;
                    border-radius: 3px;
                    border: 2px solid rgb(100, 70, 120);
                    background: rgb(40, 30, 50);
                }
                QRadioButton::indicator:checked {
                    background-color: rgb(140, 48, 201);
                    border: 2px solid rgb(199, 137, 240);
                }
                QRadioButton::indicator:hover {
                    border: 2px solid rgb(200, 170, 220);
                }
            """
            self.radio_button_1.setStyleSheet(radio_style_violet)
            self.radio_button_2.setStyleSheet(radio_style_violet)
            self.radio_button_3.setStyleSheet(radio_style_violet)

            widget_for_label.setStyleSheet("background-color: rgb(60, 40, 80);"
                                           " border-radius: 10px;")

            self.input_commission.setStyleSheet("""
                QLineEdit {
                    background: rgb(30, 20, 40);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(60, 40, 80);
                    border-radius: 8px;
                    padding: 5px 10px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid rgb(140, 100, 160);
                    background: rgb(45, 35, 55);
                }
                QLineEdit::placeholder {
                    color: rgb(100, 80, 120);
                    font-style: italic;
                }
            """)

            parsing_button.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            widget_for_label_choosing_files.setStyleSheet(
                "background-color: rgb(60, 40, 80); border-radius: 10px;")

            self.open_folder_button.setStyleSheet("""
                QPushButton {
                    background: rgb(50, 35, 65);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(70, 50, 90);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(70, 50, 90);
                    border: 1px solid rgb(100, 75, 120);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                }
            """)

            button_to_find_file_tabel.setStyleSheet("""
                QPushButton {
                    background: rgb(50, 35, 65);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(70, 50, 90);
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: rgb(70, 50, 90);
                    border: 1px solid rgb(100, 75, 120);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            button_to_find_where_save.setStyleSheet("""
                QPushButton {
                    background: rgb(50, 35, 65);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(70, 50, 90);
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: rgb(70, 50, 90);
                    border: 1px solid rgb(100, 75, 120);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            block_where_save_pdfs_now.setStyleSheet("""              
                background: rgb(50, 35, 65);
                color: rgb(255, 255, 255);
                border: 1px solid rgb(70, 50, 90);
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            """)

            tab_widget.setStyleSheet(""" 
                QTabWidget::pane {
                    border: none;
                    background: transparent;
                }
                QTabBar::tab {
                    background: rgb(45, 30, 60);
                    color: rgb(180, 160, 200);
                    border: 1px solid rgb(60, 40, 80);
                    border-radius: 8px;
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: rgb(70, 50, 90);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(120, 90, 140);
                }
                QTabBar::tab:hover {
                    background: rgb(60, 40, 80);
                    border: 1px solid rgb(100, 75, 120);
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                }
                QTabBar::tab:pressed {
                    background: rgb(30, 20, 40);
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                }
            """)

            btn_choose_universal_xl.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            btn_choose_history_commission.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            btn_chouse_foreign_commission.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            btn_choose_specialization_commission.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            button_choose_save_path.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            self.save_path_label.setStyleSheet("""
                color: rgb(220, 210, 230);
                font-size: 11px;
                background: rgb(30, 20, 40);
                border: 1px solid rgb(60, 40, 80);
                border-radius: 8px;
                padding: 5px;
            """)

            button_to_open_folder_with_done_pdf.setStyleSheet("""
                QPushButton {
                    background: rgb(60, 40, 80);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(80, 60, 100);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(80, 60, 100);
                    border: 2px solid rgb(120, 90, 140);
                }
                QPushButton:pressed {
                    background: rgb(30, 20, 40);
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)

            block_for_print_process.setStyleSheet("""
                background: rgb(30, 20, 40);
                border-radius: 10px;
                border: 1px solid rgb(50, 35, 65);
            """)

            widget_for_label_choosing_way.setStyleSheet(
                "background-color: rgb(60, 40, 80); border-radius: 10px;")

            widget_for_styles.setStyleSheet(
                "border-radius:10px; background-color: rgba(60, 40, 80, 240);")

            universal_excel_label_widget.setStyleSheet(
                "background-color: rgb(100, 75, 120); border-radius: 10px;")
            history_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 75, 120); border-radius: 10px;")
            foreign_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 75, 120); border-radius: 10px;")
            specialization_excel_choosed_widget.setStyleSheet(
                "background-color: rgb(100, 75, 120); border-radius: 10px;")

            widget_for_progress_bar.setStyleSheet(
                "background-color: rgb(60, 40, 80); border-radius: 10px;")

            self.output_text.setStyleSheet("""
                background: rgb(20, 12, 30);
                border-radius: 10px;
                color: rgb(220, 210, 230);
                font-family: 'Courier New';
                font: bold;
                font-size: 12px;
                border: 1px solid rgb(50, 35, 65);
            """)

            block_way_save.setStyleSheet("""
                background: rgb(30, 20, 40);
                border: 1px solid rgb(60, 40, 80);
                border-radius: 10px;
            """)

            window_for_choosing_styles.setStyleSheet(
                "border-radius: 10px; background-color: rgb(60, 40, 80);")

            print("[I] [style] Применена фиолетовая тема")

        button_from_choose_violet_theme.clicked.connect(change_theme_to_violet)

        # кнопка для смены темы цветового оформления на стандартную тему
        button_from_choose_standart_theme = QPushButton(tab_2)
        button_standard_path = Path(
            "resources/images/color_themes/standard_theme/standard_theme_icon.png")
        button_from_choose_standart_theme.setStyleSheet(
            f"background-image: url({button_standard_path.as_posix()});"
            f" border-radius: 10px;")
        button_from_choose_standart_theme.setFixedSize(250, 250)
        button_from_choose_standart_theme.move(540, 110)

        button_standard_path = Path(
            "resources/images/color_themes/standard_theme/standard_theme_icon.png")
        button_standard_medium_path = Path(
        "resources/images/color_themes/standard_theme/standard_theme_icon_medium.png")
        button_standard_mini_path = Path(
            "resources/images/color_themes/standard_theme/standard_theme_icon_mini.png")


        def change_theme_to_standard() -> None:
            """
            функция смены темы цветового оформления приложения на стандартный
            """
            QTimer.singleShot(10, lambda: (
                button_from_choose_standart_theme.setFixedSize(245, 245),
                button_from_choose_standart_theme.setStyleSheet(
                    f"background-image: url({button_standard_medium_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(542, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_standart_theme.setFixedSize(240, 240),
                button_from_choose_standart_theme.setStyleSheet(
                    f"background-image: url({button_standard_mini_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(545, 115)
            ))

            QTimer.singleShot(125, lambda: (
                button_from_choose_standart_theme.setFixedSize(245, 245),
                button_from_choose_standart_theme.setStyleSheet(
                    f"background-image: url({button_standard_medium_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(542, 112)
            ))

            QTimer.singleShot(160, lambda: (
                button_from_choose_standart_theme.setFixedSize(250, 250),
                button_from_choose_standart_theme.setStyleSheet(
                    f"background-image: url({button_standard_path.as_posix()});"
                    f" border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(540, 110)
            ))
            back_standard_path = Path(
                "resources/images/background_images/DSC_5174_1.jpg")
            background_block.setStyleSheet(
                f"background-image:url({back_standard_path.as_posix()});")
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
            self.output_text.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,"
            "stop: 0 rgba(60, 95, 45, 0.2),stop: 1 rgba(45, 75, 35, 0.25));"
            "border-radius: 10px;; color: white; font-family; font: bold;"
            " font-size: 12px;")
            choose_the_term.setStyleSheet(
                "background-color: rgba(100, 140, 65, 200); border-radius: 10px;"
                " color: white;")
            block_way_save.setStyleSheet("""
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 70, 35, 0.7),
                    stop: 1 rgba(35, 55, 25, 0.8));
                border: 1px solid rgba(80, 120, 55, 150);
                border-radius: 10px;
            """)
            widget_for_styles.setStyleSheet("border-radius:10px;"
                        " background-color: rgba(45, 75, 30, 240)")
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
            universal_excel_label_widget.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            history_excel_choosed_widget.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            foreign_excel_choosed_widget.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            specialization_excel_choosed_widget.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            self.save_path_label.setStyleSheet("""
                color: white;
                font-size: 11px;
                background: rgba(45, 70, 35, 150);
                border: 1px solid rgba(100, 140, 65, 150);
                border-radius: 8px;
                padding: 5px;
            """)
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
            widget_for_label.setStyleSheet("background-color: rgba(83, 140, 65, 1);"
                                           " border-radius: 10px;")
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
            parsing_button.setStyleSheet("""
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
            window_for_choosing_styles.setStyleSheet(
                "border-radius: 10px; background-color: rgba(45, 64, 30, 240)")
            widget_for_label_choosing_files.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
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
            button_to_find_file_tabel.setStyleSheet("""
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
            button_to_find_where_save.setStyleSheet("""
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
            block_where_save_pdfs_now.setStyleSheet("""              
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
            tab_widget.setStyleSheet(""" 
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
            parsing_button.setStyleSheet("""
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
            btn_choose_universal_xl.setStyleSheet("""
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
            btn_choose_history_commission.setStyleSheet("""
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
            btn_chouse_foreign_commission.setStyleSheet("""
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
            btn_choose_specialization_commission.setStyleSheet("""
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
            button_choose_save_path.setStyleSheet("""
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
            button_to_open_folder_with_done_pdf.setStyleSheet("""
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
            block_for_print_process.setStyleSheet(
                "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,"
                " stop: 0 rgba(60, 85, 45, 230),stop: 1 rgba(40, 65, 30, 230));"
                " border-radius: 10px;")
            choose_the_term.setStyleSheet(
                "background-color: rgba(100, 140, 65, 200);"
                " border-radius: 10px; color: white;")
            widget_for_label.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            widget_for_label_choosing_files.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            widget_for_label_choosing_way.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
            widget_for_progress_bar.setStyleSheet(
                "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
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
            radio_style = """
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
            """
            self.radio_button_1.setStyleSheet(radio_style)
            self.radio_button_2.setStyleSheet(radio_style)
            self.radio_button_3.setStyleSheet(radio_style)
            print("[I] [style] применена стандартная тема")


        button_from_choose_standart_theme.clicked.connect(change_theme_to_standard)

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
        choose_the_term = QWidget(tab_3)
        choose_the_term.setFixedSize(200, 50)
        choose_the_term.setStyleSheet(
        "background-color: rgba(100, 140, 65, 200); border-radius: 10px; color: white;")
        choose_the_term.move(60, 20)
        label_choose_the_term = QLabel(choose_the_term)
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
        widget_for_label = QWidget(tab_3)
        widget_for_label.setFixedSize(730,80)
        widget_for_label.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label.move(320,10)

        # label для приказа о комиссиях.
        label_commission = QLabel(widget_for_label)
        label_commission.setGeometry(10,5,700,30)
        label_commission.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_commission.setText("Приказ о комиссиях")
        label_commission.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 18px;
        """)

        # поле ввода для приказа о комиссиях
        self.input_commission = QLineEdit(widget_for_label)
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
        parsing_button = QPushButton("Начать парсинг и генерацию PDF", tab_3)
        parsing_button.setStyleSheet("""
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
        parsing_button.setFixedSize(280,40)
        parsing_button.move(370,740)
        parsing_button.clicked.connect(lambda: parsing(self))

        # background блок для выбора файлов - doc файлов и универсальной таблицы
        background_widget_for_choose_files = QWidget(tab_3)
        background_widget_for_choose_files.setFixedSize(730,310)
        background_widget_for_choose_files.move(320,100)
        background_widget_for_choose_files.setStyleSheet(
            "background-color: white; border-radius: 10px;")

        # предложение для пользователя о выборе фалов.
        widget_for_label_choosing_files = QWidget(tab_3)
        widget_for_label_choosing_files.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label_choosing_files.setFixedSize(300, 50)
        widget_for_label_choosing_files.move(525, 110)
        self.label_for_choozing_files = QLabel(widget_for_label_choosing_files)
        self.label_for_choozing_files.setStyleSheet(
            "color: white; font: bold; font-size: 14px;")
        self.label_for_choozing_files.setGeometry(0,0,300,50)
        self.label_for_choozing_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_choozing_files.setText("Пожалуйста, выберите файлы")

        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        btn_choose_universal_xl = QPushButton(
            "Выберите таблицу для парсинга",tab_3)
        btn_choose_universal_xl.setFixedSize(360,50)
        btn_choose_universal_xl.setStyleSheet("""
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
        btn_choose_universal_xl.move(680,290)
        btn_choose_universal_xl.clicked.connect(lambda: choose_universal_excel(self))

        # виджет сменит свой стандартный текст на имя выбранной таблицы
        universal_excel_label_widget = QWidget(tab_3)
        universal_excel_label_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        universal_excel_label_widget.setFixedSize(360,50)
        universal_excel_label_widget.move(680, 350)
        self.universal_excel_label = QLabel(universal_excel_label_widget)
        self.universal_excel_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setText("Здесь будет имя выбранного файла...")
        self.universal_excel_label.setGeometry(0,0,360,50)

        # кнопка для выбора doc файла с данными комиссии по истории
        btn_choose_history_commission = QPushButton(
            "Выберите таблицу 'Комиссия - история.doc'",tab_3)
        btn_choose_history_commission.setFixedSize(330,50)
        btn_choose_history_commission.setStyleSheet("""
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
        btn_choose_history_commission.move(330, 170)
        btn_choose_history_commission.clicked.connect(lambda: choose_history_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        history_excel_choosed_widget = QWidget(tab_3)
        history_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        history_excel_choosed_widget.setFixedSize(330, 50)
        history_excel_choosed_widget.move(330, 230)
        self.history_xl_choused_label = QLabel(history_excel_choosed_widget)
        self.history_xl_choused_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.history_xl_choused_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_xl_choused_label.setText(
            "Здесь будет имя выбранного файла...")
        self.history_xl_choused_label.setGeometry(0, 0, 330, 50)

        # кнопка для выбора doc файла с данными комиссии по иностранному
        btn_chouse_foreign_commission = QPushButton(
            "Выберите таблицу 'Комиссия - иностранный.doc'", tab_3)
        btn_chouse_foreign_commission.setFixedSize(360, 50)
        btn_chouse_foreign_commission.setStyleSheet("""
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
        btn_chouse_foreign_commission.move(680, 170)
        btn_chouse_foreign_commission.clicked.connect(lambda: choose_foreign_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        foreign_excel_choosed_widget = QWidget(tab_3)
        foreign_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        foreign_excel_choosed_widget.setFixedSize(360, 50)
        foreign_excel_choosed_widget.move(680, 230)
        self.foreign_xl_choosed_label = QLabel(foreign_excel_choosed_widget)
        self.foreign_xl_choosed_label.setStyleSheet(
            "color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.foreign_xl_choosed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreign_xl_choosed_label.setText(
            "Здесь будет имя выбранного файла...")
        self.foreign_xl_choosed_label.setGeometry(0, 0, 360, 50)

        # кнопка для выбора doc файла с данными комиссии по специальности
        btn_choose_specialization_commission = QPushButton(
            "Выберите таблицу 'Комиссия - специальность.doc'", tab_3)
        btn_choose_specialization_commission.setFixedSize(330, 50)
        btn_choose_specialization_commission.setStyleSheet("""
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
        btn_choose_specialization_commission.move(330, 290)
        btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        specialization_excel_choosed_widget = QWidget(tab_3)
        specialization_excel_choosed_widget.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        specialization_excel_choosed_widget.setFixedSize(330, 50)
        specialization_excel_choosed_widget.move(330, 350)
        self.specialization_xl_choosed_lb = QLabel(specialization_excel_choosed_widget)
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
        widget_for_label_choosing_way = QWidget(tab_3)
        widget_for_label_choosing_way.setFixedSize(280,50)
        widget_for_label_choosing_way.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label_choosing_way.move(20, 230)
        self.lb_choosing_way_save_parsing_pdf = QLabel(widget_for_label_choosing_way)
        self.lb_choosing_way_save_parsing_pdf.setStyleSheet(
            "color: white; font: bold; font-size: 14px;")
        self.lb_choosing_way_save_parsing_pdf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_choosing_way_save_parsing_pdf.setText(
            "Выберите путь сохранения для PDF")
        self.lb_choosing_way_save_parsing_pdf.setGeometry(0,0,280,50)

        # Кнопка выбора пути сохранения
        button_choose_save_path = QPushButton("Выбрать папку", tab_3)
        button_choose_save_path.setFixedSize(250, 40)
        button_choose_save_path.move(35, 290)
        button_choose_save_path.setStyleSheet("""
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

        button_choose_save_path.clicked.connect(self.choose_parsing_save_folder)


        # блок для пояснения к прогресс бару
        widget_for_progress_bar = QWidget(tab_3)
        widget_for_progress_bar.setFixedSize(1040,75)
        widget_for_progress_bar.setStyleSheet(
            "background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_progress_bar.move(10,420)
        self.label_for_progress = QLabel(widget_for_progress_bar)
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
        button_to_open_folder_with_done_pdf = QPushButton("Открыть папку с PDF", tab_3)
        button_to_open_folder_with_done_pdf.setFixedSize(280,50)
        button_to_open_folder_with_done_pdf.setStyleSheet("""
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
        button_to_open_folder_with_done_pdf.move(370,680)
        button_to_open_folder_with_done_pdf.clicked.connect(
            lambda: open_parsing_pdf_folder(self))


    def choose_parsing_save_folder(self) -> None:
        """
        выбор папки сохранения для собранных пдф по таблице с собранным БД
        """

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения PDF (парсинг)",
            self.parsing_save_folder_path
        )
        if folder_path:
            self.parsing_save_folder_path = folder_path
            self.save_path_label.setText(folder_path)

    def update_progress(self, current: int, total: int) -> None:
        """
        функция обновления прогресса qprogressbar.
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
        sound_path = str(Path(__file__).parent.parent / "resources"
                         / "sounds" / "guitar_sound.wav")

        # Проверяем существование файла
        if Path(sound_path).exists():
            self.sound_effect.setSource(QUrl.fromLocalFile(sound_path))
            self.sound_effect.setVolume(0.13)  # Громкость от 0.0 до 1.0
        else:
            print(f"[W] Звуковой файл не найден: {sound_path}")

    def play_open_sound(self) -> None:
        """
        Воспроизведение звука при открытии окна
        """

        if hasattr(self, 'sound_effect') and self.sound_effect.source().isValid():
            self.sound_effect.play()
        else:
            print("[W] Звук не воспроизведён - файл не найден или не загружен")

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
