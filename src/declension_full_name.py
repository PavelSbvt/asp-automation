from pytrovich.enums import NamePart, Case
from pytrovich.maker import PetrovichDeclinationMaker
from pytrovich.detector import PetrovichGenderDetector


# экземпляры
_petrovich_maker = PetrovichDeclinationMaker()
_petrovich_detector = PetrovichGenderDetector()

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

    # Полное ФИО
    surname = parts[0]
    name = parts[1]
    patronymic = parts[2]

    # пол с помощью pytrovich
    gender = _petrovich_detector.detect(firstname=name, middlename=patronymic)

    surname_acc = _petrovich_maker.make(NamePart.LASTNAME, gender, Case.ACCUSATIVE, surname)
    name_acc = _petrovich_maker.make(NamePart.FIRSTNAME, gender, Case.ACCUSATIVE, name)
    patronymic_acc = _petrovich_maker.make(NamePart.MIDDLENAME, gender, Case.ACCUSATIVE, patronymic)

    return f"{surname_acc} {name_acc} {patronymic_acc}"

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
    ("Пуха Анастасия Павловна", "РФ"),
    ("Иванов Иван Иванович", "РФ"),
    ("Петрова Анна Сергеевна", "РФ"),
    ("Смирнов Николай Петрович", "РФ"),
    ("Кузнецова Мария Алексеевна", "РФ"),
    ("Павлов Павел Павлович", "РФ"),
    ("Львов Лев Львович", "РФ"),
    ("Высоцкий Владимир Семёнович", "РФ"),
    ("Толстой Лев Николаевич", "РФ"),
    ("Достоевский Фёдор Михайлович", "РФ"),
    ("Ким Илья Ильич", "РФ"),  # корейская фамилия
    ("Шмидт Иван Иванович", "РФ"),  # немецкая фамилия
    ("Мюллер Анна Петровна", "РФ"),  # немецкая фамилия
]

def test_fio_declension() -> None:
    """
    Тестирование склонения ФИО в винительный падеж.
    """

    print("ТЕСТИРОВАНИЕ СКЛОНЕНИЯ ФИО (с pytrovich)")
    print("-" * 60)

    for fio, citizenship in test_data:
        result = _get_fio_accusative(fio, citizenship)
        print(f"{fio} ({citizenship}) = {result}")


def get_fio_initials_for_user(fio: str) -> str:
    """
    Утилитарная функция для получения инициалов из ФИО.
    Используется в основном коде.
    """

    return _get_fio_initials(fio)


def get_fio_in_accusative(fio: str, citizenship: str = "РФ") -> str:
    """
    Утилитарная функция для получения ФИО в винительном падеже.
    Используется в основном коде.
    """

    return _get_fio_accusative(fio, citizenship)


if __name__ == "__main__":
    test_fio_declension()
