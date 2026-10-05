from pathlib import Path
from win32com.client import Dispatch

from utils.output_rich import Rich


def check_exist_shortcut() -> None:
    """
    Функция для проверки существования ярлыка приложения на рабочем столе и его
     создания, если его нет на рабочем столе

    :return: None
    """

    Rich.debug_log("Проверка наличия ярлыка приложения")

    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "PDF Maker.lnk"

    if shortcut_path.exists():
        Rich.debug_log("Ярлык уже есть на рабочем столе")
    else:
        Rich.warning_log("Ярлыка приложения нет")
        create_shortcut()


def bool_exist_exe() -> bool:
    """
    Функция для проверки наличия сборки

    :return: bool - вернёт истину, если сборка есть. Иначе вернёт ложь
    """

    project_root = Path(__file__).resolve().parent.parent.parent
    exe_path = project_root / "dist" / "PDF_Maker" / "PDF_Maker.exe"

    if not exe_path.exists():
        Rich.warning_log(f"Ошибка: .exe не найден по пути: {exe_path}")
        Rich.warning_log("Не найдено сборки проекта")
        return False

    return True


def check_build() -> None:
    """
    Функция для проверки существования собранного проекта и создания ярлыка,
     если это нужно сделать

    :return: bool - флаг, указывающий на наличие/отсутствие сборки проекта
    """

    Rich.debug_log("Проверка наличия сборки приложения")

    if bool_exist_exe():
        Rich.debug_log("Найдена сборка")
        check_exist_shortcut()


def create_shortcut() -> None:
    """
    Создаёт ярлык PDF_Maker на рабочем столе.

    :return: None
    """

    Rich.simple_log("Создание ярлыка для запуска приложения")

    project_root = Path(__file__).resolve().parent.parent.parent

    exe_path = project_root / "dist" / "PDF_Maker" / "PDF_Maker.exe"

    working_dir = exe_path.parent

    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "PDF Maker.lnk"

    # Создание ярлыка
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(exe_path)
    shortcut.WorkingDirectory = str(working_dir)
    shortcut.IconLocation = str(exe_path)
    shortcut.save()

    Rich.success_log("Ярлык создан на рабочем столе")
