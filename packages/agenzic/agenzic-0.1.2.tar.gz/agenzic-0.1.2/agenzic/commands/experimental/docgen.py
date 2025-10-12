import typer
import os
from agenzic.utils.ai_client import ask_ai

def register(app: typer.Typer):
    @app.command()
    def docgen(
            file: str = typer.Option(None, "-f", help="Path to specific file to generate documentation"),
            dir: str = typer.Option(None, "-d", help="Path to project directory to generate documentation")
    ):
        """
        Generate AI-powered documentation |
        Generate for a specific file using -f |
        Or, generate for directory using -d
        """

        if file and dir:
            typer.echo("Please specify either -f or -d, not both.")
            raise typer.Exit(1)
        if not file and not dir:
            typer.echo("Please specify either -f or -d")
            raise typer.Exit(1)

        if file:
            if not os.path.exists(file):
                typer.echo(typer.style(f"File not found: ",fg=typer.colors.RED)+f"{file}")
                raise typer.Exit(1)

            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            prompt = (
                "You are an expert Python developer and technical writer.\n"
                "Generate docstrings for all functions/classes in this code and a README-style documentation.\n\n"
                f"{content}"
            )

            typer.echo(typer.style(f"Generating documentation for file: ",fg=typer.colors.BRIGHT_GREEN)+f"{file}")
            docs_output=ask_ai(prompt)

            file_dir = os.path.dirname(file)
            file_base = os.path.basename(file).replace(".py","")
            out_path = os.path.join(file_dir, f"{file_base}_README.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(docs_output)

            typer.echo(typer.style(f"Documentation written to: ",fg=typer.colors.BRIGHT_GREEN)+f"{out_path}")

        else:
            if not os.path.exists(dir):
                typer.echo(typer.style(f"Directory not found: ", fg=typer.colors.RED) + f"{dir}")
                raise typer.Exit(1)

            py_files = []
            for root, _, files in os.walk(dir):
                for f_name in files:
                    if f_name.endswith(".py"):
                        py_files.append(os.path.join(root, f_name))

            if not py_files:
                typer.echo("No Python files found in directory.")
                raise typer.Exit(1)

            combined_content = ""
            for f_path in py_files:
                with open(f_path, "r", encoding="utf-8") as f:
                    combined_content += f"# File: {f_path}\n"
                    combined_content += f.read() + "\n\n"

            prompt = (
                "You are an expert Python developer and technical writer.\n"
                "Generate a comprehensive README for the following Python project:\n\n"
                f"{combined_content}"
            )

            typer.echo(typer.style(f"Generating documentation for entire project: ",fg=typer.colors.BRIGHT_GREEN)+f"{dir}")
            docs_output = ask_ai(prompt)

            out_path = os.path.join(dir, "README.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(docs_output)

            typer.echo(typer.style(f"Project README written to: ",fg=typer.colors.BRIGHT_GREEN)+f"{out_path}")