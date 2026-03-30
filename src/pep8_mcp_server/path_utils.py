from pathlib import Path


def resolve_path(raw: str) -> Path:
    p = Path(raw).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    return p


def list_python_files(path: Path) -> list[str]:
    """Return .py files under a directory, or [path] for a single .py file."""
    if path.is_file():
        return [str(path)] if path.suffix == ".py" else []
    return sorted(str(f) for f in path.rglob("*.py"))
