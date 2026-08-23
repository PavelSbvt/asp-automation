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
