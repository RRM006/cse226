#!/usr/bin/env python3
"""
NSU Audit Core - Interactive Web Launcher
Modern CLI for starting the local environment.
"""

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR

console = None
questionary = None


def _try_import_deps():
    global console, questionary
    try:
        from rich.console import Console
        import questionary
        console = Console()
    except ImportError:
        print("Installing required CLI dependencies (rich, questionary)...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "rich", "questionary", "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            from rich.console import Console
            import questionary
            console = Console()
        except Exception as e:
            print(f"Failed to install CLI dependencies. Error: {e}")
            sys.exit(1)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def check_backend_health(url: str = "http://localhost:8000/health", timeout: int = 30) -> bool:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False


def find_python() -> str:
    venv_py = PROJECT_ROOT / ".venv" / "bin" / "python"
    return str(venv_py) if venv_py.exists() else sys.executable


def find_npm() -> str:
    venv_npm = PROJECT_ROOT / ".venv" / "bin" / "npm"
    return str(venv_npm) if venv_npm.exists() else "npm"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    from rich.panel import Panel
    console.print(Panel(
        "[bold cyan]NSU AUDIT SYSTEM[/bold cyan] [yellow]v2.0[/yellow]\n"
        "[dim]Graduation Audit Management[/dim]",
        border_style="cyan",
        box=True,
    ))


def interactive_menu() -> str:
    choices = [
        "1. Local Deploy",
        "2. Local Deploy with MCP",
        "3. Mobile Local Run",
        "4. Exit"
    ]

    custom_style = questionary.Style([
        ('qmark', 'fg:cyan bold'),
        ('question', 'bold'),
        ('answer', 'fg:green bold'),
        ('pointer', 'fg:yellow bold'),
        ('highlighted', 'fg:yellow bold'),
        ('selected', 'fg:cyan'),
        ('instruction', 'fg:black bright'),
        ('text', ''),
    ])

    choice = questionary.select(
        "Select deployment mode:",
        choices=choices,
        style=custom_style,
        instruction="(Use arrow keys and Enter to select)"
    ).ask()

    return choice if choice else "4. Exit"


def run_backend(backend_dir: Path, python: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    console.print("\n[cyan]Starting backend (FastAPI)...[/cyan]")
    return subprocess.Popen(
        [python, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=str(backend_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def wait_for_backend(timeout: int = 30) -> bool:
    with console.status("[cyan]Waiting for backend to be ready...[/cyan]"):
        start = time.time()
        while time.time() - start < timeout:
            if is_port_in_use(8000):
                if check_backend_health():
                    return True
            time.sleep(0.5)
        return False


def run_frontend(frontend_dir: Path, npm: str) -> subprocess.Popen:
    console.print("[cyan]Starting frontend (Vite)...[/cyan]")
    return subprocess.Popen(
        [npm, "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def run_mcp_server() -> subprocess.Popen:
    mcp_dir = PROJECT_ROOT / "mcp"
    mcp_script = mcp_dir / "mcp_script"
    python = find_python()

    if not mcp_script.exists():
        console.print(f"[yellow]Warning: mcp_script not found at {mcp_script}[/yellow]")
        console.print("[cyan]Starting MCP server directly (offline mode)...[/cyan]")
        return subprocess.Popen(
            [python, str(mcp_dir / "mcp_server.py")],
            cwd=str(mcp_dir),
            start_new_session=True,
        )

    console.print("[cyan]Starting MCP server (offline mode)...[/cyan]")
    return subprocess.Popen(
        ["bash", str(mcp_script), "local", "offline"],
        cwd=str(PROJECT_ROOT),
        start_new_session=True,
    )


def stream_output(proc: subprocess.Popen, label: str, color: str = "cyan"):
    try:
        for line in iter(proc.stdout.readline, b''):
            if not line:
                break
            decoded = line.decode('utf-8', errors='replace').rstrip()
            if decoded:
                console.print(f"[{color}][{label}][/{color}] {decoded}")
    except Exception:
        pass


def print_services_running(mode: str):
    from rich.panel import Panel

    status_text = "[bold green]All services running![/bold green]\n\n"
    status_text += "  [cyan]Backend:[/cyan]   http://localhost:8000\n"

    if "Deploy" in mode:
        status_text += "  [cyan]Frontend:[/cyan]  http://localhost:5173\n"

    if "MCP" in mode:
        status_text += "  [cyan]MCP:[/cyan]       Running in background (offline)\n"

    if "Mobile" in mode:
        status_text += "\n  [bold yellow]To run the Mobile App:[/bold yellow]\n"
        status_text += "  1. Open a new terminal\n"
        status_text += f"  2. Run: [cyan]cd {PROJECT_ROOT}/mobile && flutter run[/cyan]\n"

    status_text += "\n  Press [bold yellow]Ctrl+C[/bold yellow] to stop all services"

    console.print()
    console.print(Panel(
        status_text,
        title="[bold]NSU Audit System[/bold]",
        border_style="green",
    ))


def stop_service(proc: subprocess.Popen, name: str):
    try:
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main():
    _try_import_deps()

    backend_dir = PROJECT_ROOT / "backend"
    frontend_dir = PROJECT_ROOT / "frontend"

    if not backend_dir.exists():
        console.print(f"[bold red]X Backend directory not found: {backend_dir}[/bold red]")
        sys.exit(1)

    if not (backend_dir / "main.py").exists():
        console.print(f"[bold red]X Backend main.py not found[/bold red]")
        sys.exit(1)

    if not frontend_dir.exists():
        console.print(f"[bold red]X Frontend directory not found: {frontend_dir}[/bold red]")
        sys.exit(1)

    if not (frontend_dir / "package.json").exists():
        console.print(f"[bold red]X Frontend package.json not found[/bold red]")
        sys.exit(1)

    warnings = []
    if is_port_in_use(8000):
        warnings.append("[yellow]Port 8000 is already in use. Backend may fail.[/yellow]")
    if is_port_in_use(5173):
        warnings.append("[yellow]Port 5173 is already in use. Frontend may fail.[/yellow]")

    clear_screen()
    print_banner()

    for w in warnings:
        console.print(w)
        time.sleep(0.5)

    choice = interactive_menu()

    if choice.startswith("4"):
        console.print("[yellow]Exiting...[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold cyan]=== {choice.split('. ', 1)[1]} ===[/bold cyan]")

    backend_process = None
    frontend_process = None
    mcp_process = None

    def shutdown_handler(signum, frame):
        console.print("\n[yellow]Shutting down services...[/yellow]")
        if mcp_process:
            stop_service(mcp_process, "MCP")
        if frontend_process:
            stop_service(frontend_process, "Frontend")
        if backend_process:
            stop_service(backend_process, "Backend")
        console.print("[bold green]All services stopped.[/bold green]")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        backend_process = run_backend(backend_dir, find_python())

        if not wait_for_backend():
            console.print("[bold red]X Backend failed to start within 30 seconds.[/bold red]")
            if backend_process:
                backend_process.terminate()
            sys.exit(1)

        console.print("[bold green]Backend ready at http://localhost:8000[/bold green]")

        if "Deploy" in choice:
            frontend_process = run_frontend(frontend_dir, find_npm())
            time.sleep(2)

        if "MCP" in choice:
            mcp_process = run_mcp_server()
            time.sleep(2)

        print_services_running(choice)

        import threading
        threads = []
        if backend_process:
            threads.append(threading.Thread(target=stream_output, args=(backend_process, "backend", "cyan"), daemon=True))
        if frontend_process:
            threads.append(threading.Thread(target=stream_output, args=(frontend_process, "frontend", "yellow"), daemon=True))

        for t in threads:
            t.start()

        while True:
            if backend_process and backend_process.poll() is not None:
                console.print("[bold red]X Backend process died![/bold red]")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        shutdown_handler(None, None)


if __name__ == "__main__":
    main()
