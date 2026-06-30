from pyqt_functions import *

weight_window = 1200
height_window = 800
class MyWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.excel_file_path = None

            desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

            self.save_folder_path = os.path.join(desktop_path, "results_folder")

            block_background = QWidget(self)
            block_background.setFixedSize(weight_window, height_window)
            block_background.setStyleSheet("background-image:url(background_images/DSC_5174_1.jpg);")
            block_background.move(0, 0)

            self.drag_position = QPoint()

            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            tabWidgetObjects = QTabWidget(self)

            tabWidgetObjects.setFixedSize(1200, 800)

            tabWidgetObjects.setTabPosition(QTabWidget.TabPosition.West)
            tabWidgetObjects.setIconSize(QSize(65, 65))

            tabWidgetObjects.setTabBarAutoHide(False)

            tabWidgetObjects.setStyleSheet(""" 
                QTabWidget::pane {
                    border: none;
                    background: transparent;
                }
                QTabBar::tab {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(76, 110, 50, 230),    
                        stop: 1 rgba(45, 75, 30, 230));   
                    color: rgba(220, 240, 180, 220);   
                    border: 1px solid rgba(100, 140, 65, 200);
                    border-radius: 8px;
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(120, 180, 80, 250),   
                        stop: 1 rgba(80, 130, 50, 250)); 
                    color: white;
                    border: 1px solid rgba(160, 220, 110, 230);
                }
                QTabBar::tab:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(100, 150, 65, 245),
                        stop: 1 rgba(60, 100, 40, 245));
                    border: 1px solid rgba(130, 180, 85, 220);
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                    margin: 4px;
                }
                QTabBar::tab:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(60, 90, 35, 250),
                        stop: 1 rgba(35, 60, 20, 250));
                    padding: 5px;
                    padding-top: -10px;
                    padding-bottom: 7px;
                }
            """)

            tabObjects_1 = QWidget()

            tabObjects_2 = QWidget()

            self.open_folder_button = QPushButton("Открыть папку с PDF", tabObjects_1)
            self.open_folder_button.setFixedSize(300, 50)
            self.open_folder_button.move(370, 730)
            self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.open_folder_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(60, 85, 45, 230),
                        stop: 1 rgba(40, 65, 30, 230));
                    color: white;
                    border: 1px solid rgba(80, 110, 60, 200);
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(100, 140, 70, 250),
                        stop: 1 rgba(70, 110, 45, 250));
                    border: 1px solid rgba(140, 190, 100, 230);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(40, 65, 30, 230),
                        stop: 1 rgba(30, 50, 20, 230));
                }
            """)
            self.open_folder_button.clicked.connect(lambda: open_pdf_folder(self))

            tabWidgetObjects.addTab(tabObjects_1, "")
            tabWidgetObjects.addTab(tabObjects_2, "")

            def rotate_icon(icon_path, size=65, angle=90):
                icon = QIcon(icon_path)
                pixmap = icon.pixmap(size, size)
                transform = QTransform().rotate(angle)
                rotated_pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
                return QIcon(rotated_pixmap)

            icon1 = rotate_icon("icons/pdf.png")
            icon2 = rotate_icon("icons/settings.png")

            tabWidgetObjects.setTabIcon(0, icon1)
            tabWidgetObjects.setTabIcon(1, icon2)

            button_close = QPushButton(self)
            button_close.setFixedSize(45, 45)
            button_close.move(1150, 5)
            button_close.setCursor(Qt.CursorShape.DragMoveCursor)
            button_close.setStyleSheet("""
            background-image:url(icons/close_icon.png);
            background-color: transparent;
            border: none;
            background-repeat: no-repeat;
            background-position: center;
            """)
            button_close.clicked.connect(self.close)

            block_for_print_process = QWidget(tabObjects_1)
            block_for_print_process.setFixedSize(1020, 620)
            block_for_print_process.setStyleSheet(
                "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(60, 85, 45, 230),stop: 1 rgba(40, 65, 30, 230)); border-radius: 10px;")
            block_for_print_process.move(10, 100)

            self.output_text = QTextEdit(block_for_print_process)
            self.output_text.setGeometry(5, 5, 1010, 610)
            self.output_text.setStyleSheet(
                "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 rgba(60, 95, 45, 0.2),stop: 1 rgba(45, 75, 35, 0.25));border-radius: 10px;; color: white; font-family; font: bold; font-size: 12px;")
            self.output_text.setReadOnly(True)

            button_to_find_file_tabel = QPushButton(tabObjects_1)
            button_to_find_file_tabel.setFixedSize(180, 50)
            button_to_find_file_tabel.setCursor(Qt.CursorShape.PointingHandCursor)
            button_to_find_file_tabel.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(70, 110, 50, 240),
                        stop: 1 rgba(50, 85, 35, 240));
                    color: white;
                    border: 1px solid rgba(100, 140, 70, 200);
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(100, 150, 70, 250),
                        stop: 1 rgba(70, 110, 45, 250));
                    border: 1px solid rgba(140, 190, 100, 230);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(45, 75, 30, 240),
                        stop: 1 rgba(35, 60, 25, 240));
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)
            button_to_find_file_tabel.move(10, 25)
            button_to_find_file_tabel.setText("Выберите файл")
            button_to_find_file_tabel.clicked.connect(lambda: choose_file(self))

            button_to_find_where_save = QPushButton(tabObjects_1)
            button_to_find_where_save.setFixedSize(250, 50)
            button_to_find_where_save.setCursor(Qt.CursorShape.PointingHandCursor)
            button_to_find_where_save.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(70, 110, 50, 240),
                        stop: 1 rgba(50, 85, 35, 240));
                    color: white;
                    border: 1px solid rgba(100, 140, 70, 200);
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(100, 150, 70, 250),
                        stop: 1 rgba(70, 110, 45, 250));
                    border: 1px solid rgba(140, 190, 100, 230);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(45, 75, 30, 240),
                        stop: 1 rgba(35, 60, 25, 240));
                    padding-top: 6px;
                    padding-bottom: 4px;
                }
            """)
            button_to_find_where_save.move(200, 25)
            button_to_find_where_save.setText("Изменить путь для сохранения")

            block_where_save_pdfs_now = QWidget(tabObjects_1)
            block_where_save_pdfs_now.setFixedSize(160, 50)
            block_where_save_pdfs_now.setStyleSheet("""              
                            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgba(70, 110, 50, 240),
                                stop: 1 rgba(50, 85, 35, 240));
                            color: white;
                            border: 1px solid rgba(100, 140, 70, 200);
                            border-radius: 12px;
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px;
    
                    """)
            block_where_save_pdfs_now.move(460, 25)

            button_to_find_where_save.clicked.connect(lambda: choose_save_folder(self))
            block_where_save_pdfs_now_label = QLabel(block_where_save_pdfs_now)
            block_where_save_pdfs_now_label.setText("Путь сохранения:")
            block_where_save_pdfs_now_label.setGeometry(0, 0, 160, 50)
            block_where_save_pdfs_now_label.setStyleSheet("color:white; font: bold; font-size: 14px;")
            block_where_save_pdfs_now_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            block_way_save = QWidget(tabObjects_1)
            block_way_save.setFixedSize(340, 50)
            block_way_save.setStyleSheet("""
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 70, 35, 0.7),
                    stop: 1 rgba(35, 55, 25, 0.8));
                border: 1px solid rgba(80, 120, 55, 150);
                border-radius: 10px;
            """)
            block_way_save.move(630, 25)

            self.path_value_label = QLabel(block_way_save)
            short_path = self.save_folder_path
            if len(short_path) > 150:
                short_path = "..." + short_path[-150:]
            else:
                short_path = self.save_folder_path
            self.path_value_label.setText(short_path)
            self.path_value_label.setGeometry(5, 5, 330, 40)
            self.path_value_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
            self.path_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.path_value_label.setWordWrap(True)
            block_way_save.setToolTip(self.save_folder_path)

            button_do_operation = QPushButton(tabObjects_1)
            button_do_operation.setFixedSize(50, 50)
            button_do_operation.setCursor(Qt.CursorShape.ClosedHandCursor)
            button_do_operation.setStyleSheet(
                "background-image: url(icons/do_op_new.png); color: white; font-size: 14px; font:bold; border-radius: 10px;")
            button_do_operation.move(980, 25)
            button_do_operation.clicked.connect(lambda: get_pdf(self))

            widget_for_styles = QWidget(tabObjects_2)
            widget_for_styles.setFixedSize(300, 45)
            widget_for_styles.setStyleSheet("border-radius:10px; background-color: rgba(45, 75, 30, 240)")
            widget_for_styles.move(10, 27)
            label_for_styles = QLabel(widget_for_styles)
            label_for_styles.setStyleSheet("color:white; font: bold; font-size: 18px;")
            label_for_styles.setText("Выберите стиль оформления")
            label_for_styles.setGeometry(0, 0, 300, 45)
            label_for_styles.setAlignment(Qt.AlignmentFlag.AlignCenter)

            window_for_choosing_styles = QWidget(tabObjects_2)
            window_for_choosing_styles.setFixedSize(1030, 600)
            window_for_choosing_styles.setStyleSheet("border-radius: 10px; background-color: rgba(45, 64, 30, 240)")
            window_for_choosing_styles.move(10, 100)

            button_from_choose_dark_theme = QPushButton(tabObjects_2)
            button_from_choose_dark_theme.setStyleSheet("background-image: url(color_themes/dark_theme/dark_theme_icon.png); border-radius: 10px;")
            button_from_choose_dark_theme.setFixedSize(250, 250)
            button_from_choose_dark_theme.move(20, 110)

            def change_theme_to_dark():
                QTimer.singleShot(10, lambda: (
                    button_from_choose_dark_theme.setFixedSize(245, 245),
                    button_from_choose_dark_theme.setStyleSheet(
                        "background-image: url(color_themes/dark_theme/dark_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_dark_theme.move(22, 112)
                ))

                QTimer.singleShot(45, lambda: (
                    button_from_choose_dark_theme.setFixedSize(240, 240),
                    button_from_choose_dark_theme.setStyleSheet(
                        "background-image: url(color_themes/dark_theme/dark_theme_icon_mini.png); border-radius: 10px;"
                    ),
                    button_from_choose_dark_theme.move(25, 115)
                ))

                QTimer.singleShot(125, lambda: (
                    button_from_choose_dark_theme.setFixedSize(245, 245),
                    button_from_choose_dark_theme.setStyleSheet(
                        "background-image: url(color_themes/dark_theme/dark_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_dark_theme.move(22, 112)
                ))

                QTimer.singleShot(160, lambda: (
                    button_from_choose_dark_theme.setFixedSize(250, 250),
                    button_from_choose_dark_theme.setStyleSheet(
                        "background-image: url(color_themes/dark_theme/dark_theme_icon.png); border-radius: 10px;"
                    ),
                    button_from_choose_dark_theme.move(20, 110)
                ))

            button_from_choose_dark_theme.clicked.connect(change_theme_to_dark)

            button_from_choose_violet_theme = QPushButton(tabObjects_2)
            button_from_choose_violet_theme.setStyleSheet("background-image: url(color_themes/violet_theme/violet_theme_icon.png); border-radius: 10px;")
            button_from_choose_violet_theme.setFixedSize(250, 250)
            button_from_choose_violet_theme.move(280, 110)

            def change_theme_to_violet():
                QTimer.singleShot(10, lambda: (
                    button_from_choose_violet_theme.setFixedSize(245, 245),
                    button_from_choose_violet_theme.setStyleSheet(
                        "background-image: url(color_themes/violet_theme/violet_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_violet_theme.move(282, 112)
                ))

                QTimer.singleShot(45, lambda: (
                    button_from_choose_violet_theme.setFixedSize(240, 240),
                    button_from_choose_violet_theme.setStyleSheet(
                        "background-image: url(color_themes/violet_theme/violet_theme_icon_mini.png); border-radius: 10px;"
                    ),
                    button_from_choose_violet_theme.move(285, 115)
                ))
                QTimer.singleShot(125, lambda: (
                    button_from_choose_violet_theme.setFixedSize(245, 245),
                    button_from_choose_violet_theme.setStyleSheet(
                        "background-image: url(color_themes/violet_theme/violet_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_violet_theme.move(282, 112)
                ))
                QTimer.singleShot(160, lambda: (
                    button_from_choose_violet_theme.setFixedSize(250, 250),
                    button_from_choose_violet_theme.setStyleSheet(
                        "background-image: url(color_themes/violet_theme/violet_theme_icon.png); border-radius: 10px;"
                    ),
                    button_from_choose_violet_theme.move(280, 110)
                ))

            button_from_choose_violet_theme.clicked.connect(change_theme_to_violet)

            button_from_choose_standart_theme = QPushButton(tabObjects_2)
            button_from_choose_standart_theme.setStyleSheet(
                "background-image: url(color_themes/standard_theme/standard_theme_icon.png); border-radius: 10px;")
            button_from_choose_standart_theme.setFixedSize(250, 250)
            button_from_choose_standart_theme.move(540, 110)

            def change_theme_to_standard():
                QTimer.singleShot(10, lambda: (
                    button_from_choose_standart_theme.setFixedSize(245, 245),
                    button_from_choose_standart_theme.setStyleSheet(
                        "background-image: url(color_themes/standard_theme/standard_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_standart_theme.move(542, 112)
                ))

                QTimer.singleShot(45, lambda: (
                    button_from_choose_standart_theme.setFixedSize(240, 240),
                    button_from_choose_standart_theme.setStyleSheet(
                        "background-image: url(color_themes/standard_theme/standard_theme_icon_mini.png); border-radius: 10px;"
                    ),
                    button_from_choose_standart_theme.move(545, 115)
                ))

                QTimer.singleShot(125, lambda: (
                    button_from_choose_standart_theme.setFixedSize(245, 245),
                    button_from_choose_standart_theme.setStyleSheet(
                        "background-image: url(color_themes/standard_theme/standard_theme_icon_medium.png); border-radius: 10px;"
                    ),
                    button_from_choose_standart_theme.move(542, 112)
                ))

                QTimer.singleShot(160, lambda: (
                    button_from_choose_standart_theme.setFixedSize(250, 250),
                    button_from_choose_standart_theme.setStyleSheet(
                        "background-image: url(color_themes/standard_theme/standard_theme_icon.png); border-radius: 10px;"
                    ),
                    button_from_choose_standart_theme.move(540, 110)
                ))

            button_from_choose_standart_theme.clicked.connect(change_theme_to_standard)

            QTimer.singleShot(1, self.center_window)

        def center_window(self):
            qr = self.frameGeometry()
            cp = self.screen().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_position = event.globalPosition().toPoint()
                event.accept()

        #
        def mouseMoveEvent(self, event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                delta = event.globalPosition().toPoint() - self.drag_position
                self.move(self.pos() + delta)
                self.drag_position = event.globalPosition().toPoint()
                event.accept()