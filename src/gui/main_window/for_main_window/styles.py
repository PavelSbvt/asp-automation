from core.settings_manager import settings


class Styles:
    """
    класс для стилей кнопок, виджетов
    """
    def __init__(self):

        self.background_color = ""

        self.background_dark_color = ""

        self.light_font_color = ""

        self.dark_font_color = ""

        self.button_blue_style = ""

        self.button_hide_style = ""

        self.radio_button_style = ""

        self.progress_bar_style_blue = ""

        self.q_line_edit_style = ""

        self.q_scroll_bar_style = ""

        self.q_slider_style = ""

        self.standard_theme = [
            "#2B2D30", "#1E1F22", "#D4E0E4", "#8F949A",
            "#3574F0", "#2866e0", "#2557ba",
            "#595959", "rgb(110,110,110)", "rgb(60,60,60)",
            "#4ca85a", "rgb(211,211,211)", "#4ca85a", "#27ae60", "green",
            "#3C3F41", "#2196F3", "#42A5F5", "#1E88E5",
            "#2B2D30", "#4D4E51", "#4D4E51", "#CED0D6", "#6272a4",
            "#1E1F22", "#4D4E51", "#7A7B7E",
            "#3C3E42", "#3574F0", "#ffffff", "#3574F0",
            "#f0f8ff", "#4A8BF5", "#e6f0ff", "#2A5FD0"
        ]

        self.violet_theme = [
            "#2D1B3D", "#1A0F2A", "#E8D5F5", "#B8A0C8",
            "#7B4B9A", "#6A3A89", "#593078",
            "#4A2D5A", "#5A3A6A", "#3A204A",
            "#B87BD5", "#8B6B9A", "#7B4B9A", "#6A3A89", "#9A6BAA",
            "#3C3F41", "#7B4B9A", "#9A6BAA", "#6A3A89",
            "#2D1B3D", "#6A3A89", "#3D2B4D", "#9A6BAA", "#8A7A9A",
            "#1A0F2A", "#4A2D5A", "#6A3A89",
            "#3C3E42", "#7B4B9A", "#E8D5F5", "#7B4B9A",
            "#F5E8FF", "#9A6BAA", "#D5C0E5", "#6A3A89"
        ]

        self.dark_theme = [
            "#1E1E1E", "#0D0D0D", "#E0E0E0", "#A0A0A0",
            "#3C3C3C", "#4A4A4A", "#2E2E2E",
            "#2A2A2A", "#3A3A3A", "#1A1A1A",
            "#7A7A7A", "#555555", "#555555", "#444444", "#666666",
            "#2A2A2A", "#555555", "#777777", "#444444",
            "#1E1E1E", "#444444", "#2A2A2A", "#666666", "#555555",
            "#0D0D0D", "#333333", "#555555",
            "#2A2A2A", "#666666", "#CCCCCC", "#666666",
            "#DDDDDD", "#888888", "#BBBBBB", "#555555"
        ]

        current_theme = settings.get_theme_name()

        if current_theme == "standard":
            self.set_standard_theme()
        elif current_theme == "violet":
            self.set_violet_theme()
        else:
            self.set_dark_theme()

    def set_theme(self, list_args: list[str]) -> None:
        """
        Функция для получения цветов выбранной темы приложения.

        Индексы аргументов:
        0: background_color
        1: background_dark_color
        2: light_font_color
        3: dark_font_color
        4: active_button_background_color
        5: active_button_hover_background_color
        6: active_button_pressed_background_color
        7: hide_button_background_color
        8: hide_button_hover_background_color
        9: hide_button_pressed_background_color
        10: radio_button_checked_color
        11: radio_button_indicator_border_color
        12: radio_button_indicator_checked_background_color
        13: radio_button_indicator_checked_border_color
        14: button_indicator_hover_color
        15: progress_bar_background_color
        16: progress_bar_chunk_gradient_color_1
        17: progress_bar_chunk_gradient_color_2
        18: progress_bar_chunk_gradient_color_3
        19: q_line_edit_background_color
        20: q_line_edit_border_color
        21: q_line_edit_focus_background_color
        22: q_line_edit_focus_border_color
        23: q_line_edit_placeholder_color
        24: q_scroll_bar_vertical_background
        25: q_scroll_bar_handle_vertical_background
        26: q_scroll_bar_handle_vertical_hover_background
        27: q_slider_groove_horizontal_background
        28: q_slider_sub_page_horizontal_background
        29: q_slider_handle_horizontal_background
        30: q_slider_handle_horizontal_border_color
        31: q_slider_handle_horizontal_hover_background
        32: q_slider_handle_horizontal_hover_border_color
        33: q_slider_handle_horizontal_pressed_background
        34: q_slider_handle_horizontal_pressed_border_color

        :param list_args: Принимает список, состоящий из строк, содержащих строки
         со значениями цветов для тем

        :return: None. Только присваивает новые значения атрибуту класса стилей.
        """

        self.background_color = list_args[0]
        self.background_dark_color = list_args[1]
        self.light_font_color = list_args[2]
        self.dark_font_color = list_args[3]

        self.button_blue_style = f"""
            QPushButton {{
                background-color: {list_args[4]};
                color: {list_args[2]};
                border-radius: 10px;
                font-weight: bold;
                padding: 0px 10px 0px 10px;
            }}
            QPushButton:hover {{
                background-color: {list_args[5]};
            }}
            QPushButton:pressed {{
                background-color: {list_args[6]};
            }}
        """

        self.button_hide_style = f"""
            QPushButton {{
                background-color: {list_args[7]};
                color: {list_args[3]};
                border-radius: 10px;
                font-weight: bold;
                padding: 0px 10px 0px 10px;
            }}
            QPushButton:hover {{
                background-color: {list_args[8]};
            }}
            QPushButton:pressed {{
                background-color: {list_args[9]};
            }}
        """

        self.radio_button_style = f"""
            QRadioButton {{
                color: {list_args[2]};
                font-weight: bold;
                spacing: 10px;
            }}
            QRadioButton:checked {{
                color: {list_args[10]};
            }}
            QRadioButton::indicator {{
                width: 10px;
                height: 10px;
                border-radius: 3px;
                border: 2px solid {list_args[11]};
                background: white;
            }}
            QRadioButton::indicator:checked {{
                width: 15px;
                height: 15px;
                background-color: {list_args[12]};
                border: 2px solid {list_args[13]};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {list_args[14]};
            }}
        """

        self.progress_bar_style_blue = f"""
            QProgressBar {{
                background-color: {list_args[15]};
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
                color: white;
                font-size: 10px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {list_args[16]},
                    stop: 0.5 {list_args[17]},
                    stop: 1 {list_args[18]}
                );
                border-radius: 4px;
                margin: 1px;
            }}
        """

        self.q_line_edit_style = f"""
            QLineEdit {{
                background-color: {list_args[19]};
                color: {list_args[2]};
                border: 2px solid {list_args[20]};
                border-radius: 8px;
                padding: 5px 10px;
            }}
            QLineEdit:focus {{
                border: 2px solid {list_args[22]};
                background-color: {list_args[21]};
            }}
            QLineEdit::placeholder {{
                color: {list_args[23]};
            }}
        """

        self.q_scroll_bar_style = f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {list_args[24]};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {list_args[25]};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {list_args[26]};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """

        self.q_slider_style = f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: {list_args[27]};
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {list_args[28]};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {list_args[29]};
                width: 16px;
                height: 16px;
                margin: -6px 0px;
                border-radius: 8px;
                border: 2px solid {list_args[30]};
            }}
            QSlider::handle:horizontal:hover {{
                background: {list_args[31]};
                border-color: {list_args[32]};
                width: 18px;
                height: 18px;
                margin: -7px 0px;
            }}
            QSlider::handle:horizontal:pressed {{
                background: {list_args[33]};
                border-color: {list_args[34]};
            }}
        """

    def set_standard_theme(self) -> None:
        """
        Функция для получения цветов стандартной темы приложения.

        :return: None
        """

        self.set_theme(self.standard_theme)

    def set_violet_theme(self) -> None:
        """
        Функция для получения цветов фиолетовой темы приложения.

        :return: None
        """

        self.set_theme(self.violet_theme)

    def set_dark_theme(self) -> None:
        """
        Функция для получения цветов тёмной темы приложения.

        :return: None
        """

        self.set_theme(self.dark_theme)


style = Styles()
