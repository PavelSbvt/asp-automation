import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi

from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtWidgets import (QLabel,
    QWidget, QVBoxLayout, QProgressBar, QFrame, QPushButton)
from PyQt6.QtGui import QPixmap

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

        self.bg_path_check = ""

        self.close_window_animation = None

        Rich.enter_log("Показ загрузочного окна.")

        ui_path = Path('src/gui/loading_window.ui').as_posix()

        Rich.enter_log("Показ загрузочного окна.")

        print(ui_path)
        loadUi(ui_path, self)

        self.setObjectName("loading_window")
        self.setStyleSheet("""
            #loading_window {
                background-color: #1E1E1E;
                border-radius: 10px;
            }
        """)

        self.block_app_name.setFont(Fonts.get_qfont("JetBrains_Regular", 30))
        self.lb_blc_m_load.setFont(Fonts.get_qfont("JetBrains_Medium", 8))
        self.lb_hi_prog.setFont(Fonts.get_qfont("JetBrains_Medium", 20))
        self.label_text.setStyleSheet(f"color: {Style.light_font_color};")
        self.label_text.setFont(Fonts.get_qfont("JetBrains_Medium", 11))

        self.icon_path = Path("resources/images/icons/icon_pdf_maker.png")

        if self.icon_path.exists():
            self.icon.setPixmap(QPixmap(self.icon_path.as_posix()))
            self.icon.setScaledContents(True)

        else:
            Rich.warning_log(f"Изображение иконки не найдено! путь: {self.icon_path.as_posix()}")

        self.loading_window.clicked.connect(lambda: loading_window_img_click(self))

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
