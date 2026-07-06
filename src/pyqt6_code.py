from pyqt_functions import get_pdf, choose_file, choose_save_folder, open_pdf_folder, choose_universal_excel # импорт функций из файла pyqt_functions.py - функции для работы интерфейса основного окна, вынесенные в отдельный файл
import os # Для работы с файловой системой (пути, папки)
from PyQt6.QtWidgets import QWidget, QLabel, QTabWidget, QPushButton, QTextEdit, QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QFileDialog # Основные виджеты PyQt6
from PyQt6.QtCore import QPoint, QTimer, Qt, QSize # QPoint — для перетаскивания окон, QTimer — для задержек, Qt — константы, QSize — размеры
from PyQt6.QtGui import QIcon, QTransform # QIcon — иконки, QTransform — поворот иконок

from pyqt_functions import parsing, choose_foreign_excel, choose_history_excel, choose_specialization_excel, open_parsing_pdf_folder # разделил файл на два - в один написал код pyqt, в другой написал код функций, чтобы было удобнее ориентироваться по коду

class MyWindow(QWidget): # Класс главного окна программы (наследуется от QWidget)
    def __init__(self): # конструктор
        super().__init__() # Вызов конструктора родительского класса QWidget

        # устанавливаю дефолтные пути к файлам пустыми
        self.excel_file_path = None
        self.universal_file_path = None
        self.students_data = None
        self.commission_members = None

        # Пути к файлам комиссий
        self.history_commission_path = None
        self.foreign_commission_path = None
        self.specialization_commission_path = None

        desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop") # Путь к рабочему столу пользователя

        self.save_folder_path = os.path.join(desktop_path, "results_folder") # Папка для сохранения результатов

        block_background = QWidget(self)  # первый виджет. первым появится, имеет размер всего окна загрузки, используется для фона загрузочного окна
        block_background.setFixedSize(1200, 800)
        block_background.setStyleSheet("background-image:url(../images/background_images/DSC_5174_1.jpg);")
        block_background.move(0, 0)

        self.drag_position = QPoint() # Это создан атрибут для хранения позиции мыши, это будет объект класса qpoint. для начала точка будет иметь координаты 0.0

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint) #  удаление стандартной рамки окна (заголовок, кнопки свернуть, развернуть, закрыть)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # включение прозрачного фона для окна, скрывается рамка окна

        tabWidgetObjects = QTabWidget(self) # виджет вкладок

        tabWidgetObjects.setFixedSize(1200, 800)  # Размер виджета вкладок

        tabWidgetObjects.setTabPosition(QTabWidget.TabPosition.West) # позиция вкладок слева

        tabWidgetObjects.setIconSize(QSize(65, 65)) # Размер иконок на вкладках

        tabWidgetObjects.setTabBarAutoHide(False) # Вкладки всегда видны

        # стиль вкладок через qss
        tabWidgetObjects.setStyleSheet(""" 
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
        tabObjects_1 = QWidget() # вкладка 1

        tabObjects_2 = QWidget() # вкладка 2

        tabObjects_3 = QWidget() # вкладка 3

        # кнопка открытия папки с пдф (первая вкладка)
        self.open_folder_button = QPushButton("Открыть папку с PDF", tabObjects_1)
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
        self.open_folder_button.clicked.connect(lambda: open_pdf_folder(self)) # При клике открывает папку с пдф, но чтобы передать аргумент self к функции, которую я вывел в отдельный файл, пришлось использовать лямбда функцию

        # добавление вкладок
        tabWidgetObjects.addTab(tabObjects_1, "") # кладка 1
        tabWidgetObjects.addTab(tabObjects_3, "") # кладка 2
        tabWidgetObjects.addTab(tabObjects_2, "") # кладка 3
        # порядок добавления определяет их положение среди вкладок

        def rotate_icon(icon_path, size=65, angle=90): # Функция для поворота иконок на 90 градусов по пути файла и размер у всех 65
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(size, size)
            transform = QTransform().rotate(angle)
            rotated_pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            return QIcon(rotated_pixmap)

        # вызов функций поворота иконок, потому что изначально иконки находятся в неправильном положении
        icon1 = rotate_icon("../images/icons/pdf.png")
        icon2 = rotate_icon("../images/icons/settings.png")
        icon3 = rotate_icon("../images/icons/parsing_ill.png")

        # устанавливаю иконки на вкладки
        tabWidgetObjects.setTabIcon(0, icon1)
        tabWidgetObjects.setTabIcon(1, icon3)
        tabWidgetObjects.setTabIcon(2, icon2)

        button_close = QPushButton(self) # создание кастомной кнопки закрытия окна, так как стандартную я удалил
        button_close.setFixedSize(45, 45)
        button_close.move(1150, 5)
        button_close.setCursor(Qt.CursorShape.DragMoveCursor) # при наведении на кнопку курсор сменится на выбранный в методе
        button_close.setStyleSheet("""
            background-image:url(../images/icons/close_icon.png);
            background-color: transparent;
            border: none;
            background-repeat: no-repeat;
            background-position: center;
            """)
        button_close.clicked.connect(self.close) # При клике закрывает окно

        # блок для логгирования процесса работы программы, дублирования логгирования вывода из консоли
        block_for_print_process = QWidget(tabObjects_1) # Виджет-контейнер для текстового поля
        block_for_print_process.setFixedSize(1020, 620)
        block_for_print_process.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(60, 85, 45, 230),stop: 1 rgba(40, 65, 30, 230)); border-radius: 10px;")
        block_for_print_process.move(10, 100)

        self.output_text = QTextEdit(block_for_print_process) # Поле для вывода лога (self — чтобы использовать в других методах)
        self.output_text.setGeometry(5, 35, 1010, 580)
        self.output_text.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 rgba(60, 95, 45, 0.2),stop: 1 rgba(45, 75, 35, 0.25));border-radius: 10px;; color: white; font-family; font: bold; font-size: 12px;")
        self.output_text.setReadOnly(True) # Только для чтения (пользователь не может редактировать)

        # кнопка выбора файла эксель
        button_to_find_file_tabel = QPushButton(tabObjects_1)
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
        button_to_find_file_tabel.clicked.connect(lambda: choose_file(self)) # При клике открывает диалог выбора файла, но чтобы передать аргумент self к функции, которую я вывел в отдельный файл, пришлось использовать лямбда функцию

        # кнопка изменения пути сохранения
        button_to_find_where_save = QPushButton(tabObjects_1)
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
        button_to_find_where_save.clicked.connect(lambda: choose_save_folder(self)) # вызов функции выбора пути сохранения

        # блок сообщения пути отображения пути сохранения пдф файлов
        block_where_save_pdfs_now = QWidget(tabObjects_1)
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

        block_where_save_pdfs_now_label = QLabel(block_where_save_pdfs_now)
        block_where_save_pdfs_now_label.setText("Путь сохранения:")
        block_where_save_pdfs_now_label.setGeometry(0, 0, 160, 50)
        block_where_save_pdfs_now_label.setStyleSheet("color:white; font: bold; font-size: 14px;")
        block_where_save_pdfs_now_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # отображение текущего пути сохранения файлов
        block_way_save = QWidget(tabObjects_1)
        block_way_save.setFixedSize(340, 50)
        block_way_save.setStyleSheet("""
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 70, 35, 0.7),
                    stop: 1 rgba(35, 55, 25, 0.8));
                border: 1px solid rgba(80, 120, 55, 150);
                border-radius: 10px;
            """)
        block_way_save.move(630, 25)

        self.path_value_label = QLabel(block_way_save) # self — чтобы обновлять путь при изменении
        short_path = self.save_folder_path
        if len(short_path) > 150:
            short_path = "..." + short_path[-150:]
        else:
            short_path = self.save_folder_path
        self.path_value_label.setText(short_path)
        self.path_value_label.setGeometry(5, 5, 330, 40)
        self.path_value_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        self.path_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path_value_label.setWordWrap(True)
        block_way_save.setToolTip(self.save_folder_path)


        button_do_operation = QPushButton(tabObjects_1)
        button_do_operation.setFixedSize(50, 50)
        button_do_operation.setCursor(Qt.CursorShape.ClosedHandCursor)
        button_do_operation.setStyleSheet(
            "background-image: url(../images/icons/do_op_new.png); color: white; font-size: 14px; font:bold; border-radius: 10px;")
        button_do_operation.move(980, 25)
        button_do_operation.clicked.connect(lambda: get_pdf(self))

        widget_for_styles = QWidget(tabObjects_2)
        widget_for_styles.setFixedSize(300, 45)
        widget_for_styles.setStyleSheet("border-radius:10px; background-color: rgba(45, 75, 30, 240)")
        widget_for_styles.move(10, 27)
        label_for_styles = QLabel(widget_for_styles)
        label_for_styles.setStyleSheet("color:white; font: bold; font-size: 18px;")
        label_for_styles.setText("Выберите стиль оформления")
        label_for_styles.setGeometry(0, 0, 300, 45)
        label_for_styles.setAlignment(Qt.AlignmentFlag.AlignCenter)

        window_for_choosing_styles = QWidget(tabObjects_2)
        window_for_choosing_styles.setFixedSize(1030, 600)
        window_for_choosing_styles.setStyleSheet("border-radius: 10px; background-color: rgba(45, 64, 30, 240)")
        window_for_choosing_styles.move(10, 100)

        button_from_choose_dark_theme = QPushButton(tabObjects_2)
        button_from_choose_dark_theme.setStyleSheet("background-image: url(../images/color_themes/dark_theme/dark_theme_icon.png); border-radius: 10px;")
        button_from_choose_dark_theme.setFixedSize(250, 250)
        button_from_choose_dark_theme.move(20, 110)

        def change_theme_to_dark():
            QTimer.singleShot(10, lambda: (
                button_from_choose_dark_theme.setFixedSize(245, 245),
                button_from_choose_dark_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/dark_theme/dark_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(22, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_dark_theme.setFixedSize(240, 240),
                button_from_choose_dark_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/dark_theme/dark_theme_icon_mini.png); border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(25, 115)
            ))

            QTimer.singleShot(125, lambda: (
                button_from_choose_dark_theme.setFixedSize(245, 245),
                button_from_choose_dark_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/dark_theme/dark_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(22, 112)
            ))

            QTimer.singleShot(160, lambda: (
                button_from_choose_dark_theme.setFixedSize(250, 250),
                button_from_choose_dark_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/dark_theme/dark_theme_icon.png); border-radius: 10px;"
                ),
                button_from_choose_dark_theme.move(20, 110)
            ))

        button_from_choose_dark_theme.clicked.connect(change_theme_to_dark)

        button_from_choose_violet_theme = QPushButton(tabObjects_2)
        button_from_choose_violet_theme.setStyleSheet(
            "background-image: url(../images/color_themes/violet_theme/violet_theme_icon.png); border-radius: 10px;")
        button_from_choose_violet_theme.setFixedSize(250, 250)
        button_from_choose_violet_theme.move(280, 110)

        def change_theme_to_violet():
            QTimer.singleShot(10, lambda: (
                button_from_choose_violet_theme.setFixedSize(245, 245),
                button_from_choose_violet_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/violet_theme/violet_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(282, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_violet_theme.setFixedSize(240, 240),
                button_from_choose_violet_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/violet_theme/violet_theme_icon_mini.png); border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(285, 115)
            ))
            QTimer.singleShot(125, lambda: (
                button_from_choose_violet_theme.setFixedSize(245, 245),
                button_from_choose_violet_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/violet_theme/violet_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(282, 112)
            ))
            QTimer.singleShot(160, lambda: (
                button_from_choose_violet_theme.setFixedSize(250, 250),
                button_from_choose_violet_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/violet_theme/violet_theme_icon.png); border-radius: 10px;"
                ),
                button_from_choose_violet_theme.move(280, 110)
            ))

        button_from_choose_violet_theme.clicked.connect(change_theme_to_violet)

        button_from_choose_standart_theme = QPushButton(tabObjects_2)
        button_from_choose_standart_theme.setStyleSheet(
            "background-image: url(../images/color_themes/standard_theme/standard_theme_icon.png); border-radius: 10px;")
        button_from_choose_standart_theme.setFixedSize(250, 250)
        button_from_choose_standart_theme.move(540, 110)

        def change_theme_to_standard():
            QTimer.singleShot(10, lambda: (
                button_from_choose_standart_theme.setFixedSize(245, 245),
                button_from_choose_standart_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/standard_theme/standard_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(542, 112)
            ))

            QTimer.singleShot(45, lambda: (
                button_from_choose_standart_theme.setFixedSize(240, 240),
                button_from_choose_standart_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/standard_theme/standard_theme_icon_mini.png); border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(545, 115)
            ))

            QTimer.singleShot(125, lambda: (
                button_from_choose_standart_theme.setFixedSize(245, 245),
                button_from_choose_standart_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/standard_theme/standard_theme_icon_medium.png); border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(542, 112)
            ))

            QTimer.singleShot(160, lambda: (
                button_from_choose_standart_theme.setFixedSize(250, 250),
                button_from_choose_standart_theme.setStyleSheet(
                    "background-image: url(../images/color_themes/standard_theme/standard_theme_icon.png); border-radius: 10px;"
                ),
                button_from_choose_standart_theme.move(540, 110)
            ))

        button_from_choose_standart_theme.clicked.connect(change_theme_to_standard)

        QTimer.singleShot(1, self.center_window)

        self.progress_bar = QProgressBar(tabObjects_1)
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

        # ============================================================
        # Третья вкладка
        # ============================================================

        # виджет, используемый для фона для ралиокнопок выбора семестра и лейбла
        background_widget_for_choosing_term = QWidget(tabObjects_3)
        background_widget_for_choosing_term.setFixedSize(300, 200)
        background_widget_for_choosing_term.setStyleSheet("background-color: white; border-radius: 10px;")
        background_widget_for_choosing_term.move(10,10)

        # виджет с лейблом, предлагающим пользователю выбрать семестр
        choose_the_term = QWidget(tabObjects_3)
        choose_the_term.setFixedSize(200, 50)
        choose_the_term.setStyleSheet("background-color: rgba(100, 140, 65, 200); border-radius: 10px; color: white;")
        choose_the_term.move(60, 20)
        label_choose_the_term = QLabel(choose_the_term)
        label_choose_the_term.setText("Выберите семестр:")
        label_choose_the_term.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_choose_the_term.setStyleSheet("font: bold; font-size: 18px; color: white;")
        label_choose_the_term.setGeometry(0, 0, 200, 50)

        # первая радиокнока. по условию должна активировать работу с doc файлом комиссии по истории
        self.radio_button_1 = QRadioButton("Первый семестр", tabObjects_3) # активирует работу с файлом «Комиссии - История.doc»
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

        # вторая радиокнока. по условию должна активировать работу с doc файлом комиссии по иностранному
        self.radio_button_2 = QRadioButton("Второй семестр", tabObjects_3) # активирует работу с файлом «Комиссии - Иностранный.doc»
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
        # третья радиокнока. по условию должна активировать работу с doc файлом комиссии по специальности
        self.radio_button_3 = QRadioButton("Третий семестр", tabObjects_3) # активирует работу с файлом «Комиссии - Специальность.doc»
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
        self.button_group = QButtonGroup(tabObjects_3)
        self.button_group.addButton(self.radio_button_1)
        self.button_group.addButton(self.radio_button_2)
        self.button_group.addButton(self.radio_button_3)

        # Добавить input с label: «Приказ о комиссиях»
        widget_for_label = QWidget(tabObjects_3)
        widget_for_label.setFixedSize(730,80)
        widget_for_label.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label.move(320,10)

        # лейбл для приказа о комиссиях. родителем для него будет виджет с input label
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

        # Главная кнопка, запускающая и парсинг всех необходимых данных, и сбор этих данных в пдф. запускает выполнение функции parsing (функция, вызывающая все функции парсинга и сбора данных в пдф)
        parsing_button = QPushButton("Начать парсинг и генерацию PDF", tabObjects_3)
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
        background_widget_for_choose_files = QWidget(tabObjects_3)
        background_widget_for_choose_files.setFixedSize(730,310)
        background_widget_for_choose_files.move(320,100)
        background_widget_for_choose_files.setStyleSheet("background-color: white; border-radius: 10px;")

        # предложение для пользователя о выборе фалов. Виджет является родителем для самого лейбла с предложением выбора файлов
        widget_for_label_choosing_files = QWidget(tabObjects_3)
        widget_for_label_choosing_files.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label_choosing_files.setFixedSize(300, 50)
        widget_for_label_choosing_files.move(525, 110)
        self.label_for_choozing_files = QLabel(widget_for_label_choosing_files)
        self.label_for_choozing_files.setStyleSheet("color: white; font: bold; font-size: 14px;")
        self.label_for_choozing_files.setGeometry(0,0,300,50)
        self.label_for_choozing_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_choozing_files.setText("Пожалуйста, выберите файлы")

        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        button_choose_universal_excel = QPushButton("Выберите таблицу для парсинга",tabObjects_3)
        button_choose_universal_excel.setFixedSize(360,50)
        button_choose_universal_excel.setStyleSheet("""
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
        button_choose_universal_excel.move(680,290)
        button_choose_universal_excel.clicked.connect(lambda: choose_universal_excel(self))

        # виджет, который при выборе "универсальной таблицы", сменит свой стандартный текст на имя выбранной таблицы
        universal_excel_label_widget = QWidget(tabObjects_3)
        universal_excel_label_widget.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        universal_excel_label_widget.setFixedSize(360,50)
        universal_excel_label_widget.move(680, 350)
        self.universal_excel_label = QLabel(universal_excel_label_widget)
        self.universal_excel_label.setStyleSheet("color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setText("Здесь будет имя выбранного файла...")
        self.universal_excel_label.setGeometry(0,0,360,50)

        # кнопка для выбора doc файла с данными комиссии по истории
        button_choose_history_commission = QPushButton("Выберите таблицу 'Комиссия - история.doc'",tabObjects_3)
        button_choose_history_commission.setFixedSize(330,50)
        button_choose_history_commission.setStyleSheet("""
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
        button_choose_history_commission.move(330, 170)
        button_choose_history_commission.clicked.connect(lambda: choose_history_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        history_excel_choosed_widget = QWidget(tabObjects_3)
        history_excel_choosed_widget.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        history_excel_choosed_widget.setFixedSize(330, 50)
        history_excel_choosed_widget.move(330, 230)
        self.history_excel_choosed_widget_label = QLabel(history_excel_choosed_widget)
        self.history_excel_choosed_widget_label.setStyleSheet("color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.history_excel_choosed_widget_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_excel_choosed_widget_label.setText("Здесь будет имя выбранного файла...")
        self.history_excel_choosed_widget_label.setGeometry(0, 0, 330, 50)

        # кнопка для выбора doc файла с данными комиссии по иностранному
        button_choose_foreign_commission = QPushButton("Выберите таблицу 'Комиссия - иностранный.doc'", tabObjects_3)
        button_choose_foreign_commission.setFixedSize(360, 50)
        button_choose_foreign_commission.setStyleSheet("""
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
        button_choose_foreign_commission.move(680, 170)
        button_choose_foreign_commission.clicked.connect(lambda: choose_foreign_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        foreign_excel_choosed_widget = QWidget(tabObjects_3)
        foreign_excel_choosed_widget.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        foreign_excel_choosed_widget.setFixedSize(360, 50)
        foreign_excel_choosed_widget.move(680, 230)
        self.foreign_excel_choosed_widget_label = QLabel(foreign_excel_choosed_widget)
        self.foreign_excel_choosed_widget_label.setStyleSheet("color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.foreign_excel_choosed_widget_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreign_excel_choosed_widget_label.setText("Здесь будет имя выбранного файла...")
        self.foreign_excel_choosed_widget_label.setGeometry(0, 0, 360, 50)

        # кнопка для выбора doc файла с данными комиссии по специальности
        button_choose_specialization_commission = QPushButton("Выберите таблицу 'Комиссия - специальность.doc'", tabObjects_3)
        button_choose_specialization_commission.setFixedSize(330, 50)
        button_choose_specialization_commission.setStyleSheet("""
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
        button_choose_specialization_commission.move(330, 290)
        button_choose_specialization_commission.clicked.connect(lambda: choose_specialization_excel(self))

        # виджет, который сменит свой стандартный текст на имя выбранного doc файла
        specialization_excel_choosed_widget = QWidget(tabObjects_3)
        specialization_excel_choosed_widget.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        specialization_excel_choosed_widget.setFixedSize(330, 50)
        specialization_excel_choosed_widget.move(330, 350)
        self.specialization_excel_choosed_label = QLabel(specialization_excel_choosed_widget)
        self.specialization_excel_choosed_label.setStyleSheet("color: rgb(211, 211, 211); font: bold; font-size: 12px;")
        self.specialization_excel_choosed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.specialization_excel_choosed_label.setText("Здесь будет имя выбранного файла...")
        self.specialization_excel_choosed_label.setGeometry(0, 0, 330, 50)

        # виджет, используемый как фон для кнопки выбора пути сохранения готовых пдф документов
        widget_for_choose_save_way_for_parsed_pdf = QWidget(tabObjects_3)
        widget_for_choose_save_way_for_parsed_pdf.setFixedSize(300, 190)
        widget_for_choose_save_way_for_parsed_pdf.setStyleSheet("background-color: white; border-radius: 10px;")
        widget_for_choose_save_way_for_parsed_pdf.move(10, 220)

        # label с предложением пользователю выбрать папку, в которой сохранятся готовые пдф файлы.
        widget_for_label_choosing_way = QWidget(tabObjects_3)
        widget_for_label_choosing_way.setFixedSize(280,50)
        widget_for_label_choosing_way.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_label_choosing_way.move(20, 230)
        self.label_for_choosing_way_save_for_parsing_pdf = QLabel(widget_for_label_choosing_way)
        self.label_for_choosing_way_save_for_parsing_pdf.setStyleSheet("color: white; font: bold; font-size: 14px;")
        self.label_for_choosing_way_save_for_parsing_pdf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_choosing_way_save_for_parsing_pdf.setText("Выберите путь сохранения для PDF")
        self.label_for_choosing_way_save_for_parsing_pdf.setGeometry(0,0,280,50)

        # Кнопка выбора пути сохранения
        button_choose_save_path = QPushButton("Выбрать папку", tabObjects_3)
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

        # лейбл отображает текущий путь к папке сохранения пдф. Дефолтный путь сохранения - папка results_folder на рабочем столе
        self.save_path_label = QLabel("Папка не выбрана", tabObjects_3)
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


        # блок для пояснения к прогресс бару (показвает, что прогресс будет обновляться только при создании пдф, прогресс парсинга не влияет на обновление прогресса)
        widget_for_progress_bar = QWidget(tabObjects_3)
        widget_for_progress_bar.setFixedSize(1040,75)
        widget_for_progress_bar.setStyleSheet("background-color: rgba(83, 140, 65, 1); border-radius: 10px;")
        widget_for_progress_bar.move(10,420)
        self.label_for_progress = QLabel(widget_for_progress_bar)
        self.label_for_progress.setText("Прогресс сборки PDF")
        self.label_for_progress.setStyleSheet("color: white; font-size: 18px; font: bold;")
        self.label_for_progress.setGeometry(0,0,1040,50)
        self.label_for_progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # прогресс бар для второй вкладки (с парсингом)
        self.progress_bar_parsing = QProgressBar(tabObjects_3)
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
        button_to_open_folder_with_done_pdf = QPushButton("Открыть папку с PDF", tabObjects_3)
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
        button_to_open_folder_with_done_pdf.clicked.connect(lambda: open_parsing_pdf_folder(self))


    def choose_parsing_save_folder(self):
        """выбор папки сохранения для собранных пдф по таблице с собранным БД"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения PDF (парсинг)",
            self.parsing_save_folder_path
        )
        if folder_path:
            self.parsing_save_folder_path = folder_path
            self.save_path_label.setText(folder_path)

    def update_progress(self, current, total):
        """функция обновления прогресса qprogressbar."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            QApplication.processEvents()

    def center_window(self):
        """функция для центрирования главного окна, чтобы оно появлялось по центру экрана пользователя после исчезновения загрузочного окна"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        """функция, отслеживающая точку, где пользователь зажал ЛКМ"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """функция для вычисления смещения по изменения позиции зажатой ЛКМ. Перемещает окно при движении мыши с зажатой ЛКМ."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()
