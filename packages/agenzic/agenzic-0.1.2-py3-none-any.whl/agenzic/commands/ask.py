import os
import typer
from agenzic.utils.ai_client import ask_ai
from rich.markdown import Markdown
from rich.console import Console

def register(app: typer.Typer):
    @app.command()
    def ask(question: str,
            file: str = typer.Option(None, "-f",help="Path to specific file to search"),
            dir: str = typer.Option(".", "-d", help="Path folder to search if no file specified")
    ):
        """
        Ask AI a question about your project or a specific file. |
        Defaults to current directory. Use -f or -d to override.
        """
        if file:
            if not os.path.exists(file):
                typer.echo(typer.style(f"File not found: ",fg=typer.colors.RED)+f"{file}")
                raise typer.Exit(1)
            with open(file, "r", encoding="utf-8") as f:
                code_content = f.read()
        else:
            code_content=""
            for root, _, files in os.walk(dir):
                for f in files:
                    if f.endswith((".py", ".txt", ".md")):
                        path = os.path.join(root, f)
                        with open(path, "r", encoding="utf-8") as file_f:
                            code_content += f"\n\n# File: {path}\n"
                            code_content += file_f.read()

        if not code_content.strip():
            typer.echo(typer.style("No code content found to analyze in directory: ",fg=typer.colors.RED)+f"{dir}")
            raise typer.Exit(1)

        prompt = f"""
            You are an expert Python developer. Answer the question based only on the code below.
            Do not make assumptions beyond the provided code.

            Code:
            {code_content}

            Question:
            {question}
            """

        typer.echo(typer.style("Thinking...",fg=typer.colors.BRIGHT_GREEN))
        answer=ask_ai(prompt)
        typer.echo(typer.style("\nAI Answer:",fg=typer.colors.BRIGHT_GREEN))

        console = Console()
        md = Markdown(answer)
        console.print(md)