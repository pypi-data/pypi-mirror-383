import typer
from agenzic.commands import commit, summarize, review, tests, ask, codemetrics, inspect, codegen, projtree
from agenzic.commands.experimental import graph, inception, docgen, myflow
import agenzic
import platform
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Agenzic CLI - AI assistant for developers")

@app.command()
def version():
    """Show Agenzic version and environment info"""
    try:
        import typer as typer_lib
        typer.echo(f"Agenzic v{agenzic.__version__}")
        typer.echo(f"Python: {platform.python_version()}")
        typer.echo(f"Typer: {typer_lib.__version__}")
    except Exception:
        typer.echo(f"Agenzic v{agenzic.__version__} (environment details unavailable)")

@app.command()
def about():
    """Show information about Agenzic CLI"""
    typer.echo(
        f"""
        Agenzic CLI v{agenzic.__version__}
        AI-powered assistant for developers.

        Features:
          - AI commit message generator
          - AI code summarizer
          - AI-powered code review
          - Project or file documentation generator
          - AI code generation from natural language prompts
          - Unit test generation for your code
          - Ask AI questions about your project or specific files
          - Shallow project tree visualization
          - Environment and config inspector

        Available Commands:
          commit     Generate AI commit message(s) for staged changes
          summarize  Summarize a code file with AI
          review     Generate AI-powered code review of a code file
          docgen     Generate project or file documentation
          codegen    Generate code from a prompt and write to file
          tests      Generate unit tests for your code
          ask        Ask AI a question about your project or a specific file
          projtree   Show a shallow project structure
          inspect    Debug inspector: show environment, config, PATH, plugins, Python version
          version    Show Agenzic version and environment info
          about      Show project information
          help       Show command usage

        Repository: https://github.com/ratul-d/agenzic
        """
    )

@app.command()
def help():
    """Show available commands and usage examples"""
    typer.echo(typer.style("\nAgenzic CLI - Help", fg=typer.colors.BRIGHT_WHITE, bold=True))
    typer.echo("=" * 18)

    typer.echo(typer.style("\nAvailable Commands:", fg=typer.colors.BRIGHT_RED, bold=True))
    commands = {
        "commit": "Generate AI commit message(s) for staged changes",
        "summarize": "Summarize a code file with AI",
        "review": "Generate AI-powered code review of a code file",
        "docgen": "Generate project or file documentation",
        "codegen": "Generate code from a prompt and write to file",
        "tests": "Generate unit tests for your code",
        "ask": "Ask AI a question about your project or a specific file. | Defaults to current directory. Use -f or -d to override.",
        "projtree": "Show a shallow project structure, ignoring common Python-generated files.",
        "inspect": "Debug inspector: show environment, config, PATH, plugins, Python version.",
    }
    for cmd, desc in commands.items():
        typer.echo(f"  {typer.style(cmd, fg=typer.colors.BRIGHT_RED, bold=True)}  {desc}")

    typer.echo(typer.style("\nInfo Commands:", fg=typer.colors.BRIGHT_RED, bold=True))
    commands = {
        "version": "Show Agenzic version and environment info",
        "about": "Show project information",
        "help": "Show this help message",
    }
    for cmd, desc in commands.items():
        typer.echo(f"  {typer.style(cmd, fg=typer.colors.BRIGHT_RED, bold=True)}  {desc}")

    usage_examples = [
        ("Commit", ["agenzic commit"]),
        ("Summarize", ["agenzic summarize -f myscript.py"]),
        ("Review", ["agenzic review -f myscript.py"]),
        ("Docgen", ["agenzic docgen -f myscript.py", "agenzic docgen -d folder/"]),
        ("Codegen", ["agenzic codegen 'write a python code' -f abc.py"]),
        ("Tests", ["agenzic tests -f myscript.py"]),
        ("Ask", [
            "agenzic ask 'Your Question'",
            "agenzic ask 'Your Question' -f app.py",
            "agenzic ask 'Your Question' -d folder/"
        ]),
        ("Projtree", [
            "[bright_blue]# Show shallow project tree of current directory (default depth=2)[/bright_blue]",
            "agenzic projtree",
            "",
            "[bright_blue]# Show project tree for a specific folder[/bright_blue]",
            "agenzic projtree -d folder/",
            "",
            "[bright_blue]# Show project tree with custom depth (1=top-level only, 2=one level deep, etc.)[/bright_blue]",
            "agenzic projtree -d folder/ -l 3",
        ]),
        ("Inspect", ["agenzic inspect"]),
    ]

    # Create table
    table = Table(show_header= False, header_style="bold bright_blue", show_lines=True)
    table.add_column("Command", style="bright_blue", no_wrap=True)
    table.add_column("Usage Example", style="white")

    # Add rows with indented multiline examples
    for title, examples in usage_examples:
        example_text = "\n".join(f"  {line}" for line in examples)  # indent each line
        table.add_row(title, example_text)

    console.print("\nUsage Examples:", style="bold bright_blue")
    console.print(table)

@app.command(hidden=True)
def experimental():
    """Show experimental commands and usage examples"""
    typer.echo(typer.style("\nAgenzic CLI - Experimental Commands", fg=typer.colors.BRIGHT_WHITE, bold=True))
    typer.echo("=" * 35)

    typer.echo(typer.style("\nAvailable Commands:", fg=typer.colors.BRIGHT_RED, bold=True))
    commands = {
        "icodegen": "Generate code from a prompt and write to file with InceptionLabs' mercury-coder.",
        "codemetrics": "Generate code metrics for a Python file.",
        "graph": "Generate file-by-file dependency graph for a Python directory.",
        "myflow": "Manage recorded command flows",
        "\t|-> myflow record": "Record a new command flow",
        "\t|-> myflow replay": "Replay a command flow",
        "\t|-> myflow delete": "Delete a saved command flow",
        "\t|-> myflow flows": "List all recorded command flows",
    }
    for cmd, desc in commands.items():
        typer.echo(f"  {typer.style(cmd, fg=typer.colors.BRIGHT_RED, bold=True)}  {desc}")

    typer.echo(typer.style("\nUsage Examples:", fg=typer.colors.BRIGHT_BLUE, bold=True))
    usage_examples = [
        ("icodegen", ["agenzic icodegen 'write a python code' --file abc.py"]),
        ("codemetrics", ["agenzic codemetrics --file abc.py"]),
        ("graph", ["agenzic graph -d folder/"]),
        ("myflow", [
            "agenzic myflow record <name>",
            "agenzic myflow replay <name>",
            "agenzic myflow delete <name>",
            "agenzic myflow flows"
        ]),
    ]

    table = Table(show_header=False, header_style="bold bright_blue",show_lines=True)

    table.add_column("Command", style="bright_blue", no_wrap=True)
    table.add_column("Usage Example", style="white")

    for title, examples in usage_examples:
        example_text = "\n".join(f"  {line}" for line in examples)
        table.add_row(title, example_text)

    console.print(table)  # soft border color


commit.register(app)
summarize.register(app)
review.register(app)
docgen.register(app)
tests.register(app)
ask.register(app)
codegen.register(app)
projtree.register(app)

# Experimental
inception.register(app)
codemetrics.register(app)
graph.register(app)
myflow.register(app)
inspect.register(app)

def main():
    """Entry point for console_scripts"""
    app()

if __name__ == "__main__":
    main()