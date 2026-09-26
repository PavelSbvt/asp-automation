from core.settings_manager import Settings
from gui.utils.windows_functions import background_window_by_time_of_day
from gui.utils.styles import Style
from utils.output_rich import Rich


def update_progress_bar_animation(self):
    """
    Функция для обновления прогресса прогресс-бара для имитации индикации
    вымышленного процесса

    :return: None
    """

    if self.progress_bar.value() < 100:
        self.progress_bar.setValue(self.progress_bar.value() + 1)
    else:
        self.progress_bar.setValue(100)

def loading_window_img_click(self) -> None:
    """
    Функция для смены фонового изображения загрузочного окна по кнопке (изображение
    является кнопкой). Ещё раз запускает функцию выбора случайного изображения на
    фон загрузочного окна и обновляет главные цвета изображения, которые передадутся
    функции обновления градиента.

    :return: None
    """

    Rich.print_spacer()
    Rich.debug_log("нажата кнопка изменения фонового изображения загрузочного окна")

    self.current_r, self.current_g, self.current_b, self.bg_path_check \
        = background_window_by_time_of_day(self.lb_hi_prog,
            self.loading_window, self.bg_path_check)

    Rich.debug_log("Фоновое изображение загрузочного окна изменено, "
        "цвета фонового градиента изменены.")


def update_animation_gradient(self) -> None:
    """
    Функция для создания анимации виджету с градиентом на фоне 
    (виджет находится поверх основного фона окна) - плавное смещение градиента
     и уменьшение его прозрачности.

    :return: None
    """""

    r, g, b = self.current_r, self.current_g, self.current_b

    self.base_position_gradient += self.speed * self.direction_animation

    if self.base_position_gradient >= 0.5:
        self.base_position_gradient = 0.5
        self.direction_animation = -1

    elif self.base_position_gradient <= 0.0:
        self.flag_finish_animation = True
        self.base_position_gradient = 0.0

    pos = self.base_position_gradient

    self.change_color += 0.5 * self.change_color_direction

    if self.change_color >= 40:
        self.change_color = 40
        self.change_color_direction = -1
    elif self.change_color <= 1:
        self.change_color = 1
        self.change_color_direction = 1

    index_changed_color = int(self.change_color * 0.5)

    change_red = min(255, r + index_changed_color)
    change_green = min(255, g + index_changed_color)
    change_blue = min(255, b + index_changed_color)

    if not self.flag_finish_animation:
        self.widget_gradient.setStyleSheet(f"""
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0.5,
                    stop: 0 rgba({r}, {g}, {b}, 0.0),
                    stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                    {self.opacity_animation:.2f}),
                    stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                    {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                    {self.opacity_animation * 4:.2f})
                );
                border-radius: 10px;
            """)
    else:
        self.widget_gradient.setStyleSheet(f"""
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0.5,
                    stop: 0 rgba({r}, {g}, {b}, 0.0),
                    stop: {self.gradient_1_pos + pos * 0.3} rgba({r}, {g}, {b}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: {self.gradient_2_pos + pos * 0.3} rgba({change_red * 0.5:.0f}, 
                    {change_green * 0.5:.0f}, {change_blue * 0.5:.0f}, 
                    {self.opacity_animation * 1:.2f}),
                    stop: 1 rgba({change_red}, {change_green}, {change_blue}, 
                    {self.opacity_animation * 4:.2f})
                );
                border-radius: 10px;
            """)
        if self.opacity_animation <= 0.1:
            self.opacity_animation += 0.0005

        if (self.gradient_1_pos + pos * 0.6) >= 0.1:
            self.gradient_1_pos -= 0.005
            self.gradient_2_pos -= 0.005
        else:
            return

