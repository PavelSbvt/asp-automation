from pathlib import Path

from PyQt6.QtGui import QFontDatabase, QFont

from utils.output_rich import warning_log, debug_log


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
            debug_log("Инициализация шрифтов...")

            # Добавляю новые семейства шрифтов из ресурсов проекта.
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


            self.initialized = True

            debug_log("Шрифты успешно загружены")

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
        else:
            warning_log(f"Передано неправильное имя шрифта: {font_name}")
            debug_log("Применён стандартный шрифт 'Inter'")
            return self.font_family_Inter

    def get_qfont(self, font_name: str, size: int = 10) -> QFont:
        """
        Возвращает объект QFont для указанного шрифта.

        :param font_name: Название шрифта
        :param size: Размер шрифта
        :return: QFont
        """

        # Вызов функции для инициализации шрифтов
        # В момент, когда шрифт применяется, будет инициализироваться объект класса
        self.ensure_initialized()

        family = self.get_font(font_name)

        return QFont(family, size)

fonts = FontManager()
