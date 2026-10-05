from datetime import datetime
from pathlib import Path
import traceback
from typing import List, Tuple, Optional

from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QApplication, QMessageBox
import requests

from utils.output_rich import Rich


ParsingDir = Path("resources/parsing_data")

def get_current_cache_file() -> Optional[Path]:
    """
    Находит текущий файл с данными в папке parsing_data.
    Возвращает путь к файлу или None, если файлов нет.

    :return: Optional[Path] - Вернёт путь к файлу с кешем с кодами и профилями
    аспирантов или не вернёт ничего, если не найдёт ни одного файла с кешем
    или не найдёт папку для парсинга.
    """

    if not ParsingDir.exists():
        return None

    files = list(ParsingDir.glob("*.txt"))

    if not files:
        return None

    # Сортируем по времени модификации (самый свежий последний)
    # на всякий случай
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return files[0]  # самый свежий файл - на всякий случай


def load_specialties_from_cache() -> Optional[List[Tuple[str, str]]]:
    """
    Загружает данные из текущего файла кэша.
    Если файлов нет - возвращает None.

    :return: Optional[List[Tuple[str, str]]] - Вернёт массив из кортежей с
    кодами и профилями аспирантов, но может не вернуть ничего
    (если появится ошибка или не найдётся файл с кешем).
    """

    Rich.print_spacer()

    try:
        current_file = get_current_cache_file()

        if current_file is None:
            Rich.warning_log("Файл кэша не найден")
            return None

        # Имя файла = время обновления
        update_time = current_file.stem  # убираем расширение .txt

        specialties = []
        with open(current_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '|' in line:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        specialties.append((parts[0], parts[1]))

        return specialties

    except Exception as e:
        Rich.log_error(f"Ошибка загрузки кэша: {e}")
        return None


def save_specialties_to_cache(specialties: List[Tuple[str, str]]) -> None:
    """
    Сохраняет данные в файл с текущей датой и временем в имени.
    Старый файл удаляется - перезаписывается (остаётся только один свежий).
    Формат: 2026-07-17-14-30-25.txt

    :param specialties: Принимает массив из кортежей, содержащих код и профиль аспиранта

    :return: None
    """

    Rich.print_spacer()

    try:
        # Создаём папку, если её нет
        if not ParsingDir.exists():
            ParsingDir.mkdir(parents=True)
            Rich.debug_log(f"Создана папка: {ParsingDir}")

        # Удаляем старый файл (если есть)
        old_file = get_current_cache_file()
        if old_file:
            old_file.unlink()
            Rich.debug_log(f"Удалён старый файл: {old_file.name}")

        # Имя файла = текущая дата и время
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filepath = ParsingDir / f"{now}.txt"

        # Сохраняем данные
        with open(filepath, 'w', encoding='utf-8') as f:
            for code, name in specialties:
                f.write(f"{code}|{name}\n")

        Rich.success_log(f"Сохранено {len(specialties)} специальностей в кеш.")
        Rich.simple_log(f"Новый файл кеша: {filepath}")

    except Exception as e:
        Rich.log_error(f"Ошибка сохранения кэша: {e}")


def get_last_update_time() -> str:
    """
    Возвращает время последнего обновления из имени файла.
    Имя файла - время последнего сохранения

    :return: Str - имя файла - время последнего обновления кеша.
    """

    current_file = get_current_cache_file()

    if current_file:
        return current_file.stem

    return "данные не загружены"


def get_specialty_code(profile: str) -> str:
    """
    Возвращает код специальности по названию профиля.
    Сначала проверяет кэш, если данных нет - парсит сайты.

    :param profile: Принимает название профиля аспиранта.

    :return: Str - код специальности аспиранта (по названию профиля).
    """

    try:
        # Пробуем загрузить из кэша
        specialties = load_specialties_from_cache()

        if specialties is None:
            # Если кэша нет - парсим сайты
            Rich.print_spacer()
            Rich.simple_log("Кэш пуст, выполнение парсинга сайтов")
            specialties = site_parce_main()
            if not specialties:
                specialties = site_parce_dn()

            if specialties:
                save_specialties_to_cache(specialties)
            else:
                Rich.print_spacer()
                Rich.warning_log("Не удалось получить данные с сайтов")
                return ""

        # Ищем совпадение
        for code, name in specialties:
            if profile.lower() in name.lower():
                return code

        return ""

    except Exception as e:
        Rich.log_error(f"Ошибка в get_specialty_code: {e}")
        return ""


def update_data(self) -> None:
    """
    Принудительное обновление данных с сайтов.
    Вызывается по кнопке "Обновить данные".

    :return: None
    """

    Rich.print_spacer()
    Rich.simple_log("Обновление данных кодов и шифров аспирантов")

    try:
        # Обновляем текст в интерфейсе
        if hasattr(self, 'label_for_info_update_site_paring'):
            self.label_for_info_update_site_paring.setText("Обновление данных...")
            QApplication.processEvents()

        # Парсим основной сайт
        Rich.debug_log("Парсинг основного сайта (tstu.ru)...")
        specialties = site_parce_main()

        # Если основной сайт не дал данных - пробуем резервный
        if not specialties:
            Rich.debug_log("Парсинг резервного сайта (dn.tstu.ru)...")
            specialties = site_parce_dn()

        if specialties:
            # Сохраняем данные (старый файл удалится)
            save_specialties_to_cache(specialties)

            # Получаем время из имени файла
            update_time = get_last_update_time()

            if hasattr(self, 'time_update_label'):
                self.time_update_label.setText(update_time)

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Последнее обновление данных (парсинг сайтов):"
                )

            QMessageBox.information(
                self,
                "Обновление завершено",
                f"Данные успешно обновлены!\n\n"
                f"Загружено специальностей: {len(specialties)}\n"
                f"Время обновления: {update_time}"
            )
            Rich.success_log(
                f"Данные обновлены! Загружено {len(specialties)} специальностей")

        else:
            QMessageBox.warning(
                self,
                "Ошибка обновления",
                "Не удалось получить данные с сайтов.\n\n"
                "Проверьте подключение к интернету."
            )
            Rich.log_error("Не удалось получить данные с сайтов")

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Ошибка обновления данных (проверьте интернет):"
                )

    except Exception as e:
        Rich.log_error(f"Ошибка при обновлении данных: {e}")
        traceback.print_exc()

        QMessageBox.critical(
            self,
            "Ошибка",
            f"Не удалось обновить данные:\n{str(e)}"
        )

        if hasattr(self, 'label_for_info_update_site_paring'):
            self.label_for_info_update_site_paring.setText(
                "Ошибка обновления данных:"
            )


