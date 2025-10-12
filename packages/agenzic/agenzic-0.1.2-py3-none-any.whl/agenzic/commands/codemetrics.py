import os
import typer
import ast
from radon.complexity import cc_visit
from radon.metrics import h_visit,mi_visit
from rich.table import Table
from rich.console import Console

# -------------------------------------------------------------------------
# EXPERIMENTAL COMMAND: Python Function Extractor & Code Metrics
# Purpose: Extract all functions from a Python file and optionally analyze them
#          for metrics, readability, and maintainability.
# Status: Hidden / Experimental
# Notes:
#   - Reads a Python (.py) file.
#   - Splits the file into individual functions.
#   - Computes metrics like LOC, cyclomatic complexity, and maintainability index.
#   - Outputs metrics per function or for the whole file.
# -------------------------------------------------------------------------

# This command is intentionally left here for experimentation with external APIs.
# It is NOT part of the official Agenzic feature set.


def register(app: typer.Typer):
    @app.command(hidden=True)
    def codemetrics(file: str = typer.Option(..., "--file", help="Output file path")):
        """
        Generate code metrics for a Python file.
        Example:
            codemetrics --file abc.py
        """

        if not os.path.exists(file):
            typer.echo(f"File not found: {file}")
            raise typer.Exit()
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()

        tree = ast.parse(code)
        num_functions = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        num_classes = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        loc = len(code.splitlines())

        # --- Cyclomatic complexity ---
        cc_scores = [block.complexity for block in cc_visit(code)]
        avg_cc = sum(cc_scores) / len(cc_scores) if cc_scores else 0

        # --- Maintainability index ---
        try:
            mi = mi_visit(code, False)
        except Exception:
            mi = None

        metrics = {
            "loc": loc,
            "functions": num_functions,
            "classes": num_classes,
            "cyclomatic_complexity": {
                "average": avg_cc,
                "all": cc_scores
            },
            "maintainability_index": mi
        }

        console = Console()
        table = Table(title="Code Metrics")

        table.add_column("Metric", style=typer.colors.BRIGHT_GREEN, no_wrap=True)
        table.add_column("Value", style=typer.colors.BRIGHT_WHITE)

        # Add rows (with first-letter capitalized keys)
        table.add_row("Lines of Code", str(loc))
        table.add_row("Functions", str(num_functions))
        table.add_row("Classes", str(num_classes))
        table.add_row("Cyclomatic Complexity (Average)", str(avg_cc))
        table.add_row("Cyclomatic Complexity (All)", str(cc_scores))
        table.add_row("Maintainability Index", str(mi))

        console.print(table)