from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPushButton

from gui.themes import get_theme


def change_theme(self, theme_name: str, button: QPushButton) -> None:
    """
    Функция смены темы цветового оформления на заданную в аргументах функции и записанных в словаре параметрах.
    :return: None
    """

    theme = get_theme(theme_name)

    start_poz_x = theme["start_poz_x"]
    start_pos_y = theme["start_pos_y"]
    max_size_png = theme["max_size_png"]
    medium_size_png = theme["medium_size_png"]
    mini_size_png = theme["mini_size_png"]
    background_image = theme["background_image"]
    border_color_pr_bar = theme["border_color_pr_bar"]
    pr_bg_color = theme["pr_bg_color"]
    pr_gradient_colors = theme["pr_gradient_colors"]
    term_bg_color = theme["term_bg_color"]
    radio_btn_color = theme["radio_btn_color"]
    radio_border_indicator_color = theme["radio_border_indicator_color"]
    radio_bg_indicator_color = theme["radio_bg_indicator_color"]
    radio_bg_indicator_checked_color = theme["radio_bg_indicator_checked_color"]
    radio_border_indicator_checked_color = theme["radio_border_indicator_checked_color"]
    radio_border_indicator_hover_color = theme["radio_border_indicator_hover_color"]
    widget_for_label_color = theme["widget_for_label_color"]
    input_commission_bg_color = theme["input_commission_bg_color"]
    input_commission_border_color = theme["input_commission_border_color"]
    input_commission_focus_border_color = theme["input_commission_focus_border_color"]
    input_commission_focus_bg_color = theme["input_commission_focus_bg_color"]
    input_commission_placeholder_color = theme["input_commission_placeholder_color"]
    buttons_glass_style_bg_color = theme["buttons_glass_style_bg_color"]
    buttons_glass_style_bg_hover_color = theme["buttons_glass_style_bg_hover_color"]
    buttons_glass_style_bg_pressed_color = theme["buttons_glass_style_bg_pressed_color"]
    buttons_glass_style_border_color = theme["buttons_glass_style_border_color"]
    buttons_glass_style_border_hover_color = theme["buttons_glass_style_border_hover_color"]
    choosed_files_names_colors = theme["choosed_files_names_colors"]
    basic_btn_bg_color = theme["basic_btn_bg_color"]
    basic_btn_border_color = theme["basic_btn_border_color"]
    basic_bth_bg_hover_color = theme["basic_bth_bg_hover_color"]
    basic_bth_border_hover_color = theme["basic_bth_border_hover_color"]
    basic_bth_bg_pressed_color = theme["basic_bth_bg_pressed_color"]
    tab_bar_bg_color = theme["tab_bar_bg_color"]
    tab_bar_color = theme["tab_bar_color"]
    tab_bar_border_color = theme["tab_bar_border_color"]
    tab_bar_bg_selected_color = theme["tab_bar_bg_selected_color"]
    tab_bar_selected_color = theme["tab_bar_selected_color"]
    tab_bar_border_selected_color = theme["tab_bar_border_selected_color"]
    tab_bar_bg_hover_color = theme["tab_bar_bg_hover_color"]
    tab_bar_border_hover_color = theme["tab_bar_border_hover_color"]
    tab_bar_bg_pressed_color = theme["tab_bar_bg_pressed_color"]
    blc_where_save_pdf_bg_color = theme["blc_where_save_pdf_bg_color"]
    blc_where_save_pdf_color = theme["blc_where_save_pdf_color"]
    blc_where_save_pdf_border_color = theme["blc_where_save_pdf_border_color"]
    save_path_l_color = theme["save_path_l_color"]
    save_path_l_bg_color = theme["save_path_l_bg_color"]
    save_path_l_border_color = theme["save_path_l_border_color"]
    blc_for_printing_pr_bg_color = theme["blc_for_printing_pr_bg_color"]
    blc_for_printing_pr_border_color = theme["blc_for_printing_pr_border_color"]
    output_text_bg_color = theme["output_text_bg_color"]
    output_text_color = theme["output_text_color"]
    block_way_save_bg_color = theme["block_way_save_bg_color"]
    block_way_save_border_color = theme["block_way_save_border_color"]
    theme_name_display = theme["theme"]


    btn_from_theme_path = Path(
        f"resources/images/color_themes/{max_size_png}")

    btn_from_theme_medium_path = Path(
        f"resources/images/color_themes/{medium_size_png}")

    btn_from_theme_mini_path = Path(
        f"resources/images/color_themes/{mini_size_png}")

    QTimer.singleShot(10, lambda: (
        button.setFixedSize(245, 245),
        button.setStyleSheet(
            f"background-image: url({btn_from_theme_medium_path.as_posix()});"
            f" border-radius: 10px;"
        ),
        button.move(start_poz_x + 2, start_pos_y + 2)
    ))

    QTimer.singleShot(45, lambda: (
        button.setFixedSize(240, 240),
        button.setStyleSheet(
            f"background-image: url({btn_from_theme_mini_path.as_posix()}); border-radius: 10px;"
        ),
        button.move(start_poz_x + 5, start_pos_y + 5)
    ))

    QTimer.singleShot(125, lambda: (
        button.setFixedSize(245, 245),
        button.setStyleSheet(
            f"background-image: url({btn_from_theme_medium_path.as_posix()});"
            f" border-radius: 10px;"
        ),
        button.move(start_poz_x + 2, start_pos_y + 2)
    ))

    QTimer.singleShot(160, lambda: (
        button.setFixedSize(250, 250),
        button.setStyleSheet(
            f"background-image: url({btn_from_theme_path.as_posix()});"
            f" border-radius: 10px;"
        ),
        button.move(start_poz_x, start_pos_y)
    ))

    background_img_path = Path(
        f"resources/images/color_themes/{background_image}")
    self.background_block.setStyleSheet(
        f"background-image: url({background_img_path.as_posix()});")

    progressBarStyle = f"""
                    QProgressBar {{
                        color: rgb(255, 255, 255);
                        font-weight: bold;
                        font-size: 13px;
                        text-align: center;
                        border: 2px solid rgb({border_color_pr_bar});
                        border-radius: 10px;
                        background: rgb({pr_bg_color});
                    }}
                    QProgressBar::chunk {{
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 {pr_gradient_colors[0]},
                            stop: 0.5 {pr_gradient_colors[1]},
                            stop: 1 {pr_gradient_colors[2]};
                        border-radius: 8px;
                    }}
                """

    self.progress_bar.setStyleSheet(progressBarStyle)

    self.progress_bar_parsing.setStyleSheet(progressBarStyle)

    self.choose_the_term.setStyleSheet(
        f"background-color: rgb({term_bg_color}); "
        "border-radius: 10px; color: rgb(255, 255, 255);")

    radio_style = f"""
                    QRadioButton {{
                        color: rgb({radio_btn_color});
                        font-size: 18px;
                        font-weight: bold;
                        spacing: 10px;
                    }}
                    QRadioButton::indicator {{
                        width: 10px;
                        height: 10px;
                        border-radius: 3px;
                        border: 2px solid rgb({radio_border_indicator_color});
                        background: rgb({radio_bg_indicator_color});
                    }}
                    QRadioButton::indicator:checked {{
                        background-color: rgb({radio_bg_indicator_checked_color});
                        border: 2px solid rgb({radio_border_indicator_checked_color});
                    }}
                    QRadioButton::indicator:hover {{
                        border: 2px solid rgb({radio_border_indicator_hover_color});
                    }}
                """
    self.radio_button_1.setStyleSheet(radio_style)
    self.radio_button_2.setStyleSheet(radio_style)
    self.radio_button_3.setStyleSheet(radio_style)

    self.widget_for_label.setStyleSheet(
        f"background-color: rgb({widget_for_label_color}); border-radius: 10px;")

    self.input_commission.setStyleSheet(f"""
                    QLineEdit {{
                        background: rgb({input_commission_bg_color});
                        color: rgb(255, 255, 255);
                        border: 2px solid rgb({input_commission_border_color});
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-size: 14px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid rgb({input_commission_focus_border_color});
                        background: rgb({input_commission_focus_bg_color});
                    }}
                    QLineEdit::placeholder {{
                        color: rgb({input_commission_placeholder_color});
                        font-style: italic;
                    }}
                """)

    buttons_glass_style = f"""
                    QPushButton {{
                        background: rgb({buttons_glass_style_bg_color});
                        color: rgb(255, 255, 255);
                        border: 2px solid rgb({buttons_glass_style_border_color});
                        border-radius: 10px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background: rgb({buttons_glass_style_bg_hover_color});
                        border: 2px solid rgb({buttons_glass_style_border_hover_color});
                    }}
                    QPushButton:pressed {{
                        background: rgb({buttons_glass_style_bg_pressed_color});
                        padding-top: 6px;
                        padding-bottom: 4px;
                    }}
                """

    self.parsing_button.setStyleSheet(buttons_glass_style)

    self.widget_for_label_choosing_files.setStyleSheet(
        f"background-color: rgb({widget_for_label_color}); border-radius: 10px;")

    self.open_folder_button.setStyleSheet(buttons_glass_style)

    basic_buttons_style = f"""
                    QPushButton {{
                        background: rgb({basic_btn_bg_color});
                        color: rgb(255, 255, 255);
                        border: 1px solid rgb({basic_btn_border_color});
                        border-radius: 12px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background: rgb({basic_bth_bg_hover_color});
                        border: 1px solid rgb({basic_bth_border_hover_color});
                    }}
                    QPushButton:pressed {{
                        background: rgb({basic_bth_bg_pressed_color});
                        padding-top: 6px;
                        padding-bottom: 4px;
                    }}
                """

    self.button_to_find_file_tabel.setStyleSheet(basic_buttons_style)

    self.button_to_find_where_save.setStyleSheet(basic_buttons_style)

    self.block_where_save_pdfs_now.setStyleSheet(f"""              
                    background: rgb({blc_where_save_pdf_bg_color});
                    color: rgb({blc_where_save_pdf_color});
                    border: 1px solid rgb({blc_where_save_pdf_border_color});
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                """)

    self.tab_widget.setStyleSheet(f""" 
                    QTabWidget::pane {{
                        border: none;
                        background: transparent;
                    }}
                    QTabBar::tab {{
                        background: rgb({tab_bar_bg_color});
                        color: rgb({tab_bar_color});
                        border: 1px solid rgb({tab_bar_border_color});
                        border-radius: 8px;
                        padding: 5px;
                        padding-top: -10px;
                        padding-bottom: 7px;
                        margin: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    }}
                    QTabBar::tab:selected {{
                        background: rgb({tab_bar_bg_selected_color});
                        color: rgb({tab_bar_selected_color});
                        border: 1px solid rgb({tab_bar_border_selected_color});
                    }}
                    QTabBar::tab:hover {{
                        background: rgb({tab_bar_bg_hover_color});
                        border: 1px solid rgb({tab_bar_border_hover_color});
                        padding: 5px;
                        padding-top: -10px;
                        padding-bottom: 7px;
                        margin: 4px;
                    }}
                    QTabBar::tab:pressed {{
                        background: rgb({tab_bar_bg_pressed_color});
                        padding: 5px;
                        padding-top: -10px;
                        padding-bottom: 7px;
                    }}
                """)

    self.btn_choose_universal_xl.setStyleSheet(basic_buttons_style)
    self.btn_choose_history_commission.setStyleSheet(basic_buttons_style)
    self.btn_choose_foreign_commission.setStyleSheet(basic_buttons_style)
    self.btn_choose_specialization_commission.setStyleSheet(basic_buttons_style)
    self.button_choose_save_path.setStyleSheet(basic_buttons_style)

    self.save_path_label.setStyleSheet(f"""
        color: rgb({save_path_l_color});
        font-size: 11px;
        background: rgb({save_path_l_bg_color});
        border: 1px solid rgb({save_path_l_border_color});
        border-radius: 8px;
        padding: 5px;
    """)

    self.button_to_open_folder_with_done_pdf.setStyleSheet(buttons_glass_style)

    self.block_for_print_process.setStyleSheet(f"""
                    background: rgb({blc_for_printing_pr_bg_color});
                    border-radius: 10px;
                    border: 1px solid rgb({blc_for_printing_pr_border_color});
                """)
    widget_bg_style = f"background-color: rgb({choosed_files_names_colors}); border-radius: 10px;"

    self.widget_for_label_choosing_way.setStyleSheet(widget_bg_style)

    self.widget_for_styles.setStyleSheet(widget_bg_style)

    self.universal_excel_label_widget.setStyleSheet(widget_bg_style)
    self.history_excel_choosed_widget.setStyleSheet(widget_bg_style)
    self.foreign_excel_choosed_widget.setStyleSheet(widget_bg_style)
    self.specialization_excel_choosed_widget.setStyleSheet(widget_bg_style)
    self.widget_for_progress_bar.setStyleSheet(widget_bg_style)
    self.output_text.setStyleSheet(f"""
        background: rgb({output_text_bg_color});
        border-radius: 10px;
        color: rgb({output_text_color});
        font-family: 'Courier New';
        font: bold;
        font-size: 12px;
        border: 1px solid rgb({blc_for_printing_pr_border_color});
    """)
    self.block_way_save.setStyleSheet(f"""
        background: rgb({block_way_save_bg_color});
        border: 1px solid rgb({block_way_save_border_color});
        border-radius: 10px;
    """)
    self.window_for_choosing_styles.setStyleSheet(
        f"border-radius: 10px; background-color: rgb({widget_for_label_color});")

    self.widget_for_update_data_site_parsing.setStyleSheet(widget_bg_style)
    self.button_to_update_date.setStyleSheet(buttons_glass_style)

    print(f"[I] [style] Применена {theme_name_display} тема")