def site_parce_dn() -> List[Tuple[str, str]]:
    """
    Парсинг данных (профилей и их кодов) аспирантов с сайта магистратуры (резервного)

    :return: List[Tuple[str, str]] - возвращает массив из кортежей из кода
    и профиля аспиранта.
    """

    url = 'http://dn.tstu.ru/index.php/specialties'

    response = None
    for attempt in range(1, 4):  # 3 попытки
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            Rich.print_spacer()
            Rich.warning_log(f"dn.tstu.ru: попытка {attempt}/3 не удалась: {e}")
            if attempt == 3:
                Rich.print_spacer()
                Rich.log_error("dn.tstu.ru: не удалось получить страницу")
                return []

    soup = BeautifulSoup(response.text, 'html.parser')

    target_table = None
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'Шифр и наименование научной специальности' in headers:
            target_table = table
            break

    if target_table is None:
        Rich.warning_log("dn.tstu.ru: таблица не найдена на странице")
        return []

    specialties = []
    for row in target_table.find_all('tr'):
        cols = row.find_all('td')
        if not cols:
            continue

        if len(cols) == 3:
            code = cols[1].get_text(strip=True)
            name = cols[2].get_text(strip=True)
            if code and code.endswith('.') and ' ' not in code:
                specialties.append((code, name))
        elif len(cols) == 2:
            code = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            if code and code.endswith('.') and ' ' not in code:
                specialties.append((code, name))

    return specialties


def site_parce_main() -> List[Tuple[str, str]]:
    """
    Парсинг данных (аспирантов) профилей и их кодов с сайта ТГТУ

    :return: List[Tuple[str, str]] - возвращает массив из кортежей из кода
    и профиля аспиранта.
    """

    url = 'https://www.tstu.ru/r.php?r=postup.abitur.na_sp'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }  # Имитируем браузер

    Rich.print_spacer()

    response = None
    for attempt in range(1, 4):  # 3 попытки
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            Rich.warning_log(f"tstu.ru: попытка {attempt}/3 не удалась: {e}")
            if attempt == 3:
                Rich.log_error("tstu.ru: не удалось получить страницу")
                return []

    soup = BeautifulSoup(response.text, 'html.parser')

    target_table = None
    for header in soup.find_all(['h4', 'font'], class_='head4'):
        # цикл по всем элементам, чтобы найти таблицу с заголовком "Аспирантура"
        if header.get_text(strip=True) == 'Аспирантура':
            target_table = header.find_next('table')
            break

    if target_table is None:  # Поиск по якорю, если не нашлось по тегам
        anchor = soup.find('a', attrs={'name': '4'})
        if anchor:
            next_tag = anchor.find_next()
            while next_tag and next_tag.name != 'table':
                next_tag = next_tag.find_next()
            target_table = next_tag

    if target_table is None:
        Rich.warning_log("tstu.ru: таблица не найдена на странице")
        return []

    specialties = []
    for row in target_table.find_all('tr'):
        # Добавляем каждый код и каждый профиль в список как кортеж
        cols = row.find_all('td')
        if not cols:
            continue
        if len(cols) >= 2:  # Проверяем сколько ячеек в строке
            code = cols[-2].get_text(strip=True)  # Код профиля из предпоследней ячейки
            name = cols[-1].get_text(strip=True)  # Название профиля из последней ячейки
            if code and '.' in code and ' ' not in code:
                specialties.append((code, name))

    return specialties