def set_styles(self) -> None:
    """
    Функция для установки и обновления QSS стилей виджетов, кнопок, прогрессбаров и др.

    :return: None. Устанавливает стили
    """

    Style.update_styles_for_choose_theme()

    self.shortcut_button.setStyleSheet(Style.button_blue_style)

    self.tab_widget.setStyleSheet(f"""
       QTabWidget::pane {{
           background-color: #2B2B2B;
           border: none;
           top: -1px;
       }}
       QTabBar {{
           background-color: {Style.background_color};
       }}
       QTabBar::tab {{
           background: transparent;
           color: {Style.dark_font_color};
           padding: 10px 20px;
           margin-right: 0px;
           border: none;
           border-bottom: 2px solid transparent;
       }}
       QTabBar::tab:selected {{
           background: transparent;
           color: {Style.light_font_color};
           border-bottom: 2px solid rgb({self.main_color_str});
           font-weight: bold;
       }}            
       QTabBar::tab:hover:!selected {{
           color: {Style.light_font_color};
           border-bottom: 2px solid #4D4E51;
       }}
   """)

    self.main_tab_scroll_area.setStyleSheet(Style.q_scroll_bar_style)

    self.main_back_widget.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 0px;")

    # Стили с основной вкладки

    self.label_title_to_stop.setStyleSheet(f"color: {Style.light_font_color};"
        f"border: none; background-color: transparent;")

    self.label_title_stop_2.setStyleSheet(f"color: {Style.light_font_color};"
        f"border: none; background-color: transparent;")

    self.widget_for_title_to_stop.setStyleSheet(
        f"background-color: rgba({self.main_color_str}, 0.2); border-radius: 10px;"
        f"border: 2px dotted {Style.dark_font_color};")

    self.widget_title_stop_second.setStyleSheet(
        f"background-color: rgba({self.main_color_str}, 0.35);"
        f" border-radius: 10px;"
        f"border: 2px dotted {Style.dark_font_color};")

    self.progress_bar_parsing.setStyleSheet(Style.progress_bar_style_blue)
    self.app_name_button.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Style.light_font_color};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin-left: 30px;
                }}
            """)
    self.settings_button.setStyleSheet(f"""
                QPushButton {{
                    background-image: url({self.settings_path.as_posix()});
                    border: none;
                    background-repeat: no-repeat;
                    background-position: center;
                    background-color: transparent;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.08);
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.15);
                }}
            """)
    self.run_button.setStyleSheet(f"""
                QPushButton {{
                    background-image: url({self.run_button_path.as_posix()});
                    background-repeat: no-repeat;
                    background-position: center;
                    border: none;
                    background-color: transparent;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.08);
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.15);
                }}
            """)

    style_for_stop_button = f"""
            QPushButton {{
                background-image: url({self.stop_button_path.as_posix()});
                background-repeat: no-repeat;
                background-position: center;
                border: none;
                background-color: #8A3535;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #B44747;
            }}
            QPushButton:pressed {{
                background-color: #7A2E2E;
            }}
        """

    self.stop_parsing_button.setStyleSheet(style_for_stop_button)
    self.stop_button.setStyleSheet(style_for_stop_button)

    self.container_widget_main_tab.setStyleSheet(
        f"background-color: {Style.background_dark_color}; border-radius: 10px;")
    self.open_folder_button.setStyleSheet(Style.button_blue_style)
    self.radio_buttons_background.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
    )
    self.label_for_radio_buttons.setStyleSheet(
        f"color: {Style.light_font_color}; margin: 10px; font-weight: bold;")
    self.radio_button_1.setStyleSheet(Style.radio_button_style)
    self.radio_button_2.setStyleSheet(Style.radio_button_style)
    self.radio_button_3.setStyleSheet(Style.radio_button_style)
    self.input_commission.setStyleSheet(Style.q_line_edit_style)
    self.widget_for_choose_files_commission.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
    )
    self.btn_choose_universal_xl.setStyleSheet(Style.button_blue_style)
    self.universal_excel_label.setStyleSheet(
        f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color};"
        f"padding: 10px;"
    )
    self.widget_for_choose_commission_file.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
    )
    self.btn_choose_history_commission.setStyleSheet(Style.button_blue_style)
    self.history_xl_choused_label.setStyleSheet(
        f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;"
    )
    self.btn_choose_foreign_commission.setStyleSheet(Style.button_blue_style)
    self.foreign_xl_choosed_label.setStyleSheet(
        f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;"
    )
    self.btn_choose_specialization_commission.setStyleSheet(Style.button_blue_style)
    self.specialization_xl_choosed_lb.setStyleSheet(
        f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;"
    )
    self.time_update_label.setStyleSheet(
        f"color: {Style.dark_font_color}; "
        f"background-color: {Style.background_dark_color};"
    )
    self.button_to_update_date.setStyleSheet(Style.button_blue_style)
    self.label_info_last_update_cache.setStyleSheet(
        f"color: {Style.light_font_color};")
    self.label_commission_title.setStyleSheet(
        f"color: {Style.light_font_color}; padding: 10px;"
        f"background-color: {Style.background_color}; border-radius: 10px;")
    self.widget_for_cache.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
    )
    self.button_change_save_path.setStyleSheet(Style.button_blue_style)
    self.widget_for_change_save_path.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
        f"padding: 10px;")
    self.change_path_label.setStyleSheet(f"color: {Style.light_font_color};")
    self.save_path_label.setStyleSheet(f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;"
        f"padding: 10px;")

    # Стили с вкладки сборки по готовой таблице
    self.tab_second_widget.setStyleSheet(
        f"background-color: {Style.background_dark_color}; border-radius: 10px;")
    self.background_widget_for_second_tab.setStyleSheet(
        f"background-color: {Style.background_dark_color}; border-radius: 10px;")
    self.second_tab_title.setStyleSheet(f"color: {Style.light_font_color}; font: bold;")
    self.widget_for_pos_button_path_and_title_choose_save_path.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
        f"padding: 10px;")
    self.title_change_save_path.setStyleSheet(f"color: {Style.light_font_color};"
        f"background-color: {Style.background_color}; border-radius: 10px;"
        f"margin-top: 5px; font: bold;")
    self.current_save_path_label.setStyleSheet(f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;")
    self.button_shouse_save_path_for_second_tab.setStyleSheet(
        Style.button_blue_style)
    self.progress_bar.setStyleSheet(Style.progress_bar_style_blue)
    self.widget_for_choose_table.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;"
        f"padding: 10px;")
    self.title_choose_table_label.setStyleSheet(f"color: {Style.light_font_color};"
        f"background-color: {Style.background_color}; border-radius: 10px;"
        f"font: bold;")
    self.label_current_tabel.setStyleSheet(f"color: {Style.dark_font_color};"
        f"background-color: {Style.background_dark_color}; border-radius: 10px;"
        f"padding: 10px;")
    self.button_shouse_table.setStyleSheet(
        Style.button_blue_style)
    self.button_open_folder_with_pdf.setStyleSheet(
        Style.button_blue_style)

    # Стили с вкладки настроек
    self.choose_dark_theme_button.setStyleSheet(Style.button_hide_style)
    self.choose_violet_theme_button.setStyleSheet(Style.button_hide_style)
    self.choose_standard_theme_button.setStyleSheet(Style.button_hide_style)
    self.label_title_choose_theme.setStyleSheet(
        f"color: {Style.light_font_color}; font: bold;")
    self.widget_for_choose_theme.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;")
    self.indicate_loading_window_timer_duration.setStyleSheet(
        f"color: {Style.dark_font_color};")
    self.slider_loading_window_timer_duration.setStyleSheet(Style.q_slider_style)
    self.loading_window_timer_duration_param_widget.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;")

    if not Settings.get_flag_show_loading_window_hide_log():
        self.button_hide_loading_window.setStyleSheet(Style.button_blue_style)
    else:
        self.button_hide_loading_window.setStyleSheet(Style.button_hide_style)

    if Settings.get_flag_show_loading_window_hide_log():
        self.button_show_loading_window.setStyleSheet(Style.button_blue_style)
    else:
        self.button_show_loading_window.setStyleSheet(Style.button_hide_style)

    self.param_show_loading_window.setStyleSheet(f"color: {Style.light_font_color};")
    self.loading_window_param_widget.setStyleSheet(
        f"background-color: {Style.background_color}; border-radius: 10px;")
    self.settings_main_widget.setStyleSheet(
        f"background: {Style.background_dark_color}; border-radius: 10px;")
    self.settings_label.setStyleSheet(
        f"color: {Style.light_font_color}; font: bold;")
    self.settings_cap.setStyleSheet(
        f"background-color: {Style.background_dark_color};")
    self.tab_settings_widget.setStyleSheet(
        f"background-color: {Style.background_dark_color}; "
        f"border-radius: 10px;")
