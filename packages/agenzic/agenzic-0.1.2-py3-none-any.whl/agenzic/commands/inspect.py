import typer
import sys
import os
import json
from pathlib import Path

app = typer.Typer()

CONFIG_DIR = Path.home() / ".agenzic"
CONFIG_FILE = CONFIG_DIR / "config.json"
PLUGIN_DIR = CONFIG_DIR / "plugins"

def register(app: typer.Typer):
    @app.command()
    def inspect():
        """
        Debug inspector: show environment, config, PATH, plugins, Python version.
        """
        typer.echo(typer.style("Agenzic Debug Inspector\n", fg=typer.colors.BRIGHT_GREEN, bold=True))

        # Python info
        typer.echo(typer.style("Python Info:", fg=typer.colors.YELLOW, bold=True))
        typer.echo(f"  Version: {sys.version}")
        typer.echo(f"  Executable: {sys.executable}\n")

        # PATH
        typer.echo(typer.style("System PATH:", fg=typer.colors.YELLOW, bold=True))
        for p in os.environ.get("PATH", "").split(os.pathsep):
            typer.echo(f"  {p}")
        typer.echo("")

        # Config
        typer.echo(typer.style("Config File:", fg=typer.colors.YELLOW, bold=True))
        if CONFIG_FILE.exists():
            try:
                config = json.loads(CONFIG_FILE.read_text())
                typer.echo(json.dumps(config, indent=2))
            except Exception as e:
                typer.echo(f"  Failed to read config: {e}")
        else:
            typer.echo("  No config file found.")
        typer.echo("")

        # Plugins
        typer.echo(typer.style("Installed Plugins:", fg=typer.colors.YELLOW, bold=True))
        if PLUGIN_DIR.exists():
            plugins = [f.stem for f in PLUGIN_DIR.glob("*.py")]
            if plugins:
                for plugin in plugins:
                    typer.echo(f"  {plugin}")
            else:
                typer.echo("  No plugins installed.")
        else:
            typer.echo("  Plugin directory not found.")

        typer.echo("")
        typer.echo(typer.style("Debug inspection complete.", fg=typer.colors.BRIGHT_GREEN, bold=True))
