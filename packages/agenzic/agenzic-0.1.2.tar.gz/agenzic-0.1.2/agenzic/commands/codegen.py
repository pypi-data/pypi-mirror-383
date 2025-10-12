import typer
from agenzic.utils.ai_client import ask_ai


def register(app: typer.Typer):
    @app.command()
    def codegen(prompt: str, file: str = typer.Option(..., "-f", help="Output file path")):
        """
        Code Generation with a prompt and write the result to a file.
        Example:
            codegen "write a python code" -f abc.py
        """
        typer.echo(typer.style(f"Generating code for prompt: ",fg=typer.colors.BRIGHT_GREEN)+f"{prompt!r}")

        generated_code = ask_ai(prompt)

        with open(file, "w", encoding="utf-8") as f:
            f.write(generated_code)

        typer.echo(typer.style(f"Generated output written to: ",fg=typer.colors.BRIGHT_GREEN)+f"{file}")