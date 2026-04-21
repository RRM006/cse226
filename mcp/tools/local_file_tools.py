import csv
import io
from pathlib import Path
from typing import Optional


def read_local_csv(file_path: str) -> dict:
    """
    Read a local CSV file and return its content.

    Args:
        file_path: Absolute or relative path to the CSV file

    Returns:
        {status: "success", content: csv_text, file_name, rows_count} or {status: "error", message}
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
            }

        if not path.is_file():
            return {
                "status": "error",
                "message": f"Path is not a file: {file_path}",
            }

        if path.suffix.lower() not in [".csv", ".txt"]:
            return {
                "status": "error",
                "message": f"File must be CSV or TXT format. Got: {path.suffix}",
            }

        content = path.read_text(encoding="utf-8")

        if not content.strip():
            return {
                "status": "error",
                "message": "File is empty",
            }

        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        rows_count = len(rows)

        return {
            "status": "success",
            "content": content,
            "file_name": path.name,
            "file_path": str(path),
            "rows_count": rows_count,
        }

    except PermissionError:
        return {
            "status": "error",
            "message": f"Permission denied reading file: {file_path}",
        }
    except UnicodeDecodeError:
        try:
            path = Path(file_path).expanduser().resolve()
            content = path.read_text(encoding="latin-1")
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            rows_count = len(rows)
            return {
                "status": "success",
                "content": content,
                "file_name": path.name,
                "file_path": str(path),
                "rows_count": rows_count,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unable to read file encoding: {str(e)}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading file: {str(e)}",
        }


def list_local_directory(dir_path: str, file_pattern: Optional[str] = None) -> dict:
    """
    List files in a local directory.

    Args:
        dir_path: Path to directory
        file_pattern: Optional glob pattern (e.g., "*.csv")

    Returns:
        {status: "success", files: [...]} or {status: "error", message}
    """
    try:
        path = Path(dir_path).expanduser().resolve()

        if not path.exists():
            return {
                "status": "error",
                "message": f"Directory not found: {dir_path}",
            }

        if not path.is_dir():
            return {
                "status": "error",
                "message": f"Path is not a directory: {dir_path}",
            }

        if file_pattern:
            files = [f.name for f in path.glob(file_pattern) if f.is_file()]
        else:
            files = [f.name for f in path.iterdir() if f.is_file()]

        return {
            "status": "success",
            "directory": str(path),
            "files": sorted(files),
            "count": len(files),
        }
    except PermissionError:
        return {
            "status": "error",
            "message": f"Permission denied: {dir_path}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing directory: {str(e)}",
        }
