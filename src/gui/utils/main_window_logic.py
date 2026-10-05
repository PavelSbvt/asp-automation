from pathlib import Path
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from core.settings_manager import Settings
from core.parsing_and_build_pdf import parsing
from utils.output_rich import Rich
from gui.utils.styles import Style
from gui.utils.windows_functions import (
    get_random_image_from_folder, get_main_color_image)
from gui.utils.update_gui import set_styles


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

    tab_name = ""

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

        self.widget_bg_main_tab.setStyleSheet(
            f"background-image: url({photo_path});"
            f" background-position: center;"
            f" background-repeat: no-repeat;"
            f"border-radius: 10px;"
        )

        main_color_img = get_main_color_image(photo_path)

        self.main_color_str = f"{main_color_img[0]}, {main_color_img[1]}, {main_color_img[2]}"

        self.cap_widget.setStyleSheet(
            f"""
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
            """
        )

        self.tab_widget.setStyleSheet(f"""
               QTabWidget::pane {{
                   background-color: #2B2B2B;
                   border: none;
                   top: -1px;
               }}
               QTabBar {{
                   background-color: {Style.background_color};
               }}
               QTabBar::tab {{
                   background: transparent;
                   color: {Style.dark_font_color};
                   padding: 10px 20px;
                   margin-right: 0px;
                   border: none;
                   border-bottom: 2px solid transparent;
               }}
               QTabBar::tab:selected {{
                   background: transparent;
                   color: {Style.light_font_color};
                   border-bottom: 2px solid rgb({self.main_color_str});
                   font-weight: bold;
               }}            
               QTabBar::tab:hover:!selected {{
                   color: {Style.light_font_color};
                   border-bottom: 2px solid #4D4E51;
               }}
           """)

        self.widget_for_title_to_stop.setStyleSheet(
            f"background-color: rgba({self.main_color_str}, 0.35);"
            f" border-radius: 10px;"
            f"border: 2px dotted {Style.dark_font_color};")

        self.widget_title_stop_second.setStyleSheet(
            f"background-color: rgba({self.main_color_str}, 0.35);"
            f" border-radius: 10px;"
            f"border: 2px dotted {Style.dark_font_color};")

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


def app_name_clicked():
    """
    Функция для перехода по ссылке на Гит с репозиторием проекта. Просто попробовать.

    :return: None
    """

    webbrowser.open("https://lab.vr-pro.ru:8514/SAPR/asp-automation/src/branch/"
                    "development")


def on_button_choose_theme(self, theme_name: str) -> None:
    """
    Функция для смены темы приложения по кнопке

    :param theme_name: Принимает имя темы (для передачи этого имени
     в настройки приложения)

    :return: None. Меняет параметр имени темы в настройках приложения.
    """

    Settings.set_theme(theme_name)
    Rich.debug_log(f"Выбрана тема: {theme_name}")

    set_styles(self)

    self.change_active_button_styles()


def on_slider_changed(self, value):
    """
    Функция для установления нового времени для таймера показа главного окна.
    Принимает значение от слайдера (от 1 до 15 секунд (от 1000 до 15000 мс)).

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
    self.button_show_loading_window.setStyleSheet(Style.button_blue_style)
    self.button_hide_loading_window.setStyleSheet(Style.button_hide_style)


def set_false_show_loading_window(self) -> None:
    """
    Функция для запрета показа загрузочного окна (передает False флагу
    разрешения показа - в настойках). Установка стиля "скрытой" кнопки
    для кнопки "Показывать" и установка обычного стиля для кнопки "Скрывать".

    :return: None
    """

    Settings.set_flag_show_loading_window(False)
    self.button_show_loading_window.setStyleSheet(Style.button_hide_style)
    self.button_hide_loading_window.setStyleSheet(Style.button_blue_style)


def on_bg_clicked(self) -> None:
    """
    Функция для установления случайного изображения на фон
    виджета для главной вкладки

    :return: None
    """

    get_bg_for_main_tab_widget(self, "resources/images/for_main_window")


def stop_generation_second_tab(self) -> None:
    """
    Останавливает процесс генерации пдф из второй вкладки главного окна

    :return: None
    """

    Rich.simple_log("Остановка процесса по запросу пользователя")
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

    Rich.simple_log("Остановка процесса по запросу пользователя")
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

    self.run_button.setVisible(False)

    if self.choose_tab == 0:
        parsing(self)
    elif self.choose_tab == 1:
        self.start_pdf_build()
    else:
        return
