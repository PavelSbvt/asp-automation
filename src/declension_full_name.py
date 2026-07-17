from name_and_surname_exceptions import NAME_EXCEPTIONS, SURNAME_EXCEPTIONS


def _get_fio_accusative(fio: str, citizenship: str = "РФ") -> str:
    """
    Преобразует ФИО из именительного падежа в винительный.
    Используется для "СЛУШАЛИ" (слушали кого?)
    Для граждан РФ - склоняем, для иностранцев - не склоняем.
    """

    # Проверяем гражданство
    if citizenship not in ["Россия", "РФ", "Российская Федерация"]:
        return fio

    parts = fio.split()
    if not parts:
        return fio

    # Если только имя
    if len(parts) == 1:
        name = parts[0]
        # Определяем пол по окончанию имени
        is_male = not (name.endswith('а') or name.endswith('я'))
        return _decline_name_accusative(name, is_male)

    # Полное ФИО (3+ части)
    surname = parts[0]
    name = parts[1]
    patronymic = parts[2]

    # Определяем пол по отчеству
    is_male = patronymic.endswith('ич') or patronymic.endswith('ович') or patronymic.endswith('евич')

    surname_acc = _decline_surname_accusative(surname, is_male)
    name_acc = _decline_name_accusative(name, is_male)
    patronymic_acc = _decline_patronymic_accusative(patronymic, is_male)

    return f"{surname_acc} {name_acc} {patronymic_acc}"

def _decline_surname_accusative(surname: str, is_male: bool) -> str:
    """
    Склоняет фамилию в винительный падеж
    """

    if not surname:
        return surname

    # Проверка исключений для фамилий
    surname_lower = surname.lower()
    if surname_lower in SURNAME_EXCEPTIONS:
        if surname[0].isupper():
            return SURNAME_EXCEPTIONS[surname_lower].capitalize()
        return SURNAME_EXCEPTIONS[surname_lower]

    # ЖЕНСКИЕ ФАМИЛИИ
    if not is_male:
        if surname.endswith('а'):
            return surname[:-1] + 'у'
        elif surname.endswith('я'):
            return surname[:-1] + 'ю'
        else:
            return surname

    # МУЖСКИЕ ФАМИЛИИ
    if surname.endswith('ов'):
        return surname[:-2] + 'ова'
    elif surname.endswith('ев'):
        return surname[:-2] + 'ева'
    elif surname.endswith('ёв'):
        return surname[:-2] + 'ёва'
    elif surname.endswith('ин'):
        return surname[:-2] + 'ина'
    elif surname.endswith('ын'):
        return surname[:-2] + 'ына'
    elif surname.endswith('ий'):
        return surname[:-2] + 'ого'
    elif surname.endswith('ой'):
        return surname[:-2] + 'ого'
    elif surname.endswith('ый'):
        return surname[:-2] + 'ого'
    elif surname.endswith('ь'):
        return surname[:-1] + 'я'
    elif surname.endswith('й'):
        return surname[:-1] + 'я'
    elif surname.endswith('а') or surname.endswith('я'):
        return surname
    else:
        return surname + 'а'


def _decline_name_accusative(name: str, is_male: bool) -> str:
    """
    Склоняет имя в винительный падеж
    """

    if not name:
        return name

    # ПРОВЕРКА ИСКЛЮЧЕНИЙ
    name_lower = name.lower()
    if name_lower in NAME_EXCEPTIONS:
        # Если имя с заглавной буквы, возвращаем с заглавной
        if name[0].isupper():
            return NAME_EXCEPTIONS[name_lower].capitalize()
        return NAME_EXCEPTIONS[name_lower]

    # МУЖСКИЕ ИМЕНА
    if is_male:
        if name.endswith('ий'):
            return name[:-2] + 'ия'
        elif name.endswith('й'):
            return name[:-1] + 'я'
        elif name.endswith('ь'):
            return name[:-1] + 'я'
        elif name.endswith('а'):
            return name[:-1] + 'у'
        elif name.endswith('я'):
            return name[:-1] + 'ю'
        else:
            return name + 'а'

    # ЖЕНСКИЕ ИМЕНА
    else:
        if name.endswith('а'):
            return name[:-1] + 'у'
        elif name.endswith('я'):
            return name[:-1] + 'ю'
        elif name.endswith('ь'):
            return name
        elif name.endswith('й'):
            return name[:-1] + 'ю'
        else:
            return name + 'у'


def _decline_patronymic_accusative(patronymic: str, is_male: bool) -> str:
    """
    Склоняет отчество в винительный падеж
    """

    if not patronymic:
        return patronymic

    if is_male:
        if patronymic.endswith('ич'):
            return patronymic[:-2] + 'ича'
        elif patronymic.endswith('на'):
            return patronymic[:-1] + 'у'
        else:
            return patronymic + 'а'
    else:
        if patronymic.endswith('на'):
            return patronymic[:-1] + 'у'
        else:
            return patronymic + 'у'


def _get_fio_initials(fio: str) -> str:
    """
    Преобразует ФИО в формат / И.О. Фамилия /
    """

    parts = fio.split()
    if len(parts) < 2:
        return fio

    surname = parts[0]
    # Берем первые буквы имени и отчества
    initials = []
    for part in parts[1:]:
        if part:
            initials.append(part[0].upper())

    if not initials:
        return fio

    initials_str = '.'.join(initials) + '.'
    result = f"/ {initials_str} {surname} /"

    # Убираем лишние точки
    if result.endswith(' . /'):
        result = result[:-3] + ' /'

    return result

# Тестовые примеры
test_data = [
    ("Иванов Иван Иванович", "РФ"),
    # для быстрого теста
]

def test_fio_declension() -> None:
    """
    Тестирование склонения ФИО в винительный падеж.

    Выводит результаты склонения для каждого тестового случая.
    Используется для отладки и проверки корректности склонения.
    """

    print("ТЕСТИРОВАНИЕ СКЛОНЕНИЯ ФИО")
    print("-" * 50)

    for fio, citizenship in test_data:
        result = _get_fio_accusative(fio, citizenship)
        print(f"{fio} ({citizenship}) = {result}")

if __name__ == "__main__":
    test_fio_declension()
