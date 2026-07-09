from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QLabel, QWidget

class MyLoadingWindow(QWidget):
    """
    Класс загрузочного окна на PyQt6 с гиф-анимацией загрузки
    """

    closed = pyqtSignal() # как раз кастомный сигнал для закрытия окна

    def __init__(self) -> None: # конструктор класса
        super().__init__() # метод вызова конструктора родительского класса

        self.drag_position = QPoint()
        # Это создан атрибут для хранения позиции мыши, объект класса qpoint.

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        #  удаление стандартной рамки окна

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # включение прозрачного фона для окна, скрывается рамка окна

        print("[I] показ загрузочного окна.")

        loading_window = QWidget(self)
        loading_window.setFixedSize(600,400) # задание фиксированного рамера виджету
        loading_window.setStyleSheet("background-color: white; border-radius: 10px;")
        loading_window.move(0,0) # абсолютное позиционирование

        print("[I] вывод сообщения о сообщения о загрузке")

        blс_mes_load = QWidget(self)
        blс_mes_load.setFixedSize(400,50) # задание размера
        blс_mes_load.setStyleSheet("background-color:white; border-radius: 10px;")
        blс_mes_load.move(100, 175)
        self.LbBlсMesLoad = QLabel(blс_mes_load)
        self.LbBlсMesLoad.setText(""
            "Приложение загружается, подождите, пожалуйста..."
        )
        self.LbBlсMesLoad.setStyleSheet("color: black; font-size: 14px; font: bold;")
        self.LbBlсMesLoad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.LbBlсMesLoad.setGeometry(0,0,400,50)

        print("[I] вывод приветствия в соответствии с текущим времени")

        block_from_label_to_welcome = QWidget(self)
        block_from_label_to_welcome.setFixedSize(300,50)
        block_from_label_to_welcome.move(150,100)
        self.LbHiProg = QLabel(block_from_label_to_welcome)
        self.LbHiProg.setStyleSheet("color: black; font-size:18px; font:bold;")
        self.LbHiProg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.LbHiProg.setGeometry(0,0,300,50)
        now = datetime.now() # присваиваю переменной текущее время системы
        current_hour = now.hour
        # так как datatime.now возвращает точное время, оставляю только часы

        print(f"[I] текущее время {current_hour}")

        if current_hour < 6 and current_hour >= 0:
            self.LbHiProg.setText("Доброй ночи!")
        if current_hour >= 6 and current_hour < 11:
            self.LbHiProg.setText("Доброе утро!")
        if current_hour >= 11  and current_hour < 17:
            self.LbHiProg.setText("Добрый день!")
        if current_hour >= 17  and current_hour < 21:
            self.LbHiProg.setText("Добрый вечер!")
        if current_hour >= 21 and current_hour < 25:
            self.LbHiProg.setText("Доброй ночи!")

        print("[I] показ гиф анимации процесса загрузки")

        path_gif_loading = str(Path(__file__).parent.parent / "resources"
                            / "images" / "gifs" / "loading_animation.gif")

        gif_loading = QMovie(path_gif_loading)
        # создаю объект класса qmovie. как аргумент передаётся путь к гиф анимации
        movie_widget = QLabel(self)
        # метод setMovie можно применить к qlabel, поэтому создал его
        movie_widget.setFixedSize(64,66)
        movie_widget.setMovie(gif_loading) # устанавливаю гиф изображение на qlabel
        gif_loading.start() # старт анимации.
        movie_widget.move(268,250)

        print("[I] запуск таймера на 3 секунды, после чего окна закроется")

        self.timer = QTimer(self) # создаю объект класса qtimer как атрибут класса
        # загрузочного окна, родитель - self, то есть само загрузочное окно
        self.timer.timeout.connect(self.close)
        # подключение сигнала таймера к функции закрытия окна.
        self.timer.start(3000)
        # таймер сработает через 3 секунды. окно закроется через 3 секунды

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

    def closeEvent(self, event) -> None:
        """
        Обработчик события закрытия окна, для текущего окна,
         event - объект события закрытия.
         """

        super().closeEvent(event)
        # вызов обработчика закрытия окна (от qwidget) из родительского класса.
        print("[I] закрытие окна")
        self.closed.emit() # отправка сигнала о том, что окно закрылось.
        # отправляет сигнал closed.
        # emit — это «испустить» или «отправить» сигнал.
