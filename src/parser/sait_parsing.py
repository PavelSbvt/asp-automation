import traceback
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QApplication, QMessageBox


PARSING_DIR = Path("resources/parsing_data")
FILE_PATTENR = "*.txt"

def get_current_cache_file() -> Optional[Path]:
    """
    Находит текущий файл с данными в папке parsing_data.
    Возвращает путь к файлу или None, если файлов нет.

    :return: Optional[Path] - Вернёт путь к файлу с кешем с кодами и профилями
    аспирантов или не вернёт ничего, если не найдёт ни одного файла с кешем
    или не найдёт папку для парсинга.
    """

    if not PARSING_DIR.exists():
        return None

    files = list(PARSING_DIR.glob("*.txt"))

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

    try:
        current_file = get_current_cache_file()

        if current_file is None:
            print("[I] Файл кэша не найден")
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

        print(f"[I] Загружено {len(specialties)} специальностей")
        print(f"[I] Файл: {current_file.name}")
        print(f"[I] Время обновления: {update_time}")

        return specialties

    except Exception as e:
        print(f"[E] Ошибка загрузки кэша: {e}")
        return None

def save_specialties_to_cache(specialties: List[Tuple[str, str]]) -> None:
    """
    Сохраняет данные в файл с текущей датой и временем в имени.
    Старый файл удаляется - перезаписывается (остаётся только один свежий).
    Формат: 2026-07-17_14-30-25.txt

    :param specialties: Принимает массив из кортежей, содержащих код и профиль аспиранта

    :return: None
    """

    try:
        # Создаём папку, если её нет
        if not PARSING_DIR.exists():
            PARSING_DIR.mkdir(parents=True)
            print(f"[I] Создана папка: {PARSING_DIR}")

        # Удаляем старый файл (если есть)
        old_file = get_current_cache_file()
        if old_file:
            old_file.unlink()
            print(f"[I] Удалён старый файл: {old_file.name}")

        # Имя файла = текущая дата и время
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = PARSING_DIR / f"{now}.txt"

        # Сохраняем данные
        with open(filepath, 'w', encoding='utf-8') as f:
            for code, name in specialties:
                f.write(f"{code}|{name}\n")

        print(f"[I] Сохранено {len(specialties)} специальностей")
        print(f"[I] Новый файл: {filepath}")

    except Exception as e:
        print(f"[E] Ошибка сохранения кэша: {e}")

def get_last_update_time() -> str:
    """
    Возвращает время последнего обновления из имени файла.
    Имя файла - время последнего сохранения

    :return: Str - имя файла - время последнего обновления кеша.
    """

    current_file = get_current_cache_file()

    if current_file:
        return current_file.stem  # убираем расширение .txt

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
            print("[I] Кэш пуст, выполняем парсинг сайтов...")
            specialties = site_parce_main()
            if not specialties:
                specialties = site_parce_dn()

            if specialties:
                save_specialties_to_cache(specialties)
            else:
                print("[E] Не удалось получить данные с сайтов")
                return ""

        # Ищем совпадение
        for code, name in specialties:
            if profile.lower() in name.lower():
                return code

        return ""

    except Exception as e:
        print(f"[E] Ошибка в get_specialty_code: {e}")
        return ""

def update_data(self) -> None:
    """
    Принудительное обновление данных с сайтов.
    Вызывается по кнопке "Обновить данные".

    :return: None
    """

    print("[I] обновление данных кодов и шифров аспирантов")

    try:
        # Обновляем текст в интерфейсе
        if hasattr(self, 'label_for_info_update_site_paring'):
            self.label_for_info_update_site_paring.setText("Обновление данных...")
            QApplication.processEvents()

        # Парсим основной сайт
        print("[I] Парсинг основного сайта (tstu.ru)...")
        specialties = site_parce_main()

        # Если основной сайт не дал данных - пробуем резервный
        if not specialties:
            print("[I] Парсинг резервного сайта (dn.tstu.ru)...")
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
            print(f"[S] Данные обновлены! Загружено {len(specialties)} специальностей")

        else:
            QMessageBox.warning(
                self,
                "Ошибка обновления",
                "Не удалось получить данные с сайтов.\n\n"
                "Проверьте подключение к интернету."
            )
            print("[E] Не удалось получить данные с сайтов")

            if hasattr(self, 'label_for_info_update_site_paring'):
                self.label_for_info_update_site_paring.setText(
                    "Ошибка обновления данных (проверьте интернет):"
                )

    except Exception as e:
        print(f"[E] Ошибка при обновлении данных: {e}")
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
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    target_table = None
    for table in soup.find_all('table'):  # Цикл по всем таблицам на сайте
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'Шифр и наименование научной специальности' in headers: # Поиск нужной таблицы
            target_table = table
            break
    if target_table is None:
        return []

    specialties = []
    for row in target_table.find_all('tr'):# Добавление кода, профиль в список как кортеж
        cols = row.find_all('td')
        if not cols:
            continue

        # Проверяем сколько яйчеек в строке
        if len(cols) == 3:  # Если 3, то берём код и специальность из 2 и 3
            code = cols[1].get_text(strip=True)
            name = cols[2].get_text(strip=True)
            if code and code.endswith('.') and ' ' not in code:
                specialties.append((code, name))
        elif len(cols) == 2:  # Если 2, то код и специальность из 1 и 2
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
    response = requests.get(url, headers=headers, timeout=60)
    # Пытаемся получить ответ от сайта
    response.raise_for_status()

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

    specialties = []
    for row in target_table.find_all('tr'):
        # Добавляем каждый код и каждый профиль в список как кортеж
        cols = row.find_all('td')
        if not cols:
            continue
        if len(cols) >= 2:  # Проверяем сколько яйчеек в строке
            code = cols[-2].get_text(strip=True)  # Код профиля из предпоследней ячейки
            name = cols[-1].get_text(strip=True)  # Название профиля из последней ячейки
            if code and '.' in code and ' ' not in code:
                specialties.append((code, name))

    return specialties
