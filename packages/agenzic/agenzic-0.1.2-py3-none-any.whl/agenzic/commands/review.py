import subprocess
import typer
from agenzic.utils.ai_client import ask_ai
import os
from rich.console import Console
from rich.markdown import Markdown


def register(app: typer.Typer):
    @app.command()
    def review(file: str = typer.Option(..., "-f", help="Path to a specific code file to review")):
        """
        Generate AI-powered code review |
        Review a specific file using -f.
        """

        if not os.path.exists(file):
            typer.echo(typer.style(f"File not found: ",fg=typer.colors.RED)+f"{file}")
            raise typer.Exit(1)
        with open(file, "r", encoding="utf-8") as f:
            code_content = f.read()
        prompt = (
                "You are an expert Python code reviewer.\n"
                "Review the following code and provide a structured review:\n"
                "- Security issues\n"
                "- Style suggestions\n"
                "- Possible bugs\n\n"
                f"{code_content}"
        )
        typer.echo(typer.style(f"Reviewing File: ",fg=typer.colors.BRIGHT_GREEN)+f"{file}")


        review_output = ask_ai(prompt)
        typer.echo(typer.style("\nAI Review:",fg=typer.colors.BRIGHT_GREEN))

        console = Console()
        md = Markdown(review_output)
        console.print(md)