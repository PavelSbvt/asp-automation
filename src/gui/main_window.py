from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton,
    QProgressBar, QRadioButton, QButtonGroup, QLineEdit,
    QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout, QScrollArea, QSlider)

from core.settings_manager import Settings
from utils.output_rich import Rich
from utils.create_shortcut import check_build
from gui.utils.choose_files import (
    choose_universal_excel, choose_save_folder_second_tab,
    choose_parsing_save_folder, open_parsing_pdf_folder,
    choose_history_excel, choose_foreign_excel, choose_specialization_excel,
    open_pdf_folder)
from gui.utils.update_gui import set_styles
from gui.utils.main_window_logic import (run, app_name_clicked, open_settings_tab,
    stop_generation_process, stop_generation_second_tab, what_tab_is_show_now,
    on_bg_clicked, on_semester_changed, set_true_show_loading_window,
    set_false_show_loading_window, on_slider_changed, on_button_choose_theme,
    get_bg_for_main_tab_widget)
from core.generate_pdf import choose_file
from gui.utils.fonts import Fonts
from gui.utils.styles import Style
from parser.sait_parsing import update_data


class MainWindow(QMainWindow):
    """
    Класс для нового главного окна
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")

        self.setMinimumSize(900, 650)

        self.setWindowTitle(Settings.get_app_name())

        # Текущая ширина окна. Установлено стандартное значение
        self.width_now: int = 0
        # Текущая высота окна. Установлено стандартное значение
        self.height_now: int = 0

        # Текущая открытая вкладка. Для обработки ошибок установлено значение -1
        self.choose_tab: int = -1

        self.stop_generation: bool = False # булевый флаг остановки сборки пдф и парсинга

        self.stop_building_pdf: bool = False  # булевый флаг остановки сборки пдф

        # устанавливаю дефолтные пути к файлам пустыми
        self.excel_file_path: Optional[str] = None  # путь к файлу - шаблон для ЛР
        self.universal_file_path: Optional[str] = None  # путь к универсальной таблице
        self.students_data: Optional[List[Dict[str, Any]]] = None  # данные студентов
        self.commission_members: Optional[List[Dict[str, Dict]]] = None  # члены комиссии

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

        # Главный цвет случайного изображения
        self.main_color_str: str = ""

        # Главный виджет
        self.main_back_widget = QWidget(self)
        self.setCentralWidget(self.main_back_widget)

        # Главный вертикальный layout
        self.main_v_layout = QVBoxLayout()
        self.main_back_widget.setLayout(self.main_v_layout)

        # Работа с вкладками
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(Fonts.get_qfont("JetBrains_Regular", 10))

        # Вкладки
        tab_main_widget = QWidget()
        self.tab_second_widget = QWidget()
        self.tab_settings_widget = QWidget()

        # Загрузка вкладок
        self.tab_widget.addTab(tab_main_widget, "Главная")
        self.tab_widget.addTab(self.tab_second_widget, "ЛР по формированию PDF")
        self.tab_widget.addTab(self.tab_settings_widget, "Настройки")

        # Вкладка с настройками скрыта, открывается только с кнопки
        self.tab_widget.setTabVisible(2, False)

        # Шапка главного окна
        self.cap_widget = QWidget(self)
        self.cap = QHBoxLayout()
        self.cap_widget.setLayout(self.cap)
        self.cap_widget.setFixedHeight(48)
        # self.cap.setContentsMargins(12,0,12,0)

        # Кнопка с именем приложения - ссылка на репозиторий проекта
        self.app_name_button = QPushButton()
        self.app_name_button.setText(Settings.get_app_name())
        self.app_name_button.setFont(Fonts.get_qfont("JetBrains_Regular", 14))
        self.app_name_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.app_name_button.clicked.connect(lambda: app_name_clicked(self))

        self.settings_path = Path("resources/images/icons/settings_pycharm_icon.png")

        # Кнопка для перехода во вкладку настоек
        self.settings_button = QPushButton()
        self.settings_button.setFixedSize(30, 31)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(lambda: open_settings_tab(self))

        self.run_button_path = Path("resources/images/icons/run_button.png")

        # Кнопка запуска процессов - одна на всё приложение
        self.run_button = QPushButton()
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setFixedSize(30,31)
        self.run_button.clicked.connect(lambda: run(self))

        self.stop_button_path = Path("resources/images/icons/stop_button.png")

        # Кнопка остановки процесса парсинга и сборки - изначально скрыта.
        # Появится только при запуске процесса
        self.stop_parsing_button = QPushButton()
        self.stop_parsing_button.setFixedSize(30,31)
        self.stop_parsing_button.clicked.connect(lambda: stop_generation_process(self))
        self.stop_parsing_button.setVisible(False)

        self.stop_button = QPushButton()
        self.stop_button.setFixedSize(30, 31)
        self.stop_button.clicked.connect(lambda: stop_generation_second_tab(self))
        self.stop_button.setVisible(False)

        # Вызов функции для получения индекса текущей вкладки
        what_tab_is_show_now(self)
        # И вызов её при открытии другой вкладки
        self.tab_widget.currentChanged.connect(lambda: what_tab_is_show_now(self))

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

        # подключение функции изменения фона основной вкладки
        self.widget_bg_main_tab.clicked.connect(lambda: on_bg_clicked(self))

        # Лейбл для отображения виджет с фоном (без текста)
        label = QLabel(self.widget_bg_main_tab)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Виджет для позиционирования кнопки с фоном основного окна
        bg_main_tab_layout = QHBoxLayout()
        bg_main_tab_layout.addWidget(self.widget_bg_main_tab)

        # Скролл виджет для всех виджетов и кнопок в основной вкладке
        self.main_tab_scroll_area = QScrollArea()
        self.main_tab_scroll_area.setWidgetResizable(True)

        horizontal_windget_for_position = QHBoxLayout()
        self.container_widget_main_tab = QWidget()
        horizontal_windget_for_position.addWidget(self.container_widget_main_tab)
        container_layout_main_tab = QVBoxLayout(self.container_widget_main_tab)

        self.main_tab_scroll_area.setWidget(self.container_widget_main_tab)

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
        self.open_folder_button.setFont(Fonts.get_qfont("JetBrains_Regular", 12))
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.clicked.connect(lambda: open_parsing_pdf_folder(self))

        # Виджет для фона радиокнопок и заголовка
        self.radio_buttons_background = QWidget(tab_main_widget)
        self.radio_buttons_background.setMinimumHeight(200)
        self.radio_buttons_background.setFixedWidth(350)
        # Вертикальный лейаут для радиокнопок
        radio_buttons_vertical_layout = QVBoxLayout()
        self.radio_buttons_background.setLayout(radio_buttons_vertical_layout)

        # Заголовок для радиокнопок
        self.label_for_radio_buttons = QLabel()
        self.label_for_radio_buttons.setText("Выберите семестр:")
        self.label_for_radio_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_radio_buttons.setFont(Fonts.get_qfont("JetBrains_Regular", 14))

        radio_buttons_vertical_layout.addWidget(self.label_for_radio_buttons)

        widget_for_radio_buttons_and_choose_universal_excel = QWidget()
        widget_for_radio_buttons_and_choose_universal_excel.setMaximumWidth(750)

        horizontal_position_layout_for_center_poz = QHBoxLayout()
        horizontal_position_layout_for_center_poz.addWidget(
            widget_for_radio_buttons_and_choose_universal_excel)

        horizontal_layout_for_radio_buttons_and_button = QHBoxLayout()
        widget_for_radio_buttons_and_choose_universal_excel.setLayout(
            horizontal_layout_for_radio_buttons_and_button)
        horizontal_layout_for_radio_buttons_and_button.addWidget(
            self.radio_buttons_background)
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
        self.radio_button_1.setFont(Fonts.get_qfont("JetBrains_Medium", 12))

        # активирует работу с doc файлом комиссии по иностранному
        self.radio_button_2 = QRadioButton("Второй семестр - иностранный", tab_main_widget)
        # активирует работу с файлом «Комиссии - Иностранный.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_2)
        self.radio_button_2.setFont(Fonts.get_qfont("JetBrains_Medium", 12))

        # активирует работу с doc файлом комиссии по специальности
        self.radio_button_3 = QRadioButton("Третий семестр - специальность", tab_main_widget)
        # активирует работу с файлом «Комиссии - Специальность.doc»
        radio_buttons_vertical_layout.addWidget(self.radio_button_3)
        self.radio_button_3.setFont(Fonts.get_qfont("JetBrains_Medium", 12))

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
        self.progress_bar_parsing.setVisible(False)

        # поле ввода для приказа о комиссиях
        self.input_commission = QLineEdit()
        self.input_commission.setMaximumWidth(730)
        self.input_commission.setPlaceholderText(
            "Введите текст приказа..."
        )
        self.input_commission.setFont(Fonts.get_qfont("JetBrains_Medium", 10))

        horizontal_widget_for_input_commission = QHBoxLayout()
        horizontal_widget_for_input_commission.addWidget(self.input_commission)

        # Виджет для фона виджета и кнопки выбора файла универсальной таблицы
        self.widget_for_choose_files_commission = QWidget()
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
        self.btn_choose_universal_xl.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_universal_xl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_universal_xl.clicked.connect(
            lambda: choose_universal_excel(self))

        vertical_layout_for_choosing_files.addWidget(self.btn_choose_universal_xl)

        # Лейбл для показа пути к выбранной универсальной таблицы
        self.universal_excel_label = QLabel()
        self.universal_excel_label.setFont(Fonts.get_qfont("JetBrains_Light", 8))
        self.universal_excel_label.setMinimumHeight(120)
        self.universal_excel_label.setText("Путь к выбранной таблице")
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setWordWrap(True)
        vertical_layout_for_choosing_files.addWidget(self.universal_excel_label)

        horizontal_layout_for_widget_for_choose_commission_file = QHBoxLayout()

        # Виджет для фона для кнопки выбора файла таблицы с информацией о комиссии
        # и лейбла с её (таблицы) именем
        self.widget_for_choose_commission_file = QWidget()
        self.widget_for_choose_commission_file.setMaximumWidth(730)
        self.widget_for_choose_commission_file.setMinimumHeight(150)

        vertical_layout_for_chose_doc_files = QVBoxLayout()
        self.widget_for_choose_commission_file.setLayout(
            vertical_layout_for_chose_doc_files)

        # кнопка для выбора doc файла с данными комиссии по истории
        self.btn_choose_history_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_history_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_history_commission.setFixedWidth(150)
        self.btn_choose_history_commission.setFixedHeight(50)
        self.btn_choose_history_commission.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_history_commission.clicked.connect(
          lambda: choose_history_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по истории
        self.history_xl_choused_label = QLabel()
        self.history_xl_choused_label.setMinimumHeight(50)
        self.history_xl_choused_label.setWordWrap(True)
        self.history_xl_choused_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.history_xl_choused_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_xl_choused_label.setText(
            "Здесь будет имя выбранного файла...")

        # кнопка для выбора doc файла с данными комиссии по иностранному
        self.btn_choose_foreign_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_foreign_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_foreign_commission.setFixedWidth(150)
        self.btn_choose_foreign_commission.setFixedHeight(50)
        self.btn_choose_foreign_commission.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_foreign_commission.clicked.connect(
          lambda: choose_foreign_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по иностранному
        self.foreign_xl_choosed_label = QLabel()
        self.foreign_xl_choosed_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.foreign_xl_choosed_label.setMinimumHeight(50)
        self.foreign_xl_choosed_label.setWordWrap(True)
        self.foreign_xl_choosed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreign_xl_choosed_label.setText(
            "Здесь будет имя выбранного файла...")

        # кнопка для выбора doc файла с данными комиссии по специальности
        self.btn_choose_specialization_commission = QPushButton(
            "Выберите файл")
        self.btn_choose_specialization_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_specialization_commission.setFixedWidth(150)
        self.btn_choose_specialization_commission.setFixedHeight(50)
        self.btn_choose_specialization_commission.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))

        # Лейбл для отображения пути выбранной таблицы с комиссией по специализации
        self.specialization_xl_choosed_lb = QLabel()
        self.specialization_xl_choosed_lb.setMinimumHeight(50)
        self.specialization_xl_choosed_lb.setWordWrap(True)
        self.specialization_xl_choosed_lb.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.specialization_xl_choosed_lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.specialization_xl_choosed_lb.setText(
            "Здесь будет имя выбранного файла...")

        # Лейбл отображения времени последнего обновления файла
        # с кешем направлений аспирантов
        self.time_update_label = QLabel()
        self.time_update_label.setFixedWidth(220)
        self.time_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_update_label.setText("время последнего обновления")
        self.time_update_label.setFont(Fonts.get_qfont("JetBrains_Light", 10))

        # Кнопка для обновления кеша с информацией о направлениях аспирантов
        self.button_to_update_date = QPushButton()
        self.button_to_update_date.setText("Обновить данные")
        self.button_to_update_date.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.button_to_update_date.setFixedHeight(50)
        self.button_to_update_date.setFixedWidth(200)
        self.button_to_update_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_update_date.clicked.connect(lambda: update_data(self))

        # Заголовок с инфо о последнем обновлении
        self.label_info_last_update_cache = QLabel()
        self.label_info_last_update_cache.setText("Дата и время последнего обновления:")
        self.label_info_last_update_cache.setFont(Fonts.get_qfont("JetBrains_Regular", 10))

        horizontal_layout_for_widget_for_choose_commission_file.addWidget(
            self.widget_for_choose_commission_file)

        # Лейбл-заголовок для отображения вида комиссии, файл с
        # которой можно будет выбрать
        self.label_commission_title = QLabel()
        self.label_commission_title.setFixedHeight(50)
        self.label_commission_title.setMaximumWidth(400)
        self.label_commission_title.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
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
            lambda checked: on_semester_changed(self, checked, "history"))
        self.radio_button_2.toggled.connect(
            lambda checked: on_semester_changed(self, checked, "foreign"))
        self.radio_button_3.toggled.connect(
            lambda checked: on_semester_changed(self, checked, "specialization"))

        # Виджет для кеша
        self.widget_for_cache = QWidget()
        self.widget_for_cache.setFixedWidth(730)
        self.widget_for_cache.setFixedHeight(70)
        horizontal_widget_layout_for_cache = QHBoxLayout()
        self.widget_for_cache.setLayout(horizontal_widget_layout_for_cache)

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
        self.button_change_save_path.setText("Изменить")
        self.button_change_save_path.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.button_change_save_path.clicked.connect(
            lambda: choose_parsing_save_folder(self))

        self.widget_for_change_save_path = QWidget()
        self.widget_for_change_save_path.setFixedWidth(730)
        horizontal_layout_for_change_save_path = QHBoxLayout()
        self.widget_for_change_save_path.setLayout(horizontal_layout_for_change_save_path)

        # Лейбл с заголовком об изменении пути сохранения ПДФ
        self.change_path_label = QLabel()
        self.change_path_label.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.change_path_label.setText("Путь сохранения:")

        vertical_layout_for_pos_title = QVBoxLayout()
        vertical_layout_for_pos_title.addWidget(self.change_path_label)
        vertical_layout_for_pos_title.addStretch()

        self.save_path_label = QLabel()
        self.save_path_label.setFixedWidth(550)
        self.save_path_label.setFont(Fonts.get_qfont("JetBrains_Medium", 10))
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

        # Виджет для показа сообщения о возможности завершения операции по нажатии кнопки
        self.widget_for_title_to_stop = QWidget()
        self.widget_for_title_to_stop.setFixedWidth(730)
        self.widget_for_title_to_stop.setMinimumHeight(50)
        self.widget_for_title_to_stop.setVisible(False)

        layout_for_title_to_stop = QVBoxLayout()
        self.widget_for_title_to_stop.setLayout(layout_for_title_to_stop)

        self.label_title_to_stop = QLabel()
        self.label_title_to_stop.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.label_title_to_stop.setText(
            "Чтобы остановить процесс, нажмите 'Esc' или 'Space'")
        self.label_title_to_stop.setMinimumWidth(300)
        self.label_title_to_stop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_for_title_to_stop.addWidget(
            self.label_title_to_stop, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавление в основной layout
        container_layout_main_tab.addWidget(self.widget_bg_main_tab)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(self.widget_for_title_to_stop,
            alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addWidget(
            self.progress_bar_parsing, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(horizontal_widget_for_input_commission)

        container_layout_main_tab.addLayout(horizontal_position_layout_for_center_poz)

        container_layout_main_tab.addLayout(
            horizontal_layout_for_widget_for_choose_commission_file)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(
            self.widget_for_cache, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(
            self.widget_for_change_save_path, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(widgets_horizontal_main_tab_layout)

        # Первая вкладка - сбор пдф по готовой таблице ==================================
        # ===============================================================================

        main_layout_for_second_tab = QVBoxLayout()
        self.tab_second_widget.setLayout(main_layout_for_second_tab)

        # Виджет для фона заголовка
        self.background_widget_for_second_tab = QWidget()

        main_layout_for_second_tab.addWidget(
            self.background_widget_for_second_tab)

        # Заголовок для вкладки
        self.second_tab_title = QLabel()
        self.second_tab_title.setText("Сборка ПДФ по готовой таблице")
        self.second_tab_title.setFont(Fonts.get_qfont("JetBrains_Regular", 12))

        title_second_tab_widget = QWidget()

        # Лейаут для позиционирования заголовка по левому краю
        horizontal_layout_for_second_tab_title = QHBoxLayout()
        title_second_tab_widget.setLayout(horizontal_layout_for_second_tab_title)
        horizontal_layout_for_second_tab_title.addWidget(self.second_tab_title)
        horizontal_layout_for_second_tab_title.addStretch()

        # Основной вертикальный контейнер для второй (первой) вкладки
        background_widget_for_second_tab_container = QVBoxLayout()
        self.background_widget_for_second_tab.setLayout(
            background_widget_for_second_tab_container)

        # Виджет для кнопки выбора пути сохранения ПДФ, лейбла с текущим путём
        # сохранения и заголовка
        self.widget_for_pos_button_path_and_title_choose_save_path = QWidget()
        self.widget_for_pos_button_path_and_title_choose_save_path.setFixedWidth(730)
        self.widget_for_pos_button_path_and_title_choose_save_path.setMinimumHeight(50)

        # Заголовок изменения пути сохранения
        self.title_change_save_path = QLabel()
        self.title_change_save_path.setFont(Fonts.get_qfont("JetBrains_Regular", 11))
        self.title_change_save_path.setText("Текущий путь сохранения")

        # Отдельный путь для сохранения ПДФ (без парсинга)
        self.save_folder_second_tab_path: str = str(
            Path.home() / "Desktop" / "results_folder")

        # Лейбл для отображения текущего пути сохранения ПДФ
        self.current_save_path_label = QLabel()
        self.current_save_path_label.setMinimumHeight(50)
        self.current_save_path_label.setFixedWidth(450)
        self.current_save_path_label.setWordWrap(True)
        self.current_save_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_save_path_label.setFont(Fonts.get_qfont("JetBrains_Medium", 10))
        self.current_save_path_label.setText(self.save_folder_second_tab_path)

        # Кнопка выбора пути сохранения ПДФ
        self.button_shouse_save_path_for_second_tab = QPushButton()
        self.button_shouse_save_path_for_second_tab.setFixedWidth(150)
        self.button_shouse_save_path_for_second_tab.setFixedHeight(50)
        self.button_shouse_save_path_for_second_tab.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.button_shouse_save_path_for_second_tab.setText("Изменить")
        self.button_shouse_save_path_for_second_tab.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_shouse_save_path_for_second_tab.clicked.connect(
            lambda: choose_save_folder_second_tab(self))

        # прогресс бар для первой вкладки (без парсинга). Изначально скрыто
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(730)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setVisible(False)

        # Лейаут для виджетов: кнопки выбора пути сохранения, лейбла с путём и заголовка
        layout_for_save_path_widgets = QHBoxLayout()
        self.widget_for_pos_button_path_and_title_choose_save_path.setLayout(
            layout_for_save_path_widgets)

        vertical_layout_for_pos_title_second_tab =QVBoxLayout()
        vertical_layout_for_pos_title_second_tab.addWidget(self.title_change_save_path)
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

        self.widget_for_choose_table = QWidget()
        self.widget_for_choose_table.setFixedWidth(730)

        self.title_choose_table_label = QLabel()
        self.title_choose_table_label.setFixedHeight(50)
        self.title_choose_table_label.setMaximumWidth(250)
        self.title_choose_table_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_choose_table_label.setFont(Fonts.get_qfont("JetBrains_Regular", 11))
        self.title_choose_table_label.setText("Таблица с данными")

        self.label_current_tabel = QLabel()
        self.label_current_tabel.setWordWrap(True)
        self.label_current_tabel.setMinimumHeight(50)
        self.label_current_tabel.setFixedWidth(450)
        self.label_current_tabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_current_tabel.setFont(Fonts.get_qfont("JetBrains_Regular", 10))

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
        self.button_shouse_table.setText("Выбрать файл")
        self.button_shouse_table.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_shouse_table.clicked.connect(
            lambda: choose_file(self))

        # Кнопка открытия папки сохранения
        self.button_open_folder_with_pdf = QPushButton()
        self.button_open_folder_with_pdf.setFixedWidth(250)
        self.button_open_folder_with_pdf.setFixedHeight(50)
        self.button_open_folder_with_pdf.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.button_open_folder_with_pdf.setText("Открыть папку с PDF")
        self.button_open_folder_with_pdf.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_open_folder_with_pdf.clicked.connect(
            lambda: open_pdf_folder(self))

        layout_for_choose_table = QVBoxLayout()
        self.widget_for_choose_table.setLayout(layout_for_choose_table)
        layout_for_choose_table.setSpacing(15)

        # Виджет для показа сообщения о возможности завершения операции по нажатии кнопки
        self.widget_title_stop_second = QWidget()
        self.widget_title_stop_second.setFixedWidth(730)
        self.widget_title_stop_second.setMinimumHeight(50)
        self.widget_title_stop_second.setVisible(False)

        layout_title_stop_second = QVBoxLayout()
        self.widget_title_stop_second.setLayout(layout_title_stop_second)

        self.label_title_stop_2 = QLabel()
        self.label_title_stop_2.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.label_title_stop_2.setText(
            "Чтобы остановить процесс, нажмите 'Esc' или 'Space'")
        self.label_title_stop_2.setMinimumWidth(300)
        self.label_title_stop_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_title_stop_second.addWidget(
            self.label_title_stop_2, alignment=Qt.AlignmentFlag.AlignCenter)

        horizontal_pos_layout = QHBoxLayout()

        layout_for_choose_table.addLayout(horizontal_pos_layout)

        horizontal_pos_layout.addWidget(
            self.title_choose_table_label)

        horizontal_pos_layout.addStretch()

        horizontal_pos_layout.addWidget(
            self.label_current_tabel)

        layout_for_choose_table.addWidget(
            self.button_shouse_table, alignment=Qt.AlignmentFlag.AlignRight)

        background_widget_for_second_tab_container.addWidget(
            self.widget_title_stop_second, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addWidget(
            self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addWidget(
            self.widget_for_choose_table, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addWidget(
            self.widget_for_pos_button_path_and_title_choose_save_path,
            alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.addStretch()
        background_widget_for_second_tab_container.addWidget(
            self.button_open_folder_with_pdf, alignment=Qt.AlignmentFlag.AlignCenter)

        background_widget_for_second_tab_container.setSpacing(15)

        # Вторая вкладка - настройки ====================================================
        # ===============================================================================

        tab_settings_layout = QVBoxLayout()
        self.tab_settings_widget.setLayout(tab_settings_layout)

        self.settings_cap = QWidget()
        self.settings_cap.setFixedHeight(48)

        self.settings_label = QLabel()
        self.settings_label.setText("Настройки")
        self.settings_label.setFont(Fonts.get_qfont("JetBrains_Regular", 14))

        layout_for_settings_cap = QHBoxLayout()
        layout_for_settings_cap.addWidget(self.settings_label)

        self.settings_cap.setLayout(layout_for_settings_cap)

        tab_settings_layout.addWidget(self.settings_cap, alignment=Qt.AlignmentFlag.AlignTop)

        self.settings_main_widget = QWidget()
        self.settings_main_widget.setFixedWidth(740)

        layout_for_settings = QVBoxLayout()
        self.settings_main_widget.setLayout(layout_for_settings)

        self.loading_window_param_widget = QWidget()
        self.loading_window_param_widget.setMaximumWidth(720)
        self.loading_window_param_widget.setFixedHeight(70)

        loading_param_h_layout = QHBoxLayout()
        self.loading_window_param_widget.setLayout(loading_param_h_layout)

        self.param_show_loading_window = QLabel()
        self.param_show_loading_window.setText("Загрузочное окно")
        self.param_show_loading_window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param_show_loading_window.setFont(Fonts.get_qfont("JetBrains_Medium", 10))

        self.button_show_loading_window = QPushButton()
        self.button_show_loading_window.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_show_loading_window.setText("Показывать")
        self.button_show_loading_window.setFixedHeight(50)
        self.button_show_loading_window.setFixedWidth(200)
        self.button_show_loading_window.setFont(Fonts.get_qfont("JetBrains_Light", 8))
        self.button_show_loading_window.clicked.connect(lambda: set_true_show_loading_window(self))

        self.button_hide_loading_window = QPushButton()
        self.button_hide_loading_window.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_hide_loading_window.setText("Скрывать")
        self.button_hide_loading_window.setFixedHeight(50)
        self.button_hide_loading_window.setFixedWidth(200)
        self.button_hide_loading_window.setFont(Fonts.get_qfont("JetBrains_Light", 8))
        self.button_hide_loading_window.clicked.connect(lambda: set_false_show_loading_window(self))

        loading_param_h_layout.addWidget(self.param_show_loading_window)
        loading_param_h_layout.addStretch()
        loading_param_h_layout.addWidget(self.button_show_loading_window)
        loading_param_h_layout.addWidget(self.button_hide_loading_window)

        self.loading_window_timer_duration_param_widget = QWidget()
        self.loading_window_timer_duration_param_widget.setMaximumWidth(720)
        self.loading_window_timer_duration_param_widget.setFixedHeight(70)

        loading_timer_duration_param_h_layout = QHBoxLayout()
        self.loading_window_timer_duration_param_widget.setLayout(loading_timer_duration_param_h_layout)

        # Лейбл для заголовка времени показа загрузочного экрана
        self.param_timer_duration_loading_window = QLabel()
        self.param_timer_duration_loading_window.setText("Время показа загрузочного окна")
        self.param_timer_duration_loading_window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param_timer_duration_loading_window.setFont(Fonts.get_qfont("JetBrains_Medium", 10))

        # Слайдер, который меняет время показа загрузочного окна
        self.slider_loading_window_timer_duration = QSlider(Qt.Orientation.Horizontal)
        self.slider_loading_window_timer_duration.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_loading_window_timer_duration.setRange(1000, 15000)
        self.slider_loading_window_timer_duration.setValue(Settings.get_loading_window_timer_duration())
        self.slider_loading_window_timer_duration.setFixedWidth(350)
        self.slider_loading_window_timer_duration.valueChanged.connect(lambda value: on_slider_changed(self, value))

        # Индикатор текущей длительности показа загрузочного окна
        self.indicate_loading_window_timer_duration = QLabel()
        self.indicate_loading_window_timer_duration.setFixedWidth(60)
        self.indicate_loading_window_timer_duration.setFont(Fonts.get_qfont("JetBrains_Light", 10))
        self.indicate_loading_window_timer_duration.setText(
            f"{str(Settings.get_loading_window_timer_duration())} мс")

        loading_timer_duration_param_h_layout.addWidget(self.param_timer_duration_loading_window)
        loading_timer_duration_param_h_layout.addStretch()
        loading_timer_duration_param_h_layout.addWidget(self.slider_loading_window_timer_duration)
        loading_timer_duration_param_h_layout.addStretch()
        loading_timer_duration_param_h_layout.addWidget(self.indicate_loading_window_timer_duration)

        # Виджет для выбора цветовой темы приложения
        self.widget_for_choose_theme = QWidget()
        self.widget_for_choose_theme.setFixedHeight(70)
        self.widget_for_choose_theme.setFixedWidth(720)

        # Заголовок для виджета выбора тем
        self.label_title_choose_theme = QLabel()
        self.label_title_choose_theme.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.label_title_choose_theme.setText("Тема приложения")

        # Кнопки для выбора тем
        self.choose_standard_theme_button = QPushButton()
        self.choose_standard_theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose_standard_theme_button.setText("Стандартная")
        self.choose_standard_theme_button.setFixedWidth(150)
        self.choose_standard_theme_button.setFixedHeight(50)
        self.choose_standard_theme_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.choose_standard_theme_button.clicked.connect(
            lambda: on_button_choose_theme(self, "standard"))

        self.choose_violet_theme_button = QPushButton()
        self.choose_violet_theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose_violet_theme_button.setText("Фиолетовая")
        self.choose_violet_theme_button.setFixedWidth(150)
        self.choose_violet_theme_button.setFixedHeight(50)
        self.choose_violet_theme_button.setFont(Fonts.get_qfont("JetBrains_Regular", 10))
        self.choose_violet_theme_button.clicked.connect(
            lambda: on_button_choose_theme(self, "violet"))

        self.choose_dark_theme_button = QPushButton()
        self.choose_dark_theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose_dark_theme_button.setText("Тёмная")
        self.choose_dark_theme_button.setFixedWidth(150)
        self.choose_dark_theme_button.setFixedHeight(50)
        self.choose_dark_theme_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.choose_dark_theme_button.clicked.connect(
            lambda: on_button_choose_theme(self, "dark"))

        layout_for_theme_widget = QHBoxLayout()
        self.widget_for_choose_theme.setLayout(layout_for_theme_widget)
        layout_for_theme_widget.addWidget(self.label_title_choose_theme)
        layout_for_theme_widget.addWidget(self.choose_standard_theme_button)
        layout_for_theme_widget.addWidget(self.choose_violet_theme_button)
        layout_for_theme_widget.addWidget(self.choose_dark_theme_button)

        # Кнопка для создания ярлыка
        self.shortcut_button = QPushButton()
        self.shortcut_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shortcut_button.setText("Создать ярлык на рабочем столе")
        self.shortcut_button.setFixedWidth(300)
        self.shortcut_button.setFixedHeight(50)
        self.shortcut_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.shortcut_button.clicked.connect(self.get_shortcut)

        layout_for_settings.addWidget(self.loading_window_param_widget)
        layout_for_settings.addWidget(self.loading_window_timer_duration_param_widget)

        layout_for_settings.addWidget(self.widget_for_choose_theme,
            alignment=Qt.AlignmentFlag.AlignCenter)

        tab_settings_layout.addWidget(self.settings_main_widget,
            alignment = Qt.AlignmentFlag.AlignCenter)

        tab_settings_layout.addWidget(self.shortcut_button,
            alignment=Qt.AlignmentFlag.AlignCenter)

        tab_settings_layout.addStretch()

        set_styles(self)

        self.change_active_button_styles()

        # ПУть к папке с изображениями для фона главного окна (основной вкладки)
        get_bg_for_main_tab_widget(self, "resources/images/for_main_window")


    def get_shortcut(self) -> None:
        """
        Функция для создания ярлыка на рабочий стол для быстрого запуска приложения
        До создания ярлыка выполняются все проверки - на наличие сборки проекта и
        на существование ярлыка (если уже есть)
        :return: None
        """

        check_build()

    def keyPressEvent(self, event) -> None:
        """
        Обработка нажатий клавиш для остановки процесса

        :return: None
        """

        # Пробел - обычная остановка
        if event.key() == Qt.Key.Key_Space:
            if (self.stop_parsing_button.isVisible() and
                    self.stop_parsing_button.isEnabled()):
                stop_generation_process(self)
                event.accept()
                return

            elif (self.stop_button.isVisible() and
                    self.stop_button.isEnabled()):
                stop_generation_second_tab(self)
                event.accept()
                return

        # ESC - аварийная остановка (работает даже если кнопка скрыта)
        if event.key() == Qt.Key.Key_Escape:
            if self.stop_parsing_button.isVisible():
                Rich.warning_log("Аварийная остановка парсинга по ESC")
                self.stop_generation = True
                QMessageBox.warning(self, "Аварийная остановка",
                                    "Парсинг остановлен по клавише ESC")
                event.accept()
                return
            elif self.stop_button.isVisible():
                Rich.warning_log("Аварийная остановка сборки PDF по ESC")
                self.stop_building_pdf = True
                QMessageBox.warning(self, "Аварийная остановка",
                                    "Сборка PDF остановлена по клавише ESC")
                event.accept()
                return

        # Запуск процессов с комбинации шифт + ф9
        if (event.key() == Qt.Key.Key_F9 and
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            run(self)
            event.accept()
            return

        # Передаем событие дальше
        super().keyPressEvent(event)

    def change_active_button_styles(self) -> None:
        """
        Функция для смены стиля кнопок (одна кнопка должна быть "активной",
        остальные - "неактивные").

        :return: None. Устанавливает стили для кнопок в соответствии
        с выбранной темой приложения (активна та кнопка, имя темы за
        которую она отвечает установлено в параметрах на данных момент).
        """

        current_theme = Settings.get_theme_name()

        if current_theme == "standard":
            self.choose_dark_theme_button.setStyleSheet(Style.button_hide_style)
            self.choose_violet_theme_button.setStyleSheet(Style.button_hide_style)
            self.choose_standard_theme_button.setStyleSheet(Style.button_blue_style)
        elif current_theme == "violet":
            self.choose_dark_theme_button.setStyleSheet(Style.button_hide_style)
            self.choose_violet_theme_button.setStyleSheet(Style.button_blue_style)
            self.choose_standard_theme_button.setStyleSheet(Style.button_hide_style)
        elif current_theme == "dark":
            self.choose_dark_theme_button.setStyleSheet(Style.button_blue_style)
            self.choose_violet_theme_button.setStyleSheet(Style.button_hide_style)
            self.choose_standard_theme_button.setStyleSheet(Style.button_hide_style)

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
