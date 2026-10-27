import colorsys
from pathlib import Path
from typing import Tuple
import random

from PIL import Image

from utils.output_rich import Rich


def get_main_color_image(image_path: str) -> Tuple[int, int, int]:
    """
    Функция нужна для определения главного цвета изображения на фоне виджета.
    Пока для загрузочного окна

    :param image_path: Принимает путь к изображению, средний цвет которого нужно найти

    :return: tuple[int, int, int] - Возвращает кортеж цветов rgb
    """

    try:
        img = Image.open(image_path)
        img = img.resize((1, 1))
        r, g, b = img.getpixel((0, 0))

        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        s = max(0.6, min(1.0, s * 1.6))
        v = max(0.5, min(1.0, v * 1.4))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        brightness = (r + g + b) / 3
        max_diff = max(abs(r - g), abs(r - b), abs(g - b))

        if brightness < 100 or max_diff < 50:
            Rich.debug_log(f"Цвет недостаточно яркий")

            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            s = max(0.8, min(1.0, s * 2.0))
            v = max(0.7, min(1.0, v * 1.6))
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = int(r * 255), int(g * 255), int(b * 255)

            brightness2 = (r + g + b) / 3
            max_diff2 = max(abs(r - g), abs(r - b), abs(g - b))

            if brightness2 < 80 or max_diff2 < 40:
                Rich.debug_log(
                    f"Не удалось извлечь главный цвет изображения - "
                    f"малая яркость (яркость: {brightness2:.0f})")

                return (220, 220, 220)

            Rich.debug_log(f"Усиленный цвет: rgb({r}, {g}, {b})")
            return (r, g, b)

        Rich.debug_log(f"Главный цвет изображения: rgb({r}, {g}, {b})")
        return (r, g, b)

    except Exception as e:
        Rich.log_error(f"Ошибка: {e}")
        return (220, 220, 220)


def get_random_image_from_folder(folder_path: str) -> str:
    """
    Возвращает путь к случайному изображению из указанной папки

    :param folder_path: путь к папке с изображениями

    :return: Str - путь к случайному изображению
    """
    folder = Path(folder_path)

    if not folder.exists():
        Rich.warning_log(f"Папка не найдена: {folder_path}")
        return ""

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    images = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]

    if not images:
        Rich.warning_log(f"В папке нет изображений: {folder_path}")
        return ""

    random_image = random.choice(images)

    return str(random_image)
