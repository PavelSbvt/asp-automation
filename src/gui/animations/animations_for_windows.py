from PyQt6.QtCore import (QPropertyAnimation,QEasingCurve)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from utils.output_rich import debug_log


def animationAppearanceWindow(widget, duration: int = 700,
easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic) -> QPropertyAnimation:
    """
    анимация появления окна (увеличение прозрачности)
    :param widget:
    :param duration:
    :param easing:
    :return: QPropertyAnimation
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

    return animation_appearance

def animationDisappearanceWindow(widget, duration: int = 450,
easing: QEasingCurve.Type = QEasingCurve.Type.InCubic, callback=None) -> QPropertyAnimation:
    """
    анимация плавного исчезания окна (уменьшение прозрачности)
    :param widget:
    :param duration:
    :param easing:
    :param callback:
    :return: QPropertyAnimation
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

    return animation_disappearance

def animationDindisappearanceAndClosing(widget, duration: int = 450) -> None:
    """
    функция для создания анимации плавного исчезания окна и его закрытия
    :param widget:
    :param duration:
    :return: None
    """

    def closeWindow():
        widget.close()
        debug_log("[I] закрытие загрузочного окна")
        if hasattr(widget, 'closed'):
            widget.closed.emit()
        widget.deleteLater()

    widget.close_animation = animationDisappearanceWindow(
        widget,
        duration=duration,
        callback=closeWindow
    )
