import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: str | None = None) -> tuple[str, str, int]:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
    )
    return result.stdout, result.stderr, result.returncode


def run_flake8(path: Path) -> tuple[str, str, int]:
    return _run([
        sys.executable, "-m", "flake8",
        str(path),
        "--max-line-length", "120",
        "--statistics",
    ])


def run_complexity(path: Path) -> tuple[str, str, int]:
    return _run([
        sys.executable, "-m", "flake8",
        str(path),
        "--max-complexity", "10",
        "--max-line-length", "120",
        "--select", "C",
    ])


def run_vulture(path: Path) -> tuple[str, str, int]:
    return _run([
        sys.executable, "-m", "vulture",
        str(path),
        "--min-confidence", "100",
    ])


def run_mypy(path: Path) -> tuple[str, str, int]:
    base_flags = [
        "--ignore-missing-imports",
        "--install-types", "--non-interactive",
        "--implicit-optional",
        "--disallow-incomplete-defs",
        "--disallow-untyped-defs",
    ]
    if path.is_dir() and (path / "__init__.py").exists():
        return _run(
            [sys.executable, "-m", "mypy", "-p", path.name] + base_flags,
            cwd=str(path.parent),
        )
    return _run([sys.executable, "-m", "mypy", str(path)] + base_flags)
