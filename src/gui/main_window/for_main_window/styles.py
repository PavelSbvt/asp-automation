class Styles:
    """
    класс для стилей кнопок, виджетов
    """
    def __init__(self):

        self.background_color = "#2B2D30"

        self.background_dark_color = "#1E1F22"

        self.light_font_color = "#D4E0E4"

        self.dark_font_color = "#8F949A"

        self.button_blue_style = f"""
                QPushButton {{
                    background-color: #3574F0;
                    color: {self.light_font_color};
                    border-radius: 10px;
                    font-weight: bold;
                    padding: 0px 10px 0px 10px;
                }}
                QPushButton:hover {{
                    background-color: #2866e0;
                }}
                QPushButton:pressed {{
                    background-color: #2557ba;
                }}
            """
        self.radio_button_style = f"""
                QRadioButton {{
                    color: {self.light_font_color};
                    font-weight: bold;
                    spacing: 10px;
                }}
                QRadioButton:checked{{
                    color: #4ca85a;
                }}
                QRadioButton::indicator {{
                    width: 10px;
                    height: 10px;
                    border-radius: 3px;
                    border: 2px solid rgb(211,211,211);
                    background: white;
                }}
                QRadioButton::indicator:checked {{
                    width: 15px;
                    height: 15px;
                    background-color: #4ca85a;
                    border: 2px solid #27ae60;
                }}
                QRadioButton::indicator:hover {{
                    border: 2px solid green;
                }}
            """

        self.progress_bar_style_blue = """
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
            """


style = Styles()
