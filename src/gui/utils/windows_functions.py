from datetime import datetime
import colorsys
from pathlib import Path
import random

from PIL import Image
from PyQt6.QtWidgets import QLabel, QWidget

from utils.output_rich import Rich
from parser.sait_parsing import PARSING_DIR


def center_window(self) -> None:
    """
    Функция для центрирования главного окна, чтобы оно появлялось
    по центру экрана пользователя после исчезновения загрузочного окна

    :return: None
    """

    qr = self.frameGeometry()
    cp = self.screen().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

def get_main_color_image(image_path: str) -> tuple[int, int, int]:
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

def background_window_by_time_of_day(target_label: QLabel,
        target_widget: QWidget, check_bg_path: str) -> tuple[int,int,int, str]:
    """
    Функция для установления текста лейбл приветствия пользователя (в соответствии
    с временем) + передача главного цвета атрибуту класса загрузочного окна (именно
    для атрибутов созданы параметры return_r, return_g и return_b)

    :param target_label: Принимает имя объекта QLabel, текст которого будет изменять.

    :param target_widget: Принимает имя виджета, фон которого будет менять
     в соответствии с временем суток.

     :param check_bg_path: Принимает имя атрибута класса, в котором сохраняется путь к
      последнему выбранному фоновому изображению - чтобы избежать повторного выбора
       фонового изображения при поиске случайного изображения.

    :return: tuple[int,int,int, str] - возвращает кортеж, содержащий
     главные (усреднённые цвета случайного изображения для фона) цвета rgb и строку
     с путём случайно выбранного для фона изображения.
    """

    current_hour = datetime.now().hour
    # current_hour = 12 # - отладка и тестирование

    time_of_day = ""

    Rich.print_spacer()
    Rich.debug_log("Вывод приветствия в соответствии с текущим времени")

    if 6 <= current_hour < 11:
        time_of_day = "утро"
        target_label.setText("Доброе утро!")
        folder_path = "resources/images/for_start_window/images/morning"


    elif 11 <= current_hour < 17:
        time_of_day = "день"
        target_label.setText("Добрый день")
        folder_path = "resources/images/for_start_window/images/day"

    elif 17 <= current_hour < 21:
        time_of_day = "вечер"
        target_label.setText("Добрый вечер")
        folder_path = "resources/images/for_start_window/images/evening"

    else:
        time_of_day = "ночь"
        target_label.setText("Доброй ночи")
        folder_path = "resources/images/for_start_window/images/night"

    Rich.debug_log(f"Текущее время {current_hour} часа ({time_of_day})")

    img_path = Path(get_random_image_from_folder(folder_path)).as_posix()

    path_bg_loading = ""
    if check_bg_path == "":
        check_bg_path = img_path
        path_bg_loading = img_path
    else:
        if img_path != check_bg_path:
            check_bg_path = img_path
            path_bg_loading = img_path
        elif img_path == check_bg_path:
            while img_path == check_bg_path:
                img_path = Path(get_random_image_from_folder(folder_path)).as_posix()
            check_bg_path = img_path
            path_bg_loading = img_path

    Rich.debug_log(f"Выбрано случайное изображение: {img_path}")

    target_widget.setStyleSheet(
            f"background-image: url({path_bg_loading}); border-radius: 10px;")

    # главный цвет изображения
    main_color = get_main_color_image(img_path)
    target_label.setStyleSheet(f"font-weight: bold; color: rgb{main_color}")

    return main_color[0], main_color[1], main_color[2], check_bg_path

def load_cached_data(self) -> None:
    """
    Загружает данные из кэша (файла txt) и обновляет лейбл с временем в
    главном окне приложения.

    :return: None
    """

    files = list(PARSING_DIR.glob("*.txt")) if PARSING_DIR.exists() else []

    if files:
        filename = files[0].stem

        if hasattr(self, 'time_update_label'):
            self.time_update_label.setText(filename)

        if hasattr(self, 'label_for_info_update_site_paring'):
            self.label_for_info_update_site_paring.setText(
                "Последнее обновление данных (парсинг сайтов):"
            )

        Rich.success_log(
            f"Загружен файл с информацией о специальностях аспирантов: {filename}")

    else:
        if hasattr(self, 'time_update_label'):
            self.time_update_label.setText("Данные не загружены")

        if hasattr(self, 'label_for_info_update_site_paring'):
            self.label_for_info_update_site_paring.setText(
                "Данные не загружены (нажмите 'Обновить данные'):"
            )

        Rich.warning_log("Файл кэша не найден")
