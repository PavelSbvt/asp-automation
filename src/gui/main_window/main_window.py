import sys
import random
from pathlib import Path
from typing import Optional, List, Dict, Any
import webbrowser

from PyQt6.QtCore import QPoint, QTimer, Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QTransform, QCursor
from PyQt6.QtWidgets import (QWidget, QLabel, QTabWidget, QPushButton, QTextEdit,
QProgressBar, QApplication, QRadioButton, QButtonGroup, QLineEdit, QMessageBox,
QMainWindow, QVBoxLayout, QHBoxLayout, QScrollArea)

from core.settings_manager import settings
from utils.output_rich import debug_log, warning_log, simple_log
from utils.functions_for_window_gui import (get_random_image_from_folder,
    get_main_color_image)
from gui.functions.choose_files import (choose_universal_excel,
    choose_parsing_save_folder, open_parsing_pdf_folder,
    choose_history_excel, choose_foreign_excel, choose_specialization_excel,
    )
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

        self.width_now = 0
        self.height_now = 0

        self.choose_tab = -1

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

        self.bg_path_check = ""

        # стандартная папка сохранения пдф фалов в результате работы функций
        self.save_folder_path: str = str(Path.home() / "Desktop" / "results_folder")
        self.parsing_save_folder_path = self.save_folder_path

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        # Главный виджет
        self.main_back_widget = QWidget(self)
        self.main_back_widget.setStyleSheet(f"background-color: {style.background_color}; border-radius: 0px;")
        self.setCentralWidget(self.main_back_widget)

        # Главный вертикальный layout
        self.main_v_layout = QVBoxLayout()
        self.main_back_widget.setLayout(self.main_v_layout)

        # Работа с вкладками
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.tab_widget.setStyleSheet(
            f"color: {style.light_font_color};"
        )

        # Вкладки
        tab_main_widget = QWidget()
        tab_second_widget = QWidget()
        tab_settings_widget = QWidget()

        self.tab_widget.addTab(tab_main_widget, "Главная")
        self.tab_widget.addTab(tab_second_widget, "ЛР по формированию PDF")
        self.tab_widget.addTab(tab_settings_widget, "Настройки")

        self.tab_widget.setTabVisible(2, False)

        self.main_image_color = "(211, 211, 211)"

        # Шапка
        self.cap_widget = QWidget(self)

        self.cap = QHBoxLayout()

        self.cap_widget.setLayout(self.cap)
        self.cap_widget.setFixedHeight(48)
        # self.cap_widget.setMaximumWidth(1400)

        self.cap.setContentsMargins(12,0,12,0)

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

        self.cap.addWidget(self.app_name_button)
        self.cap.addStretch()

        settings_path = Path("resources/images/icons/settings_pycharm_icon.png")
        settings_hover_path = Path("resources/images/icons/settings_pycharm_icon_hover.png")

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
                    QPushButton:disabled {{
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 rgba(100, 50, 50, 120),
                            stop: 1 rgba(70, 35, 35, 160));
                        color: rgba(200, 200, 200, 120);
                        border: 1px solid rgba(100, 50, 50, 80);
                    }}
                """
        )
        self.stop_parsing_button.clicked.connect(self.stop_generation_process)
        self.stop_parsing_button.setVisible(False)

        self.what_tab_is_show_now()
        self.tab_widget.currentChanged.connect(self.what_tab_is_show_now)

        self.cap.addWidget(self.run_button)
        self.cap.addWidget(self.stop_parsing_button)
        self.cap.addWidget(self.settings_button)

        self.main_v_layout.addWidget(self.cap_widget)

        self.main_v_layout.addWidget(self.tab_widget)

        # Виджет для фона основной вкладки приложения
        self.widget_bg_main_tab = QPushButton()
        self.widget_bg_main_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.widget_bg_main_tab.setMinimumHeight(200)
        self.widget_bg_main_tab.setMaximumWidth(1900)

        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

        self.widget_bg_main_tab.clicked.connect(self.on_bg_clicked)

        # Лейбл для того, чтобы показался виджет с фоном (без текста)
        label = QLabel(self.widget_bg_main_tab)
        label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout для виджета, чтобы расположить текст лейбла
        bg_layout = QVBoxLayout()
        bg_layout.addWidget(label)
        self.widget_bg_main_tab.setLayout(bg_layout)

        bg_main_tab_layout = QHBoxLayout()
        bg_main_tab_layout.addWidget(self.widget_bg_main_tab)

        main_tab_scroll_area = QScrollArea()
        main_tab_scroll_area.setWidgetResizable(True)
        main_tab_scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1E1F22;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4D4E51;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7A7B7E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent; 
            }
        """)

        horizontal_windget_for_position = QHBoxLayout()

        container_widget_main_tab = QWidget()

        horizontal_windget_for_position.addWidget(container_widget_main_tab)

        # container_widget_main_tab.setMaximumWidth(750)
        container_layout_main_tab = QVBoxLayout(container_widget_main_tab)
        container_widget_main_tab.setStyleSheet(
            f"background-color: {style.background_dark_color}; border-radius: 10px;")

        main_tab_scroll_area.setWidget(container_widget_main_tab)

        # Установка лейаута для главной вкладки и загрузка в неё виджета фона
        tab_main_layout = QVBoxLayout(tab_main_widget)

        tab_main_layout.addLayout(bg_main_tab_layout)
        # tab_main_layout.addStretch()

        tab_main_widget.setLayout(tab_main_layout)

        tab_main_layout.addWidget(main_tab_scroll_area)

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
        self.open_folder_button.setFont(fonts.get_qfont("JetBrains_Regular", 12))
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.setStyleSheet(style.button_blue_style)
        self.open_folder_button.clicked.connect(lambda: open_parsing_pdf_folder(self))

        # кнопка изменения пути сохранения
        self.button_to_find_where_save = QPushButton(tab_main_widget)
        self.button_to_find_where_save.setMaximumWidth(400)
        self.button_to_find_where_save.setFixedHeight(30)
        self.button_to_find_where_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_find_where_save.setStyleSheet(style.button_blue_style)
        self.button_to_find_where_save.setText("Изменить путь для сохранения PDF")
        self.button_to_find_where_save.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.button_to_find_where_save.clicked.connect(
            lambda: choose_parsing_save_folder(self))

        # ================================================================

        self.radio_buttons_background = QWidget(tab_main_widget)
        self.radio_buttons_background.setFixedHeight(200)
        self.radio_buttons_background.setFixedWidth(350)
        self.radio_buttons_background.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
            )

        radio_buttons_vertical_layout = QVBoxLayout()
        self.radio_buttons_background.setLayout(radio_buttons_vertical_layout)

        self.label_for_radio_buttons = QLabel()
        self.label_for_radio_buttons.setText("Выберите семестр:")
        self.label_for_radio_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_for_radio_buttons.setStyleSheet(f"color: {style.light_font_color}; margin: 10px; font-weight: bold;")
        self.label_for_radio_buttons.setFont(fonts.get_qfont("JetBrains_Regular", 14))

        radio_buttons_vertical_layout.addWidget(self.label_for_radio_buttons)

        horizontal_position_layout_for_center_poz = QHBoxLayout()

        widget_for_radio_buttons_and_choose_universal_excel = QWidget()
        widget_for_radio_buttons_and_choose_universal_excel.setMaximumWidth(750)

        horizontal_position_layout_for_center_poz.addWidget(widget_for_radio_buttons_and_choose_universal_excel)

        horizontal_layout_for_radio_buttons_and_button = QHBoxLayout()

        widget_for_radio_buttons_and_choose_universal_excel.setLayout(
            horizontal_layout_for_radio_buttons_and_button)

        horizontal_layout_for_radio_buttons_and_button.addWidget(self.radio_buttons_background)
        horizontal_layout_for_radio_buttons_and_button.addStretch()

        widgets_vertical_main_tab_layout.addWidget(self.button_to_find_where_save)
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

        # =============================================

        # прогресс бар для второй вкладки (с парсингом)
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
        self.input_commission.setStyleSheet("""
                   QLineEdit {
                       background-color: #2B2D30;
                       color: white;
                       border: 2px solid #4D4E51;
                       border-radius: 8px;
                       padding: 5px 10px;
                   }
                   QLineEdit:focus {
                       border: 2px solid #CED0D6;
                       background-color: #4D4E51;
                   }
                   QLineEdit::placeholder {
                       color: #6272a4;
                   }
               """)
        self.input_commission.setFont(fonts.get_qfont("JetBrains_Medium", 10))

        horizontal_widget_for_input_commission = QHBoxLayout()
        horizontal_widget_for_input_commission.addWidget(self.input_commission)

        # ===========================================================

        self.widget_for_choose_files_commission = QWidget()
        self.widget_for_choose_files_commission.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
        )
        self.widget_for_choose_files_commission.setFixedHeight(200)
        self.widget_for_choose_files_commission.setFixedWidth(350)

        horizontal_layout_for_radio_buttons_and_button.addWidget(
            self.widget_for_choose_files_commission)

        vertical_layout_for_choosing_files = QVBoxLayout()
        self.widget_for_choose_files_commission.setLayout(
            vertical_layout_for_choosing_files)


        # кнопка для выбора .xlsx файла - таблицы с данными "универсальной таблицы"
        self.btn_choose_universal_xl = QPushButton(
            "Выберите таблицу для парсинга")
        self.btn_choose_universal_xl.setFixedHeight(50)
        self.btn_choose_universal_xl.setMaximumWidth(330)
        self.btn_choose_universal_xl.setStyleSheet(style.button_blue_style)
        self.btn_choose_universal_xl.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_universal_xl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_universal_xl.clicked.connect(
            lambda: choose_universal_excel(self))

        vertical_layout_for_choosing_files.addWidget(self.btn_choose_universal_xl)

        self.universal_excel_label = QLabel()
        self.universal_excel_label.setFont(fonts.get_qfont("JetBrains_Light", 8))
        self.universal_excel_label.setMaximumHeight(120)
        self.universal_excel_label.setText("Имя файла универсальной таблицы")
        self.universal_excel_label.setStyleSheet(
            f"color: {style.dark_font_color};"
            f"background-color: {style.background_dark_color};"
            f"padding: 10px;"
        )
        self.universal_excel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universal_excel_label.setWordWrap(True)
        vertical_layout_for_choosing_files.addWidget(self.universal_excel_label)

        # ================================================================

        horizontal_layout_for_widget_for_choose_commission_file = QHBoxLayout()

        widget_for_choose_commission_file = QWidget()
        widget_for_choose_commission_file.setMaximumWidth(730)
        widget_for_choose_commission_file.setMinimumHeight(150)
        widget_for_choose_commission_file.setStyleSheet(
            f"background-color: {style.background_color}; border-radius: 10px;"
        )

        vertical_layout_for_chose_doc_files = QVBoxLayout()
        widget_for_choose_commission_file.setLayout(
            vertical_layout_for_chose_doc_files)

        # ======================================================================

        # кнопка для выбора doc файла с данными комиссии по истории
        self.btn_choose_history_commission = QPushButton(
            "Выберите таблицу с данными комиссии по истории")
        self.btn_choose_history_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_history_commission.setFixedWidth(450)
        self.btn_choose_history_commission.setFixedHeight(50)
        self.btn_choose_history_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_history_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_history_commission.clicked.connect(
          lambda: choose_history_excel(self))

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
            "Выберите таблицу с данными комиссии по иностранному")
        self.btn_choose_foreign_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_foreign_commission.setFixedWidth(450)
        self.btn_choose_foreign_commission.setFixedHeight(50)
        self.btn_choose_foreign_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_foreign_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_foreign_commission.clicked.connect(
          lambda: choose_foreign_excel(self))

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
            "Выберите таблицу с данными комиссии по специальности")
        self.btn_choose_specialization_commission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_specialization_commission.setFixedWidth(450)
        self.btn_choose_specialization_commission.setFixedHeight(50)
        self.btn_choose_specialization_commission.setStyleSheet(style.button_blue_style)
        self.btn_choose_specialization_commission.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))

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

        # ======================================================================

        self.time_update_label = QLabel()
        self.time_update_label.setFixedWidth(220)
        self.time_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_update_label.setStyleSheet(
            f"color: {style.dark_font_color}; "
            f"background-color: {style.background_dark_color};"
        )
        self.time_update_label.setText("время последнего обновления")
        self.time_update_label.setFont(fonts.get_qfont("JetBrains_Light", 10))

        self.button_to_update_date = QPushButton()
        self.button_to_update_date.setText("Обновить данные")
        self.button_to_update_date.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.button_to_update_date.setFixedHeight(50)
        self.button_to_update_date.setFixedWidth(200)
        self.button_to_update_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_to_update_date.setStyleSheet(style.button_blue_style)
        self.button_to_update_date.clicked.connect(lambda: update_data(self))

        self.label_info_last_update_cache = QLabel()
        self.label_info_last_update_cache.setText("Дата и время последнего обновления:")
        self.label_info_last_update_cache.setFont(fonts.get_qfont("JetBrains_Regular", 10))
        self.label_info_last_update_cache.setStyleSheet(f"color: {style.light_font_color};")

        # ======================================================================

        horizontal_layout_for_widget_for_choose_commission_file.addWidget(
            widget_for_choose_commission_file)

        vertical_layout_for_chose_doc_files.addWidget(
            self.btn_choose_history_commission, alignment=Qt.AlignmentFlag.AlignCenter)
        vertical_layout_for_chose_doc_files.addWidget(self.history_xl_choused_label)

        vertical_layout_for_chose_doc_files.addWidget(
            self.btn_choose_foreign_commission, alignment=Qt.AlignmentFlag.AlignCenter)
        vertical_layout_for_chose_doc_files.addWidget(self.foreign_xl_choosed_label)

        vertical_layout_for_chose_doc_files.addWidget(
            self.btn_choose_specialization_commission, alignment=Qt.AlignmentFlag.AlignCenter)
        vertical_layout_for_chose_doc_files.addWidget(self.specialization_xl_choosed_lb)

        self.btn_choose_history_commission.setVisible(True)
        self.history_xl_choused_label.setVisible(True)
        self.btn_choose_foreign_commission.setVisible(False)
        self.foreign_xl_choosed_label.setVisible(False)
        self.btn_choose_specialization_commission.setVisible(False)
        self.specialization_xl_choosed_lb.setVisible(False)

        self.radio_button_1.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "history"))
        self.radio_button_2.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "foreign"))
        self.radio_button_3.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "specialization"))

        widget_for_cache = QWidget()
        widget_for_cache.setFixedWidth(730)
        widget_for_cache.setFixedHeight(70)
        widget_for_cache.setStyleSheet(
            "background-color: #2B2D30; border-radius: 10px;"
        )
        horizontal_widget_layout_for_cache = QHBoxLayout()
        widget_for_cache.setLayout(horizontal_widget_layout_for_cache)

        # horizontal_widget_layout_for_cache.setSpacing(20)

        horizontal_widget_layout_for_cache.addWidget(self.label_info_last_update_cache)
        horizontal_widget_layout_for_cache.addWidget(self.time_update_label)
        horizontal_widget_layout_for_cache.addStretch()
        horizontal_widget_layout_for_cache.addWidget(self.button_to_update_date)







        container_layout_main_tab.addWidget(self.widget_bg_main_tab)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(self.progress_bar_parsing, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(horizontal_widget_for_input_commission)

        container_layout_main_tab.addLayout(horizontal_position_layout_for_center_poz)

        container_layout_main_tab.addLayout(horizontal_layout_for_widget_for_choose_commission_file)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addWidget(widget_for_cache, alignment=Qt.AlignmentFlag.AlignCenter)

        # container_layout_main_tab.addWidget(self.time_update_label)
        # container_layout_main_tab.addWidget(self.button_to_update_date)

        container_layout_main_tab.addStretch()

        container_layout_main_tab.addLayout(widgets_horizontal_main_tab_layout)

    def on_bg_clicked(self):
        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

    def stop_generation_process(self) -> None:
        """
        Останавливает процесс генерации

        :return: None
        """

        simple_log("Остановка процесса по запросу пользователя")
        self.stop_generation = True
        # self.blc_for_stop.setVisible(True)
        self.run_button.setVisible(False)


        # Делаем кнопку неактивной, чтобы нельзя было нажать дважды
        self.stop_parsing_button.setEnabled(False)

        QMessageBox.information(
            self,
            "Остановка",
            "Процесс остановки запущен...\n\n"
            "Программа завершит текущую операцию и остановится."
        )

    def run(self):
        if self.choose_tab == 0:
            parsing(self)
        else:
            return

    def on_semester_changed(self, checked: bool, semester: str) -> None:
        """
        Показывает нужные кнопки в зависимости от выбранного семестра

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
        elif semester == "foreign":
            self.btn_choose_foreign_commission.setVisible(True)
            self.foreign_xl_choosed_label.setVisible(True)
        elif semester == "specialization":
            self.btn_choose_specialization_commission.setVisible(True)
            self.specialization_xl_choosed_lb.setVisible(True)

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

        old_bg_path = self.bg_path_check

        img_path = get_random_image_from_folder(folder_path)
        path_bg_widget = Path(f'{img_path}')

        new_image_path = path_bg_widget.as_posix()

        def use_random_photo(photo_path):
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

            self.bg_path_check = f"{photo_path}"

            debug_log(f"Для фона главного окна выбрано изображение: {photo_path}")

        def get_random_path():
            img_path_new = get_random_image_from_folder(folder_path)
            path_bg_widget_new = Path(f'{img_path_new}')

            return path_bg_widget_new.as_posix()

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
        Функция для получения индекса текущей вкладки

        :return: int
        """

        tabs_name = ["Главная", "ЛР по формированию PDF", "Настройки"]

        current_index = self.tab_widget.currentIndex()

        tab_name = ""

        if current_index == 0:
            tab_name = tabs_name[0]
            self.choose_tab = 0

        elif current_index == 1:
            tab_name = tabs_name[1]
            self.choose_tab = 1

        elif current_index == 2:
            tab_name = tabs_name[2]
            self.choose_tab = 2

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
