from PyQt6.QtCore import QPropertyAnimation,QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget

from utils.output_rich import Rich


class AnimationsManager:
    """
    Класс для функций анимации появления/исчезания окна
    """

    @staticmethod
    def animation_appearance_window(widget: QWidget, duration: int = 700,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic) -> QPropertyAnimation:
        """
        Анимация появления окна (увеличение прозрачности от 0 до 1)

        :param widget: Принимает имя виджета, для которого нужно сделать анимацию появления

        :param duration: Принимает значение времени анимации

        :param easing: Принимает тип кривой ускорения
        (тип кривой определят скорость изменения свойств функции - по аналогии с
        математическими функциями - линейная, кубическая и др. + специальные). Также может
        определять, когда именно это ускорение применяется - в начале или в конце анимации.

        :return: QPropertyAnimation - созданный объект анимации для управления её ходом
             (остановка, пауза, изменение параметров)
        """

        opacity_effect = widget.graphicsEffect()
        if not opacity_effect:
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

        animation_appearance = QPropertyAnimation(opacity_effect, b"opacity")
        animation_appearance.setDuration(duration)
        animation_appearance.setStartValue(0.0)
        animation_appearance.setEndValue(1.0)
        animation_appearance.setEasingCurve(easing)
        animation_appearance.start()

        widget.appearance_animation = animation_appearance

        Rich.print_spacer()
        Rich.debug_log(f"Запуск анимации появления окна "
            f"({widget.objectName() or widget.__class__.__name__})")

        return animation_appearance


    @staticmethod
    def animation_disappearance_window(widget: QWidget, duration: int = 450,
        easing: QEasingCurve.Type = QEasingCurve.Type.InCubic, callback = None) \
            -> QPropertyAnimation:
        """
        Анимация плавного исчезания окна (уменьшение прозрачности от 1 до 0)

        :param widget: Принимает имя виджета, для которого нужно сделать анимацию исчезания

        :param duration: Принимает значение времени, которое отведено анимации

        :param easing: Принимает тип кривой ускорения
        (тип кривой определят скорость изменения свойств функции - по аналогии с
        математическими функциями - линейная, кубическая и др. + специальные). Также может
        определять, когда именно это ускорение применяется - в начале или в конце анимации.

        :param callback: Функция, вызываемая после завершения анимации. Опционально.

        :return: QPropertyAnimation - созданный объект анимации для управления её ходом
             (остановка, пауза, изменение параметров)
        """

        opacity_effect = widget.graphicsEffect()
        if not opacity_effect:
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

        animation_disappearance = QPropertyAnimation(opacity_effect, b"opacity")
        animation_disappearance.setDuration(duration)
        animation_disappearance.setStartValue(1.0)
        animation_disappearance.setEndValue(0.0)
        animation_disappearance.setEasingCurve(easing)

        if callback:
            animation_disappearance.finished.connect(callback)

        animation_disappearance.start()

        Rich.print_spacer()
        Rich.debug_log(f"Запуск анимации исчезания окна "
            f"({widget.objectName() or widget.__class__.__name__})")

        return animation_disappearance


    @staticmethod
    def animation_disappearance_and_closing(widget: QWidget,
            duration: int = 450) -> None:
        """
        Функция для создания анимации плавного исчезания окна и его закрытия

        :param widget: Принимает имя виджета, который нужно закрыть с анимацией исчезания

        :param duration: Время, за которое виджет должен полностью стать прозрачным

        :return: None
        """

        def close_window() -> None:
            """
            Функция для закрытия окна (виджета, который принимает функция).

            :return: None
            """

            widget.close()
            Rich.debug_log(
                f"Закрытие окна ({widget.objectName() or widget.__class__.__name__})")

            if hasattr(widget, 'closed'):
                widget.closed.emit()

            widget.deleteLater()


        # Вызов функции исчезания виджета с последующим закрытием
        widget.close_animation = AnimationsManager.animation_disappearance_window(
            widget,
            duration=duration,
            callback=close_window
        )


    @staticmethod
    def window_appearance_animation(
            window_name: QWidget,
            duration: int = 250
            ) -> QPropertyAnimation:
        """
        Функция для анимирования появления основного окна приложения. Анимирует
        плавное появление окна.

        :param window_name: принимает ссылку объект окна
        :param duration: int - принимает время длительности анимации в миллисекундах

        :return: QPropertyAnimation
        """

        Rich.debug_log(f"Запуск анимации появления окна '{window_name.objectName()}'")

        fade_in = QPropertyAnimation(window_name, b"windowOpacity")
        fade_in.setDuration(duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_in.start()

        return fade_in


    @staticmethod
    def animation_of_window_disappearing(
            window_name: QWidget,
            duration: int = 200
            ) -> QPropertyAnimation:
        """
        Функция для анимирования исчезновения основного окна приложения.
        Анимирует плавное исчезновение окна.

        :param window_name: принимает ссылку объект окна
        :param duration: int - принимает время длительности анимации в миллисекундах

        :return: QPropertyAnimation
        """

        fade_anim = QPropertyAnimation(window_name, b"windowOpacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        fade_anim.finished.connect(window_name.close)

        fade_anim.start()

        return fade_anim
