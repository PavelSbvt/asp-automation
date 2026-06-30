from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QWidget
from datetime import datetime

width_loading = 600
height_loading = 400
class My_loading_window(QWidget):
        closed = pyqtSignal()
        def __init__(self):
            super().__init__()

            self.drag_position = QPoint()

            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            loading_window = QWidget(self)
            loading_window.setFixedSize(width_loading,height_loading)
            loading_window.setStyleSheet("background-color: white; border-radius: 10px;")
            loading_window.move(0,0)

            block_for_message_to_loading = QWidget(self)
            block_for_message_to_loading.setFixedSize(400,50)
            block_for_message_to_loading.setStyleSheet("backgrond-color:white; border-radius: 10px;")
            block_for_message_to_loading.move(100, 175)
            self.label_to_message_loading = QLabel(block_for_message_to_loading)
            self.label_to_message_loading.setText("Приложение загружается, подождите, пожалуйста...")
            self.label_to_message_loading.setStyleSheet("color: black; font-size: 14px; font: bold;")
            self.label_to_message_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_to_message_loading.setGeometry(0,0,400,50)

            block_from_label_to_welcome = QWidget(self)
            block_from_label_to_welcome.setFixedSize(300,50)
            block_from_label_to_welcome.move(150,100)
            self.label_welcome_to_program = QLabel(block_from_label_to_welcome)
            self.label_welcome_to_program.setStyleSheet("color: black; font-size:18px; font:bold;")
            self.label_welcome_to_program.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_welcome_to_program.setGeometry(0,0,300,50)
            now = datetime.now()
            current_hour = now.hour
            if current_hour >= 6:
                self.label_welcome_to_program.setText("Доброе утро!")
            if current_hour >= 11:
                self.label_welcome_to_program.setText("Добрый день!")
            if current_hour >= 17:
                self.label_welcome_to_program.setText("Добрый вечер!")
            if current_hour >= 21:
                self.label_welcome_to_program.setText("Доброй ночи!")

            gif_loading = QMovie("../images/gifs/loading_animation.gif")
            movie_widget = QLabel(self)
            movie_widget.setFixedSize(64,66)
            movie_widget.setMovie(gif_loading)
            gif_loading.start()
            movie_widget.move(268,250)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.close)
            self.timer.start(3000)

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_position = event.globalPosition().toPoint()
                event.accept()

        #
        def mouseMoveEvent(self, event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                delta = event.globalPosition().toPoint() - self.drag_position
                self.move(self.pos() + delta)
                self.drag_position = event.globalPosition().toPoint()
                event.accept()

        def closeEvent(self, event):
            super().closeEvent(event)
            self.closed.emit()

if __name__ == "__main__":
    from pyqt_general_file import main
    main()