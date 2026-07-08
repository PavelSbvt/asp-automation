from PyQt6.QtWidgets import QLabel # Импорт класса qlabel из pyqt6
from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt # Импорт классов qpoint (для перетаскивания окна, так как оно кастомное, нужен был "драг поинт" - для хранения координат при перетаскивании окон (окна без рамки)),
# qtimer, pyqtsignal (для создания своего сигнала - в моём файле для создания согнала закрытия загрузочного экрана),
# qt (константы: типы окон, выравнивание, курсоры и др.) из pyqt6
from PyQt6.QtGui import QMovie # класс из pyqt6 для показа гиф-анимации
from PyQt6.QtWidgets import QWidget # базовый класс для виджетов
from datetime import datetime # питоновский модуль для работы со временем и датой
from pathlib import Path

class My_loading_window(QWidget): # класс загрузочного окна
        closed = pyqtSignal() # как раз кастомный сигнал для закрытия окна (здесь инициализируется)
        def __init__(self): # конструктор
            super().__init__() # метод вызова конструктора родительского класса (можно берём его методы-функции и остальное)

            self.drag_position = QPoint() # Это создан атрибут для хранения позиции мыши, это будет объект класса qpoint. для начала точка будет иметь координаты 0.0

            self.setWindowFlag(Qt.WindowType.FramelessWindowHint) #  удаление стандартной рамки окна (заголовок, кнопки свернуть, развернуть, закрыть)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # включение прозрачного фона для окна, скрывается рамка окна

            print("[I] показ загрузочного окна.")

            loading_window = QWidget(self) # первый виджет. первым появится, имеет размер всего окна загрузки, используется для фона загрузочного окна
            loading_window.setFixedSize(600,400) # задание фиксированного рамера виджету
            loading_window.setStyleSheet("background-color: white; border-radius: 10px;") # стиль через qss
            loading_window.move(0,0) # абсолютное позиционирование

            print("[I] вывод сообщения о сообщения о загрузке")

            block_for_message_to_loading = QWidget(self)  # создание виджета для сообщения о загрузке программы. создан как родительский виджет - главному окну
            block_for_message_to_loading.setFixedSize(400,50) # задание размера
            block_for_message_to_loading.setStyleSheet("background-color:white; border-radius: 10px;") # задание стиля
            block_for_message_to_loading.move(100, 175) # тут, как и в остальных файлах программы использую абсолютное позиционирование
            self.label_to_message_loading = QLabel(block_for_message_to_loading) # делаю атрибутом класса, лабел для надписи, как объект qlabel, родитель - блок для надписи о загрузке программы
            self.label_to_message_loading.setText("Приложение загружается, подождите, пожалуйста...") # установка текста лейблу
            self.label_to_message_loading.setStyleSheet("color: black; font-size: 14px; font: bold;") # установка стиля для qlabel
            self.label_to_message_loading.setAlignment(Qt.AlignmentFlag.AlignCenter) # выравнивание текста лайбла по центру
            self.label_to_message_loading.setGeometry(0,0,400,50) # установка позиции и размера виджета. позииция относительно родителя

            print("[I] вывод приветствия в соответствии с текущим времени")

            block_from_label_to_welcome = QWidget(self)
            block_from_label_to_welcome.setFixedSize(300,50)
            block_from_label_to_welcome.move(150,100)
            self.label_welcome_to_program = QLabel(block_from_label_to_welcome)
            self.label_welcome_to_program.setStyleSheet("color: black; font-size:18px; font:bold;")
            self.label_welcome_to_program.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_welcome_to_program.setGeometry(0,0,300,50)
            now = datetime.now() # присваиваю переменной текущее время системы
            current_hour = now.hour # так как datatime.now возвращает точное время, отсекаю всё и оставляю только часы
            print(f"[I] текущее время {current_hour}")
            if current_hour < 6 and current_hour >= 0:
                self.label_welcome_to_program.setText("Доброй ночи!")
            if current_hour >= 6 and current_hour < 11:
                self.label_welcome_to_program.setText("Доброе утро!")
            if current_hour >= 11  and current_hour < 17:
                self.label_welcome_to_program.setText("Добрый день!")
            if current_hour >= 17  and current_hour < 21:
                self.label_welcome_to_program.setText("Добрый вечер!")
            if current_hour >= 21 and current_hour < 25:
                self.label_welcome_to_program.setText("Доброй ночи!")

            print("[I] показ гиф анимации процесса загрузки")

            path_gif_loading = str(Path(__file__).parent.parent / "images" / "gifs" / "loading_animation.gif")
            gif_loading = QMovie(path_gif_loading) # создаю объект класса qmovie. как аргумент передаётся путь к гиф анимации
            movie_widget = QLabel(self) # метод setMovie можно применить к qlabel, поэтому создал его
            movie_widget.setFixedSize(64,66)
            movie_widget.setMovie(gif_loading) # устанавливаю гиф изображение на qlabel
            gif_loading.start() # старт анимации.
            movie_widget.move(268,250)

            print("[I] запуск таймера на 3 секунды, после чего окна закроется")

            self.timer = QTimer(self) # создаю объект класса qtimer как атрибут класса загрузочного окна, родитель - self, то есть само загрузочное окно
            self.timer.timeout.connect(self.close) # подключение сигнала таймера к функции закрытия окна.
            self.timer.start(3000) # таймер сработает через 3 секунды. окно закроется через 3 секунды

        def mousePressEvent(self, event): # обработчик события нажатия кнопки мыши. self - ссылка на текущий объект, event - объект события, содержащий информацию о нажатии (какая кнопка, координаты и т.д.)
            if event.button() == Qt.MouseButton.LeftButton: # проверка, нажата ли левая кнопка мыши. возвращает булево
                self.drag_position = event.globalPosition().toPoint() # сохранение координат курсора в момент нажатия мыши.
                # .toPoint() - Преобразует позицию в объект QPoint (целочисленные координаты x, y)
                event.accept() # Подтверждает, что событие обработано (не передаёт дальше)

        #
        def mouseMoveEvent(self, event): # обработчик события движения мыши. self - ссылка на текущий объект, event	- объект события, содержащий информацию о движении (координаты, кнопки)
            if event.buttons() == Qt.MouseButton.LeftButton: # если зажата лкм, то вернёт True
                delta = event.globalPosition().toPoint() - self.drag_position # вычисление смещения (дельты) для перемещения окна,
                # event.globalPosition().toPoint() - текущая позиция курсора на экране,
                # self.drag_position - позиция, где пользователь нажал ЛКМ
                # delta - хранит вычисленное смещение
                self.move(self.pos() + delta) # перемещение окна на вычисленное смещение
                self.drag_position = event.globalPosition().toPoint() # обновление сохранённой позиции курсора.
                event.accept() # Подтверждает, что событие обработано (не передаёт дальше)

        def closeEvent(self, event): # обработчик события закрытия окна, для текущего окна, event - объект события закрытия
            super().closeEvent(event) # вызов обработчика закрытия окна (от qwidget) из родительского класса.
            print("[I] закрытие окна")
            self.closed.emit() # отправка сигнала о том, что окно закрылось. отправляет сигнал closed.
            # emit — это «испустить» или «отправить» сигнал.
