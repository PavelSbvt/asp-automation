from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (QPoint, QTimer, pyqtSignal, Qt, QPropertyAnimation,
                          QEasingCurve)
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect

from utils.output_rich import simple_log


class MyLoadingWindow(QWidget):
    """
    Класс загрузочного окна на PyQt6 с гиф-анимацией загрузки
    """

    closed = pyqtSignal() # как раз кастомный сигнал для закрытия окна

    def __init__(self) -> None: # конструктор класса
        """
        Инициализация загрузочного окна с гиф-анимацией.
        """

        super().__init__() # метод вызова конструктора родительского класса
        self.drag_position: QPoint = QPoint()
        # Это создан атрибут для хранения позиции мыши, объект класса qpoint.
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        #  удаление стандартной рамки окна
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # включение прозрачного фона для окна, скрывается рамка окна

        simple_log("[I] показ загрузочного окна.")

        self.loading_window = QWidget(self)
        self.loading_window.setFixedSize(600,400)
        self.loading_window.move(0,0)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(700)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)

        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        simple_log("[I] вывод сообщения о сообщения о загрузке ('Приложение загружается...')")

        self.colored_widget = QWidget(self)
        self.colored_widget.setStyleSheet("background-color: rgba(0,0,0,0.5); border-radius: 10px;")
        self.colored_widget.setFixedSize(430, 28)
        self.colored_widget.move(10,362)

        self.lb_blс_m_load = QLabel(self)
        self.lb_blс_m_load.setText("Приложение загружается, подождите, пожалуйста...")
        self.lb_blс_m_load.setStyleSheet("color: white; font-size: 16px; "
                                         "font-weight: bold;")
        self.lb_blс_m_load.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_blс_m_load.setGeometry(10, 350, 430, 50)

        self.block_shadow = QWidget(self)
        self.block_shadow.setFixedSize(250, 60)
        self.block_shadow.move(40, 15)

        self.lb_hi_prog = QLabel(self)
        self.lb_hi_prog.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_hi_prog.setGeometry(150, 100, 300, 50)

        simple_log("[I] показ гиф анимации процесса загрузки")

        path_gif_loading = Path('resources/images/gifs/loading_animation.gif')

        gif_loading = QMovie(path_gif_loading.as_posix())
        movie_widget = QLabel(self)
        movie_widget.setFixedSize(64,66)
        movie_widget.setMovie(gif_loading) # устанавливаю гиф изображение на qlabel
        gif_loading.start() # старт анимации.
        movie_widget.move(520, 320)

        self.background_window_by_time_of_day()

        simple_log("[I] запуск таймера на 3 секунды, после чего окна закроется")

        self.timer = QTimer(self) # создаю объект класса qtimer как атрибут класса
        # загрузочного окна, родитель - self, то есть само загрузочное окно
        self.timer.timeout.connect(self.start_fade_out)
        # подключение сигнала таймера к функции закрытия окна.
        self.timer.start(3000)
        # таймер сработает через 3 секунды. окно закроется через 3 секунды

        self.animation.start()

    def background_window_by_time_of_day(self) -> None:
        """
        Функция для смены фона загрузочного окна на то, что соответствует времени суток.
        :return:
        """

        current_hour = datetime.now().hour

        simple_log(f"[I] текущее время {current_hour}")

        simple_log("[I] вывод приветствия в соответствии с текущим времени")

        if 6 <= current_hour < 11:
            self.lb_hi_prog.setGeometry(290, 15, 300, 50)
            self.lb_hi_prog.setText("Доброе утро!")
            self.lb_hi_prog.setStyleSheet("color: rgb(195, 206, 53); font-size: 28px; font-weight: bold;")
            path_bg_loading = Path('resources/images/loading_window/birds_in_the_park.jpg')

        elif 11 <= current_hour < 17:
            self.lb_hi_prog.setGeometry(150, 15, 300, 50)
            self.lb_hi_prog.setText("Добрый день")
            self.lb_hi_prog.setStyleSheet("color: rgb(54, 201, 255); font-size: 28px; font-weight: bold;")
            path_bg_loading = Path('resources/images/loading_window/plane_in_the_sky.jpg')

        elif 17 <= current_hour < 21:
            self.block_shadow.setStyleSheet("background-color: rgba(0,0,0,0.5); border-radius: 10px;")
            self.lb_hi_prog.setGeometry(15, 15, 300, 50)
            self.lb_hi_prog.setText("Добрый вечер")
            self.lb_hi_prog.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
            path_bg_loading = Path('resources/images/loading_window/bird_feeder_in_the_park.jpg')

        else:
            self.lb_hi_prog.setGeometry(150, 25, 300, 50)
            self.lb_hi_prog.setText("Доброй ночи")
            self.lb_hi_prog.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
            path_bg_loading = Path('resources/images/loading_window/porshe_at_night.jpg')

        self.loading_window.setStyleSheet(
            f"background-image: url({path_bg_loading.as_posix()}); border-radius: 10px;")

    def start_fade_out(self) -> None:
        """
        Запускает анимацию исчезания окна
        """

        self.close_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.close_animation.setDuration(450)
        self.close_animation.setStartValue(1.0)
        self.close_animation.setEndValue(0.0)
        self.close_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.close_animation.finished.connect(self.closeWindow)
        self.close_animation.start()

    def closeWindow(self) -> None:
        """
        закрытие окна
        """

        self.close_animation.deleteLater()
        self.close_animation = None

        self.close()
        simple_log("[I] закрытие загрузочного окна")
        self.closed.emit()
        self.deleteLater()

    def mousePressEvent(self, event) -> None:
        """
        обработчик события нажатия кнопки мыши. self - ссылка на текущий объект,
         event - объект события, содержащий информацию о нажатии
        (какая кнопка, координаты и т.д.).
        """

        if event.button() == Qt.MouseButton.LeftButton:
            # проверка, нажата ли левая кнопка мыши. возвращает булево
            self.drag_position = event.globalPosition().toPoint()
            # сохранение координат курсора в момент нажатия мыши.
            # .toPoint() - Преобразует позицию в объект QPoint (x, y)
            event.accept() #Подтверждает, что событие обработано (не передаёт дальше)


    def mouseMoveEvent(self, event) -> None:
        """
        обработчик события движения мыши. self - ссылка на текущий объект,
         event	- объект события, содержащий информацию о движении
        (координаты, кнопки)
        """

        if event.buttons() == Qt.MouseButton.LeftButton:
            # если зажата лкм, то вернёт True
            delta = event.globalPosition().toPoint() - self.drag_position
            # вычисление смещения (дельты) для перемещения окна,
            # event.globalPosition().toPoint() - текущая позиция курсора на экране,
            # self.drag_position - позиция, где пользователь нажал ЛКМ
            # delta - хранит вычисленное смещение
            self.move(self.pos() + delta) # перемещение окна на вычисленное смещение
            self.drag_position = event.globalPosition().toPoint()
            # обновление сохранённой позиции курсора.
            event.accept() # Подтверждает, что событие обработано (не передаёт дальше)
