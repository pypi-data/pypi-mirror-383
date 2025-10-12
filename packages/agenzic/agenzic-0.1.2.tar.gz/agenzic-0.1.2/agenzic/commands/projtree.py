from pathlib import Path
import fnmatch
import typer
from rich.console import Console
from rich.tree import Tree

console = Console()

# Files/folders to ignore
IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "build",
    "dist",
    "wheels",
    "*.egg-info",
    ".idea",
    ".venv",
    ".env",
    ".git",
    ".gitignore",
    ".python-version",
]

def should_ignore(name: str) -> bool:
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

def build_project_tree(path: Path, depth: int = 1):
    """
    Build a shallow project tree up to `depth` levels, ignoring certain files/folders.
    """
    root = Tree(f"[bold blue]{path.name}[/]")

    def add_items(parent, current_path: Path, current_depth: int):
        if current_depth > depth:
            return
        for item in sorted(current_path.iterdir()):
            if should_ignore(item.name):
                continue
            if item.is_dir():
                dir_node = parent.add(f"[cyan]{item.name}/[/]")
                add_items(dir_node, item, current_depth + 1)
            else:
                parent.add(f"{item.name}")

    add_items(root, path, 1)
    return root

def register(app: typer.Typer):
    @app.command()
    def projtree(
        dir: str = typer.Option(".", "-d", help="Path to project directory"),
        depth: int = typer.Option(2, "-l", help="Depth of directory tree to show"),
    ):
        """Show a shallow project structure, ignoring common Python-generated files."""
        path = Path(dir)
        if not path.exists() or not path.is_dir():
            typer.echo(typer.style(f"Invalid directory: {dir}", fg=typer.colors.RED))
            return

        tree = build_project_tree(path, depth)
        console.print(tree)
