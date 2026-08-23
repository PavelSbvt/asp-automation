from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import (QLabel, QWidget, QVBoxLayout, QProgressBar, QFrame)

from utils.output_rich import enter_log, debug_log
from gui.animations.animations_for_windows import (animationAppearanceWindow,
    animationDindisappearanceAndClosing)
from utils.functions_for_window_gui import (center_window,
    background_window_by_time_of_day, update_animation_gradient)
from utils.citations import get_citation_with_author
from core.settings_manager import settings
from utils.update_gui import update_progress_bar_animation



class MyLoadingWindow(QWidget):
    """
    Класс загрузочного окна на PyQt6 с гиф-анимацией загрузки
    """

    closed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # Добавляю новые семейства шрифтов из ресурсов проекта.
        front_Inter_italic_path = Path("resources/fonts/Inter/Inter-Italic-VariableFont_opsz,wght.ttf")
        font_Inter_path = Path("resources/fonts/Inter/Inter-VariableFont_opsz,wght.ttf")

        font_Inter_italic_id = QFontDatabase.addApplicationFont(front_Inter_italic_path.as_posix())
        font_Inter_id = QFontDatabase.addApplicationFont(font_Inter_path.as_posix())

        self.font_family_Inter = QFontDatabase.applicationFontFamilies(font_Inter_id)[0]
        self.font_family_Inter_italic = QFontDatabase.applicationFontFamilies(font_Inter_italic_id)[0]

        font_Playfair_Display_path = Path("resources/fonts/Playfair_Display/PlayfairDisplay-VariableFont_wght.ttf")
        font_Playfair_Display_italic_path = Path("resources/fonts/Playfair_Display/PlayfairDisplay-Italic-VariableFont_wght.ttf")

        font_Playfair_Display_id = QFontDatabase.addApplicationFont(font_Playfair_Display_path.as_posix())
        font_Playfair_Display_italic_id = QFontDatabase.addApplicationFont(font_Playfair_Display_italic_path.as_posix())

        self.font_family_Playfair_Display = QFontDatabase.applicationFontFamilies(font_Playfair_Display_id)[0]
        self.font_family_Playfair_Display_italic = QFontDatabase.applicationFontFamilies(font_Playfair_Display_italic_id)[0]

        self.drag_position: QPoint = QPoint()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.close_window_animation = None

        enter_log("Показ загрузочного окна.")

        # Виджет для фона (большой тёмный)
        self.widget_background_fill = QWidget(self)
        self.widget_background_fill.setStyleSheet("background-color: rgb(43, 43, 43);"
            " border-radius: 10px;")
        self.widget_background_fill.setFixedSize(780, 520)
        self.widget_background_fill.move(0, 0)

        # виджет с градиентом от главного цвета изображения до цвета главного фона
        self.widget_gradient = QWidget(self)
        self.widget_gradient.setFixedSize(780, 520)
        self.widget_gradient.move(0,0)

        # фото
        self.loading_window = QWidget(self)
        self.loading_window.setFixedSize(390,500)
        self.loading_window.move(380,10)

        debug_log("Вывод сообщения о сообщения о загрузке ('Приложение загружается...')")

        # Сообщение о загрузке
        self.lb_blс_m_load = QLabel(self)
        self.lb_blс_m_load.setText("Приложение загружается, подождите, пожалуйста...")
        self.lb_blс_m_load.setStyleSheet("color: rgb(169, 183, 198);")
        self.lb_blс_m_load.setFont(QFont(self.font_family_Inter, 10))
        self.lb_blс_m_load.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_blс_m_load.setGeometry(0, 490, 370, 30)
        self.lb_blс_m_load.setWordWrap(True)

        # Название приложения
        self.block_app_name = QLabel(self)
        self.block_app_name.setStyleSheet("color: white; font: bold;")
        self.block_app_name.setFont(QFont(self.font_family_Playfair_Display, 30))
        self.block_app_name.setText(f"{settings.get_app_name()}")
        self.block_app_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.block_app_name.setGeometry(10,0,370,50)

        # фон текста
        self.background_widget_text = QWidget(self)
        self.background_widget_text.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.03); border-radius: 10px;")
        self.background_widget_text.setFixedSize(360, 150)
        self.background_widget_text.move(10,60)
        self.label_text = QLabel(self.background_widget_text)
        self.label_text.setText("PDF_maker - приложение для "
            "автоматизации работы УПиАКВК.")
        self.label_text.setWordWrap(True)
        self.label_text.setFont(QFont(self.font_family_Inter, 12))
        self.label_text.setGeometry(10,50, 340, 130)
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Текст приветствия (меняется по времени суток)
        self.lb_hi_prog = QLabel(self)
        self.lb_hi_prog.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_hi_prog.setFont(QFont(self.font_family_Playfair_Display, 20))
        self.lb_hi_prog.setGeometry(10, 60, 370, 40)

        # Виджет для цитат
        self.citation = QWidget(self)
        self.citation.setFixedSize(360, 240)
        self.citation.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        """)
        self.citation.move(10, 225)

        # Лайаут
        self.citation_layout = QVBoxLayout()
        self.citation_layout.setSpacing(10)
        self.citation_layout.setContentsMargins(10, 10, 10, 10)

        citation_text, author_text = get_citation_with_author()

        # Цитата
        self.citation_label = QLabel()
        self.citation_label.setText(citation_text)
        self.citation_label.setWordWrap(True)
        self.citation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if len(citation_text) < 37:
            self.citation_label.setFont(QFont(self.font_family_Playfair_Display, 18))
        elif len(citation_text) < 70:
            self.citation_label.setFont(QFont(self.font_family_Playfair_Display, 14))
        elif len(citation_text) < 150:
            self.citation_label.setFont(QFont(self.font_family_Playfair_Display, 12))
        else:
            self.citation_label.setFont(QFont(self.font_family_Playfair_Display, 10))
        self.citation_label.setStyleSheet("""
            color: #E8E8E8;
            line-height: 1.7;
            font-weight: 300;
            padding: 5px;
        """)

        # Разделитель между текстом цитаты и её автором
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.25);
            max-height: 1px;
            margin: 2px 20px;
        """)
        separator.setFixedHeight(2)

        # Автор цитаты
        self.citation_author_label = QLabel()
        self.citation_author_label.setText(author_text)
        self.citation_author_label.setWordWrap(True)
        self.citation_author_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        if len(author_text) < 40:
            self.citation_author_label.setFont(QFont(self.font_family_Inter, 12))
        elif len(author_text) < 80:
            self.citation_author_label.setFont(QFont(self.font_family_Inter, 10))
        elif len(author_text) > 120:
            self.citation_author_label.setFont(QFont(self.font_family_Inter, 6))
        else:
            self.citation_author_label.setFont(QFont(self.font_family_Inter, 8))
        self.citation_author_label.setStyleSheet("""
            color: #42A5F5;
            font-weight: 400;
            letter-spacing: 0.3px;
            opacity: 0.9;
            padding: 7px;
        """)
        self.citation_author_label.setMinimumHeight(20)
        self.citation_author_label.setMaximumHeight(50)

        self.citation_layout.addWidget(self.citation_label)
        self.citation_layout.addWidget(separator)
        self.citation_layout.addWidget(self.citation_author_label)

        self.citation.setLayout(self.citation_layout)

        # Progressbar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3C3F41;
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
                color: white;
                font-size: 10px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2196F3,
                    stop: 0.5 #42A5F5,
                    stop: 1 #1E88E5
                );
                border-radius: 4px;
                margin: 1px;
            }
        """)
        self.progress_bar.setFixedSize(360,17)
        self.progress_bar.move(10,475)

        # Таймер для progressbar
        self.timer_animation = QTimer()
        self.timer_animation.timeout.connect(lambda: update_progress_bar_animation(self))
        self.timer_animation.start(32)

        animationAppearanceWindow(self, duration = 700)

        debug_log("Запуск таймера на 3 секунды, после чего окна закроется")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_closing)
        self.timer.start(settings.get_loading_window_timer_duration())

        center_window(self)

        # Таймер для запуска анимации градиента
        self.gradient_timer = QTimer()
        self.gradient_timer.start(30)

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
        self.current_r, self.current_g, self.current_b\
            = background_window_by_time_of_day(self.lb_hi_prog, self.loading_window)

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

    def start_closing(self) -> None:
        """
        Запускает анимацию исчезновения и закрытия загрузочного окна.

        :return: None
        """

        debug_log("Запуск анимации исчезания окна")

        if hasattr(self, 'gradient_timer'):
            self.gradient_timer.stop()

        if hasattr(self, 'timer_animation'):
            self.timer_animation.stop()

        animationDindisappearanceAndClosing(self, duration=1000)

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
