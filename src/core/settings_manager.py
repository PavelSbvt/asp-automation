import json
from typing import Optional
from pathlib import Path

from utils.output_rich import Rich


class SettingsManager:
    """
    Класс для работы с настройками приложения.
    """

    def __init__(self) -> None:
        """
        Конструктор класса настроек.
        """

        self.config_path = Path("config/settings.json")
        self.settings = {}

        self.loading_window_timer_duration = 5000
        self.flag_show_loading_window = True
        self.theme = "standard"

        self.get_settings()

    def write_standard_settings(self) -> None:
        """
        Функция для записи стандартных настроек в файл (по пути сохранения настроек -
        self.config_path).

        :return: None.
        """

        with open(self.config_path, "w", encoding="utf-8") as json_file:
            # Стандартные настройки
            data = {
                "loading_window_timer": self.loading_window_timer_duration,
                "flag_show_loading_window": self.flag_show_loading_window,
                "theme": self.theme
            }
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            Rich.debug_log("Применены стандартные настройки")

    def write_settings(self) -> None:
        """
        Записывает стандартные настройки в JSON-файл, создаёт родительскую папку и файл
        по пути файла из атрибута класса настроек - self.config_path.

        :return: None.
        """

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.write_standard_settings()

        Rich.success_log(f"Файл с настройками сохранён: {self.config_path}")

    def read_settings(self) -> dict:
        """
        Читает настройки из JSON-файла

        :return: dict.
        """

        if not self.config_path.exists():
            Rich.warning_log(f"Файл с настройками не найден: {self.config_path}")
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as file:
            settings_data = json.load(file)
            self.settings = settings_data
            # print(settings_data)

            Rich.success_log("Настройки получены")
            return settings_data

    def read_one_param(self, param_name: str):
        """
        Функция для чтения из файла настроек только одного параметра

        :param param_name: принимает имя параметра из настроек,
         по которому будет искать значение

        :return: param_value
        """

        Rich.debug_log(f"Получение '{param_name}' из настроек.")
        if not self.config_path.exists():
            Rich.warning_log(f"Файл с настройками не найден: {self.config_path}")
            return "Неизвестно"

        with open(self.config_path, 'r', encoding='utf-8') as file:
            settings_data = json.load(file)
            param_value = settings_data.get(f"{param_name}", "Неизвестно")
            return param_value

    def read_one_param_hide_log(self, param_name: str):
        """
        Функция для чтения из файла настроек только одного параметра.
        Минимальный вывод логов в консоль

        :param param_name: принимает имя параметра из настроек, по которому
         будет искать значение

        :return: param_value
        """

        if not self.config_path.exists():
            Rich.warning_log(f"Файл с настройками не найден: {self.config_path}")
            return "Неизвестно"

        with open(self.config_path, 'r', encoding='utf-8') as file:
            settings_data = json.load(file)
            param_value = settings_data.get(f"{param_name}", "Неизвестно")
            return param_value

    def rewrite_settings(self) -> None:
        """
        Функция для перезаписи файла с настройками.

        Заполнит файл с настройками данными атрибутов класса.

        :return: None.
        """
        # Очистка
        with open(self.config_path, "w", encoding="utf-8") as file:
            Rich.debug_log("Очистка файла с настройками (перезапись).")
            file.write("")
        # Запись
        self.write_standard_settings()
        Rich.debug_log("Настройки обновлены.")

    def get_settings(self) -> None:
        """
        Функция для инициализации проверки файла настроек (проверка наличия данных и
        их заполнение в случае необходимости).

        Читает файл с настройками, если это возможно, или заполняет стандартные
        настройки в файл. Обновляет атрибуты класса теми, которые найдет в файле
         с настройками.

        :return: None.
        """

        if not self.config_path.exists():
            Rich.warning_log(f"Файл с настройками не найден: {self.config_path}")
            self.write_settings()
            Rich.debug_log("Принудительно записаны стандартные настройки")

        try:
            settings_data = self.read_settings()

            broken_settings_parameters = []

            loading_window_timer_duration = settings_data.get("loading_window_timer",
                "Неизвестно")
            if loading_window_timer_duration == "Неизвестно" or not isinstance(
                    loading_window_timer_duration, int):
                broken_settings_parameters.append("loading_window_timer_duration")
            else:
                self.loading_window_timer_duration = loading_window_timer_duration

            flag_show_loading_window = settings_data.get("flag_show_loading_window",
                "Неизвестно")
            if flag_show_loading_window == "Неизвестно" or not isinstance(
                    flag_show_loading_window, bool):
                broken_settings_parameters.append("flag_show_loading_window")
            else:
                self.flag_show_loading_window = flag_show_loading_window

            theme = settings_data.get("theme", "Неизвестно")

            if theme == "Неизвестно" or not isinstance(
                    theme, str):
                broken_settings_parameters.append("theme")
            else:
                self.theme = theme

            if broken_settings_parameters:
                Rich.warning_log(f"Данные настроек не содержат информацию "
                    f"о {broken_settings_parameters}")
                Rich.debug_log("Перезапись настроек")
                self.rewrite_settings()
                Rich.debug_log("Повторное получение настроек")
                return

        except json.JSONDecodeError as e:
            Rich.warning_log(f"Ошибка открытия json файла с настройками. "
                f"Текст ошибки: {e}")

            with open(self.config_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    # Если файл с настройками пуст, то записать стандартные настройки.
                    Rich.warning_log("Файл с настройками пуст")

                    self.write_standard_settings()
                else:
                    # Если файл с настройками битый, то переписать.
                    self.rewrite_settings()

    def print_settings(self) -> None:
        """
        Функция для вывода настроек (при запуске программы в лог)

        Только вывод в лог.

        :return: None.
        """

        Rich.simple_log(f"Время работы таймера показа загрузочного окна: "
            f"{self.loading_window_timer_duration}")
        Rich.simple_log(f"Время показа окна загрузки: {self.flag_show_loading_window}")
        Rich.simple_log(f"Цветовая тема: {self.theme}")

    def update_settings_param(self, param_name: str, new_value: Optional) -> None:
        """
        Обновляет конкретное поле в файле настроек, не трогая остальные.

        :param param_name: Имя поля для обновления (например, "app_name")

        :param new_value: Новое значение для этого поля

        :return: None
        """

        settings_data = {}

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    settings_data = json.load(file)

            except (json.JSONDecodeError, IOError):
                Rich.warning_log(f"Не удалось прочитать файл настроек")

        settings_data[param_name] = new_value

        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(settings_data, file, ensure_ascii=False, indent=4)

        self.settings = settings_data

        Rich.print_spacer()
        Rich.debug_log(f"Обновлено поле '{param_name}' = {new_value}")

    def set_theme(self, theme_name: str) -> None:
        """
        Функция для задания цветовой темы приложения.
        Перепишет настройки на новое значение.

        Атрибут класса настроек (self.theme) получает новое значение.

        :param theme_name: Принимается новое имя темы приложения

        :return: None.
        """
        self.theme = theme_name
        self.update_settings_param("theme", theme_name)

    def get_theme_name(self) -> str:
        """
        Функция для получения имени темы приложения.

        Вернёт значение атрибута класса настроек (имени темы приложения - self.theme).

        :return: Str(self.theme).
        """
        theme_name = self.theme

        return theme_name

    def set_loading_window_timer_duration(self,
            loading_window_timer_duration: int) -> None:
        """
        Функция для задания нового значения таймера загрузочного окна приложения.
        Перепишет настройки на новое значение.

        Атрибут класса настроек (self.loading_window_timer_duration)
        получает новое значение.

        :param loading_window_timer_duration: Принимается новое значения таймера
         загрузочного окна приложения

        :return: None.
        """

        self.loading_window_timer_duration = loading_window_timer_duration
        self.update_settings_param("loading_window_timer",
            loading_window_timer_duration)

    def get_loading_window_timer_duration(self) -> int:
        """
        Функция для получения значения таймера загрузочного окна приложения.

        Вернёт значение атрибута класса настроек
        (значение таймера загрузочного окна приложения -
        self.loading_window_timer_duration).

        :return: Int(self.loading_window_timer_duration).
        """

        loading_window_timer_duration = self.loading_window_timer_duration

        return loading_window_timer_duration


    def get_flag_show_loading_window(self) -> bool:
        """
        Функция для проверки разрешения приложения на показ загрузочного окна

        :return: flag_show - Текущее значение флага, разрешающего или
        запрещающего показ загрузочного окна
        """

        flag_show = self.read_one_param("flag_show_loading_window")

        if flag_show:
            Rich.debug_log("Показ загрузочного окна разрешён")
        else:
            Rich.debug_log("Показ загрузочного окна запрещен")

        return flag_show

    def get_flag_show_loading_window_hide_log(self) -> bool:
        """
        Функция для проверки разрешения приложения на показ загрузочного окна.
        Минимальный вывод информации в лог

        :return: flag_show - Текущее значение флага, разрешающего или
        запрещающего показ загрузочного окна
        """

        flag_show = self.read_one_param_hide_log("flag_show_loading_window")

        return flag_show

    def set_flag_show_loading_window(self, bool_value: bool) -> None:
        """
        Функция для задания нового значения флагу разрешения показа загрузочного окна.

        Атрибут класса настроек (self.flag_show_loading_window) получает новое значение.

        :param bool_value: Принимается новое значения флага для показа загрузочного окна

        :return: None.
        """

        self.flag_show_loading_window = bool_value

        self.update_settings_param("flag_show_loading_window", bool_value)



Settings = SettingsManager()
