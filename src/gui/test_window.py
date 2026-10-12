import sys
from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi

from utils.output_rich import Rich
from gui.utils.windows_animations import AnimateManager
from gui.utils.windows_functions import (center_window,
    background_window_by_time_of_day)

from core.settings_manager import Settings
from gui.utils.styles import Style
from gui.utils.update_gui import (update_progress_bar_animation,
    loading_window_img_click, update_animation_gradient)
from gui.utils.fonts import Fonts
from utils.citations import get_citation_with_author


class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("loading_window")

        self.bg_path_check = ""

        self.close_window_animation = None

        Rich.enter_log("Показ загрузочного окна.")

        ui_path = Path('src/gui/ui/loading_window.ui').as_posix()
        loadUi(ui_path, self)

        self.set_stylesheet_by_theme_in_settings()

        self.set_text_on_size_for_labels_citations()

        # установка внутренних отступов для текста
        self.label_text.setContentsMargins(15, 0, 10, 0)
        self.lb_blc_m_load.setContentsMargins(10, 0, 0, 0)

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

        self.loading_window.clicked.connect(lambda: loading_window_img_click(self))

        # Таймер для progressbar
        self.timer_animation = QTimer()
        self.timer_animation.timeout.connect(lambda: update_progress_bar_animation(self))
        time_progress_bar_step = int(Settings.get_loading_window_timer_duration() // 130)
        self.timer_animation.start(time_progress_bar_step)

        AnimateManager.animation_appearance_window(self, duration=700)

        timer_time = Settings.get_loading_window_timer_duration() / 1000

        Rich.debug_log(f"Запуск таймера на {timer_time:.2f} сек., после чего окна закроется")

        # Основной таймер работы загрузочного окна
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_closing)
        self.timer.start(Settings.get_loading_window_timer_duration())

        # Центрирование окна
        center_window(self)

        # Таймер для запуска анимации градиента
        self.gradient_timer = QTimer()
        gradient_timer_duration = int(Settings.get_loading_window_timer_duration() * 0.005)
        self.gradient_timer.start(gradient_timer_duration)

        # Флаг окончания анимации градиента (градиент проходит по одному разу
        # сначала слева направо, а затем возвращается - нужно передать момент остановки)
        self.flag_finish_animation = False

        # Переменная для указания базовой позиции сдвига градиента.
        # Сначала ноль, потом меняется в функции анимации
        self.base_position_gradient = 0.0
        # Направление анимации - 1 = вперёд (True), -1 = ложь - назад
        self.direction_animation = 1
        # Коэффициент скорости анимации
        self.speed = 0.015

        # Переменные для сохранения в классе (чтобы менять в функциях по таймеру)
        # данных о среднем цвете изображения
        self.current_r, self.current_g, self.current_b, self.bg_path_check \
            = background_window_by_time_of_day(
            self.lb_hi_prog, self.loading_window, self.bg_path_check)

        # Позиция второй точки градиента (первой с заданным цветом)
        self.gradient_1_pos = 0.4
        # Позиция третьей точки градиента (второй с заданным цветом)
        self.gradient_2_pos = 0.55

        # переменная для задания стандартной прозрачности точек градиента
        # (сохранено в классе, чтобы менять в функции по таймеру)
        self.opacity_animation = 0.05

        # Метка индекс смены главного цвета изображения
        self.change_color = 1
        # Направление смены главного цвета изображения - для анимации
        self.change_color_direction = 1

        self.gradient_timer.timeout.connect(lambda: update_animation_gradient(self))

        self.drag_position: QPoint = QPoint()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


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

        AnimateManager.animation_disappearance_and_closing(self, duration=1000)


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoadingWindow()
    window.show()
    sys.exit(app.exec())
