from rich.console import Console
from rich.panel import Panel


console = Console()

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

    content = f"[bold white on red] ⚠️ ОШИБКА ⚠️ [/bold white on red]\n\n{message}"
    if details:
        content += f"\n\n[dim]{details}[/dim]"

    console.print(
        Panel(
            content,
            title="[red]Ошибка[/red]",
            border_style="red",
            padding=(1, 2)
        )
    )

def success_log(message: str) -> None:
    """
    Лог об успешном выполнении (используется при сообщении об успешном выполнении
    какой-то операции) - вывод в терминал (с использованием библиотеки Rich)

    :param message: Принимает текст сообщения об успешном выполнении какой-то операции,
    который будет выведен в терминал (консоль)

    :return: None
    """

    console.log(f"[green]{message}[/green]")

def simple_log(message: str) -> None:
    """
    Обычный лог (информационный) - вывод в терминал (с использованием библиотеки Rich)

    :param message: Принимает текст лога (информационный), который будет выведен в
    терминал (консоль)

    :return: None
    """

    console.log(f"[cyan]i {message}[/cyan]")

def debug_log(message: str) -> None:
    """
    Лог для дебаггинга - вывод в терминал (с использованием библиотеки Rich)

    :param message: Принимает тест дебаг лога, который будет выведен в терминал (консоль)

    :return: None
    """

    console.log(f"[grey46][Debug] {message}[/grey46]")

def warning_log(message: str) -> None:
    """
    Лог-предупреждение о каких-то незначительных проблемах выполнения операции
     - вывод в терминал (с использованием библиотеки Rich)

    :param message: Принимает тест лога, который будет выведен в терминал (консоль)

    :return: None
    """

    console.log(f"[bold yellow] ⚠ ВНИМАНИЕ: {message}[/bold yellow]")

def enter_log(message: str) -> None:
    """
    Лог, информирующий о запуске какого-нибудь окна интерфейса.
    Например, если запустится загрузочное окно, то выведется лог о "входе" в это окно.

    :param message: Принимает текст сообщения о входе (показе) в какое-то окно.

    :return: None
    """

    console.log(f"[magenta]▶ ВХОД: {message}[/magenta]")

def exit_log(message: str) -> None:
    """
    Лог, информирующий о закрытии какого-нибудь окна интерфейса.
    Например, если закрыть основное окно приложения, то выведется лог о "выходе" из
    этого окна.

    :param message: Принимает текст сообщения о выходе (закрытии) в какого-то окна.

    :return: None
    """
    console.log(f"[magenta]◀ ВЫХОД: {message}[/magenta]")
