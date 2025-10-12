import subprocess
import typer
from agenzic.utils.ai_client import ask_ai

def register(app: typer.Typer):
    @app.command()
    def commit(alt: int = 1):
        """Generate AI commit message"""
        diff = subprocess.getoutput("git diff --staged")

        if not diff:
            typer.echo(typer.style("No staged changes found. Stage your changes with `git add`.",fg=typer.colors.RED))
            raise typer.Exit(1)

        prompt = f"Generate {alt} conventional/professional commit message(s) for this git diff:\n{diff}"

        typer.echo(typer.style("Generating Commit Message:", fg=typer.colors.BRIGHT_GREEN))
        result = ask_ai(prompt)

        typer.echo(typer.style("\nAI Suggestion(s):",fg=typer.colors.BRIGHT_GREEN))
        typer.echo(result)

        flag = True
        while flag:
            choice = typer.prompt(typer.style("\nDo you want to (c)ommit, (e)dit, or (q)uit?", fg=typer.colors.BRIGHT_GREEN), default="q")

            if choice.lower().startswith("c"):
                flag = False
                commit_lines = result.split("\n")
                subprocess.run(["git", "commit", "-m", commit_lines[0], "-m", "\n".join(commit_lines[1:])])
                typer.echo(typer.style("Commited.",fg=typer.colors.BRIGHT_GREEN))

            elif choice.lower().startswith("e"):
                changes = typer.prompt(typer.style("\nDescribe changes you would like the AI to make to your commit message", fg=typer.colors.BRIGHT_GREEN))
                prompt = (
                    f"You are a commit message assistant.\n"
                    f"Original Git Diff:\n{diff}\n\n"
                    f"Old Commit Message:\n{result}\n\n"
                    f"Requested changes:\n{changes}\n\n"
                    f"Generate {alt} conventional/professional commit message(s) with the changes suggested."
                    f"Your response should only have the updated commit message."
                )
                typer.echo(typer.style("\nAI Suggestion(s):",fg=typer.colors.BRIGHT_GREEN))
                result =  ask_ai(prompt)
                typer.echo(result)

            else:
                flag = False
                typer.echo(typer.style("Commit cancelled", fg=typer.colors.RED))