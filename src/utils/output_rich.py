import inspect
import os

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()

class Rich:
    """
    Класс с методами вывода логов в консоль с использованием библиотеки Rich
    """

    def __init__(self):
        pass


    @staticmethod
    def log_error(message: str, details: str = "") -> None:
        """
        Вывод панели с текстом ошибки и деталями ошибки (если такая информация есть).
        - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст сообщения ошибки, который будет
        выведен в терминал (консоль)

        :param details: Дефолтно равно пустой строке. Принимает текст детали ошибки,
        который будет выведен в терминал (консоль)

        :return: None
        """

        def get_caller_info() -> str:
            """
            Возвращает имя файла и номер строки, откуда была вызвана функция.

            :return: str - строка с номером строки и именем файла, из которого была
             вызвана функция
            """

            try:
                # Поднимает на два уровня по стеку вызова. Должен быть файл,
                # из которого вызвал функцию

                frame = inspect.currentframe().f_back.f_back
                filename = os.path.basename(frame.f_code.co_filename)
                line = frame.f_lineno

                return f"{filename}:{line}"

            except (AttributeError, KeyError, ValueError, TypeError):
                return "Неизвестно:?"

        caller = get_caller_info()

        content = f"[bold white on red]ERROR[/bold white on red]\n\n{message}"

        if details:
            content += f"\n\n[dim]{details}[/dim]"

        content += f"\n\n[dim]Вызов из: {caller}[/dim]"

        console.print(
            Panel(
                content,
                title="[red]Ошибка[/red]",
                border_style="red",
                padding=(1, 2),
            )
        )


    @staticmethod
    def success_log(message: str) -> None:
        """
        Лог об успешном выполнении (используется при сообщении об успешном выполнении
        какой-то операции) - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст сообщения об успешном выполнении какой-то операции,
        который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(f"[green][SUCCESS] {message}[/green]", _stack_offset=2)


    @staticmethod
    def simple_log(message: str) -> None:
        """
        Обычный лог (информационный) - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст лога (информационный), который будет выведен в
        терминал (консоль)

        :return: None
        """

        console.log(f"[cyan][INFO] {message}[/cyan]", _stack_offset=2)


    @staticmethod
    def debug_log(message: str) -> None:
        """
        Лог для логирования - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст лога, который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(f"[grey46][Debug] {message}[/grey46]", _stack_offset=2)


    @staticmethod
    def warning_log(message: str) -> None:
        """
        Лог-предупреждение о каких-то незначительных проблемах выполнения операции
         - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст лога, который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(f"[bold yellow][WARN] ВНИМАНИЕ: {message}[/bold yellow]", _stack_offset=2)


    @staticmethod
    def enter_log(message: str) -> None:
        """
        Лог, информирующий о запуске какого-нибудь окна интерфейса.
        Например, если запустится загрузочное окно, то выведется лог о "входе" в это окно.

        :param message: Принимает текст сообщения о входе (показе) в какое-то окно.

        :return: None
        """

        console.log(f"[magenta][ENTER] ▶ ВХОД: {message}[/magenta]",  _stack_offset=2)


    @staticmethod
    def exit_log(message: str) -> None:
        """
        Лог, информирующий о закрытии какого-нибудь окна интерфейса.
        Например, если закрыть основное окно приложения, то выведется лог о "выходе" из
        этого окна.

        :param message: Принимает текст сообщения о выходе (закрытии) в какого-то окна.

        :return: None
        """
        console.log(f"[magenta][EXIT] ◀ ВЫХОД: {message}[/magenta]",  _stack_offset=2)


    @staticmethod
    def print_spacer() -> None:
        """
        Разделитель для более наглядного показа лога процессов в консоли

        :return: None
        """

        console.log(f"[grey46][Debug] {'-' * 151}[/grey46]", _stack_offset=2)


    @staticmethod
    def print_spacer_points() -> None:
        """
        Разделитель для более наглядного показа лога процессов в консоли -
        разделитель в виде точек

        :return: None
        """

        console.log(f"[grey46][Debug] {'.' * 151}[/grey46]", _stack_offset=2)


    @staticmethod
    def print_table(title: str, cols: list, rows: list) -> None:
        """
        Функция для вывода таблицы в консоль с помощью библиотеки Rich

        :param title: Str - Принимает заголовок таблицы
        :param cols: list - Принимает список с содержимым столбцов
        :param rows: list - Принимает список с содержимым строк

        :return: None
        """

        table = Table(title=title)

        for col in cols:
            table.add_column(col)

        for row in rows:
            table.add_row(*[str(cell) for cell in row])

        console.print(table)
