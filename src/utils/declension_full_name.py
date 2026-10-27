from pytrovich.detector import PetrovichGenderDetector
from pytrovich.enums import NamePart, Case
from pytrovich.maker import PetrovichDeclinationMaker


petrovichMaker = PetrovichDeclinationMaker()
petrovichDetector = PetrovichGenderDetector()


def get_fio_accusative(fio: str, citizenship: str = "РФ") -> str:
    """
    Преобразует ФИО из именительного падежа в винительный.
    Используется для "СЛУШАЛИ" (слушали кого?)
    Для граждан РФ - склоняем, для иностранцев - не склоняем.

    :param fio: Принимает исходное фио в И.П.

    :param citizenship: дефолтное значение "РФ" - гражданство

    :return: Str - склонённое фио (иностранные фио не склоняются)
    """

    # Проверяем гражданство
    if citizenship not in ["Россия", "РФ", "Российская Федерация"]:
        return fio

    parts = fio.split()
    if not parts:
        return fio

    # Полное ФИО
    surname = parts[0]
    name = parts[1]
    patronymic = parts[2]

    # пол с помощью pytrovich
    gender = petrovichDetector.detect(firstname=name, middlename=patronymic)

    surname_acc = petrovichMaker.make(NamePart.LASTNAME, gender, Case.ACCUSATIVE, surname)
    name_acc = petrovichMaker.make(NamePart.FIRSTNAME, gender, Case.ACCUSATIVE, name)
    patronymic_acc = petrovichMaker.make(NamePart.MIDDLENAME, gender, Case.ACCUSATIVE, patronymic)

    return f"{surname_acc} {name_acc} {patronymic_acc}"


def get_fio_initials(fio: str) -> str:
    """
    Преобразует ФИО в формат / И.О. Фамилия /

    :param fio: Принимает фио, которое нужно преобразовать.

    :return: Str - обработанное фио
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


def get_fio_initials_for_user(fio: str) -> str:
    """
    Утилитарная функция для получения инициалов из ФИО.
    Используется в основном коде.

    :param fio: Str - принимает фио, из которого нужно составить строку с инициалами

    :return: Str - строка с инициалами
    """

    return get_fio_initials(fio)


def get_fio_in_accusative(fio: str, citizenship: str = "РФ") -> str:
    """
    Утилитарная функция для получения ФИО в винительном падеже.
    Используется в основном коде.

    :param fio: Принимает исходное фио в И.П.

    :param citizenship: дефолтное значение "РФ" - гражданство

    :return: Str - склонённое фио (иностранные фио не склоняются)
    """

    return get_fio_accusative(fio, citizenship)
