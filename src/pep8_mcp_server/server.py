import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import formatters, runners
from .path_utils import list_python_files, resolve_path

app = Server("pep8-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="run_flake8",         description="Run flake8 PEP8 style checks (max-line-length=120). path: file or directory.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="run_mypy",           description="Run mypy type checking with strict flags. path: .py file or package directory.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="run_complexity",     description="Run McCabe cyclomatic complexity check (threshold=10). path: file or directory.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="run_vulture",        description="Detect dead code with vulture (min-confidence=100%). path: file or directory.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="run_all_checks",     description="Run all 4 quality checks and return a combined structured summary.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="read_file",          description="Read the contents of a Python source file.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        Tool(name="write_file",         description="Overwrite a file with corrected content.", inputSchema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}),
        Tool(name="list_python_files",  description="List all .py files under a directory (or confirm a single .py file).", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = await _dispatch(name, arguments)
    except FileNotFoundError as e:
        result = f"ERROR: {e}"
    except Exception as e:
        result = f"ERROR: {type(e).__name__}: {e}"
    return [TextContent(type="text", text=result)]


async def _dispatch(name: str, args: dict) -> str:
    path_str = args.get("path", "")

    if name == "run_flake8":
        p = resolve_path(path_str)
        return formatters.format_flake8(*runners.run_flake8(p))

    if name == "run_mypy":
        p = resolve_path(path_str)
        return formatters.format_mypy(*runners.run_mypy(p))

    if name == "run_complexity":
        p = resolve_path(path_str)
        return formatters.format_flake8(*runners.run_complexity(p))

    if name == "run_vulture":
        p = resolve_path(path_str)
        return formatters.format_vulture(*runners.run_vulture(p))

    if name == "run_all_checks":
        p = resolve_path(path_str)
        sections = {
            "FLAKE8":     formatters.format_flake8(*runners.run_flake8(p)),
            "MYPY":       formatters.format_mypy(*runners.run_mypy(p)),
            "COMPLEXITY": formatters.format_flake8(*runners.run_complexity(p)),
            "VULTURE":    formatters.format_vulture(*runners.run_vulture(p)),
        }
        return "\n\n".join(f"=== {k} ===\n{v}" for k, v in sections.items())

    if name == "read_file":
        p = resolve_path(path_str)
        if not p.is_file():
            return f"ERROR: {path_str} is not a file."
        return p.read_text(encoding="utf-8", errors="replace")

    if name == "write_file":
        p = Path(path_str).resolve()
        content = args.get("content", "")
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} characters to {p}."

    if name == "list_python_files":
        p = resolve_path(path_str)
        files = list_python_files(p)
        if not files:
            return "No Python files found."
        return "\n".join(files) + f"\n\n{len(files)} file(s) found."

    return f"ERROR: Unknown tool '{name}'"


def main() -> None:
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()
