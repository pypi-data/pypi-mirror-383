import typer
from agenzic.utils.ai_client import ask_ai
import os
from rich.console import Console
from rich.markdown import Markdown

def register(app: typer.Typer):
    @app.command()
    def summarize(file: str = typer.Option(..., "-f", help="Path to a specific code file to summarize")):
        """Summarize a file with AI"""
        if not os.path.exists(file):
            typer.echo(typer.style("File not found: ",fg=typer.colors.RED)+f"{file}")
            raise typer.Exit(1)
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        prompt = f"Summarize the following code/file in a concise, human readable way:\n{content}"
        typer.echo(typer.style("Summarizing: ",fg=typer.colors.BRIGHT_GREEN)+f"{file}")
        summary = ask_ai(prompt)
        typer.echo(typer.style("\nAI Summary:",fg=typer.colors.BRIGHT_GREEN))

        console = Console()
        md = Markdown(summary)
        console.print(md)