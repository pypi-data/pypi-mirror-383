import typer
import json
from pathlib import Path
import subprocess

myflow_app = typer.Typer(help="Manage recorded command flows | CMDs: record, replay, delete, flows")

FLOWS_DIR = Path.home() / ".agenzic" / "flows"
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

def register(app: typer.Typer):
    app.add_typer(myflow_app, name="myflow",hidden=True)

@myflow_app.command()
def record(name: str):
    """
    Record a sequence of agenzic commands into a flow.
    End recording by typing 'done'.
    """
    typer.echo(typer.style(f"Recording flow: {name}, \nENTER ('done', 'exit', 'quit') to stop recording",fg=typer.colors.BRIGHT_GREEN))
    commands = []
    while True:
        cmd = input(">>> ").strip()
        if cmd in ("done", "exit", "quit"):
            break
        if cmd:
            commands.append(cmd)

    flow_file = FLOWS_DIR / f"{name}.json"
    flow_file.write_text(json.dumps(commands, indent=2))
    typer.echo(typer.style(f"Saved flow '{name}' with {len(commands)} commands.",fg=typer.colors.BRIGHT_GREEN))


@myflow_app.command()
def replay(name: str, dry_run: bool = False):
    """
    Replay a recorded flow.
    """
    flow_file = FLOWS_DIR / f"{name}.json"
    if not flow_file.exists():
        typer.echo(typer.style(f"Flow '{name}' not found.",fg=typer.colors.RED))
        raise typer.Exit(1)

    commands = json.loads(flow_file.read_text())
    typer.echo(typer.style(f"Replaying flow '{name}' with {len(commands)} commands...", fg=typer.colors.BRIGHT_GREEN))
    for cmd in commands:
        typer.echo(typer.style(f"$ {cmd}", fg=typer.colors.BRIGHT_GREEN))
        if not dry_run:
            subprocess.run(cmd.split(), check=False)
    typer.echo(typer.style(f"Command Flow '{name}' ends here.", fg=typer.colors.BRIGHT_GREEN))


@myflow_app.command()
def flows():
    """
    List saved flows.
    """
    typer.echo(typer.style(f"Command Flows:", fg=typer.colors.BRIGHT_GREEN))
    for f in FLOWS_DIR.glob("*.json"):
        typer.echo(f.stem)


@myflow_app.command()
def delete(name: str):
    """
    Delete a saved flow.
    """
    flow_file = FLOWS_DIR / f"{name}.json"
    if flow_file.exists():
        flow_file.unlink()
        typer.echo(typer.style(f"Deleted flow '{name}'.",fg=typer.colors.BRIGHT_GREEN))
    else:
        typer.echo(typer.style(f"Flow '{name}' not found.",fg=typer.colors.RED))
