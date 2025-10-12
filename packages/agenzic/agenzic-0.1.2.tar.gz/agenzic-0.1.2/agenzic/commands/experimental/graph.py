import ast
from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

console = Console()


def parse_imports(file_path: Path):
    """Parse imports from a single Python file and return full dotted paths."""
    code = file_path.read_text(encoding="utf-8")
    parsed = ast.parse(code)

    imports = []
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)  # full dotted path
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)  # keep full path
    return imports


def build_dependency_graph(files):
    """Return a dict {file: [imported modules]} for all files."""
    graph = {}
    for file in files:
        graph[file.name] = parse_imports(file)
    return graph


def add_hierarchy(parent, dotted_path: str):
    """Add a hierarchical tree node from a dotted path."""
    parts = dotted_path.split(".")
    current = parent
    for part in parts:
        # reuse existing child if already present
        found = None
        for child in current.children:
            if str(child.label) == part:
                found = child
                break
        if not found:
            found = current.add(part)
        current = found


def build_tree(graph: dict):
    """Build a Rich tree for the dependency graph with hierarchy."""
    root = Tree("[bold white]Dependency Graph[/]")
    for file, deps in graph.items():
        file_node = root.add(f"[green]{file}[/]")
        if deps:
            for dep in deps:
                add_hierarchy(file_node, dep)
        else:
            file_node.add("[dim]No imports[/]")
    return root

def register(app: typer.Typer):
    @app.command(hidden=True)
    def graph(dir: str = typer.Option(".", "-d", help="Path to project directory")):
        """Analyze all Python files in a directory and show dependency graph."""
        path = Path(dir)
        py_files = list(path.glob("*.py"))

        if not py_files:
            typer.echo(typer.style(f"No Python files found in: ",fg=typer.colors.RED)+f"{dir}")
            return

        graph = build_dependency_graph(py_files)
        tree = build_tree(graph)
        console.print(tree)