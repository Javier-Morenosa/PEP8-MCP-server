import re

_FLAKE8_RE = re.compile(r"^(.+?):(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)$")
_MYPY_RE = re.compile(r"^(.+?):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[(.+?)\])?$")


def format_flake8(stdout: str, stderr: str, returncode: int) -> str:
    violations = []
    for line in stdout.splitlines():
        m = _FLAKE8_RE.match(line)
        if m:
            violations.append(
                f"[{m.group(1)}:{m.group(2)}:{m.group(3)}] {m.group(4)} -- {m.group(5)}"
            )
    count = len(violations)
    lines = violations + [f"{count} violation(s) found."]
    return "\n".join(lines)


def format_mypy(stdout: str, stderr: str, returncode: int) -> str:
    issues = []
    for line in stdout.splitlines():
        m = _MYPY_RE.match(line)
        if m:
            code = f"  [{m.group(5)}]" if m.group(5) else ""
            issues.append(
                f"[{m.group(1)}:{m.group(2)}] {m.group(3).upper()}{code} -- {m.group(4)}"
            )
    count = len(issues)
    return "\n".join(issues + [f"{count} issue(s) found."])


def format_vulture(stdout: str, stderr: str, returncode: int) -> str:
    lines = [l for l in stdout.splitlines() if l.strip()]
    count = len(lines)
    return "\n".join(lines + [f"{count} dead code item(s) found."])
