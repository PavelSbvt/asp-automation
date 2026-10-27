from pathlib import Path

from PyQt6.QtGui import QFontDatabase, QFont

from utils.output_rich import Rich


class Fonts:
    """
    Класс для работы со шрифтами. С ленивой инициализацией (Lazy Initialization)

    Шрифты загружаются только при первом обращении к get_qfont().
    """

    # Флаг индикатор - загружены ли шрифты. Атрибут класса
    _initialized: bool = False

    # Словарь для хранения имен загруженных семейств шрифтов
    _font_families: dict = {}


    @classmethod
    def ensure_initialized(cls) -> None:
        """
        Ленивая инициализация — вызывается только при первом обращении к шрифтам
        и инициализирует их. Загружает шрифты и сохраняет их в атрибутах класса.

        :return: None
        """

        if cls._initialized:
            return

        Rich.debug_log("Инициализация шрифтов...")

        # Словарь для удобства: ключ (короткое имя) -> путь к файлу
        fonts_to_load = {
            "Inter": "resources/fonts/Inter/Inter-VariableFont_opsz,wght.ttf",

            "Inter_italic": "resources/fonts/Inter/Inter-Italic-VariableFont_opsz,wght.ttf",

            "Playfair_Display":
                "resources/fonts/Playfair_Display/PlayfairDisplay-VariableFont_wght.ttf",

            "Playfair_Display_italic":
                "resources/fonts/Playfair_Display/"
                "PlayfairDisplay-Italic-VariableFont_wght.ttf",

            "JetBrains_Regular": "resources/fonts/JetBrains/JetBrainsMonoNL-Regular.ttf",

            "JetBrains_Medium": "resources/fonts/JetBrains/JetBrainsMono-Medium.ttf",

            "JetBrains_Light": "resources/fonts/JetBrains/JetBrainsMono-Light.ttf",

            "JetBrains_LightItalic":
                "resources/fonts/JetBrains/JetBrainsMono-LightItalic.ttf"
        }

        for key, path_str in fonts_to_load.items():
            font_path = Path(path_str)
            font_id = QFontDatabase.addApplicationFont(font_path.as_posix())

            if font_id != -1:
                # Получаем имя семейства и сохраняем в словарь класса
                family_name = QFontDatabase.applicationFontFamilies(font_id)[0]
                cls._font_families[key] = family_name
            else:
                Rich.warning_log(f"Не удалось загрузить шрифт: {path_str}")

        cls._initialized = True
        Rich.debug_log("Шрифты успешно загружены")


    @classmethod
    def get_font(cls, font_name: str) -> str:
        """
        Возвращает имя семейства шрифта.

        :param font_name: Название шрифта

        :return: Имя семейства шрифта
        """

        cls.ensure_initialized()

        if font_name in cls._font_families:
            return cls._font_families[font_name]
        else:
            Rich.warning_log(f"Передано неправильное имя шрифта: {font_name}")
            Rich.debug_log("Применён стандартный шрифт 'Inter'")
            return cls._font_families.get("Inter")


    @classmethod
    def get_qfont(cls, font_name: str, size: int = 10) -> QFont:
        """
        Возвращает объект QFont для указанного шрифта.

        :param font_name: Название шрифта

        :param size: Размер шрифта. Дефолтно равен 10

        :return: объект QFont, который можно передавать PyQt для установки тексту шрифта
        """

        # Вызов функции для инициализации шрифтов
        # В момент, когда шрифт применяется, будет инициализироваться объект класса

        family = cls.get_font(font_name)
        return QFont(family, size)
