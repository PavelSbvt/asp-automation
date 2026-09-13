import os
import inspect

from rich.console import Console
from rich.panel import Panel


console = Console(width=200)

class RichLog:
    """
    Класс с методами вывода логов в консоль с использованием библиотеки Ruch
    """

    def __init__(self):
        pass

    def get_caller_info(self) -> str:
        """
        Возвращает имя файла и номер строки, откуда была вызвана функция.

        :return: Str - строка с номером строки и именем файла, из которого была
        вызвана функция
        """

        try:
            # Поднимает на два уровня по стеку вызова. Должен быть файл,
            # из которого вызвал функцию

            frame = inspect.currentframe().f_back.f_back
            filename = os.path.basename(frame.f_code.co_filename)
            line= frame.f_lineno

            return f"{filename}:{line}"

        except (AttributeError, KeyError, ValueError, TypeError):
            return "Неизвестно:?"

    def log_error(self, message: str, details: str = "") -> None:
        """
        Вывод панели с текстом ошибки и деталями ошибки (если такая информация есть).
        - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст сообщения ошибки, который будет
        выведен в терминал (консоль)

        :param details: Дефолтно равно пустой строке. Принимает текст детали ошибки,
        который будет выведен в терминал (консоль)

        :return: None
        """

        caller = self.get_caller_info()

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

    def success_log(self, message: str) -> None:
        """
        Лог об успешном выполнении (используется при сообщении об успешном выполнении
        какой-то операции) - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает текст сообщения об успешном выполнении
         какой-то операции, который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(f"[green][SUCCESS] {message}[/green]",  _stack_offset=2)

    def simple_log(self, message: str) -> None:
        """
        Обычный лог (информационный) - вывод в терминал
         (с использованием библиотеки Rich)

        :param message: Принимает текст лога (информационный), который будет выведен в
        терминал (консоль)

        :return: None
        """

        console.log(f"[cyan][INFO] {message}[/cyan]",  _stack_offset=2)

    def debug_log(self, message: str) -> None:
        """
        Лог для дебаггинга - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает тест дебаг лога,
         который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(f"[grey46][Debug] {message}[/grey46]",  _stack_offset=2)

    def warning_log(self, message: str) -> None:
        """
        Лог-предупреждение о каких-то незначительных проблемах выполнения операции
         - вывод в терминал (с использованием библиотеки Rich)

        :param message: Принимает тест лога, который будет выведен в терминал (консоль)

        :return: None
        """

        console.log(
            f"[bold yellow][WARN] ВНИМАНИЕ: {message}[/bold yellow]",  _stack_offset=2)

    def enter_log(self, message: str) -> None:
        """
        Лог, информирующий о запуске какого-нибудь окна интерфейса.
        Например, если запустится загрузочное окно, то выведется лог о "входе" в это окно.

        :param message: Принимает текст сообщения о входе (показе) в какое-то окно.

        :return: None
        """

        console.log(f"[magenta][ENTER] ▶ ВХОД: {message}[/magenta]",  _stack_offset=2)

    def exit_log(self, message: str) -> None:
        """
        Лог, информирующий о закрытии какого-нибудь окна интерфейса.
        Например, если закрыть основное окно приложения, то выведется лог о "выходе" из
        этого окна.

        :param message: Принимает текст сообщения о выходе (закрытии) в какого-то окна.

        :return: None
        """
        console.log(f"[magenta][EXIT] ◀ ВЫХОД: {message}[/magenta]",  _stack_offset=2)

    def print_spacer(self) -> None:
        """
        Разделитель для более наглядного показа лога процессов в консоли

        :return: None
        """

        console.log(f"[grey46 dim][Spacer] {"-" * 130}[/grey46 dim]", _stack_offset=2)

    def print_spacer_points(self) -> None:
        """
        Разделитель для более наглядного показа лога процессов в консоли -
        разделитель в виде точек

        :return: None
        """

        console.log(f"[grey46 dim][Spacer] {"." * 130}[/grey46 dim]", _stack_offset=2)



Rich = RichLog()
