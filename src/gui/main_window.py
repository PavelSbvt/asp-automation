from pathlib import Path
import traceback
import webbrowser
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import QPoint, Qt, QThread
from PyQt6.QtWidgets import (
    QApplication, QMessageBox,
    QMainWindow, QFileDialog)
from PyQt6.QtGui import QMouseEvent, QResizeEvent, QCloseEvent
from PyQt6.uic import loadUi

from core.settings_manager import Settings
from core.worker_parse_and_generate_pdf import PdfParseAndGenerateWorker
from utils.output_rich import Rich
from utils.create_shortcut import check_build
from gui.utils.choose_files import (
    choose_universal_excel,
    choose_save_folder_second_tab,
    choose_parsing_save_folder,
    open_parsing_pdf_folder,
    choose_history_excel,
    choose_foreign_excel,
    choose_specialization_excel,
    open_pdf_folder)
from gui.utils.fonts import Fonts
from parser.sait_parsing import (
    site_parce_main, site_parce_dn,
    save_specialties_to_cache, get_last_update_time,
    ParsingDir)
from core.worker_generate_pdf import PdfBuilderWorker
from gui.utils.windows_functions import (
    get_random_image_from_folder,
    get_main_color_image)
from gui.utils.windows_animations import AnimationsManager


class MainWindow(QMainWindow):
    """
    Класс для нового главного окна
    """

    def __init__(self):
        super().__init__()

        self.thread: QThread | None = None
        self.worker: PdfBuilderWorker | None = None

        self.setObjectName("MainWindow")

        self.setMinimumSize(900, 650)

        self.setWindowTitle("PDF_Maker")

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
        self.bg_path_check: str = ""

        # стандартная папка сохранения пдф фалов в результате работы функций
        self.save_folder_path: str = str(
            Path.home() / "Desktop" / "results_folder")
        self.parsing_save_folder_path: str = self.save_folder_path

        # Отдельный путь для сохранения ПДФ (без парсинга)
        self.save_folder_second_tab_path: str = str(
            Path.home() / "Desktop" / "results_folder")

        # атрибут для хранения позиции мыши(x,y), объект класса qpoint
        self.drag_position: QPoint = QPoint()

        # Главный цвет случайного изображения
        self.main_color_str: str = ""

        ui_path = Path('src/gui/ui/main-window.ui').as_posix()
        loadUi(ui_path, self)

        self.set_stylesheet_by_theme_in_settings()

        self.change_active_button_styles()
        self._update_loading_window_buttons()

        # Вкладка с настройками скрыта, открывается только с кнопки
        self.tab_widget.setTabVisible(2, False)

        self.app_name_button.clicked.connect(self.app_name_clicked)
        self.settings_button.clicked.connect(self.open_settings_tab)
        self.run_button.clicked.connect(self.run)
        self.stop_parsing_button.clicked.connect(self.stop_generation_process)
        self.stop_button.clicked.connect(self.on_stop_clicked)

        self.widget_bg_main_tab.clicked.connect(
            self.on_bg_clicked)
        self.open_folder_button.clicked.connect(
            lambda: open_parsing_pdf_folder(self))
        self.btn_choose_universal_xl.clicked.connect(
            lambda: choose_universal_excel(self))
        self.btn_choose_foreign_commission.clicked.connect(
            lambda: choose_foreign_excel(self))
        self.btn_choose_specialization_commission.clicked.connect(
            lambda: choose_specialization_excel(self))
        self.button_to_update_date.clicked.connect(
            lambda: self.update_data())
        self.button_change_save_path.clicked.connect(
            lambda: choose_parsing_save_folder(self))

        self.button_shouse_save_path_for_second_tab.clicked.connect(
            lambda: choose_save_folder_second_tab(self))
        self.button_shouse_table.clicked.connect(
            self.choose_file)
        self.button_open_folder_with_pdf.clicked.connect(
            lambda: open_pdf_folder(self))

        self.button_show_loading_window.clicked.connect(
            self.set_true_show_loading_window)
        self.button_hide_loading_window.clicked.connect(
            self.set_false_show_loading_window)
        self.choose_standard_theme_button.clicked.connect(
            lambda: self.on_button_choose_theme("standard"))
        self.choose_violet_theme_button.clicked.connect(
            lambda: self.on_button_choose_theme("violet"))
        self.choose_dark_theme_button.clicked.connect(
            lambda: self.on_button_choose_theme("dark"))
        self.shortcut_button.clicked.connect(self.get_shortcut)

        # Слайдер
        self.slider_loading_window_timer_duration.valueChanged.connect(
            lambda value: self.on_slider_changed(value))

        # Радиокнопки
        self.radio_button_1.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "history"))
        self.radio_button_2.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "foreign"))
        self.radio_button_3.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "specialization"))

        self.btn_choose_history_commission.clicked.connect(
            lambda: choose_history_excel(self))

        # Вкладки
        self.what_tab_is_show_now()
        self.tab_widget.currentChanged.connect(self.what_tab_is_show_now)

        # Установка шрифтов
        self.app_name_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 14))
        self.tab_widget.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.open_folder_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 12))
        self.label_for_radio_buttons.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 14))
        self.radio_button_1.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 12))
        self.radio_button_2.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 12))
        self.radio_button_3.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 12))
        self.input_commission.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 10))
        self.btn_choose_universal_xl.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.universal_excel_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 8))
        self.btn_choose_history_commission.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.history_xl_choused_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.btn_choose_foreign_commission.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.foreign_xl_choosed_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.btn_choose_specialization_commission.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.specialization_xl_choosed_lb.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.time_update_label.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.button_to_update_date.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.label_info_last_update_cache.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.label_commission_title.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_change_save_path.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.change_path_label.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.save_path_label.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 10))
        self.label_title_to_stop.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.second_tab_title.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 12))
        self.title_change_save_path.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 11))
        self.current_save_path_label.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 10))
        self.button_shouse_save_path_for_second_tab.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.title_choose_table_label.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 11))
        self.label_current_tabel.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_shouse_table.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.button_open_folder_with_pdf.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.label_title_stop_2.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.settings_label.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 14))
        self.param_show_loading_window.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 10))
        self.button_show_loading_window.setFont(Fonts.get_qfont(
            "JetBrains_Light", 8))
        self.button_hide_loading_window.setFont(Fonts.get_qfont(
            "JetBrains_Light", 8))
        self.param_timer_duration_loading_window.setFont(Fonts.get_qfont(
            "JetBrains_Medium", 10))
        self.indicate_loading_window_timer_duration.setFont(Fonts.get_qfont(
            "JetBrains_Light", 10))
        self.label_title_choose_theme.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.choose_standard_theme_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.choose_violet_theme_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.choose_dark_theme_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))
        self.shortcut_button.setFont(Fonts.get_qfont(
            "JetBrains_Regular", 10))

        self.stop_button_path = Path("resources/images/icons/stop_button.png")
        self.run_button_path = Path("resources/images/icons/run_button.png")
        self.settings_path = Path("resources/images/icons/settings_pycharm_icon.png")

        self.settings_button.setStyleSheet(f"""
                                   QPushButton {{
                                       background-image: url({self.settings_path.as_posix()});
                                       border: none;
                                       background-repeat: no-repeat;
                                       background-position: center;
                                       background-color: transparent;
                                       border-radius: 5px;
                                   }}
                                   QPushButton:hover {{
                                       background-color: rgba(255, 255, 255, 0.08);
                                   }}
                                   QPushButton:pressed {{
                                       background-color: rgba(255, 255, 255, 0.15);
                                   }}
                               """)
        self.run_button.setStyleSheet(f"""
                                   QPushButton {{
                                       background-image: url({self.run_button_path.as_posix()});
                                       background-repeat: no-repeat;
                                       background-position: center;
                                       border: none;
                                       background-color: transparent;
                                       border-radius: 5px;
                                   }}
                                   QPushButton:hover {{
                                       background-color: rgba(255, 255, 255, 0.08);
                                   }}
                                   QPushButton:pressed {{
                                       background-color: rgba(255, 255, 255, 0.15);
                                   }}
                               """)

        style_for_stop_button = f"""
                               QPushButton {{
                                   background-image: url({self.stop_button_path.as_posix()});
                                   background-repeat: no-repeat;
                                   background-position: center;
                                   border: none;
                                   background-color: #8A3535;
                                   border-radius: 5px;
                               }}
                               QPushButton:hover {{
                                   background-color: #B44747;
                               }}
                               QPushButton:pressed {{
                                   background-color: #7A2E2E;
                               }}
                           """

        self.stop_parsing_button.setStyleSheet(style_for_stop_button)
        self.stop_button.setStyleSheet(style_for_stop_button)

        self.slider_loading_window_timer_duration.setRange(1000, 15000)
        self.slider_loading_window_timer_duration.setValue(
            Settings.get_loading_window_timer_duration())
        self.indicate_loading_window_timer_duration.setText(
            f"{Settings.get_loading_window_timer_duration()} мс")

        # Путь к папке с изображениями для фона главного окна (основной вкладки)
        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    # Переопределённые методы родительского класса
    def keyPressEvent(self, event) -> None:
        """
        Обработка нажатий клавиш для остановки процесса

        :return: None
        """

        # Пробел - обычная остановка
        if event.key() == Qt.Key.Key_Space:
            if (self.stop_parsing_button.isVisible() and
                    self.stop_parsing_button.isEnabled()):
                self.stop_generation_process()
                event.accept()
                return

            elif (self.stop_button.isVisible() and
                  self.stop_button.isEnabled()):
                self.stop_generation_second_tab()
                event.accept()
                return

        # ESC - аварийная остановка (работает даже если кнопка скрыта)
        if event.key() == Qt.Key.Key_Escape:
            if self.stop_parsing_button.isVisible():
                Rich.warning_log("Аварийная остановка парсинга по ESC")
                self.stop_generation = True
                if self.worker is not None:
                    try:
                        self.worker.request_stop()
                    except RuntimeError:
                        self.worker = None
                self.run_button.setVisible(False)
                self.stop_parsing_button.setEnabled(False)
                event.accept()
                return
            elif self.stop_button.isVisible():
                Rich.warning_log("Аварийная остановка сборки PDF по ESC")
                self.stop_building_pdf = True
                if self.worker is not None:
                    try:
                        self.worker.request_stop()
                    except RuntimeError:
                        self.worker = None
                self.run_button.setVisible(False)
                self.stop_button.setEnabled(False)
                QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
                event.accept()
                return

        # Запуск процессов с комбинации шифт + ф9
        if (event.key() == Qt.Key.Key_F9 and
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.run()
            event.accept()
            return

        # Передаем событие дальше
        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent):
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Обработчик события нажатия кнопки мыши.

        :param event: Принимает event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).

        :return: None
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
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

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Функция, вызывающаяся при закрытии окна.

        :param event: событие закрытия окна

        :return: None
        """

        if getattr(self, "_is_closing", False):
            event.accept()
            return

        if hasattr(self, "worker") and self.worker is not None:
            try:
                self.worker.request_stop()
            except RuntimeError:
                self.worker = None

        if hasattr(self, "worker_thread") and self.worker_thread is not None:
            try:
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait(3000)
            except RuntimeError:
                pass

            self.worker_thread = None

        Rich.exit_log("Выход из приложения - закрытие главного окна")

        self._is_closing = True

        event.ignore()

        Rich.debug_log("Запуск анимации исчезновения окна")

        self.close_anim = AnimationsManager.animation_of_window_disappearing(self, 265)

    # Публичные методы
    def set_stylesheet_by_theme_in_settings(self) -> None:
        """
        Функция выбирает и подключает файл qss в соответствии с выбранной темой стилями

        :return: None
        """

        theme = Settings.get_theme_name()

        qss_path = Path(f"src/gui/styles/main-window-{theme}.qss")

        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            Rich.warning_log(f"QSS-файл не найден: {qss_path}")

    def update_data(self) -> None:
        """
        Принудительное обновление данных с сайтов.
        Вызывается по кнопке "Обновить данные".

        :return: None
        """

        Rich.print_spacer()
        Rich.simple_log("Обновление данных кодов и шифров аспирантов")

        try:
            # Обновляем текст в интерфейсе
            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText("Обновление данных...")
                QApplication.processEvents()

            # Парсим основной сайт
            Rich.debug_log("Парсинг основного сайта (tstu.ru)...")
            specialties = site_parce_main()

            # Если основной сайт не дал данных - пробуем резервный
            if not specialties:
                Rich.debug_log("Парсинг резервного сайта (dn.tstu.ru)...")
                specialties = site_parce_dn()

            if specialties:
                # Сохраняем данные (старый файл удалится)
                save_specialties_to_cache(specialties)

                # Получаем время из имени файла
                update_time = get_last_update_time()

                if hasattr(self, 'time_update_label'):
                    self.time_update_label.setText(update_time)

                if hasattr(self, 'label_for_info_update_site_paring'):
                    self.label_for_info_update_site_paring.setText(
                        "Последнее обновление данных (парсинг сайтов):"
                    )

                QMessageBox.information(
                    self,
                    "Обновление завершено",
                    f"Данные успешно обновлены!\n\n"
                    f"Загружено специальностей: {len(specialties)}\n"
                    f"Время обновления: {update_time}"
                )
                Rich.success_log(
                    f"Данные обновлены! Загружено {len(specialties)} специальностей")

            else:
                QMessageBox.warning(
                    self,
                    "Ошибка обновления",
                    "Не удалось получить данные с сайтов.\n\n"
                    "Проверьте подключение к интернету."
                )
                Rich.log_error("Не удалось получить данные с сайтов")

                if hasattr(self, 'label_for_info_update_site_paring'):
                    self.label_for_info_update_site_paring.setText(
                        "Ошибка обновления данных (проверьте интернет):"
                    )

        except Exception as e:
            Rich.log_error(f"Ошибка при обновлении данных: {e}")
            traceback.print_exc()

            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось обновить данные:\n{str(e)}"
            )

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Ошибка обновления данных:"
                )

    def load_cached_data(self) -> None:
        """
        Загружает данные из кэша (файла txt) и обновляет лейбл с временем в
        главном окне приложения.

        :return: None
        """

        files = list(ParsingDir.glob("*.txt")) if ParsingDir.exists() else []

        if files:
            filename = files[0].stem

            if hasattr(self, 'time_update_label'):
                self.time_update_label.setText(filename)

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Последнее обновление данных (парсинг сайтов):"
                )

            Rich.success_log(
                f"Загружен файл с информацией о специальностях аспирантов: {filename}")

        else:
            if hasattr(self, 'time_update_label'):
                self.time_update_label.setText("Данные не загружены")

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Данные не загружены (нажмите 'Обновить данные'):"
                )

            Rich.warning_log("Файл кэша не найден")

    def on_error(self, message: str) -> None:
        """
        Функция показывает ошибку в логе в консоли и диалогом.

        :param message: Принимает сообщение об ошибке и передаёт его диалогу и логу
        """

        Rich.log_error(message)
        QMessageBox.warning(self, "Ошибка", message)

    def on_finished(self, processed: int, output_folder: str) -> None:
        """
        Вызывается, когда worker завершил работу.

        :param processed: Принимает количество созданных пдф.
        :param output_folder: Принимает путь к папке сохранения документов

        :return: None
        """

        Rich.success_log("Сборка ПДФ завершена")
        Rich.simple_log(f"Создано PDF: {processed}")
        Rich.simple_log(f"Папка: {output_folder}")

        QMessageBox.information(
            self,
            "Сборка ПДФ завершена!",
            f"Создано PDF: {processed}\n\nДокументы сохранены в:\n{output_folder}",
            QMessageBox.StandardButton.Ok,
        )

    def on_thread_finished(self) -> None:
        """
        Сбрасывает состояния кнопок и остального UI после завершения потока в
         базовое состояние.

        :return: None
        """

        self.progress_bar.setVisible(False)
        self.stop_button.setVisible(False)
        self.run_button.setVisible(True)
        self.widget_title_stop_second.setVisible(False)
        self.stop_button.setEnabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def on_stop_clicked(self) -> None:
        """
        Функция-обработчик кнопки остановки процесса сборки пдф на второй вкладке.

        :return: None
        """

        if self.worker is not None:
            Rich.warning_log("Запрошена остановка сборки...")
            self.worker.request_stop()
            self.stop_button.setEnabled(False)

    def on_progress(self, value: int) -> None:
        """
        Функция для обновления состояния прогресс-бара, индицирующего
         прогресс сборки пдф на второй вкладке.

        :param value: Принимает значение, которое будет назначено прогресс-бару

        :return: None
        """

        self.progress_bar.setValue(value)

    def choose_file(self) -> None:
        """
        Функция для выбора файла обрабатываемой таблицы для генерации пдф.

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл Excel с данными",
            "",
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )

        if file_path:
            self.excel_file_path = file_path
            self.label_current_tabel.setText(self.excel_file_path)
            Rich.success_log(f"Выбрана таблица  с данными для сборки ПДФ: {file_path}")

    def change_active_button_styles(self) -> None:
        """
        Подсвечивает кнопку текущей темы через динамическое свойство 'active'.

        Активная кнопка получает active=True, остальные — active=False.
        Внешний вид задаётся в QSS-файле через селекторы:
            QPushButton#choose_standard_theme_button[active="true"]  { ... }
            QPushButton#choose_standard_theme_button[active="false"] { ... }
        """

        current_theme = Settings.get_theme_name()

        theme_buttons = {
            "standard": self.choose_standard_theme_button,
            "violet": self.choose_violet_theme_button,
            "dark": self.choose_dark_theme_button,
        }

        for name, btn in theme_buttons.items():
            btn.setProperty("active", name == current_theme)

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

        if current_theme not in theme_buttons:
            Rich.warning_log(
                f"Неизвестная тема '{current_theme}' — активная кнопка не подсвечена"
            )

    def open_settings_tab(self) -> None:
        """
        Функция для открытия вкладки с настройками

        :return: None
        """

        self.tab_widget.setCurrentIndex(2)

    def what_tab_is_show_now(self) -> int:
        """
        Функция для получения индекса текущей вкладки.

        :return: int - индекс открытой вкладки
        """

        tabs_name = ["Главная", "ЛР по формированию PDF", "Настройки"]

        current_index = self.tab_widget.currentIndex()

        busy = None

        if ((self.thread is not None and self.thread.isRunning()) or
                self.stop_generation or self.stop_building_pdf):
            busy = True

        if current_index == 0:
            tab_name = tabs_name[0]
            self.choose_tab = 0
            self.run_button.setVisible(not busy)

        elif current_index == 1:
            tab_name = tabs_name[1]
            self.choose_tab = 1
            self.run_button.setVisible(not busy)

        elif current_index == 2:
            tab_name = tabs_name[2]
            self.choose_tab = 2
            self.run_button.setVisible(False)

        else:
            tab_name = "неизвестно"
            self.choose_tab = -1

        Rich.print_spacer()
        Rich.debug_log(f"Открыта вкладка: {current_index} ({tab_name})")

        return current_index

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

            # Локальные цвета под текущую тему
            theme_colors = {
                "standard": {
                    "bg": "#2B2D30",
                    "dark_text": "#8F949A",
                    "light_text": "#D4E0E4",
                    "tab_hover": "#4D4E51",
                },
                "violet": {
                    "bg": "#2D1B3D",
                    "dark_text": "#B8A0C8",
                    "light_text": "#E8D5F5",
                    "tab_hover": "#6A3A89",
                },
                "dark": {
                    "bg": "#1E1E1E",
                    "dark_text": "#A0A0A0",
                    "light_text": "#E0E0E0",
                    "tab_hover": "#4A4A4A",
                },
            }

            current_theme = Settings.get_theme_name()
            colors = theme_colors.get(current_theme, theme_colors["standard"])

            local_bg = colors["bg"]
            local_dark_text = colors["dark_text"]
            local_light_text = colors["light_text"]
            local_tab_hover = colors["tab_hover"]

            self.widget_bg_main_tab.setStyleSheet(f"""
                    QPushButton#widget_bg_main_tab {{
                        background-image: url({photo_path});
                        background-position: center;
                        background-repeat: no-repeat;
                        border-radius: 10px;
                    }}
                """)

            main_color_img = get_main_color_image(photo_path)

            self.main_color_str = f"{main_color_img[0]}, {main_color_img[1]}, {main_color_img[2]}"

            self.cap_widget.setStyleSheet(f"""
                    QWidget#cap_widget {{
                        background: qlineargradient(
                            x1: 0, y1: 0,
                            x2: 1, y2: 0,
                            stop: 0 rgba({self.main_color_str}, 0.01),
                            stop: 0.1 rgba({self.main_color_str}, 0.35),
                            stop: 0.2 rgba({self.main_color_str}, 0.35),
                            stop: 0.3 rgba({self.main_color_str}, 0.01),
                            stop: 0.41 rgba(1, 1, 1, 0),
                            stop: 1 rgba(1, 1, 1, 0)
                        );
                    }}
                """)

            self.tab_widget.setStyleSheet(f"""
                    QTabWidget#tab_widget::pane {{
                        background-color: #2B2B2B;
                        border: none;
                        top: -1px;
                    }}
                    QTabWidget#tab_widget QTabBar {{
                        background-color: {local_bg};
                    }}
                    QTabWidget#tab_widget QTabBar::tab {{
                        background: transparent;
                        color: {local_dark_text};
                        padding: 10px 20px;
                        margin-right: 0px;
                        border: none;
                        border-bottom: 2px solid transparent;
                    }}
                    QTabWidget#tab_widget QTabBar::tab:selected {{
                        background: transparent;
                        color: {local_light_text};
                        border-bottom: 2px solid rgb({self.main_color_str});
                        font-weight: bold;
                    }}
                    QTabWidget#tab_widget QTabBar::tab:hover:!selected {{
                        color: {local_light_text};
                        border-bottom: 2px solid {local_tab_hover};
                    }}
                """)

            self.widget_for_title_to_stop.setStyleSheet(f"""
                    QWidget#widget_for_title_to_stop {{
                        background-color: rgba({self.main_color_str}, 0.35);
                        border-radius: 10px;
                        border: 2px dotted {local_dark_text};
                    }}
                """)

            self.widget_title_stop_second.setStyleSheet(f"""
                    QWidget#widget_title_stop_second {{
                        background-color: rgba({self.main_color_str}, 0.35);
                        border-radius: 10px;
                        border: 2px dotted {local_dark_text};
                    }}
                """)

            self.bg_path_check = f"{photo_path}"

            Rich.print_spacer()
            Rich.simple_log(f"Для фона главного окна выбрано изображение: {photo_path}")


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

    def on_semester_changed(self, checked: bool, semester: str) -> None:
        """
        Показывает нужные кнопки в зависимости от выбранного семестра
        (выбранной радиокнопки)

        :param checked: принимает имя булевого флага для проверки выбрана ли
         радиокнопка с семестрами

        :param semester: принимает строку с названием семестра, на выбор
         которого назначена радиокнопка

        :return: None.
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

    def on_button_choose_theme(self, theme_name: str) -> None:
        """
        Функция для смены темы приложения по кнопке

        :param theme_name: Принимает имя темы (для передачи этого имени
         в настройки приложения)

        :return: None. Меняет параметр имени темы в настройках приложения.
        """

        Settings.set_theme(theme_name)
        Rich.debug_log(f"Выбрана тема: {theme_name}")

        self.set_stylesheet_by_theme_in_settings()

        self.change_active_button_styles()

        self._update_loading_window_buttons()

        self.refresh_dynamic_styles()

    def refresh_dynamic_styles(self) -> None:
        """
        Пересобирает inline-стили для виджетов, которые зависят от темы
        (tab_widget, cap_widget, widget_for_title_to_stop, widget_title_stop_second),
        используя уже выбранный путь к картинке (self.bg_path_check).
        """

        if not self.bg_path_check:
            return

        theme_colors = {
            "standard": {
                "bg": "#2B2D30",
                "dark_text": "#8F949A",
                "light_text": "#D4E0E4",
                "tab_hover": "#4D4E51",
            },
            "violet": {
                "bg": "#2D1B3D",
                "dark_text": "#B8A0C8",
                "light_text": "#E8D5F5",
                "tab_hover": "#6A3A89",
            },
            "dark": {
                "bg": "#1E1E1E",
                "dark_text": "#A0A0A0",
                "light_text": "#E0E0E0",
                "tab_hover": "#4A4A4A",
            },
        }

        current_theme = Settings.get_theme_name()
        colors = theme_colors.get(current_theme, theme_colors["standard"])

        local_bg = colors["bg"]
        local_dark_text = colors["dark_text"]
        local_light_text = colors["light_text"]
        local_tab_hover = colors["tab_hover"]

        self.tab_widget.setStyleSheet(f"""
            QTabWidget#tab_widget::pane {{
                background-color: #2B2B2B;
                border: none;
                top: -1px;
            }}
            QTabWidget#tab_widget QTabBar {{
                background-color: {local_bg};
            }}
            QTabWidget#tab_widget QTabBar::tab {{
                background: transparent;
                color: {local_dark_text};
                padding: 10px 20px;
                margin-right: 0px;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabWidget#tab_widget QTabBar::tab:selected {{
                background: transparent;
                color: {local_light_text};
                border-bottom: 2px solid rgb({self.main_color_str});
                font-weight: bold;
            }}
            QTabWidget#tab_widget QTabBar::tab:hover:!selected {{
                color: {local_light_text};
                border-bottom: 2px solid {local_tab_hover};
            }}
        """)

        self.widget_for_title_to_stop.setStyleSheet(f"""
            QWidget#widget_for_title_to_stop {{
                background-color: rgba({self.main_color_str}, 0.35);
                border-radius: 10px;
                border: 2px dotted {local_dark_text};
            }}
        """)

        self.widget_title_stop_second.setStyleSheet(f"""
            QWidget#widget_title_stop_second {{
                background-color: rgba({self.main_color_str}, 0.35);
                border-radius: 10px;
                border: 2px dotted {local_dark_text};
            }}
        """)

    def on_slider_changed(self, value: int):
        """
        Функция для установления нового времени для таймера показа главного окна.
        Принимает значение от слайдера (от 1 до 15 секунд (от 1000 до 15000 мс)).

        :param value: принимает значение слайдера

        :return: None
        """

        self.indicate_loading_window_timer_duration.setText(f"{str(value)} мс")
        Settings.set_loading_window_timer_duration(value)

    def set_true_show_loading_window(self) -> None:
        """
        Функция для разрешения показа загрузочного окна (передает True флагу
        разрешения показа - в настойках). Установка стиля "скрытой" кнопки
        для кнопки "Скрывать" и установка обычного стиля для кнопки "Показывать".

        :return: None
        """

        Settings.set_flag_show_loading_window(True)
        self._update_loading_window_buttons()

    def set_false_show_loading_window(self) -> None:
        """
        Функция для запрета показа загрузочного окна (передает False флагу
        разрешения показа - в настойках). Установка стиля "скрытой" кнопки
        для кнопки "Показывать" и установка обычного стиля для кнопки "Скрывать".

        :return: None
        """

        Settings.set_flag_show_loading_window(False)
        self._update_loading_window_buttons()

    def _update_loading_window_buttons(self) -> None:
        """
        Обновляет active-свойство у кнопок «Показывать» / «Скрывать»
        и просит Qt перечитать QSS.

        Активная кнопка (та, чей флаг сейчас True) получает active=True,
        неактивная — active=False. Внешний вид задаётся в QSS:
            QPushButton#button_show_loading_window[active="true"]  { ... }
            QPushButton#button_show_loading_window[active="false"] { ... }
        """
        show_active = Settings.get_flag_show_loading_window()

        self.button_show_loading_window.setProperty("active", show_active)
        self.button_hide_loading_window.setProperty("active", not show_active)

        for btn in (self.button_show_loading_window,
                    self.button_hide_loading_window):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

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

        Rich.simple_log("Остановка процесса по запросу пользователя")
        self.stop_building_pdf = True

        if self.worker is not None:
            try:
                self.worker.request_stop()
            except RuntimeError:
                self.worker = None

        self.run_button.setVisible(False)
        self.stop_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def stop_generation_process(self) -> None:
        """
        Останавливает процесс генерации и парсинга из основной вкладки главного окна

        :return: None
        """

        Rich.simple_log("Остановка процесса по запросу пользователя")
        self.stop_generation = True

        if hasattr(self, "worker") and self.worker is not None:
            try:
                self.worker.request_stop()
            except RuntimeError:
                self.worker = None

        self.run_button.setVisible(False)
        self.stop_parsing_button.setEnabled(False)

    def run(self) -> None:
        """
        Сигнал для кнопки запуска процессов для run_button

        :return:None
        """

        self.run_button.setVisible(False)

        if self.choose_tab == 0:
            # parsing(self)
            self.start_parsing()
        elif self.choose_tab == 1:
            self.start_pdf_build()
        else:
            return

    def start_pdf_build(self) -> None:
        """
        Функция запускает сборку PDF в отдельном потоке.
        Проверяет, что выбран файл и папка сохранения.

        :return: None
        """

        self.run_button.setVisible(False)

        if self.thread is not None and self.thread.isRunning():
            Rich.warning_log("Сборка уже запущена")
            return

        if not self.excel_file_path:
            Rich.log_error("Сначала выберите файл с данными!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите файл с данными!",
                QMessageBox.StandardButton.Ok,
            )
            return

        if not self.save_folder_second_tab_path:
            Rich.log_error("Сначала выберите папку для сохранения!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите папку для сохранения!",
                QMessageBox.StandardButton.Ok,
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.run_button.setVisible(False)
        self.stop_button.setVisible(True)
        self.stop_button.setEnabled(True)
        self.widget_title_stop_second.setVisible(True)

        Rich.debug_log("load_workbook в главном потоке")
        try:
            from openpyxl import load_workbook
            test_wb = load_workbook(self.excel_file_path)
            test_wb.close()
            Rich.debug_log("load_workbook работает")

        except BaseException as e:
            import traceback
            traceback.print_exc()
            Rich.log_error(f"load_workbook не работает. ошибка: {e}")
            return

        # блокировка UI
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.progress_bar.setVisible(True)

        # Создание потока и worker
        self.thread = QThread()
        self.worker = PdfBuilderWorker(
            excel_file=self.excel_file_path,
            output_folder=self.save_folder_second_tab_path,
        )
        self.worker.moveToThread(self.thread)

        # Связывание сигналов
        self.thread.started.connect(self.worker.run)

        self.worker.progress.connect(self.on_progress)
        self.worker.status.connect(self.on_status)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)

        # завершение потока
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.on_thread_finished)

        self.thread.start()

    def start_parsing(self) -> None:
        """
        Функция для запуска процесса парсинга и сборки ПДФ с первой вкладки
        """
        # Собираем параметры из UI
        universal = self.universal_file_path
        commission = self.history_commission_path
        output = self.parsing_save_folder_path
        commission_text = self.input_commission.text().strip()

        if self.worker_thread is not None and self.worker_thread.isRunning():
            Rich.warning_log("Парсинг уже запущен")
            return

        if not universal:
            Rich.log_error("Сначала выберите универсальную таблицу для парсинга!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите универсальную таблицу для парсинга!\n\n"
                "Нажмите кнопку «Выберите таблицу для парсинга» на главной вкладке.",
                QMessageBox.StandardButton.Ok,
            )
            self.run_button.setVisible(True)
            return

        if not commission:
            Rich.log_error("Сначала выберите файл с комиссией!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите файл с комиссией!\n\n"
                "Нажмите кнопку «Выберите файл» рядом с заголовком комиссии.",
                QMessageBox.StandardButton.Ok,
            )
            self.run_button.setVisible(True)
            return

        if not output:
            Rich.log_error("Сначала выберите папку для сохранения!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите папку для сохранения!",
                QMessageBox.StandardButton.Ok,
            )
            self.run_button.setVisible(True)
            return

        if self.radio_button_1.isChecked():
            semester = 1
        elif self.radio_button_2.isChecked():
            semester = 2
        else:
            semester = 3

        self.progress_bar_parsing.setVisible(True)
        self.progress_bar_parsing.setValue(0)

        self.stop_parsing_button.setVisible(True)
        self.stop_parsing_button.setEnabled(True)

        self.widget_for_title_to_stop.setVisible(True)

        self.run_button.setVisible(False)

        # Создаём поток и воркер
        self.worker_thread = QThread()
        self.worker = PdfParseAndGenerateWorker(
            universal_excel_file_path=universal,
            doc_file_with_commission_path=commission,
            output_folder_path=output,
            commission_text=commission_text,
            selected_semester=semester,
        )
        self.worker.moveToThread(self.worker_thread)

        # Подключаем сигналы
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar_parsing.setValue)
        self.worker.status.connect(self._on_status)
        self.worker.file_done.connect(
            lambda name: Rich.success_log(f"Готов: {name}"))
        self.worker.error.connect(
            lambda msg: QMessageBox.critical(self, "Ошибка", msg))
        self.worker.finished.connect(self._on_finished)

        # Останавливаем поток после завершения
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.on_parser_thread_finished)

        # UI: блокируем кнопки
        self.run_button.setEnabled(False)
        self.stop_parsing_button.setEnabled(True)
        self.progress_bar_parsing.setValue(0)

        self.worker_thread.start()

    def on_parser_thread_finished(self) -> None:
        """
        Вызывается, когда поток парсера завершился.
        Обнуляет ссылки, чтобы не было RuntimeError.
        """

        # Обнуляем ссылку на поток
        self.worker_thread = None

        # Восстанавливаем UI (если не сделано в _on_finished)
        self.progress_bar_parsing.setVisible(False)
        self.stop_parsing_button.setVisible(False)
        self.run_button.setVisible(True)
        self.widget_for_title_to_stop.setVisible(False)
        self.stop_parsing_button.setEnabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def _on_finished(self, count: int, folder: str):
        self.progress_bar_parsing.setVisible(False)
        self.stop_parsing_button.setVisible(False)
        self.stop_parsing_button.setEnabled(True)
        self.widget_for_title_to_stop.setVisible(False)
        self.run_button.setVisible(True)
        self.run_button.setEnabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

        QMessageBox.information(
            self, "Готово",
            f"Создано PDF: {count}\n\nПапка: {folder}",
        )
        self.progress_bar_parsing.setValue(100)
        self.worker = None

    def stop_parsing(self):
        if hasattr(self, "worker") and self.worker:
            self.worker.request_stop()

    # Статические методы
    @staticmethod
    def _on_status(text: str):
        Rich.debug_log(text)


    @staticmethod
    def get_shortcut() -> None:
        """
        Функция для создания ярлыка на рабочий стол для быстрого запуска приложения
        До создания ярлыка выполняются все проверки - на наличие сборки проекта и
        на существование ярлыка (если уже есть)
        :return: None
        """

        check_build()

    @staticmethod
    def on_status(message: str) -> None:
        """
        Функция для вывода статуса операции в лог в консоль

        :param message: Принимает текст с информацией о состоянии операции,
         который передастся в лог

        :return: None
        """

        Rich.debug_log(message)

    @staticmethod
    def on_file_done(file_name: str) -> None:
        """
        Сообщает, что один PDF готов.

        :param file_name: Принимает имя файла, который только что создался

        :return: None
        """

        Rich.success_log(f"Собран ПДФ: {file_name}")

    @staticmethod
    def app_name_clicked():
        """
        Функция для перехода по ссылке на Гит с репозиторием проекта. Просто попробовать.

        :return: None
        """

        webbrowser.open("https://lab.vr-pro.ru:8514/SAPR/asp-automation/src/branch/"
                        "development")
