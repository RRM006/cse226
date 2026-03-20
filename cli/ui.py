import os
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, PromptBase
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console()

def rich_available() -> bool:
    if not RICH_AVAILABLE:
        return False
    try:
        console.print("[cyan]Rich library loaded successfully[/cyan]")
        return True
    except Exception:
        return False

def print_title(text: str):
    if RICH_AVAILABLE:
        console.print(Panel(f"[bold cyan]{text}[/bold cyan]", border_style="cyan"))
    else:
        print("=" * 60)
        print(text.upper())
        print("=" * 60)

def print_success(text: str):
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/bold green] {text}")
    else:
        print(f"✅ {text}")

def print_error(text: str):
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/bold red] {text}")
    else:
        print(f"❌ {text}")

def print_warning(text: str):
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]![/bold yellow] {text}")
    else:
        print(f"⚠️ {text}")

def print_info(text: str):
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ[/bold blue] {text}")
    else:
        print(f"ℹ️ {text}")

def print_menu_item(number: int, text: str, selected: bool = False):
    if RICH_AVAILABLE:
        prefix = "[bold yellow]▶[/bold yellow]" if selected else " "
        console.print(f"{prefix}  [cyan]{number}.[/cyan] {text}")
    else:
        mark = "→" if selected else " "
        print(f"{mark} {number}. {text}")

def print_header(text: str):
    if RICH_AVAILABLE:
        console.print(f"\n[bold cyan]{text}[/bold cyan]")
    else:
        print(f"\n--- {text} ---")

def print_divider():
    if RICH_AVAILABLE:
        console.print("[dim]" + "─" * 50 + "[/dim]")
    else:
        print("-" * 50)

def prompt_input(message: str, default: str = None) -> str:
    if RICH_AVAILABLE:
        try:
            return Prompt.ask(f"[blue]{message}[/blue]").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
    else:
        try:
            suffix = f" [{default}]" if default else ""
            response = input(f"➤ {message}{suffix}: ").strip()
            return response if response else (default or "")
        except (EOFError, KeyboardInterrupt):
            return ""

def prompt_yes_no(message: str, default: bool = True) -> bool:
    if RICH_AVAILABLE:
        try:
            return Confirm.ask(f"[blue]{message}[/blue]", default=default)
        except (EOFError, KeyboardInterrupt):
            return False
    else:
        suffix = "[Y/n]" if default else "[y/N]"
        try:
            response = input(f"➤ {message} {suffix}: ").strip().lower()
            if not response:
                return default
            return response in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False

def prompt_choice(message: str, choices: list) -> int:
    if RICH_AVAILABLE:
        try:
            choice_map = {str(i+1): i for i in range(len(choices))}
            while True:
                choice = Prompt.ask(f"[blue]{message}[/blue]", choices=list(choice_map.keys()))
                if choice in choice_map:
                    return choice_map[choice]
                print_warning("Invalid choice. Please try again.")
        except (EOFError, KeyboardInterrupt):
            return -1
    else:
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        while True:
            try:
                response = input(f"➤ {message}: ").strip()
                if not response:
                    continue
                try:
                    idx = int(response) - 1
                    if 0 <= idx < len(choices):
                        return idx
                except ValueError:
                    pass
                print("Invalid choice. Please try again.")
            except (EOFError, KeyboardInterrupt):
                return -1

def with_spinner(message: str, func, *args, **kwargs):
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]{message}[/cyan]", total=None)
            result = func(*args, **kwargs)
            progress.update(task, completed=True)
            return result
    else:
        print(f"⏳ {message}...")
        result = func(*args, **kwargs)
        print(f"✅ Done")
        return result

def create_table(headers: list, rows: list, title: str = None) -> Table:
    table = Table(show_header=True, header_style="bold cyan", title=title)
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    return table

def print_table(headers: list, rows: list, title: str = None):
    if RICH_AVAILABLE:
        table = create_table(headers, rows, title)
        console.print(table)
    else:
        if title:
            print(f"\n{title}")
            print("-" * 50)
        header_str = "  ".join(f"{h:<15}" for h in headers)
        print(header_str)
        print("-" * 50)
        for row in rows:
            row_str = "  ".join(f"{str(c):<15}" for c in row)
            print(row_str)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(message: str = "Press Enter to continue..."):
    try:
        input(f"\n{message}")
    except (EOFError, KeyboardInterrupt):
        pass

def install_rich():
    print_info("Installing rich library for colorful terminal...")
    os.system(f"{sys.executable} -m pip install rich -q")
    print_success("Rich library installed. Please restart the CLI.")
    sys.exit(0)

class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys
        self.is_tty = sys.stdin.isatty()

    def __call__(self):
        import sys, tty, termios
        if not self.is_tty:
            return '\n'
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            mapping = {b'H': '\x1b[A', b'P': '\x1b[B', b'K': '\x1b[D', b'M': '\x1b[C'}
            return mapping.get(ch2, '')
        if ch == b'\r':
            return '\n'
        return ch.decode('utf-8', 'ignore')

getch = _Getch()

def interactive_menu_prompt(title: str, subtitle: str, options: list) -> int:
    """Show an interactive menu and return the selected index."""
    selected = 0
    
    # Hide cursor
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

    try:
        while True:
            clear_screen()
            print_title(title)
            if subtitle:
                console.print(subtitle)
            print()
            
            for i, opt in enumerate(options):
                marker = "▶" if i == selected else " "
                if RICH_AVAILABLE:
                    color = "yellow" if i == selected else "white"
                    console.print(f"  [bold {color}]{marker}[/bold {color}] [cyan]{i+1}.[/cyan] [{color}]{opt}[/{color}]")
                else:
                    print(f"  {marker} {i+1}. {opt}")
            
            print()
            print_info("Use ↑ ↓ arrows to navigate, Enter to select")
            
            key = getch()
            
            if key == '\x1b[A': # Up arrow
                selected = max(0, selected - 1)
            elif key == '\x1b[B': # Down arrow
                selected = min(len(options) - 1, selected + 1)
            elif key == '\n' or key == '\r':
                return selected
            elif key == '\x03': # Ctrl+C
                raise KeyboardInterrupt
            
    finally:
        # Show cursor
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
