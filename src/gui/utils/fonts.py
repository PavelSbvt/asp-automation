from pathlib import Path

from PyQt6.QtGui import QFontDatabase, QFont

from utils.output_rich import Rich


class FontManager:
    """
    Класс для работы со шрифтами. С ленивой инициализацией (Lazy Initialization)

    Шрифты загружаются только при первом обращении к get_qfont().
    """

    # Флаг индикатор - загружены ли шрифты.
    initialized = False

    def ensure_initialized(self) -> None:
        """
        Ленивая инициализация — вызывается только при первом обращении к шрифтам
        и инициализирует их. Загружает шрифты и сохраняет их в атрибутах класса

        :return: None
        """

        if self.initialized:
            return

        else:
            Rich.debug_log("Инициализация шрифтов...")

            # Добавляю новые семейства шрифтов из ресурсов проекта.

            # Inter и Inter italic
            font_Inter_italic_path = Path("resources/fonts/Inter/"
                "Inter-Italic-VariableFont_opsz,wght.ttf")
            font_Inter_path = Path("resources/fonts/Inter/"
                                   "Inter-VariableFont_opsz,wght.ttf")

            font_Inter_italic_id = (
                QFontDatabase.addApplicationFont(font_Inter_italic_path.as_posix()))
            font_Inter_id = QFontDatabase.addApplicationFont(font_Inter_path.as_posix())

            self.font_family_Inter = (
                QFontDatabase.applicationFontFamilies(font_Inter_id))[0]
            self.font_family_Inter_italic = (
                QFontDatabase.applicationFontFamilies(font_Inter_italic_id))[0]

            # Playfair_Display и Playfair_Display italic
            font_Playfair_Display_path = (
                Path("resources/fonts/Playfair_Display/"
                     "PlayfairDisplay-VariableFont_wght.ttf"))
            font_Playfair_Display_italic_path = (
                Path("resources/fonts/Playfair_Display/"
                     "PlayfairDisplay-Italic-VariableFont_wght.ttf"))

            font_Playfair_Display_id = (
                QFontDatabase.addApplicationFont(font_Playfair_Display_path.as_posix()))
            font_Playfair_Display_italic_id = (
                QFontDatabase.addApplicationFont(
                    font_Playfair_Display_italic_path.as_posix()))

            self.font_family_Playfair_Display = (
                QFontDatabase.applicationFontFamilies(font_Playfair_Display_id))[0]
            self.font_family_Playfair_Display_italic = (
                QFontDatabase.applicationFontFamilies(
                    font_Playfair_Display_italic_id))[0]

            # JetBrainsMono Regular
            font_JetBrains_Regular_path = Path("resources/fonts/JetBrains/"
                                          "JetBrainsMonoNL-Regular.ttf")
            font_JetBrains_Regular_id = (
                QFontDatabase.addApplicationFont(font_JetBrains_Regular_path.as_posix()))
            self.font_JetBrains_Regular = (
                QFontDatabase.applicationFontFamilies(font_JetBrains_Regular_id))[0]

            # JetBrainsMono Medium
            font_JetBrainsMono_Medium_path = Path("resources/fonts/JetBrains/"
                                          "JetBrainsMono-Medium.ttf")
            font_JetBrainsMono_Medium_id = (
                QFontDatabase.addApplicationFont(font_JetBrainsMono_Medium_path.as_posix()))
            self.font_JetBrainsMono_Medium = (
                QFontDatabase.applicationFontFamilies(font_JetBrainsMono_Medium_id))[0]

            # JetBrainsMono Light
            font_JetBrainsMono_Light_path = Path("resources/fonts/JetBrains/"
                                                  "JetBrainsMono-Light.ttf")
            font_JetBrainsMono_Light_id = (
                QFontDatabase.addApplicationFont(font_JetBrainsMono_Light_path.as_posix()))
            self.font_JetBrainsMono_Light = (
                QFontDatabase.applicationFontFamilies(font_JetBrainsMono_Light_id))[0]

            # JetBrainsMono LightItalic
            font_JetBrainsMono_LightItalic_path = Path("resources/fonts/JetBrains/"
                                                 "JetBrainsMono-Light.ttf")
            font_JetBrainsMono_LightItalic_id = (
                QFontDatabase.addApplicationFont(font_JetBrainsMono_LightItalic_path.as_posix()))
            self.font_JetBrainsMono_LightItalic = (
                QFontDatabase.applicationFontFamilies(font_JetBrainsMono_LightItalic_id))[0]


            self.initialized = True

            Rich.debug_log("Шрифты успешно загружены")

    def get_font(self, font_name: str) -> str:
        """
        Возвращает имя семейства шрифта.

        :param font_name: Название шрифта

        :return: Имя семейства шрифта
        """

        if font_name == "Inter":
            return self.font_family_Inter
        elif font_name == "Playfair_Display":
            return self.font_family_Playfair_Display
        elif font_name == "JetBrains_Regular":
            return self.font_JetBrains_Regular
        elif font_name == "JetBrains_Medium":
            return self.font_JetBrainsMono_Medium
        elif font_name == "JetBrains_Light":
            return self.font_JetBrainsMono_Light
        elif font_name == "JetBrains_LightItalic":
            return self.font_JetBrainsMono_LightItalic
        else:
            Rich.warning_log(f"Передано неправильное имя шрифта: {font_name}")
            Rich.debug_log("Применён стандартный шрифт 'Inter'")
            return self.font_family_Inter

    def get_qfont(self, font_name: str, size: int = 10) -> QFont:
        """
        Возвращает объект QFont для указанного шрифта.

        :param font_name: Название шрифта

        :param size: Размер шрифта. Дефолтно равен 10

        :return: объект QFont, который можно передавать PyQt для установки тексту шрифта
        """

        # Вызов функции для инициализации шрифтов
        # В момент, когда шрифт применяется, будет инициализироваться объект класса
        self.ensure_initialized()

        family = self.get_font(font_name)

        return QFont(family, size)

Fonts = FontManager()
