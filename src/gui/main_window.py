import os
import traceback
import webbrowser
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPoint, QThread, Qt
from PyQt6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox)
from PyQt6.uic import loadUi

from core.settings_manager import Settings
from core.worker_generate_pdf import PdfBuilderWorker
from core.worker_parse_and_generate_pdf import PdfParseAndGenerateWorker
from gui.utils.fonts import Fonts
from gui.utils.windows_animations import AnimationsManager
from gui.utils.windows_functions import (
    get_main_color_image,
    get_random_image_from_folder)
from parser.sait_parsing import (
    ParsingDir,
    get_last_update_time,
    save_specialties_to_cache,
    site_parce_dn,
    site_parce_main)
from utils.create_shortcut import check_build
from utils.output_rich import Rich


class MainWindow(QMainWindow):
    """
    Класс главного окна приложения.
    """

    def __init__(self) -> None:
        """
        Создаёт главное окно, загружает интерфейс и подключает сигналы.
        """

        super().__init__()

        self.save_folder_path: str = str(
            Path.home() / "Desktop" / "results_folder")
        self.parsing_save_folder_path: str = self.save_folder_path
        self.save_folder_second_tab_path: str = str(
            Path.home() / "Desktop" / "results_folder")

        self.stop_generation: bool = False
        self.stop_building_pdf: bool = False

        self.excel_file_path: Optional[str] = None
        self.universal_file_path: Optional[str] = None
        self.history_commission_path: Optional[str] = None
        self.foreign_commission_path: Optional[str] = None
        self.specialization_commission_path: Optional[str] = None

        self.thread: Optional[QThread] = None
        self.worker: Optional[PdfBuilderWorker] = None

        self.width_now: int = 0
        self.height_now: int = 0

        self.choose_tab: int = -1

        self.bg_path_check: str = ""
        self.drag_position: QPoint = QPoint()
        self.main_color_str: str = ""

        self.setObjectName("MainWindow")
        self.setMinimumSize(900, 650)
        self.setWindowTitle("PDF_Maker")

        ui_path = Path("src/gui/ui/main-window.ui").as_posix()
        loadUi(ui_path, self)

        self.set_stylesheet_by_theme_in_settings()

        self.change_active_button_styles()
        self._update_loading_window_buttons()

        self.tab_widget.setTabVisible(2, False)

        self._connect_signals()

        self.what_tab_is_show_now()
        self.tab_widget.currentChanged.connect(self.what_tab_is_show_now)

        self._apply_fonts()

        self.stop_button_path = Path("resources/images/icons/stop_button.png")
        self.run_button_path = Path("resources/images/icons/run_button.png")
        self.settings_path = Path(
            "resources/images/icons/settings_pycharm_icon.png")

        self._apply_header_icon_styles()

        self.slider_loading_window_timer_duration.setRange(1000, 15000)
        self.slider_loading_window_timer_duration.setValue(
            Settings.get_loading_window_timer_duration())
        self.indicate_loading_window_timer_duration.setText(
            f"{Settings.get_loading_window_timer_duration()} мс")

        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Обрабатывает нажатия клавиш для остановки процессов.

        :param event: событие нажатия клавиши
        """

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

        if (event.key() == Qt.Key.Key_F9 and
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.run()
            event.accept()
            return

        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Подстраивает высоту фонового виджета под размер окна.

        :param event: событие изменения размера окна
        """

        self.width_now = self.width()
        self.height_now = self.height()

        if self.height_now <= 800:
            self.widget_bg_main_tab.setMinimumHeight(200)
        else:
            self.widget_bg_main_tab.setMinimumHeight(350)

        super().resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Запоминает позицию курсора для перетаскивания окна.

        :param event: событие нажатия кнопки мыши
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Перемещает окно при перетаскивании.

        :param event: событие движения мыши
        """

        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Останавливает воркеры и запускает анимацию закрытия окна.

        :param event: событие закрытия окна
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

        self.close_anim = AnimationsManager.animation_of_window_disappearing(
            self, 265)

    def set_stylesheet_by_theme_in_settings(self) -> None:
        """
        Подключает QSS-файл в соответствии с выбранной темой.
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
        Обновляет данные о специальностях аспирантов с сайтов.
        """

        Rich.print_spacer()
        Rich.simple_log("Обновление данных кодов и шифров аспирантов")

        try:
            if hasattr(self, "label_for_info_update_site_paring"):
                self.label_for_info_update_site_paring.setText(
                    "Обновление данных...")
                QApplication.processEvents()

            Rich.debug_log("Парсинг основного сайта (tstu.ru)...")
            specialties = site_parce_main()

            if not specialties:
                Rich.debug_log("Парсинг резервного сайта (dn.tstu.ru)...")
                specialties = site_parce_dn()

            if specialties:
                save_specialties_to_cache(specialties)

                update_time = get_last_update_time()

                if hasattr(self, "time_update_label"):
                    self.time_update_label.setText(update_time)

                if hasattr(self, "label_for_info_update_site_paring"):
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
                    f"Данные обновлены! Загружено {len(specialties)} "
                    f"специальностей")

            else:
                QMessageBox.warning(
                    self,
                    "Ошибка обновления",
                    "Не удалось получить данные с сайтов.\n\n"
                    "Проверьте подключение к интернету."
                )
                Rich.log_error("Не удалось получить данные с сайтов")

                if hasattr(self, "label_for_info_update_site_paring"):
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

            if hasattr(self, "label_for_info_update_site_paring"):
                self.label_for_info_update_site_paring.setText(
                    "Ошибка обновления данных:"
                )

    def load_cached_data(self) -> None:
        """
        Загружает данные из кэша и обновляет лейбл с временем обновления.
        """

        files = list(ParsingDir.glob("*.txt")) if ParsingDir.exists() else []

        if files:
            filename = files[0].stem

            if hasattr(self, "time_update_label"):
                self.time_update_label.setText(filename)

            if hasattr(self, "label_for_info_update_site_paring"):
                self.label_for_info_update_site_paring.setText(
                    "Последнее обновление данных (парсинг сайтов):"
                )

            Rich.success_log(
                f"Загружен файл с информацией о специальностях аспирантов: "
                f"{filename}")

        else:
            if hasattr(self, "time_update_label"):
                self.time_update_label.setText("Данные не загружены")

            if hasattr(self, "label_for_info_update_site_paring"):
                self.label_for_info_update_site_paring.setText(
                    "Данные не загружены (нажмите 'Обновить данные'):"
                )

            Rich.warning_log("Файл кэша не найден")

    def on_error(self, message: str) -> None:
        """
        Показывает сообщение об ошибке в логе и диалогом.

        :param message: текст ошибки
        """

        Rich.log_error(message)
        QMessageBox.warning(self, "Ошибка", message)

    def on_finished(self, processed: int, output_folder: str) -> None:
        """
        Вызывается после завершения сборки PDF и показывает результат.

        :param processed: количество созданных PDF
        :param output_folder: путь к папке сохранения
        """

        Rich.success_log("Сборка ПДФ завершена")
        Rich.simple_log(f"Создано PDF: {processed}")
        Rich.simple_log(f"Папка: {output_folder}")

        QMessageBox.information(
            self,
            "Сборка ПДФ завершена!",
            f"Создано PDF: {processed}\n\n"
            f"Документы сохранены в:\n{output_folder}",
            QMessageBox.StandardButton.Ok,
        )

    def on_thread_finished(self) -> None:
        """
        Сбрасывает состояние кнопок после завершения потока сборки PDF.
        """

        self.progress_bar.setVisible(False)
        self.stop_button.setVisible(False)
        self.run_button.setVisible(True)
        self.widget_title_stop_second.setVisible(False)
        self.stop_button.setEnabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def on_stop_clicked(self) -> None:
        """
        Обрабатывает нажатие кнопки остановки сборки PDF на второй вкладке.
        """

        if self.worker is not None:
            Rich.warning_log("Запрошена остановка сборки...")
            self.worker.request_stop()
            self.stop_button.setEnabled(False)

    def on_progress(self, value: int) -> None:
        """
        Обновляет прогресс-бар сборки PDF.

        :param value: новое значение прогресса
        """

        self.progress_bar.setValue(value)

    def choose_file(self) -> None:
        """
        Открывает диалог выбора Excel-файла для сборки PDF.
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
            Rich.success_log(
                f"Выбрана таблица с данными для сборки ПДФ: {file_path}")

    def choose_parsing_save_folder(self) -> None:
        """
        выбор папки сохранения для собранных пдф по напарсенным данным

        :return: None
        """

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения PDF (парсинг)",
            self.parsing_save_folder_path
        )
        if folder_path:
            self.parsing_save_folder_path = folder_path
            self.save_path_label.setText(folder_path)

    def choose_save_folder_second_tab(self) -> None:
        """
        выбор папки сохранения для собранных пдф по таблице с собранным БД

        :param self: Принимает имя родительского класса-виджета

        :return: None
        """

        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения PDF (сборка)",
            self.save_folder_second_tab_path
        )
        if folder_path:
            self.save_folder_second_tab_path = folder_path
            self.current_save_path_label.setText(folder_path)

    def open_parsing_pdf_folder(self) -> None:
        """
        Открывает папку с созданными по напарсенным данным PDF

        :return: None
        """

        folder_path = self.parsing_save_folder_path
        if not os.path.exists(folder_path):
            QMessageBox.warning(
                self,
                "Папка не найдена",
                f"Папка '{folder_path}' не существует.\n\n"
                f"Сначала создайте PDF файлы, нажав кнопку "
                f"запуска процесса на первой вкладке."
            )
            Rich.log_error("[E] ошибка с открытием папки с пдф")
            return
        os.startfile(folder_path)

    def open_pdf_folder(self) -> None:
        """
        Открывает папку с созданными по готовым данным PDF

        :return: None
        """

        folder_path = self.save_folder_second_tab_path
        if not os.path.exists(folder_path):
            QMessageBox.warning(
                self,
                "Папка не найдена",
                f"Папка '{folder_path}' не существует.\n\n"
                f"Сначала создайте PDF файлы, нажав кнопку "
                f"запуска процесса на первой вкладке."
            )
            Rich.log_error("[E] ошибка с открытием папки с пдф")
            return
        os.startfile(folder_path)

    def choose_universal_excel(self) -> None:
        """
        Функция для выбора файла "универсальной" таблицы и сохранения его
        пути в атрибут класса главного окна

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл Excel с данными",
            "",
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )

        if file_path:
            self.universal_file_path = file_path

            self.universal_excel_label.setText(f"{file_path}")

            Rich.success_log(f"Выбран файл универсальной таблицы: {file_path}")

    def choose_history_excel(self) -> None:
        """
        выбор doc файла с таблицей, содержащей информацию и комиссии по истории

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл комиссии по истории",
            "",
            "Word files (*.doc *.docx);;All files (*.*)"
        )
        if file_path:
            self.history_commission_path = file_path

            self.history_xl_choused_label.setText(file_path)

            Rich.success_log(f"Выбран файл комиссии по истории: {file_path}")

    def choose_foreign_excel(self) -> None:
        """
        выбор doc файла с таблицей, содержащей информацию и комиссии по иностранному

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл комиссии по иностранному",
            "",
            "Word files (*.doc *.docx);;All files (*.*)"
        )
        if file_path:
            self.foreign_commission_path = file_path

            self.foreign_xl_choosed_label.setText(file_path)

            Rich.success_log(f"Выбран файл комиссии по иностранному: {file_path}")

    def choose_specialization_excel(self) -> None:
        """
        выбор doc файла с таблицей, содержащей информацию и комиссии по специальности

        :return: None
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл комиссии по специальности",
            "",
            "Word files (*.doc *.docx);;All files (*.*)"
        )
        if file_path:
            self.specialization_commission_path = file_path

            self.specialization_xl_choosed_lb.setText(file_path)

            Rich.success_log(f"Выбран файл комиссии по специальности: {file_path}")

    def change_active_button_styles(self) -> None:
        """
        Подсвечивает активную кнопку темы через свойство 'active'.
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
                f"Неизвестная тема '{current_theme}' — активная кнопка "
                f"не подсвечена")

    def open_settings_tab(self) -> None:
        """
        Открывает вкладку настроек.
        """

        self.tab_widget.setCurrentIndex(2)

    def what_tab_is_show_now(self) -> int:
        """
        Возвращает индекс текущей вкладки и обновляет видимость кнопки запуска.

        :return: индекс текущей вкладки
        """

        tabs_name = ["Главная", "ЛР по формированию PDF", "Настройки"]

        current_index = self.tab_widget.currentIndex()

        busy: bool = False

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
        Устанавливает случайное фоновое изображение на главную вкладку и
        пересобирает зависящие от темы стили.

        :param folder_path: путь к папке с изображениями
        """

        old_bg_path = self.bg_path_check

        def get_random_path() -> str:
            """
            Возвращает путь к случайному изображению из указанной папки.

            :return: путь к изображению
            """

            img_path_new = get_random_image_from_folder(folder_path)
            path_bg_widget_new = Path(f"{img_path_new}")

            return path_bg_widget_new.as_posix()

        new_image_path = get_random_path()

        def use_random_photo(photo_path: str) -> None:
            """
            Применяет выбранное изображение и обновляет цвета темы.

            :param photo_path: путь к изображению
            """

            self.widget_bg_main_tab.setStyleSheet(f"""
                QPushButton#widget_bg_main_tab {{
                    background-image: url({photo_path});
                    background-position: center;
                    background-repeat: no-repeat;
                    border-radius: 10px;
                }}
            """)

            main_color_img = get_main_color_image(photo_path)
            self.main_color_str = (
                f"{main_color_img[0]}, "
                f"{main_color_img[1]}, "
                f"{main_color_img[2]}"
            )

            self.refresh_dynamic_styles()

            self.bg_path_check = f"{photo_path}"

            Rich.print_spacer()
            Rich.simple_log(
                f"Для фона главного окна выбрано изображение: {photo_path}")

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

    def refresh_dynamic_styles(self) -> None:
        """
        Пересобирает inline-стили для виджетов, зависящих от темы.
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

    def on_semester_changed(self, checked: bool, semester: str) -> None:
        """
        Показывает кнопки и лейблы для выбранного семестра.

        :param checked: состояние радиокнопки
        :param semester: название семестра
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
            self.label_commission_title.setText(
                "Таблица с комиссией по истории")
        elif semester == "foreign":
            self.btn_choose_foreign_commission.setVisible(True)
            self.foreign_xl_choosed_label.setVisible(True)
            self.label_commission_title.setText(
                "Таблица с комиссией по иностранному")
        elif semester == "specialization":
            self.btn_choose_specialization_commission.setVisible(True)
            self.specialization_xl_choosed_lb.setVisible(True)
            self.label_commission_title.setText(
                "Таблица с комиссией по специальности")

    def on_button_choose_theme(self, theme_name: str) -> None:
        """
        Меняет тему приложения по нажатию кнопки.

        :param theme_name: имя выбранной темы
        """

        Settings.set_theme(theme_name)
        Rich.debug_log(f"Выбрана тема: {theme_name}")

        self.set_stylesheet_by_theme_in_settings()
        self.change_active_button_styles()
        self._update_loading_window_buttons()
        self.refresh_dynamic_styles()

    def on_slider_changed(self, value: int) -> None:
        """
        Обновляет время показа загрузочного окна.

        :param value: новое значение таймера в миллисекундах
        """

        self.indicate_loading_window_timer_duration.setText(f"{value} мс")
        Settings.set_loading_window_timer_duration(value)

    def set_true_show_loading_window(self) -> None:
        """
        Разрешает показ загрузочного окна.
        """

        Settings.set_flag_show_loading_window(True)
        self._update_loading_window_buttons()

    def set_false_show_loading_window(self) -> None:
        """
        Запрещает показ загрузочного окна.
        """

        Settings.set_flag_show_loading_window(False)
        self._update_loading_window_buttons()

    def on_bg_clicked(self) -> None:
        """
        Меняет фоновое изображение главной вкладки на случайное.
        """

        self.get_bg_for_main_tab_widget("resources/images/for_main_window")

    def stop_generation_second_tab(self) -> None:
        """
        Останавливает сборку PDF на второй вкладке.
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
        Останавливает парсинг и сборку PDF на главной вкладке.
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
        Запускает процесс, соответствующий текущей вкладке.
        """

        self.run_button.setVisible(False)

        if self.choose_tab == 0:
            self.start_parsing()
        elif self.choose_tab == 1:
            self.start_pdf_build()
        else:
            return

    def start_pdf_build(self) -> None:
        """
        Запускает сборку PDF в отдельном потоке.
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
            traceback.print_exc()
            Rich.log_error(f"load_workbook не работает. ошибка: {e}")
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.progress_bar.setVisible(True)

        self.thread = QThread()
        self.worker = PdfBuilderWorker(
            excel_file=self.excel_file_path,
            output_folder=self.save_folder_second_tab_path,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.progress.connect(self.on_progress)
        self.worker.status.connect(self.on_status)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.on_thread_finished)

        self.thread.start()

    def start_parsing(self) -> None:
        """
        Запускает парсинг и сборку PDF с главной вкладки в отдельном потоке.
        """

        universal = self.universal_file_path
        commission = self.history_commission_path
        output = self.parsing_save_folder_path
        commission_text = self.input_commission.text().strip()

        if self.worker_thread is not None and self.worker_thread.isRunning():
            Rich.warning_log("Парсинг уже запущен")
            return

        if not universal:
            Rich.log_error(
                "Сначала выберите универсальную таблицу для парсинга!")
            QMessageBox.warning(
                self, "Предупреждение",
                "Сначала выберите универсальную таблицу для парсинга!\n\n"
                "Нажмите кнопку «Выберите таблицу для парсинга» "
                "на главной вкладке.",
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

        self.worker_thread = QThread()
        self.worker = PdfParseAndGenerateWorker(
            universal_excel_file_path=universal,
            doc_file_with_commission_path=commission,
            output_folder_path=output,
            commission_text=commission_text,
            selected_semester=semester,
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar_parsing.setValue)
        self.worker.status.connect(self._on_status)
        self.worker.file_done.connect(
            lambda name: Rich.success_log(f"Готов: {name}"))
        self.worker.error.connect(
            lambda msg: QMessageBox.critical(self, "Ошибка", msg))
        self.worker.finished.connect(self._on_finished)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.on_parser_thread_finished)

        self.run_button.setEnabled(False)
        self.stop_parsing_button.setEnabled(True)
        self.progress_bar_parsing.setValue(0)

        self.worker_thread.start()

    def on_parser_thread_finished(self) -> None:
        """
        Сбрасывает ссылку на поток и состояние кнопок после парсинга.
        """

        self.worker_thread = None

        self.progress_bar_parsing.setVisible(False)
        self.stop_parsing_button.setVisible(False)
        self.run_button.setVisible(True)
        self.widget_for_title_to_stop.setVisible(False)
        self.stop_parsing_button.setEnabled(True)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def _connect_signals(self) -> None:
        """
        Подключает сигналы виджетов к обработчикам.
        """

        self.app_name_button.clicked.connect(self.app_name_clicked)
        self.settings_button.clicked.connect(self.open_settings_tab)
        self.run_button.clicked.connect(self.run)
        self.stop_parsing_button.clicked.connect(self.stop_generation_process)
        self.stop_button.clicked.connect(self.on_stop_clicked)

        self.widget_bg_main_tab.clicked.connect(self.on_bg_clicked)
        self.open_folder_button.clicked.connect(
            self.open_parsing_pdf_folder)
        self.btn_choose_universal_xl.clicked.connect(
            self.choose_universal_excel)
        self.btn_choose_foreign_commission.clicked.connect(
            self.choose_foreign_excel)
        self.btn_choose_specialization_commission.clicked.connect(
            self.choose_specialization_excel)
        self.button_to_update_date.clicked.connect(
            lambda: self.update_data())
        self.button_change_save_path.clicked.connect(
            self.choose_parsing_save_folder)

        self.button_shouse_save_path_for_second_tab.clicked.connect(
            self.choose_save_folder_second_tab)
        self.button_shouse_table.clicked.connect(self.choose_file)
        self.button_open_folder_with_pdf.clicked.connect(
            self.open_pdf_folder)

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

        self.slider_loading_window_timer_duration.valueChanged.connect(
            lambda value: self.on_slider_changed(value))

        self.radio_button_1.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "history"))
        self.radio_button_2.toggled.connect(
            lambda checked: self.on_semester_changed(checked, "foreign"))
        self.radio_button_3.toggled.connect(
            lambda checked: self.on_semester_changed(
                checked, "specialization"))

        self.btn_choose_history_commission.clicked.connect(
            self.choose_history_excel)

    def _apply_fonts(self) -> None:
        """
        Устанавливает шрифты для виджетов окна.
        """

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

    def _apply_header_icon_styles(self) -> None:
        """
        Устанавливает inline-стили для кнопок-иконок в шапке окна.
        """

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

    def _update_loading_window_buttons(self) -> None:
        """
        Обновляет свойство 'active' у кнопок «Показывать» и «Скрывать».
        """

        show_active = Settings.get_flag_show_loading_window()

        self.button_show_loading_window.setProperty("active", show_active)
        self.button_hide_loading_window.setProperty("active", not show_active)

        for btn in (self.button_show_loading_window,
                    self.button_hide_loading_window):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def _on_finished(self, count: int, folder: str) -> None:
        """
        Скрывает элементы процесса и показывает результат парсинга.

        :param count: количество созданных PDF
        :param folder: путь к папке сохранения
        """

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

    @staticmethod
    def on_status(message: str) -> None:
        """
        Пишет сообщение о состоянии операции в лог.

        :param message: текст сообщения
        """

        Rich.debug_log(message)

    @staticmethod
    def on_file_done(file_name: str) -> None:
        """
        Сообщает, что один PDF готов.

        :param file_name: имя созданного файла
        """

        Rich.success_log(f"Собран ПДФ: {file_name}")

    @staticmethod
    def get_shortcut() -> None:
        """
        Создаёт ярлык на рабочем столе для быстрого запуска приложения.
        """

        check_build()

    @staticmethod
    def app_name_clicked() -> None:
        """
        Открывает ссылку на репозиторий проекта в браузере.
        """

        webbrowser.open(
            "https://lab.vr-pro.ru:8514/SAPR/asp-automation/src/branch/"
            "development")

    @staticmethod
    def _on_status(text: str) -> None:
        """
        Пишет статус воркера в лог.

        :param text: текст статуса
        """

        Rich.debug_log(text)
