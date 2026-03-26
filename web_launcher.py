#!/usr/bin/env python3
"""
NSU Audit Core - Interactive Web Launcher
Hierarchical menu for all deployment and service management.
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

MCP_DIR = PROJECT_ROOT / "mcp"
MCP_VENV = MCP_DIR / "venv"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
RAILWAY_TOKEN_PATH = Path.home() / ".nsu_mcp" / "api_token.txt"

console = None  # type: ignore
questionary = None  # type: ignore

_running_processes = []


def _try_import_deps():
    global console, questionary
    try:
        from rich.console import Console
        import questionary
        console = Console()
    except ImportError:
        print("Installing required CLI dependencies (rich, questionary)...")
        try:
            venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
            python_bin = str(venv_python) if venv_python.exists() else sys.executable
            subprocess.check_call(
                [python_bin, "-m", "pip", "install", "rich", "questionary", "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            from rich.console import Console
            import questionary
            console = Console()
        except Exception as e:
            print(f"Failed to install CLI dependencies. Error: {e}")
            sys.exit(1)


def _style():
    return questionary.Style([
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:green bold"),
        ("pointer", "fg:yellow bold"),
        ("highlighted", "fg:yellow bold"),
        ("selected", "fg:cyan"),
        ("instruction", "fg:#888888"),
        ("text", ""),
    ])


def is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
            if s.connect_ex(("localhost", port)) == 0:
                return True
    except Exception:
        pass

    if socket.has_ipv6:
        try:
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                if s.connect_ex(("::1", port)) == 0:
                    return True
        except Exception:
            pass
            
    return False


def check_backend_health(url: str = "http://localhost:8000/health", timeout: int = 30) -> bool:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False


def get_backend_pid():
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "uvicorn" in line and "main:app" in line and "grep" not in line:
                return line.split()[1]
    except Exception:
        pass
    return None


def get_frontend_pid():
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "vite" in line and "grep" not in line:
                return line.split()[1]
    except Exception:
        pass
    return None


def get_mcp_pid():
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "python" in line and "mcp_server.py" in line and "grep" not in line:
                return line.split()[1]
    except Exception:
        pass
    return None


def find_python() -> str:
    venv_py = PROJECT_ROOT / ".venv" / "bin" / "python"
    return str(venv_py) if venv_py.exists() else sys.executable


def find_npm() -> str:
    venv_npm = PROJECT_ROOT / ".venv" / "bin" / "npm"
    return str(venv_npm) if venv_npm.exists() else "npm"


def ensure_mcp_venv():
    if not MCP_VENV.exists():
        console.print("[cyan]Creating MCP virtual environment...[/cyan]")
        subprocess.run([sys.executable, "-m", "venv", str(MCP_VENV)], capture_output=True)
    subprocess.run(
        [str(MCP_VENV / "bin" / "pip"), "install", "-r", str(MCP_DIR / "requirements.txt"), "-q"],
        capture_output=True
    )


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    from rich.panel import Panel
    from rich import box
    console.print(Panel(
        "[bold cyan]NSU AUDIT SYSTEM[/bold cyan] [yellow]v2.0[/yellow]\n"
        "[dim]Interactive Service Launcher[/dim]",
        border_style="cyan",
        box=box.ROUNDED,
    ))


def _kill_process_tree(pid):
    """Kill a process and all its children."""
    if pid is None:
        return
    try:
        os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
    except (ProcessLookupError, OSError):
        pass
    except AttributeError:
        try:
            os.kill(int(pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass


def _cleanup():
    """Stop all running services and reset terminal."""
    for proc_info in _running_processes:
        pid = proc_info.get("pid")
        if pid:
            _kill_process_tree(pid)
    _running_processes.clear()


def stop_all_running():
    """Stop all running services."""
    for proc_info in _running_processes:
        pid = proc_info.get("pid")
        if pid:
            _kill_process_tree(pid)
    _running_processes.clear()

    for pid_str in [get_mcp_pid(), get_backend_pid(), get_frontend_pid()]:
        if pid_str:
            _kill_process_tree(pid_str)

    try:
        subprocess.run(["fuser", "-k", "8000/tcp"], capture_output=True)
        subprocess.run(["fuser", "-k", "5173/tcp"], capture_output=True)
    except Exception:
        pass


def ask_railway_token() -> str | None:
    console.print()
    token = questionary.password(
        "Paste your Railway API token (or press Enter to cancel):",
        style=_style()
    ).ask()

    if not token or not token.strip():
        return None

    RAILWAY_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAILWAY_TOKEN_PATH.write_text(token.strip())
    RAILWAY_TOKEN_PATH.chmod(0o600)
    console.print("[green]Token saved.[/green]")
    return token.strip()


def get_railway_token() -> str | None:
    if RAILWAY_TOKEN_PATH.exists() and RAILWAY_TOKEN_PATH.stat().st_size > 0:
        return RAILWAY_TOKEN_PATH.read_text().strip()
    return None


def run_backend(check_existing: bool = True) -> tuple[subprocess.Popen | None, bool]:
    """
    Start backend server. Returns (process, was_existing).
    was_existing=True means backend was already running and we reused it.
    """
    if check_existing and is_port_in_use(8000):
        if check_backend_health():
            console.print("[cyan]Backend already running on port 8000, reusing existing instance...[/cyan]")
            return None, True
        else:
            console.print("[yellow]Port 8000 in use but backend not healthy, killing stale process...[/yellow]")
            try:
                subprocess.run(["pkill", "-f", "uvicorn.*main:app"], check=False)
                time.sleep(1)
            except Exception:
                pass
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    console.print("[cyan]Starting backend (FastAPI) on port 8000...[/cyan]")
    
    try:
        proc = subprocess.Popen(
            [find_python(), "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
            cwd=str(BACKEND_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        _running_processes.append({"name": "backend", "pid": proc.pid, "proc": proc})
        return proc, False
    except Exception as e:
        console.print(f"[bold red]Failed to start backend: {e}[/bold red]")
        return None, False


def wait_for_backend(timeout: int = 30) -> bool:
    with console.status("[cyan]Waiting for backend to be ready...[/cyan]"):
        start = time.time()
        while time.time() - start < timeout:
            if is_port_in_use(8000):
                if check_backend_health():
                    return True
            time.sleep(0.5)
    return False


def wait_for_frontend(timeout: int = 15) -> bool:
    with console.status("[yellow]Waiting for frontend to be ready...[/yellow]"):
        start = time.time()
        while time.time() - start < timeout:
            if is_port_in_use(5173):
                return True
            time.sleep(0.5)
    return False


def run_frontend() -> subprocess.Popen:
    console.print("[cyan]Starting frontend (Vite) on port 5173...[/cyan]")
    proc = subprocess.Popen(
        [find_npm(), "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _running_processes.append({"name": "frontend", "pid": proc.pid, "proc": proc})
    return proc


def run_mcp_server(mode: str = "offline", http: bool = True) -> subprocess.Popen:
    """Start MCP server. mode: 'offline' (local) or 'remote' (Railway). http: always True now."""
    ensure_mcp_venv()
    mode_label = "local" if mode == "offline" else "Railway"
    console.print(f"[cyan]Starting MCP server ({mode_label} backend, HTTP transport)...[/cyan]")

    python = str(MCP_VENV / "bin" / "python")

    args = [python, str(MCP_DIR / "mcp_server.py")]
    if mode == "remote":
        args.append("--remote")
    args.extend(["--http", "--http-port", "8001"])

    proc = subprocess.Popen(
        args,
        cwd=str(MCP_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _running_processes.append({"name": "mcp", "pid": proc.pid, "proc": proc})
    return proc


def stream_output(proc, label: str, color: str = "cyan"):
    try:
        for line in iter(proc.stdout.readline, b""):
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:
                console.print(f"[{color}][{label}][/{color}] {decoded}")
    except Exception:
        pass


def print_status_panel(mcp_mode: str = None):
    from rich.panel import Panel

    backend_running = is_port_in_use(8000)
    backend_pid = get_backend_pid()
    backend_detail = f"PID {backend_pid}" if backend_pid else ("port 8000" if backend_running else "")

    frontend_running = is_port_in_use(5173)
    frontend_pid = get_frontend_pid()
    frontend_detail = f"PID {frontend_pid}" if frontend_pid else ("port 5173" if frontend_running else "")

    mcp_pid = get_mcp_pid()
    mcp_running = mcp_pid is not None
    mcp_detail = ""
    if mcp_running:
        mode_str = f"{mcp_mode}" if mcp_mode else "offline"
        mcp_detail = f"{mode_str} | PID {mcp_pid}"

    lines = [
        f"  {'[green]●[/green]' if backend_running else '[red]○[/red]'} [cyan]Backend:[/cyan]     {'[green]Running[/green]' if backend_running else '[red]Not running[/red]'}{(' ' + f'[dim]({backend_detail})[/dim]') if backend_detail else ''}",
        f"  {'[green]●[/green]' if frontend_running else '[red]○[/red]'} [cyan]Frontend:[/cyan]    {'[green]Running[/green]' if frontend_running else '[red]Not running[/red]'}{(' ' + f'[dim]({frontend_detail})[/dim]') if frontend_detail else ''}",
        f"  {'[green]●[/green]' if mcp_running else '[red]○[/red]'} [cyan]MCP:[/cyan]          {'[green]Running[/green]' if mcp_running else '[red]Not running[/red]'}{(' ' + f'[dim]({mcp_detail})[/dim]') if mcp_detail else ''}",
    ]

    panel_content = "\n".join(lines)
    console.print(Panel(panel_content, title="[bold]Service Status[/bold]", border_style="cyan"))


# ─── MENU HANDLERS ────────────────────────────────────────────────────────────

def handle_deploy_services():
    """Submenu: Deploy Services."""
    while True:
        console.print()
        choice = questionary.select(
            "Deploy Services:",
            choices=[
                "1.1  Start Local Dev (Backend + Frontend + MCP)",
                "1.2  Start Local with Railway MCP (Remote)",
                "1.3  Start MCP Server Only (Local)",
                "1.4  Backend + Frontend Only (No MCP)",
                "Back to Main Menu",
            ],
            style=_style(),
        ).ask()

        if choice == "1.1  Start Local Dev (Backend + Frontend + MCP)":
            do_deploy_local(include_frontend=True, include_mcp=True, mcp_mode="offline", mcp_http=True)
            return
        elif choice == "1.2  Start Local with Railway MCP (Remote)":
            do_deploy_local(include_frontend=True, include_mcp=True, mcp_mode="remote", mcp_http=True)
            return
        elif choice == "1.3  Start MCP Server Only (Local)":
            do_mcp_only(mcp_mode="offline", http=True)
            return
        elif choice == "1.4  Backend + Frontend Only (No MCP)":
            do_deploy_local(include_frontend=True, include_mcp=False, mcp_mode="offline", mcp_http=False)
            return
        elif choice == "Back to Main Menu" or choice is None:
            return


def handle_service_management():
    """Submenu: Service Management."""
    while True:
        console.print()
        choice = questionary.select(
            "Service Management:",
            choices=[
                "2.1  Status Check",
                "2.2  Stop MCP Server",
                "2.3  Stop All Services",
                "Back to Main Menu",
            ],
            style=_style(),
        ).ask()

        if choice == "2.1  Status Check":
            clear_screen()
            print_banner()
            print_status_panel()
            console.print()
        elif choice == "2.2  Stop MCP Server":
            do_stop_mcp()
        elif choice == "2.3  Stop All Services":
            do_stop_all()
        elif choice == "Back to Main Menu" or choice is None:
            return


# ─── ACTION FUNCTIONS ────────────────────────────────────────────────────────

def do_deploy_local(include_frontend: bool = False, include_mcp: bool = False, mcp_mode: str = "offline", mcp_http: bool = False):
    """Deploy locally: backend, optionally frontend and/or MCP."""
    frontend_process = None
    mcp_process = None
    backend_existing = False

    def shutdown(signum=None, frame=None):
        console.print("\n[yellow]Shutting down services...[/yellow]")
        _cleanup()
        console.print("[bold green]All services stopped.[/bold green]")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        backend_result = run_backend()
        if backend_result[0] is None and not backend_result[1]:
            console.print("[bold red]Failed to start backend.[/bold red]")
            shutdown()
            return
        
        backend_process, backend_existing = backend_result

        if not backend_existing:
            if not wait_for_backend():
                console.print("[bold red]Backend failed to start within 30 seconds.[/bold red]")
                shutdown()
                return

        console.print("[bold green]Backend ready at http://localhost:8000[/bold green]")

        if include_frontend:
            if is_port_in_use(5173):
                console.print("[cyan]Frontend already running on port 5173, reusing existing instance...[/cyan]")
            else:
                frontend_process = run_frontend()
                if not wait_for_frontend():
                    console.print("[bold red]Frontend failed to start within 15 seconds.[/bold red]")
                else:
                    console.print("[bold green]Frontend ready at http://localhost:5173[/bold green]")

        if include_mcp:
            mcp_port = 8001 if mcp_http else None
            if mcp_http and is_port_in_use(8001):
                console.print("[cyan]MCP HTTP server already running on port 8001, reusing...[/cyan]")
            else:
                if mcp_mode == "remote":
                    if not get_railway_token():
                        token = ask_railway_token()
                        if not token:
                            console.print("[yellow]Skipping MCP (no token provided).[/yellow]")
                        else:
                            os.environ["RAILWAY_API_TOKEN"] = token
                            mcp_process = run_mcp_server(mcp_mode, mcp_http)
                            time.sleep(2)
                    else:
                        mcp_process = run_mcp_server(mcp_mode, mcp_http)
                        time.sleep(2)
                else:
                    mcp_process = run_mcp_server(mcp_mode, mcp_http)
                    time.sleep(2)

        clear_screen()
        print_banner()
        print_status_panel(mcp_mode if include_mcp else None)
        console.print()
        if backend_existing:
            console.print("[yellow]Note: Backend was already running (not managed by this session)[/yellow]")
        console.print("[yellow]Press [bold]Ctrl+C[/bold] to stop all services.[/yellow]")

        import threading
        threads = []
        if backend_process and not backend_existing:
            threads.append(threading.Thread(target=stream_output, args=(backend_process, "backend", "cyan"), daemon=True))
        if frontend_process:
            threads.append(threading.Thread(target=stream_output, args=(frontend_process, "frontend", "yellow"), daemon=True))

        for t in threads:
            t.start()

        while True:
            if backend_process and backend_process.poll() is not None:
                console.print("[bold red]Backend process died![/bold red]")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


def do_mcp_only(mcp_mode: str = "offline", http: bool = False):
    """Start MCP server only."""
    mcp_process = None
    
    if http and is_port_in_use(8001):
        console.print("[cyan]MCP HTTP server already running on port 8001![/cyan]")
        console.print("[cyan]opencode can connect to http://localhost:8001/mcp[/cyan]")
        console.print("[yellow]Press Enter to return to menu...[/yellow]")
        try:
            input()
        except KeyboardInterrupt:
            pass
        return
    
    if mcp_mode == "remote" and not get_railway_token():
        token = ask_railway_token()
        if not token:
            console.print("[yellow]Cannot start MCP without Railway token.[/yellow]")
            return

    mcp_process = run_mcp_server(mcp_mode, http)
    backend_url = "Railway" if mcp_mode == "remote" else "localhost:8000"

    def shutdown(signum=None, frame=None):
        console.print("\n[yellow]Stopping MCP server...[/yellow]")
        if mcp_process:
            _kill_process_tree(mcp_process.pid)
        console.print("[bold green]MCP server stopped.[/bold green]")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    clear_screen()
    print_banner()
    console.print(f"[cyan]MCP Server running — backend: {backend_url}[/cyan]")
    if http:
        console.print(f"[cyan]opencode: connect to http://localhost:8001/mcp[/cyan]")
    console.print("[yellow]Press [bold]Ctrl+C[/bold] to stop.[/yellow]")

    try:
        for line in iter(mcp_process.stdout.readline, b""):
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:
                console.print(f"[cyan][mcp][/cyan] {decoded}")
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


def do_stop_mcp():
    pid = get_mcp_pid()
    if pid:
        console.print(f"[cyan]Stopping MCP server (PID: {pid})...[/cyan]")
        _kill_process_tree(pid)
        time.sleep(1)
        console.print("[bold green]MCP server stopped.[/bold green]")
    else:
        console.print("[yellow]MCP server is not running.[/yellow]")


def do_stop_all():
    console.print("[cyan]Stopping all services...[/cyan]")
    stop_all_running()
    console.print("[bold green]All services stopped.[/bold green]")


def do_reauth():
    ensure_mcp_venv()
    token_path = Path.home() / ".nsu_mcp" / "token.json"
    if token_path.exists():
        console.print("[cyan]Removing existing token...[/cyan]")
        token_path.unlink()
    console.print("[cyan]Opening browser for Google re-authentication...[/cyan]")
    python = str(MCP_VENV / "bin" / "python")
    result = subprocess.run(
        [python, str(MCP_DIR / "mcp_server.py"), "--reauth"],
        cwd=str(MCP_DIR),
    )
    if result.returncode == 0:
        console.print("[bold green]Re-authentication successful.[/bold green]")
    else:
        console.print("[red]Re-authentication failed.[/red]")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    _try_import_deps()

    def handle_ctrl_c(signum, frame):
        _cleanup()
        clear_screen()
        console.print("[yellow]Interrupted. Goodbye![/yellow]")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_ctrl_c)
    signal.signal(signal.SIGTERM, handle_ctrl_c)

    if not (BACKEND_DIR / "main.py").exists():
        console.print(f"[bold red]Backend directory or main.py not found: {BACKEND_DIR}[/bold red]")
        sys.exit(1)

    if not (FRONTEND_DIR / "package.json").exists():
        console.print(f"[bold red]Frontend not found: {FRONTEND_DIR}[/bold red]")
        sys.exit(1)

    port_warnings = []
    if is_port_in_use(8000):
        port_warnings.append("[yellow]Port 8000 is already in use.[/yellow]")
    if is_port_in_use(5173):
        port_warnings.append("[yellow]Port 5173 is already in use.[/yellow]")

    clear_screen()
    print_banner()

    for w in port_warnings:
        console.print(w)
        time.sleep(0.5)

    while True:
        console.print()
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "1. Start Local Development",
                "2. Service Management",
                "3. Re-authenticate Google Account",
                "4. Help",
                "5. Exit",
            ],
            style=_style(),
        ).ask()

        if choice == "1. Start Local Development":
            handle_deploy_services()
        elif choice == "2. Service Management":
            handle_service_management()
        elif choice == "3. Re-authenticate Google Account":
            do_reauth()
        elif choice == "4. Help":
            do_help()
        elif choice == "5. Exit" or choice is None:
            clear_screen()
            console.print("[yellow]Goodbye![/yellow]")
            break


def do_help():
    """Show help and use case documentation."""
    while True:
        clear_screen()
        
        help_panel = """
