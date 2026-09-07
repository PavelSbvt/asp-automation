import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import webbrowser

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton,
    QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit,
    QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout, QScrollArea, QSlider)

from core.settings_manager import settings
from utils.output_rich import debug_log, simple_log
from utils.functions_for_window_gui import (get_random_image_from_folder,
    get_main_color_image)
from gui.functions.choose_files import (choose_universal_excel,
    choose_parsing_save_folder, open_parsing_pdf_folder,
    choose_history_excel, choose_foreign_excel, choose_specialization_excel,
    open_pdf_folder, choose_save_folder_second_tab
    )
from core.generate_pdf import choose_file, get_pdf
from utils.fonts import fonts
from gui.functions.pyqt_functions import parsing
from gui.main_window.for_main_window.styles import style
from parser.sait_parsing import update_data


class MainWindow(QMainWindow):
    """
    Класс для нового главного окна
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")

        self.setMinimumSize(900, 650)

        self.setWindowTitle(settings.get_app_name())

        # Текущая ширина окна. Установлено стандартное значение
        self.width_now = 0
        # Текущая высота окна. Установлено стандартное значение
        self.height_now = 0

        # Текущая открытая вкладка. Для обработки ошибок установлено значение -1
        self.choose_tab = -1

        self.stop_generation: bool = False  # булевый флаг остановки сборки пдф и парсинга

        self.stop_building_pdf: bool = False  # булевый флаг остановки сборки пдф

        # устанавливаю дефолтные пути к файлам пустыми
        self.excel_file_path: Optional[str] = None  # путь к файлу - шаблон для ЛР
        self.universal_file_path: Optional[str] = None  # путь к универсальной таблице
        self.students_data: Optional[List[Dict[str, Any]]] = None  # данные студентов
        self.commission_members: Optional[List[str]] = None  # члены комиссии

        # Пути к файлам комиссий
        self.history_commission_path: Optional[str] = None
        self.foreign_commission_path: Optional[str] = None
        self.specialization_commission_path: Optional[str] = None

        # Путь к последнему установленному фоновому
        # изображению для фона виджета основной вкладки
        self.bg_path_check = ""

        # стандартная папка сохранения пдф фалов в результате работы функций
        self.save_folder_path: str = str(
            Path.home() / "Desktop" / "results_folder")
        self.parsing_save_folder_path = self.save_folder_path

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        # Главный виджет
        self.main_back_widget = QWidget(self)
        self.main_back_widget.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 0px;")
        self.setCentralWidget(self.main_back_widget)

        # Главный вертикальный layout
        self.main_v_layout = QVBoxLayout()
        self.main_back_widget.setLayout(self.main_v_layout)

        # Работа с вкладками
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(fonts.get_qfont("JetBrains_Regular", 10))

        # Вкладки
        tab_main_widget = QWidget()
        tab_second_widget = QWidget()
        tab_settings_widget = QWidget()

        # Загрузка вкладок
        self.tab_widget.addTab(tab_main_widget, "Главная")
        self.tab_widget.addTab(tab_second_widget, "ЛР по формированию PDF")
        self.tab_widget.addTab(tab_settings_widget, "Настройки")

        # Вкладка с настройками скрыта, открывается только с кнопки
        self.tab_widget.setTabVisible(2, False)

        # Шапка главного окна
        self.cap_widget = QWidget(self)
        self.cap = QHBoxLayout()
        self.cap_widget.setLayout(self.cap)
        self.cap_widget.setFixedHeight(48)
        self.cap.setContentsMargins(12,0,12,0)

        # Кнопка с именем приложения - ссылка на репозиторий проекта
        self.app_name_button = QPushButton()
        self.app_name_button.setText(settings.get_app_name())
        self.app_name_button.setFont(fonts.get_qfont("JetBrains_Regular", 14))
        self.app_name_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {style.light_font_color};
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                margin-left: 30px;
            }}
        """)
        self.app_name_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.app_name_button.clicked.connect(self.app_name_clicked)

        settings_path = Path("resources/images/icons/settings_pycharm_icon.png")
        settings_hover_path = Path("resources/images/icons/settings_pycharm_icon_hover.png")

        # Кнопка для перехода во вкладку настоек
        self.settings_button = QPushButton()
        self.settings_button.setFixedSize(30, 31)
        self.settings_button.setStyleSheet(f"""
            QPushButton {{
                background-image: url({settings_path.as_posix()});
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-image: url({settings_hover_path.as_posix()});
            }}
        """)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(self.open_settings_tab)

        run_button_path = Path("resources/images/icons/run_button.png")
        run_button_hover_path = Path("resources/images/icons/run_button_hover.png")

        # Кнопка запуска процессов - одна на всё приложение
        self.run_button = QPushButton()
        self.run_button.setFixedSize(30,31)
        self.run_button.setStyleSheet(f"""
            QPushButton {{
                background-image: url({run_button_path.as_posix()});
            }}
            QPushButton:hover {{
                background-image: url({run_button_hover_path.as_posix()});
            }}
            QPushButton:pressed {{
                background-image: url({run_button_hover_path.as_posix()});
            }}
        """)
        self.run_button.clicked.connect(self.run)

        stop_button_path = Path("resources/images/icons/stop_button_hover.png")
        stop_button_hover_path = Path("resources/images/icons/stop_button_hover.png")

        # Кнопка остановки процесса парсинга и сборки - изначально скрыта.
        # Появится только при запуске процесса
        self.stop_parsing_button = QPushButton()
        self.stop_parsing_button.setFixedSize(30,31)
        self.stop_parsing_button.setStyleSheet(f"""
                    QPushButton {{
                        background-image: url({stop_button_path.as_posix()});
                    }}
                    QPushButton:hover {{
                        background-image: url({stop_button_hover_path.as_posix()});
                    }}
                    QPushButton:pressed {{
                        background-image: url({stop_button_path.as_posix()});
                    }}
                """
        )
        self.stop_parsing_button.clicked.connect(self.stop_generation_process)
        self.stop_parsing_button.setVisible(False)

        self.stop_button = QPushButton()
        self.stop_button.setFixedSize(30, 31)
        self.stop_button.setStyleSheet(f"""
                            QPushButton {{
                                background-image: url({stop_button_path.as_posix()});
                            }}
                            QPushButton:hover {{
                                background-image: url({stop_button_hover_path.as_posix()});
                            }}
                            QPushButton:pressed {{
                                background-image: url({stop_button_path.as_posix()});
                            }}
                        """
                                               )
        self.stop_button.clicked.connect(self.stop_generation_second_tab)
        self.stop_button.setVisible(False)

        # Вызов функции для получения индекса текущей вкладки
        self.what_tab_is_show_now()
        # И вызов её при открытии другой вкладки
        self.tab_widget.currentChanged.connect(self.what_tab_is_show_now)

        # Добавление виджетов в шапку
        self.cap.addWidget(self.app_name_button)
        self.cap.addStretch()
        self.cap.addWidget(self.run_button)
        self.cap.addWidget(self.stop_parsing_button)
        self.cap.addWidget(self.stop_button)
        self.cap.addWidget(self.settings_button)

        # Добавление в главный вертикальный layout шапки и виджета с вкладками
        self.main_v_layout.addWidget(self.cap_widget)
        self.main_v_layout.addWidget(self.tab_widget)

        # Виджет для фона основной вкладки приложения (кнопка, при нажатии которой можно сменить фон)
        self.widget_bg_main_tab = QPushButton()
        self.widget_bg_main_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.widget_bg_main_tab.setMinimumHeight(200)
        self.widget_bg_main_tab.setMaximumWidth(1900)

        # ПУть к папке с изображениями для фона главного окна (основной вкладки)
        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

        # подключение функции изменения фона основной вкладки
        self.widget_bg_main_tab.clicked.connect(self.on_bg_clicked)

        # Лейбл для отображения виджет с фоном (без текста)
        label = QLabel(self.widget_bg_main_tab)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Виджет для позиционирования кнопки с фоном основного окна
        bg_main_tab_layout = QHBoxLayout()
        bg_main_tab_layout.addWidget(self.widget_bg_main_tab)

        # Скролл виджет для всех виджетов и кнопок в основной вкладке
        self.main_tab_scroll_area = QScrollArea()
        self.main_tab_scroll_area.setWidgetResizable(True)
        self.main_tab_scroll_area.setStyleSheet(style.q_scroll_bar_style)

        horizontal_windget_for_position = QHBoxLayout()
        container_widget_main_tab = QWidget()
        horizontal_windget_for_position.addWidget(container_widget_main_tab)
        container_layout_main_tab = QVBoxLayout(container_widget_main_tab)
        container_widget_main_tab.setStyleSheet(
            f"background-color: {style.background_dark_color}; border-radius: 10px;")

        self.main_tab_scroll_area.setWidget(container_widget_main_tab)

        # Установка лейаута для главной вкладки и загрузка в неё виджета фона
        tab_main_layout = QVBoxLayout(tab_main_widget)
        tab_main_layout.addLayout(bg_main_tab_layout)
        tab_main_widget.setLayout(tab_main_layout)
        tab_main_layout.addWidget(self.main_tab_scroll_area)

        # Специальный лейаут для кнопок и остального на главной вкладке
        widgets_horizontal_main_tab_layout = QHBoxLayout()
        widgets_horizontal_main_tab_layout.addStretch()

        # кнопка открытия папки с пдф (главная вкладка
        self.open_folder_button = QPushButton("Открыть папку с PDF", tab_main_widget)
        self.open_folder_button.setMaximumWidth(400)
        self.open_folder_button.setFixedHeight(30)
        self.open_folder_button.setFont(fonts.get_qfont("JetBrains_Regular", 12))
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.setStyleSheet(style.button_blue_style)
        self.open_folder_button.clicked.connect(lambda: open_parsing_pdf_folder(self))

        # Виджет для фона радиокнопок и заголовка
        self.radio_buttons_background = QWidget(tab_main_widget)
        self.radio_buttons_background.setMinimumHeight(200)
        self.radio_buttons_background.setFixedWidth(350)
        self.radio_buttons_background.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
            )
        # Вертикальный лейаут для радиокнопок
        radio_buttons_vertical_layout = QVBoxLayout()
        self.radio_buttons_background.setLayout(radio_buttons_vertical_layout)

        # Заголовок для радиокнопок
        self.label_for_radio_buttons = QLabel()
        self.label_for_radio_buttons.setText("Выберите семестр:")
        self.label_for_radio_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_radio_buttons.setStyleSheet(
            f"color: {style.light_font_color}; margin: 10px; font-weight: bold;")
        self.label_for_radio_buttons.setFont(fonts.get_qfont("JetBrains_Regular", 14))

        radio_buttons_vertical_layout.addWidget(self.label_for_radio_buttons)

        widget_for_radio_buttons_and_choose_universal_excel = QWidget()
        widget_for_radio_buttons_and_choose_universal_excel.setMaximumWidth(750)

        horizontal_position_layout_for_center_poz = QHBoxLayout()
        horizontal_position_layout_for_center_poz.addWidget(widget_for_radio_buttons_and_choose_universal_excel)

        horizontal_layout_for_radio_buttons_and_button = QHBoxLayout()
        widget_for_radio_buttons_and_choose_universal_excel.setLayout(
            horizontal_layout_for_radio_buttons_and_button)
        horizontal_layout_for_radio_buttons_and_button.addWidget(self.radio_buttons_background)
        horizontal_layout_for_radio_buttons_and_button.addStretch()

        widgets_vertical_main_tab_layout = QVBoxLayout()
        widgets_horizontal_main_tab_layout.addLayout(widgets_vertical_main_tab_layout)
        widgets_horizontal_main_tab_layout.addStretch()
        widgets_vertical_main_tab_layout.addWidget(self.open_folder_button)

        # Радиокнопки
        # активирует работу с doc файлом комиссии по истории
        self.radio_button_1 = QRadioButton("Первый семестр - история", tab_main_widget)
        # активирует работу с файлом «Комиссии - История.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_1)
        self.radio_button_1.setFont(fonts.get_qfont("JetBrains_Medium", 12))
        self.radio_button_1.setStyleSheet(style.radio_button_style)

        # активирует работу с doc файлом комиссии по иностранному
        self.radio_button_2 = QRadioButton("Второй семестр - иностранный", tab_main_widget)
        # активирует работу с файлом «Комиссии - Иностранный.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_2)
        self.radio_button_2.setFont(fonts.get_qfont("JetBrains_Medium", 12))
        self.radio_button_2.setStyleSheet(style.radio_button_style)
        # активирует работу с doc файлом комиссии по специальности
        self.radio_button_3 = QRadioButton("Третий семестр - специальность", tab_main_widget)
        # активирует работу с файлом «Комиссии - Специальность.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_3)
        self.radio_button_3.setFont(fonts.get_qfont("JetBrains_Medium", 12))
        self.radio_button_3.setStyleSheet(style.radio_button_style)

        # Группируем (чтобы работало как "только один выбор")
        self.button_group = QButtonGroup(tab_main_widget)
        self.button_group.addButton(self.radio_button_1)
        self.button_group.addButton(self.radio_button_2)
        self.button_group.addButton(self.radio_button_3)

        radio_buttons_vertical_layout.setContentsMargins(10,30,10,20)
        radio_buttons_vertical_layout.addStretch()

        # прогресс бар для нулевой вкладки (с парсингом). Изначально скрыто
        self.progress_bar_parsing = QProgressBar()
        self.progress_bar_parsing.setFixedWidth(730)
        self.progress_bar_parsing.setFixedHeight(25)
        self.progress_bar_parsing.setRange(0, 100)
        self.progress_bar_parsing.setValue(0)
        self.progress_bar_parsing.setStyleSheet(style.progress_bar_style_blue)
        self.progress_bar_parsing.setVisible(False)

        # поле ввода для приказа о комиссиях
        self.input_commission = QLineEdit()
        self.input_commission.setMaximumWidth(730)
        self.input_commission.setPlaceholderText(
            "Введите текст приказа..."
        )
        self.input_commission.setStyleSheet(style.q_line_edit_style)
        self.input_commission.setFont(fonts.get_qfont("JetBrains_Medium", 10))

        horizontal_widget_for_input_commission = QHBoxLayout()
        horizontal_widget_for_input_commission.addWidget(self.input_commission)

        # Виджет для фона виджета и кнопки выбора файла универсальной таблицы
        self.widget_for_choose_files_commission = QWidget()
        self.widget_for_choose_files_commission.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
        )
        self.widget_for_choose_files_commission.setMinimumHeight(200)
        self.widget_for_choose_files_commission.setFixedWidth(370)

        horizontal_layout_for_radio_buttons_and_button.addWidget(
            self.widget_for_choose_files_commission)

        vertical_layout_for_choosing_files = QVBoxLayout()
        self.widget_for_choose_files_commission.setLayout(
            vertical_layout_for_choosing_files)

        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        self.btn_choose_universal_xl = QPushButton(
            "Выберите таблицу для парсинга")
        self.btn_choose_universal_xl.setFixedHeight(50)
        self.btn_choose_universal_xl.setMaximumWidth(350)
        self.btn_choose_universal_xl.setStyleSheet(style.button_blue_style)
        self.btn_choose_universal_xl.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_universal_xl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_universal_xl.clicked.connect(
            lambda: choose_universal_excel(self))

        vertical_layout_for_choosing_files.addWidget(self.btn_choose_universal_xl)

        # Лейбл для показа пути к выбранной универсальной таблицы
        self.universal_excel_label = QLabel()
        self.universal_excel_label.setFont(fonts.get_qfont("JetBrains_Light", 8))
        self.universal_excel_label.setMinimumHeight(120)
        self.universal_excel_label.setText("Путь к выбранной таблице")
        self.universal_excel_label.setStyleSheet(
            f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color};"
            f"padding: 10px;"
        )
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setWordWrap(True)
        vertical_layout_for_choosing_files.addWidget(self.universal_excel_label)

        horizontal_layout_for_widget_for_choose_commission_file = QHBoxLayout()

        # Виджет для фона для кнопки выбора файла таблицы с информацией о комиссии
        # и лейбла с её (таблицы) именем
        widget_for_choose_commission_file = QWidget()
        widget_for_choose_commission_file.setMaximumWidth(730)
        widget_for_choose_commission_file.setMinimumHeight(150)
        widget_for_choose_commission_file.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
        )

        vertical_layout_for_chose_doc_files = QVBoxLayout()
        widget_for_choose_commission_file.setLayout(
            vertical_layout_for_chose_doc_files)

        # кнопка для выбора doc файла с данными комиссии по истории
        self.btn_choose_history_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_history_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_history_commission.setFixedWidth(150)
        self.btn_choose_history_commission.setFixedHeight(50)
        self.btn_choose_history_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_history_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_history_commission.clicked.connect(
          lambda: choose_history_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по истории
        self.history_xl_choused_label = QLabel()
        self.history_xl_choused_label.setMinimumHeight(50)
        self.history_xl_choused_label.setWordWrap(True)
        self.history_xl_choused_label.setFont(fonts.get_qfont(
            "JetBrains_Light", 10))
        self.history_xl_choused_label.setStyleSheet(
            f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;"
        )
        self.history_xl_choused_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_xl_choused_label.setText(
            "Здесь будет имя выбранного файла...")

        # кнопка для выбора doc файла с данными комиссии по иностранному
        self.btn_choose_foreign_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_foreign_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_foreign_commission.setFixedWidth(150)
        self.btn_choose_foreign_commission.setFixedHeight(50)
        self.btn_choose_foreign_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_foreign_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_foreign_commission.clicked.connect(
          lambda: choose_foreign_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по иностранному
        self.foreign_xl_choosed_label = QLabel()
        self.foreign_xl_choosed_label.setFont(fonts.get_qfont(
            "JetBrains_Light", 10))
        self.foreign_xl_choosed_label.setMinimumHeight(50)
        self.foreign_xl_choosed_label.setWordWrap(True)
        self.foreign_xl_choosed_label.setStyleSheet(
            f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;"
        )
        self.foreign_xl_choosed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreign_xl_choosed_label.setText(
            "Здесь будет имя выбранного файла...")

        # кнопка для выбора doc файла с данными комиссии по специальности
        self.btn_choose_specialization_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_specialization_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_specialization_commission.setFixedWidth(150)
        self.btn_choose_specialization_commission.setFixedHeight(50)
        self.btn_choose_specialization_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_specialization_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по специализации
        self.specialization_xl_choosed_lb = QLabel()
        self.specialization_xl_choosed_lb.setMinimumHeight(50)
        self.specialization_xl_choosed_lb.setWordWrap(True)
        self.specialization_xl_choosed_lb.setFont(fonts.get_qfont(
            "JetBrains_Light", 10))
        self.specialization_xl_choosed_lb.setStyleSheet(
            f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;"
        )
        self.specialization_xl_choosed_lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.specialization_xl_choosed_lb.setText(
            "Здесь будет имя выбранного файла...")

        # Лейбл отображения времени последнего обновления файла
        # с кешем направлений аспирантов
        self.time_update_label = QLabel()
        self.time_update_label.setFixedWidth(220)
        self.time_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_update_label.setStyleSheet(
            f"color: {style.dark_font_color}; "
            f"background-color: {style.background_dark_color};"
        )
        self.time_update_label.setText("время последнего обновления")
        self.time_update_label.setFont(fonts.get_qfont("JetBrains_Light", 10))

        # Кнопка для обновления кеша с информацией о направлениях аспирантов
        self.button_to_update_date = QPushButton()
        self.button_to_update_date.setText("Обновить данные")
        self.button_to_update_date.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.button_to_update_date.setFixedHeight(50)
        self.button_to_update_date.setFixedWidth(200)
        self.button_to_update_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_update_date.setStyleSheet(style.button_blue_style)
        self.button_to_update_date.clicked.connect(lambda: update_data(self))

        # Заголовок с инфо о последнем обновлении
        self.label_info_last_update_cache = QLabel()
        self.label_info_last_update_cache.setText("Дата и время последнего обновления:")
        self.label_info_last_update_cache.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.label_info_last_update_cache.setStyleSheet(f"color: {style.light_font_color};")

        horizontal_layout_for_widget_for_choose_commission_file.addWidget(
            widget_for_choose_commission_file)

        # Лейбл-заголовок для отображения вида комиссии, файл с
        # которой можно будет выбрать
        self.label_commission_title = QLabel()
        self.label_commission_title.setFixedHeight(50)
        self.label_commission_title.setMaximumWidth(400)
        self.label_commission_title.setStyleSheet(
            f"color: {style.light_font_color}; padding: 10px;"
            f"background-color: {style.background_color}; border-radius: 10px;")
        self.label_commission_title.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.label_commission_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_commission_title.setText("Таблица с комиссией по истории")

        h_layout_title_choose_commission_file_and_button_choose = QHBoxLayout()
        h_layout_title_choose_commission_file_and_button_choose.addWidget(self.label_commission_title)
        h_layout_title_choose_commission_file_and_button_choose.addStretch()

        vertical_layout_for_chose_doc_files.addLayout(
            h_layout_title_choose_commission_file_and_button_choose)

        h_layout_title_choose_commission_file_and_button_choose.addWidget(
            self.btn_choose_history_commission)

        vertical_layout_for_chose_doc_files.addWidget(self.history_xl_choused_label)

        h_layout_title_choose_commission_file_and_button_choose.addWidget(
            self.btn_choose_foreign_commission)

        vertical_layout_for_chose_doc_files.addWidget(self.foreign_xl_choosed_label)

        h_layout_title_choose_commission_file_and_button_choose.addWidget(
            self.btn_choose_specialization_commission)

        vertical_layout_for_chose_doc_files.addWidget(self.specialization_xl_choosed_lb)

        # Скрываю все кнопки и лейблы для выбора файлов комиссии,
        # кроме дефолтного - комиссии по истории
        self.btn_choose_history_commission.setVisible(True)
        self.history_xl_choused_label.setVisible(True)
        self.btn_choose_foreign_commission.setVisible(False)
        self.foreign_xl_choosed_label.setVisible(False)
        self.btn_choose_specialization_commission.setVisible(False)
        self.specialization_xl_choosed_lb.setVisible(False)

        # Подключение к радиокнопкам сигала для показа кнопки и лейбла выбора файла
        # комиссии в соответствии с выбранным семестром
        self.radio_button_1.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "history"))
        self.radio_button_2.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "foreign"))
        self.radio_button_3.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "specialization"))

        # Виджет для кеша
        widget_for_cache = QWidget()
        widget_for_cache.setFixedWidth(730)
        widget_for_cache.setFixedHeight(70)
        widget_for_cache.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
        )
        horizontal_widget_layout_for_cache = QHBoxLayout()
        widget_for_cache.setLayout(horizontal_widget_layout_for_cache)

        # Добавление виджета, лейбла и кнопки для кеша
        horizontal_widget_layout_for_cache.addWidget(self.label_info_last_update_cache)
        horizontal_widget_layout_for_cache.addWidget(self.time_update_label)
        horizontal_widget_layout_for_cache.addStretch()
        horizontal_widget_layout_for_cache.addWidget(self.button_to_update_date)

        # кнопка изменения пути сохранения
        self.button_change_save_path = QPushButton()
        self.button_change_save_path.setMaximumWidth(100)
        self.button_change_save_path.setFixedHeight(50)
        self.button_change_save_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_change_save_path.setStyleSheet(style.button_blue_style)
        self.button_change_save_path.setText("Изменить")
        self.button_change_save_path.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.button_change_save_path.clicked.connect(
            lambda: choose_parsing_save_folder(self))

        widget_for_change_save_path = QWidget()
        widget_for_change_save_path.setFixedWidth(730)
        widget_for_change_save_path.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
            f"padding: 10px;")
        horizontal_layout_for_change_save_path = QHBoxLayout()
        widget_for_change_save_path.setLayout(horizontal_layout_for_change_save_path)

        # Лейбл с заголовком об изменении пути сохранения ПДФ
        change_path_label = QLabel()
        change_path_label.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        change_path_label.setText("Путь сохранения:")
        change_path_label.setStyleSheet(f"color: {style.light_font_color};")

        vertical_layout_for_pos_title = QVBoxLayout()
        vertical_layout_for_pos_title.addWidget(change_path_label)
        vertical_layout_for_pos_title.addStretch()

        self.save_path_label = QLabel()
        self.save_path_label.setFixedWidth(550)
        self.save_path_label.setFont(fonts.get_qfont("JetBrains_Medium", 10))
        self.save_path_label.setStyleSheet(f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;"
            f"padding: 10px;")
        self.save_path_label.setWordWrap(True)
        self.save_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_path_label.setText(self.save_folder_path)

        vertical_layout_for_show_save_path_and_button_change = QVBoxLayout()
        vertical_layout_for_show_save_path_and_button_change.addWidget(
            self.save_path_label)
        vertical_layout_for_show_save_path_and_button_change.addStretch()
        vertical_layout_for_show_save_path_and_button_change.addWidget(
            self.button_change_save_path, alignment=Qt.AlignmentFlag.AlignRight)
        vertical_layout_for_show_save_path_and_button_change.setSpacing(15)

        horizontal_layout_for_change_save_path.addLayout(
            vertical_layout_for_pos_title)
        horizontal_layout_for_change_save_path.addStretch()
        horizontal_layout_for_change_save_path.addLayout(
            vertical_layout_for_show_save_path_and_button_change)

        # Добавление в основной layout
        container_layout_main_tab.addWidget(self.widget_bg_main_tab)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(
            self.progress_bar_parsing, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(horizontal_widget_for_input_commission)

        container_layout_main_tab.addLayout(horizontal_position_layout_for_center_poz)

        container_layout_main_tab.addLayout(
            horizontal_layout_for_widget_for_choose_commission_file)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(
            widget_for_cache, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(
            widget_for_change_save_path, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(widgets_horizontal_main_tab_layout)

        # Первая вкладка - сбор пдф по готовой таблице ==================================
        # ===============================================================================

        tab_second_widget.setStyleSheet(
            f"background-color: {style.background_dark_color}; border-radius: 10px;")

        main_layout_for_second_tab = QVBoxLayout()
        tab_second_widget.setLayout(main_layout_for_second_tab)

        # Виджет для фона заголовка
        background_widget_for_second_tab = QWidget()
        background_widget_for_second_tab.setStyleSheet(
            f"background-color: {style.background_dark_color}; border-radius: 10px;")

        main_layout_for_second_tab.addWidget(
            background_widget_for_second_tab)

        # Заголовок для вкладки
        second_tab_title = QLabel()
        second_tab_title.setText("Сборка ПДФ по готовой таблице")
        second_tab_title.setStyleSheet(f"color: {style.light_font_color}; font: bold;")
        second_tab_title.setFont(fonts.get_qfont("JetBrains_Regular", 12))

        title_second_tab_widget = QWidget()

        # Лейаут для позиционирования заголовка по левому краю
        horizontal_layout_for_second_tab_title = QHBoxLayout()
        title_second_tab_widget.setLayout(horizontal_layout_for_second_tab_title)
        horizontal_layout_for_second_tab_title.addWidget(second_tab_title)
        horizontal_layout_for_second_tab_title.addStretch()

        # Основной вертикальный контейнер для второй (первой) вкладки
        background_widget_for_second_tab_container = QVBoxLayout()
        background_widget_for_second_tab.setLayout(
            background_widget_for_second_tab_container)

        # Виджет для кнопки выбора пути сохранения ПДФ, лейбла с текущим путём
        # сохранения и заголовка
        widget_for_pos_button_path_and_title_choose_save_path = QWidget()
        widget_for_pos_button_path_and_title_choose_save_path.setFixedWidth(730)
        widget_for_pos_button_path_and_title_choose_save_path.setMinimumHeight(50)
        widget_for_pos_button_path_and_title_choose_save_path.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
            f"padding: 10px;")

        # Заголовок изменения пути сохранения
        title_change_save_path = QLabel()
        title_change_save_path.setFont(fonts.get_qfont("JetBrains_Regular", 11))
        title_change_save_path.setStyleSheet(f"color: {style.light_font_color};"
            f"background-color: {style.background_color}; border-radius: 10px;"
            f"margin-top: 5px; font: bold;")
        title_change_save_path.setText("Текущий путь сохранения")

        # Отдельный путь для сохранения ПДФ (без парсинга)
        self.save_folder_second_tab_path: str = str(
            Path.home() / "Desktop" / "results_folder")

        # Лейбл для отображения текущего пути сохранения ПДФ
        self.current_save_path_label = QLabel()
        self.current_save_path_label.setMinimumHeight(50)
        self.current_save_path_label.setFixedWidth(450)
        self.current_save_path_label.setWordWrap(True)
        self.current_save_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_save_path_label.setFont(fonts.get_qfont("JetBrains_Medium", 10))
        self.current_save_path_label.setStyleSheet(f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;")
        self.current_save_path_label.setText(self.save_folder_second_tab_path)

        # Кнопка выбора пути сохранения ПДФ
        self.button_shouse_save_path_for_second_tab = QPushButton()
        self.button_shouse_save_path_for_second_tab.setFixedWidth(150)
        self.button_shouse_save_path_for_second_tab.setFixedHeight(50)
        self.button_shouse_save_path_for_second_tab.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.button_shouse_save_path_for_second_tab.setStyleSheet(
            style.button_blue_style)
        self.button_shouse_save_path_for_second_tab.setText("Изменить")
        self.button_shouse_save_path_for_second_tab.setFont(fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_shouse_save_path_for_second_tab.clicked.connect(
            lambda: choose_save_folder_second_tab(self))

        # прогресс бар для первой вкладки (без парсинга). Изначально скрыто
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(730)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet(style.progress_bar_style_blue)
        self.progress_bar.setVisible(False)

        # Лейаут для виджетов: кнопки выбора пути сохранения, лейбла с путём и заголовка
        layout_for_save_path_widgets = QHBoxLayout()
        widget_for_pos_button_path_and_title_choose_save_path.setLayout(
            layout_for_save_path_widgets)

        vertical_layout_for_pos_title_second_tab =QVBoxLayout()
        vertical_layout_for_pos_title_second_tab.addWidget(title_change_save_path)
        vertical_layout_for_pos_title_second_tab.addStretch()

        vertical_layout_save_path_widgets = QVBoxLayout()
        vertical_layout_save_path_widgets.addWidget(self.current_save_path_label)
        vertical_layout_save_path_widgets.addWidget(
            self.button_shouse_save_path_for_second_tab,
            alignment=Qt.AlignmentFlag.AlignRight)
        vertical_layout_save_path_widgets.addStretch()

        layout_for_save_path_widgets.addLayout(vertical_layout_for_pos_title_second_tab)
        layout_for_save_path_widgets.addLayout(vertical_layout_save_path_widgets)
        vertical_layout_save_path_widgets.setSpacing(15)

        background_widget_for_second_tab_container.addWidget(
            title_second_tab_widget)

        widget_for_choose_table = QWidget()
        widget_for_choose_table.setFixedWidth(730)
        widget_for_choose_table.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
            f"padding: 10px;")

        title_choose_table_label = QLabel()
        title_choose_table_label.setFixedHeight(50)
        title_choose_table_label.setMaximumWidth(250)
        title_choose_table_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_choose_table_label.setFont(fonts.get_qfont("JetBrains_Regular", 11))
        title_choose_table_label.setStyleSheet(f"color: {style.light_font_color};"
            f"background-color: {style.background_color}; border-radius: 10px;"
            f"font: bold;")
        title_choose_table_label.setText("Таблица с данными")

        self.label_current_tabel = QLabel()
        self.label_current_tabel.setWordWrap(True)
        self.label_current_tabel.setMinimumHeight(50)
        self.label_current_tabel.setFixedWidth(450)
        self.label_current_tabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_current_tabel.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.label_current_tabel.setStyleSheet(f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color}; border-radius: 10px;"
            f"padding: 10px;")
        if self.excel_file_path:
            self.label_current_tabel.setText(self.excel_file_path)
        else:
            self.label_current_tabel.setText("Путь к выбранной таблице")

        # Кнопка выбора файла с таблицей для сборки
        self.button_shouse_table = QPushButton()
        self.button_shouse_table.setFixedWidth(150)
        self.button_shouse_table.setFixedHeight(50)
        self.button_shouse_table.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.button_shouse_table.setStyleSheet(
            style.button_blue_style)
        self.button_shouse_table.setText("Выбрать файл")
        self.button_shouse_table.setFont(fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_shouse_table.clicked.connect(
            lambda: choose_file(self))

        # Кнопка открытия папки сохранения
        self.button_open_folder_with_pdf = QPushButton()
        self.button_open_folder_with_pdf.setFixedWidth(250)
        self.button_open_folder_with_pdf.setFixedHeight(50)
        self.button_open_folder_with_pdf.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.button_open_folder_with_pdf.setStyleSheet(
            style.button_blue_style)
        self.button_open_folder_with_pdf.setText("Открыть папку с PDF")
        self.button_open_folder_with_pdf.setFont(fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_open_folder_with_pdf.clicked.connect(
            lambda: open_pdf_folder(self))

        layout_for_choose_table = QVBoxLayout()
        widget_for_choose_table.setLayout(layout_for_choose_table)
        layout_for_choose_table.setSpacing(15)

        horizontal_pos_layout = QHBoxLayout()

        layout_for_choose_table.addLayout(horizontal_pos_layout)

        horizontal_pos_layout.addWidget(
            title_choose_table_label)

        horizontal_pos_layout.addStretch()

        horizontal_pos_layout.addWidget(
            self.label_current_tabel)

        layout_for_choose_table.addWidget(
            self.button_shouse_table, alignment=Qt.AlignmentFlag.AlignRight)

        background_widget_for_second_tab_container.addWidget(
            self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addWidget(
            widget_for_choose_table, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addWidget(
            widget_for_pos_button_path_and_title_choose_save_path,
            alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addStretch()
        background_widget_for_second_tab_container.addWidget(
            self.button_open_folder_with_pdf, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.setSpacing(15)

        # Вторая вкладка - настройки ====================================================
        # ===============================================================================

        tab_settings_layout = QVBoxLayout()
        tab_settings_widget.setLayout(tab_settings_layout)
        tab_settings_widget.setStyleSheet(
            f"background-color: {style.background_dark_color}; "
            f"border-radius: 10px;")

        self.settings_cap = QWidget()
        self.settings_cap.setStyleSheet(
            f"background-color: {style.background_dark_color};")
        self.settings_cap.setFixedHeight(48)

        self.settings_label = QLabel()
        self.settings_label.setText("Настройки")
        self.settings_label.setFont(fonts.get_qfont("JetBrains_Regular", 14))
        self.settings_label.setStyleSheet(
            f"color: {style.light_font_color}; font: bold;")

        layout_for_settings_cap = QHBoxLayout()
        layout_for_settings_cap.addWidget(self.settings_label)

        self.settings_cap.setLayout(layout_for_settings_cap)

        tab_settings_layout.addWidget(self.settings_cap, alignment=Qt.AlignmentFlag.AlignTop)

        self.settings_main_widget = QWidget()
        self.settings_main_widget.setFixedWidth(740)
        self.settings_main_widget.setStyleSheet(
            f"background: {style.background_dark_color}; border-radius: 10px;")

        layout_for_settings = QVBoxLayout()
        self.settings_main_widget.setLayout(layout_for_settings)

        loading_window_param_widget = QWidget()
        loading_window_param_widget.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;")
        loading_window_param_widget.setMaximumWidth(720)

        loading_param_h_layout = QHBoxLayout()
        loading_window_param_widget.setLayout(loading_param_h_layout)

        self.param_show_loading_window = QLabel()
        self.param_show_loading_window.setText("Загрузочное окно")
        self.param_show_loading_window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param_show_loading_window.setFont(fonts.get_qfont("JetBrains_Medium", 10))

        self.button_show_loading_window = QPushButton()
        self.button_show_loading_window.setText("Показывать")
        self.button_show_loading_window.setFixedHeight(35)
        self.button_show_loading_window.setFixedWidth(200)
        self.button_show_loading_window.setFont(fonts.get_qfont("JetBrains_Light", 8))
        self.button_show_loading_window.clicked.connect(self.set_true_show_loading_window)
        if settings.get_flag_show_loading_window():
            self.button_show_loading_window.setStyleSheet(style.button_blue_style)
        else:
            self.button_show_loading_window.setStyleSheet(style.button_hide_style)

        self.button_hide_loading_window = QPushButton()
        self.button_hide_loading_window.setText("Скрывать")
        self.button_hide_loading_window.setFixedHeight(35)
        self.button_hide_loading_window.setFixedWidth(200)
        self.button_hide_loading_window.setFont(fonts.get_qfont("JetBrains_Light", 8))
        self.button_hide_loading_window.clicked.connect(self.set_false_show_loading_window)
        if not settings.get_flag_show_loading_window():
            self.button_hide_loading_window.setStyleSheet(style.button_blue_style)
        else:
            self.button_hide_loading_window.setStyleSheet(style.button_hide_style)

        loading_param_h_layout.addWidget( self.param_show_loading_window)
        loading_param_h_layout.addWidget( self.button_show_loading_window)
        loading_param_h_layout.addWidget( self.button_hide_loading_window)

        loading_window_timer_duration_param_widget = QWidget()
        loading_window_timer_duration_param_widget.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;")
        loading_window_timer_duration_param_widget.setMaximumWidth(720)

        loading_timer_duration_param_h_layout = QHBoxLayout()
        loading_window_timer_duration_param_widget.setLayout(loading_timer_duration_param_h_layout)

        # Лейбл для заголовка времени показа загрузочного экрана
        self.param_timer_duration_loading_window = QLabel()
        self.param_timer_duration_loading_window.setText("Время показа загрузочного окна")
        self.param_timer_duration_loading_window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param_timer_duration_loading_window.setFont(fonts.get_qfont("JetBrains_Medium", 10))

        # Слайдер, который меняет время показа загрузочного окна
        self.slider_loading_window_timer_duration = QSlider(Qt.Orientation.Horizontal)
        self.slider_loading_window_timer_duration.setRange(1000, 15000)
        self.slider_loading_window_timer_duration.setValue(settings.get_loading_window_timer_duration())
        self.slider_loading_window_timer_duration.setFixedWidth(350)
        self.slider_loading_window_timer_duration.setStyleSheet(style.q_slider_style)
        self.slider_loading_window_timer_duration.valueChanged.connect(self.on_slider_changed)

        # Индикатор текущей длительности показа загрузочного окна
        self.indicate_loading_window_timer_duration = QLabel()
        self.indicate_loading_window_timer_duration.setFixedWidth(60)
        self.indicate_loading_window_timer_duration.setFont(fonts.get_qfont("JetBrains_Light", 10))
        self.indicate_loading_window_timer_duration.setStyleSheet(f"color: {style.dark_font_color};")
        self.indicate_loading_window_timer_duration.setText(
            f"{str(settings.get_loading_window_timer_duration())} мс")
        self.indicate_loading_window_timer_duration.setAlignment(Qt.AlignmentFlag.AlignRight)

        loading_timer_duration_param_h_layout.addWidget(self.param_timer_duration_loading_window)
        loading_timer_duration_param_h_layout.addStretch()
        loading_timer_duration_param_h_layout.addWidget(self.slider_loading_window_timer_duration)
        loading_timer_duration_param_h_layout.addStretch()
        loading_timer_duration_param_h_layout.addWidget(self.indicate_loading_window_timer_duration)

        layout_for_settings.addWidget(loading_window_param_widget)
        layout_for_settings.addWidget(loading_window_timer_duration_param_widget)

        tab_settings_layout.addWidget(self.settings_main_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        tab_settings_layout.addStretch()

    def on_slider_changed(self, value):
        """
        Функция для установления нового времени для таймера показа главного окна.
        Принимает значение от слайдера (от 1 до 15 секунд (от 1000 до 15000 мс)).

        :return: None
        """

        self.indicate_loading_window_timer_duration.setText(f"{str(value)} мс")
        settings.set_loading_window_timer_duration(value)

    def set_true_show_loading_window(self) -> None:
        """
        Функция для разрешения показа загрузочного окна (передает True флагу
        разрешения показа - в настойках). Установка стиля "скрытой" кнопки
        для кнопки "Скрывать" и установка обычного стиля для кнопки "Показывать".

        :return: None
        """

        settings.set_flag_show_loading_window(True)
        self.button_show_loading_window.setStyleSheet(style.button_blue_style)
        self.button_hide_loading_window.setStyleSheet(style.button_hide_style)

    def set_false_show_loading_window(self) -> None:
        """
        Функция для запрета показа загрузочного окна (передает False флагу
        разрешения показа - в настойках). Установка стиля "скрытой" кнопки
        для кнопки "Показывать" и установка обычного стиля для кнопки "Скрывать".

        :return: None
        """

        settings.set_flag_show_loading_window(False)
        self.button_show_loading_window.setStyleSheet(style.button_hide_style)
        self.button_hide_loading_window.setStyleSheet(style.button_blue_style)

    def on_bg_clicked(self) -> None:
        """
        Функция для установления случайного изображения на фон
        виджета для главной вкладки

        :return: None
        """

        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

    def stop_generation_second_tab(self) -> None:
        """
        Останавливает процесс генерации пдф из второй вкладки главного окна

        :return: None
        """

        simple_log("Остановка процесса по запросу пользователя")
        self.stop_building_pdf= True
        self.run_button.setVisible(False)
        self.stop_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

        QMessageBox.information(
            self,
            "Остановка",
            "Процесс остановки запущен...\n\n"
            "Программа завершит текущую операцию и остановится."
        )

    def stop_generation_process(self) -> None:
        """
        Останавливает процесс генерации и парсинга из основной вкладки главного окна

        :return: None
        """

        simple_log("Остановка процесса по запросу пользователя")
        self.stop_generation = True
        self.run_button.setVisible(False)
        self.stop_parsing_button.setEnabled(False)

        QMessageBox.information(
            self,
            "Остановка",
            "Процесс остановки запущен...\n\n"
            "Программа завершит текущую операцию и остановится."
        )

    def run(self) -> None:
        """
        Сигнал для кнопки запуска процессов для run_button

        :return:None
        """
        if self.choose_tab == 0:
            parsing(self)
        elif self.choose_tab == 1:
            get_pdf(self)
        else:
            return

    def on_semester_changed(self, checked: bool, semester: str) -> None:
        """
        Показывает нужные кнопки в зависимости от выбранного семестра
        (выбранной радиокнопки)

        :return: None
        """

        if not checked:
            return

        self.btn_choose_history_commission.setVisible(False)
        self.history_xl_choused_label.setVisible(False)
        self.btn_choose_foreign_commission.setVisible(False)
        self.foreign_xl_choosed_label.setVisible(False)
        self.btn_choose_specialization_commission.setVisible(False)
        self.specialization_xl_choosed_lb.setVisible(False)

        if semester == "history":
            self.btn_choose_history_commission.setVisible(True)
            self.history_xl_choused_label.setVisible(True)
            self.label_commission_title.setText("Таблица с комиссией по истории")
        elif semester == "foreign":
            self.btn_choose_foreign_commission.setVisible(True)
            self.foreign_xl_choosed_label.setVisible(True)
            self.label_commission_title.setText("Таблица с комиссией по иностранному")
        elif semester == "specialization":
            self.btn_choose_specialization_commission.setVisible(True)
            self.specialization_xl_choosed_lb.setVisible(True)
            self.label_commission_title.setText("Таблица с комиссией по специальности")

    def app_name_clicked(self):
        """
        Функция для перехода по ссылке на Гит с репозиторием проекта. Просто попробовать.

        :return: None
        """

        webbrowser.open("https://lab.vr-pro.ru:8514/SAPR/asp-automation/src/branch/"
                        "development")

    def resizeEvent(self, event):
        """
        Вызывается при изменении размера окна. Используется для адаптации размера фона.

        :param event: QResizeEvent — содержит новую информацию о размере

        :return: None
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
        Функция для смены фона виджета с фотографией в главной вкладке.
        Выбирает случайный путь к изображению и передаёт его стилям qss, которые
        устанавливают его на фон. Также по этому случайному изображению с помощью
        функции get_main_color_image() вычисляется главный (средний по всему
        изображению) цвет, который после также используется в стилях qss для
        QTabWidget - вкладок главного окна и небольшого градиента в шапке
        возле имени приложения.

        Также функция включает проверку на повторение фона (актуально, потому что,
        нажав на фон главного окна, снова его поменять - на другое случайное
        изображение. Для этого есть проверка и в атрибут класса постоянно сохраняется
         путь к последнему фоновому изображению и сличается с новым случайным путём -
         чтобы не было повторов.).

        :param folder_path: Принимает путь к папке, в которой можно брать случайное изображение

        :return: None
        """

        old_bg_path = self.bg_path_check

        def get_random_path() -> str:
            """
            Вложенная функция для получения случайного пути к изображению из папки
            (путь к папке берётся из аргумента основной функции)

            :return: Str - путь к случайному изображению.
            """

            img_path_new = get_random_image_from_folder(folder_path)
            path_bg_widget_new = Path(f'{img_path_new}')

            return path_bg_widget_new.as_posix()

        new_image_path = get_random_path()

        def use_random_photo(photo_path: str) -> None:
            """
            Вложенная функция для использования изображения по случайному пути -
            для стилей qss и обновления пути в атрибуте класса - сохранение последнего
             выбранного пути к случайному изображению.

            :param photo_path: Принимает путь к случайному изображению.

            :return: None
            """

            self.widget_bg_main_tab.setStyleSheet(
                f"background-image: url({photo_path});"
                f" background-position: center;"
                f" background-repeat: no-repeat;"
                f"border-radius: 10px;"
            )

            main_color_img = get_main_color_image(photo_path)

            main_color_str = f"{main_color_img[0]}, {main_color_img[1]}, {main_color_img[2]}"

            self.cap_widget.setStyleSheet(
                f"""
                    background: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 0,    
                    stop: 0 rgba({main_color_str}, 0.02),
                    stop: 0.025 rgba({main_color_str}, 0.1),
                    stop: 0.05 rgba({main_color_str}, 0.18),
                    stop: 0.15 rgba({main_color_str}, 0.13),
                    stop: 0.2 rgba({main_color_str}, 0.02),
                    stop: 0.25 rgba({main_color_str}, 0.01),
                    stop: 0.3 rgba(1, 1, 1, 0),
                    stop: 1 rgba(1, 1, 1, 0)
                    );
                """
            )

            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    background-color: #2B2B2B;
                    border: none;
                    top: -1px;
                }}
                QTabBar {{
                    background-color: {style.background_color};
                }}
                QTabBar::tab {{
                    background: transparent;
                    color: {style.dark_font_color};
                    padding: 10px 20px;
                    margin-right: 0px;
                    border: none;
                    border-bottom: 2px solid transparent;
                }}
                QTabBar::tab:selected {{
                    background: transparent;
                    color: {style.light_font_color};
                    border-bottom: 2px solid rgb({main_color_str});
                    font-weight: bold;
                }}            
                QTabBar::tab:hover:!selected {{
                    color: {style.light_font_color};
                    border-bottom: 2px solid #4D4E51;
                }}
            """)

            self.bg_path_check = f"{photo_path}"

            simple_log(f"Для фона главного окна выбрано изображение: {photo_path}")

        if self.bg_path_check == "":
            use_random_photo(new_image_path)
        elif old_bg_path != new_image_path:
            use_random_photo(new_image_path)
        else:
            image_path = get_random_path()
            while image_path == old_bg_path:
                image_path = get_random_path()
            else:
                use_random_photo(image_path)

    def what_tab_is_show_now(self) -> int:
        """
        Функция для получения индекса текущей вкладки.

        :return: int - индекс открытой вкладки
        """

        tabs_name = ["Главная", "ЛР по формированию PDF", "Настройки"]

        current_index = self.tab_widget.currentIndex()

        tab_name = ""

        if current_index == 0:
            tab_name = tabs_name[0]
            self.choose_tab = 0
            self.run_button.setVisible(True)

        elif current_index == 1:
            tab_name = tabs_name[1]
            self.choose_tab = 1
            self.run_button.setVisible(True)

        elif current_index == 2:
            tab_name = tabs_name[2]
            self.choose_tab = 2
            self.run_button.setVisible(False)

        else:
            tab_name = "неизвестно"
            self.choose_tab = -1

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
