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

        self.button_hide_style = f"""
                        QPushButton {{
                            background-color: #595959;
                            color: {self.dark_font_color};
                            border-radius: 10px;
                            font-weight: bold;
                            padding: 0px 10px 0px 10px;
                        }}
                        QPushButton:hover {{
                            background-color: rgb(110,110,110);
                        }}
                        QPushButton:pressed {{
                            background-color: rgb(60,60,60);
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

        self.q_line_edit_style = """
                   QLineEdit {
                       background-color: #2B2D30;
                       color: white;
                       border: 2px solid #4D4E51;
                       border-radius: 8px;
                       padding: 5px 10px;
                   }
                   QLineEdit:focus {
                       border: 2px solid #CED0D6;
                       background-color: #4D4E51;
                   }
                   QLineEdit::placeholder {
                       color: #6272a4;
                   }
               """

        self.q_scroll_bar_style = """
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: #1E1F22;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #4D4E51;
                    border-radius: 6px;
                    min-height: 30px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #7A7B7E;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: transparent; 
                }
            """

        self.q_slider_style = """
                QSlider::groove:horizontal {
                    height: 4px;
                    background: #3C3E42;
                    border-radius: 2px;
                }
                QSlider::sub-page:horizontal {
                    background: #3574F0;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #ffffff;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0px;
                    border-radius: 8px;
                    border: 2px solid #3574F0;
                }
                QSlider::handle:horizontal:hover {
                    background: #f0f8ff;
                    border-color: #4A8BF5;
                    width: 18px;
                    height: 18px;
                    margin: -7px 0px;
                }
                QSlider::handle:horizontal:pressed {
                    background: #e6f0ff;
                    border-color: #2A5FD0;
                }
            """


style = Styles()