[bold cyan]═══════════════════════════════════════════════════════════════════════[/bold cyan]
[bold white]                              HELP & USE CASES[/bold white]
[bold cyan]═══════════════════════════════════════════════════════════════════════[/bold cyan]

[bold yellow]📌 MENU STRUCTURE[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
┌─────┬────────────────────────────────────────┬─────────────────────────────────┐
│ No. │ Option                                 │ Description                     │
├─────┼────────────────────────────────────────┼─────────────────────────────────┤
│  1  │ Start Local Development               │ Opens submenu (1.1-1.4)         │
│  2  │ Service Management                    │ Opens submenu (2.1-2.3)         │
│  3  │ Re-authenticate Google Account        │ Re-authenticate with Google     │
│  4  │ Help                                   │ Show this help                  │
│  5  │ Exit                                   │ Quit                            │
└─────┴────────────────────────────────────────┴─────────────────────────────────┘

[bold yellow]📌 SUBMENU 1: DEPLOY SERVICES (1.x)[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
  1.1  Start Local Dev (Backend + Frontend + MCP)   - Full local stack
  1.2  Start Local with Railway MCP (Remote)       - Backend + Railway MCP
  1.3  Start MCP Server Only (Local)               - MCP only on port 8001
  1.4  Backend + Frontend Only (No MCP)             - No MCP server

[bold yellow]📌 SUBMENU 2: SERVICE MANAGEMENT (2.x)[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
  2.1  Status Check          - Show running services status
  2.2  Stop MCP Server       - Kill MCP server only
  2.3  Stop All Services    - Kill all services

[bold yellow]📌 PORTS[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
  Backend:   http://localhost:8000
  MCP:       http://localhost:8001/mcp
  Frontend:  http://localhost:5173

[bold yellow]📌 OPENCODE INTEGRATION[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
  1. Run: [cyan]1.1 Start Local Dev[/cyan]
  2. Authenticate with Google (first time only)
  3. OpenCode Desktop: connect to [cyan]http://localhost:8001/mcp[/cyan]

[bold yellow]📌 RAILWAY DEPLOYMENT[/bold yellow]
[dim]──────────────────────────────────────────────────────────────────────────────[/dim]
  1. Run: [cyan]1.2 Start Local with Railway MCP[/cyan]
  2. Enter Railway API token when prompted
  3. MCP available at: https://your-app.up.railway.app/mcp

[bold cyan]═══════════════════════════════════════════════════════════════════════[/bold cyan]
"""
        console.print(help_panel)
        
        choice = questionary.select(
            "Select an option:",
            choices=[
                "Back to Main Menu",
            ],
            style=_style(),
        ).ask()
        
        if choice == "Back to Main Menu" or choice is None:
            break


if __name__ == "__main__":
    main()
