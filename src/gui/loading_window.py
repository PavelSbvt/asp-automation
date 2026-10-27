from datetime import datetime
from pathlib import Path
from typing import Tuple

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.uic import loadUi

from core.settings_manager import Settings
from gui.utils.fonts import Fonts
from gui.utils.styles import Style
from gui.utils.windows_animations import AnimationsManager
from gui.utils.windows_functions import (
    get_main_color_image,
    get_random_image_from_folder)
from utils.citations import get_citation_with_author
from utils.output_rich import Rich


class MyLoadingWindow(QWidget):
    """
    Класс загрузочного окна
    """

    closed = pyqtSignal()

    def __init__(self) -> None:
        """
        Конструктор класса
        """
        super().__init__()

        self.setObjectName("loading_window")

        self.bg_path_check: str = ""

        Rich.enter_log("Показ загрузочного окна.")

        ui_path = Path('src/gui/ui/loading_window.ui').as_posix()
        loadUi(ui_path, self)

        self.set_stylesheet_by_theme_in_settings()

        self.set_text_on_size_for_labels_citations()

        # установка
        self.block_app_name.setFont(Fonts.get_qfont("JetBrains_Regular", 28))
        self.lb_blc_m_load.setFont(Fonts.get_qfont("JetBrains_Medium", 8))
        self.lb_hi_prog.setFont(Fonts.get_qfont("JetBrains_Medium", 20))
        self.label_text.setFont(Fonts.get_qfont("JetBrains_Medium", 11))

        # Временная установка старых стилей (через Style)
        self.label_text.setStyleSheet(f"color: {Style.light_font_color};")
        self.progress_bar.setStyleSheet(Style.progress_bar_style_blue)

        icon_path = Path("resources/images/icons/icon_pdf_maker.png")
        self.icon.setPixmap(QPixmap(icon_path.as_posix()))
        self.icon.setScaledContents(True)

        self.loading_window.clicked.connect(self.loading_window_img_click)

        # Таймер для progressbar
        self.timer_animation = QTimer()
        self.timer_animation.timeout.connect(self.update_progress_bar_animation)
        time_progress_bar_step = int(Settings.get_loading_window_timer_duration() // 130)
        self.timer_animation.start(time_progress_bar_step)

        AnimationsManager.animation_appearance_window(self, duration=700)

        timer_time = Settings.get_loading_window_timer_duration() / 1000

        Rich.debug_log(f"Запуск таймера на {timer_time:.2f} сек.,"
            f" после чего окна закроется")

        # Основной таймер работы загрузочного окна
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self.start_closing)
        self.timer.start(Settings.get_loading_window_timer_duration())

        # Центрирование окна
        self.center_window()

        # Таймер для запуска анимации градиента
        self.gradient_timer: QTimer = QTimer()
        gradient_timer_duration = int(Settings.get_loading_window_timer_duration() * 0.005)
        self.gradient_timer.start(gradient_timer_duration)

        # Флаг окончания анимации градиента (градиент проходит по одному разу
        # сначала слева направо, а затем возвращается - нужно передать момент остановки)
        self.flag_finish_animation: bool = False

        # Переменная для указания базовой позиции сдвига градиента.
        # Сначала ноль, потом меняется в функции анимации
        self.base_position_gradient: float = 0.0
        # Направление анимации - 1 = вперёд (True), -1 = ложь - назад
        self.direction_animation: int = 1
        # Коэффициент скорости анимации
        self.speed: float = 0.015

        # Переменные для сохранения в классе (чтобы менять в функциях по таймеру)
        # данных о среднем цвете изображения
        (self.current_r,
         self.current_g,
         self.current_b,
         self.bg_path_check) = MyLoadingWindow.background_window_by_time_of_day(
            self.lb_hi_prog,
            self.loading_window,
            self.bg_path_check)

        # Позиция второй точки градиента (первой с заданным цветом)
        self.gradient_1_pos: float = 0.4
        # Позиция третьей точки градиента (второй с заданным цветом)
        self.gradient_2_pos: float = 0.55

        # переменная для задания стандартной прозрачности точек градиента
        # (сохранено в классе, чтобы менять в функции по таймеру)
        self.opacity_animation: float = 0.05

        # Метка индекс смены главного цвета изображения
        self.change_color: int = 1
        # Направление смены главного цвета изображения - для анимации
        self.change_color_direction: int = 1

        self.gradient_timer.timeout.connect(self.update_animation_gradient)

        self.drag_position: QPoint = QPoint()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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

    def center_window(self) -> None:
        """
        Функция для центрирования главного окна, чтобы оно появлялось
        по центру экрана пользователя после исчезновения загрузочного окна

        :return: None
        """

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_stylesheet_by_theme_in_settings(self) -> None:
        """
        Функция выбирает и подключает файл qss в соответствии с выбранной темой стилями

        :return: None
        """

        theme = Settings.get_theme_name()

        qss_path = Path(f"src/gui/styles/loading_window_{theme}.qss")

        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            Rich.warning_log(f"QSS-файл не найден: {qss_path}")

    def set_text_on_size_for_labels_citations(self) -> None:
        """
        Функция для установки размера и шрифта для лейблов с текстом цитаты и её автора

        :return: None. в зависимости от длины текста функция установит оптимальный
         размер шрифта.
        """

        citation_text, author_text = get_citation_with_author()

        # для текста цитаты
        if len(citation_text) < 37:
            self.citation_label.setFont(Fonts.get_qfont("Playfair_Display", 18))
        elif len(citation_text) < 70:
            self.citation_label.setFont(Fonts.get_qfont("Playfair_Display", 14))
        elif len(citation_text) < 150:
            self.citation_label.setFont(Fonts.get_qfont("Playfair_Display", 12))
        else:
            self.citation_label.setFont(Fonts.get_qfont("Playfair_Display", 10))

        # для текста автора
        if len(author_text) < 40:
            self.citation_author_label.setFont(Fonts.get_qfont("Inter", 12))
        elif len(author_text) < 80:
            self.citation_author_label.setFont(Fonts.get_qfont("Inter", 10))
        elif len(author_text) > 120:
            self.citation_author_label.setFont(Fonts.get_qfont("Inter", 6))
        else:
            self.citation_author_label.setFont(Fonts.get_qfont("Inter", 8))

        # установка текста лейблам + установка внутренних отступов для текста цитаты
        self.citation_author_label.setText(author_text)
        self.label_text.setContentsMargins(10, 0, 10, 0)
        self.citation_label.setText(citation_text)

    def update_animation_gradient(self) -> None:
        """
        Функция для создания анимации виджету с градиентом на фоне 
        (виджет находится поверх основного фона окна) - плавное смещение градиента
         и уменьшение его прозрачности.

        :return: None
        """

        r, g, b = self.current_r, self.current_g, self.current_b

        self.base_position_gradient += self.speed * self.direction_animation

        if self.base_position_gradient >= 0.5:
            self.base_position_gradient = 0.5
            self.direction_animation = -1

        elif self.base_position_gradient <= 0.0:
            self.flag_finish_animation = True
            self.base_position_gradient = 0.0

        pos = self.base_position_gradient

        self.change_color += 0.5 * self.change_color_direction

        if self.change_color >= 40:
            self.change_color = 40
            self.change_color_direction = -1
        elif self.change_color <= 1:
            self.change_color = 1
            self.change_color_direction = 1

        index_changed_color = int(self.change_color * 0.5)

        change_red = min(255, r + index_changed_color)
        change_green = min(255, g + index_changed_color)
        change_blue = min(255, b + index_changed_color)

        if not self.flag_finish_animation:
            self.widget_gradient.setStyleSheet(f"""
                    #widget_gradient{{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0.5,
                        stop: 0 rgba({r}, {g}, {b}, 0.0),
                        stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                        {self.opacity_animation:.2f}),
                        stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                        {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                        {self.opacity_animation * 1:.2f}),
                        stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                        {self.opacity_animation * 4:.2f})
                    );
                    border-radius: 10px;}}
                """)
        else:
            self.widget_gradient.setStyleSheet(f"""
                    #widget_gradient{{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0.5,
                        stop: 0 rgba({r}, {g}, {b}, 0.0),
                        stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                        {self.opacity_animation * 1:.2f}),
                        stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                        {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                        {self.opacity_animation * 1:.2f}),
                        stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                        {self.opacity_animation * 4:.2f})
                    );
                    border-radius: 10px;}}
                """)
            if self.opacity_animation <= 0.1:
                self.opacity_animation += 0.0005

            if (self.gradient_1_pos + pos * 0.6) >= 0.1:
                self.gradient_1_pos -= 0.005
                self.gradient_2_pos -= 0.005
            else:
                return

    def loading_window_img_click(self) -> None:
        """
        Функция для смены фонового изображения загрузочного окна по кнопке (изображение
        является кнопкой). Ещё раз запускает функцию выбора случайного изображения на
        фон загрузочного окна и обновляет главные цвета изображения, которые передадутся
        функции обновления градиента.

        :return: None
        """

        Rich.print_spacer()
        Rich.debug_log("нажата кнопка изменения фонового изображения загрузочного окна")

        (self.current_r,
         self.current_g,
         self.current_b,
         self.bg_path_check) = MyLoadingWindow.background_window_by_time_of_day(
            self.lb_hi_prog,
            self.loading_window,
            self.bg_path_check)

        Rich.debug_log("Фоновое изображение загрузочного окна изменено, "
                       "цвета фонового градиента изменены.")

    def update_progress_bar_animation(self) -> None:
        """
        Функция для обновления прогресса прогресс-бара для имитации индикации
        вымышленного процесса

        :return: None
        """

        if self.progress_bar.value() < 100:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        else:
            self.progress_bar.setValue(100)

    def start_closing(self) -> None:
        """
        Запускает анимацию исчезновения и закрытия загрузочного окна.

        :return: None
        """

        if hasattr(self, 'gradient_timer'):
            self.gradient_timer.stop()

        if hasattr(self, 'timer_animation'):
            self.timer_animation.stop()
            self.progress_bar.setValue(100)

        AnimationsManager.animation_disappearance_and_closing(self, duration=500)

    @staticmethod
    def background_window_by_time_of_day(
            target_label: QLabel,
            target_widget: QWidget,
            check_bg_path: str) -> Tuple[int, int, int, str]:
        """
        Функция для установления текста лейбл приветствия пользователя (в соответствии
        с временем) + передача главного цвета атрибуту класса загрузочного окна

        :param target_label: Принимает имя объекта QLabel, текст которого будет изменять.

        :param target_widget: Принимает имя виджета, фон которого будет менять
         в соответствии с временем суток.

         :param check_bg_path: Принимает имя атрибута класса, в котором сохраняется путь к
          последнему выбранному фоновому изображению - чтобы избежать повторного выбора
           фонового изображения при поиске случайного изображения.

        :return: tuple[int,int,int, str] - возвращает кортеж, содержащий
         главные (усреднённые цвета случайного изображения для фона) цвета rgb и строку
         с путём случайно выбранного для фона изображения.
        """

        current_hour = datetime.now().hour

        Rich.print_spacer()
        Rich.debug_log("Вывод приветствия в соответствии с текущим времени")

        if 6 <= current_hour < 11:
            time_of_day = "утро"
            target_label.setText("Доброе утро!")
            folder_path = "resources/images/for_start_window/images/morning"

        elif 11 <= current_hour < 17:
            time_of_day = "день"
            target_label.setText("Добрый день")
            folder_path = "resources/images/for_start_window/images/day"

        elif 17 <= current_hour < 21:
            time_of_day = "вечер"
            target_label.setText("Добрый вечер")
            folder_path = "resources/images/for_start_window/images/evening"

        else:
            time_of_day = "ночь"
            target_label.setText("Доброй ночи")
            folder_path = "resources/images/for_start_window/images/night"

        Rich.debug_log(f"Текущее время {current_hour} часа ({time_of_day})")

        img_path = Path(get_random_image_from_folder(folder_path)).as_posix()

        path_bg_loading = ""
        if check_bg_path == "":
            check_bg_path = img_path
            path_bg_loading = img_path
        else:
            if img_path != check_bg_path:
                check_bg_path = img_path
                path_bg_loading = img_path
            elif img_path == check_bg_path:
                while img_path == check_bg_path:
                    img_path = Path(get_random_image_from_folder(folder_path)).as_posix()
                check_bg_path = img_path
                path_bg_loading = img_path

        Rich.debug_log(f"Выбрано случайное изображение: {img_path}")

        target_widget.setStyleSheet(
            f"background-image: url({path_bg_loading}); border-radius: 10px;")

        # главный цвет изображения
        main_color = get_main_color_image(img_path)
        target_label.setStyleSheet(f"font-weight: bold; color: rgb{main_color}")

        return main_color[0], main_color[1], main_color[2], check_bg_path
