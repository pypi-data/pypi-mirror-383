import os
import typer
import requests


# -------------------------------------------------------------------------
# EXPERIMENTAL COMMAND
# Purpose: Testing InceptionLabs' `mercury-coder` for code generation.
# Benchmark: ~7 seconds faster than `gpt-4o-mini` on codegen tests.
# Status: Hidden / Experimental
# Notes:
#   - Needs environment variable `INCEPTION_API_KEY` to be set.
# -------------------------------------------------------------------------

# This command is intentionally left here for experimentation with external APIs.
# It is NOT part of the official Agenzic feature set.


def get_inception_api_key() -> str:
    key = os.getenv("INCEPTION_API_KEY")
    if not key:
        typer.echo("Please set INCEPTION_API_KEY environment variable")
        raise typer.Exit()
    return key

API_URL = "https://api.inceptionlabs.ai/v1/chat/completions"

def ask_inception(prompt: str) -> str:
    key = get_inception_api_key()
    headers = {"Authorization":f"Bearer {key}",
               "Content-Type": "application/json"
    }
    payload = {
        "model":"mercury-coder",
        "messages": [{"role":"user","content":prompt}],
    }

    try:
        response = requests.post(API_URL,headers=headers,json=payload,timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        typer.echo(f"API CALL FAILER {e}")
        raise typer.Exit(1)


def register(app: typer.Typer):
    @app.command(hidden=True)
    def icodegen(prompt: str, file: str = typer.Option(..., "--file", help="Output file path")):
        """
        Code Generation with a prompt and write the result to a file using InceptionLabs' mercury-coder.
        Example:
            icodegen "write a python code" --file abc.py
        """
        typer.echo(f"Generating code for prompt: {prompt!r}")

        generated_code = ask_inception(prompt)

        with open(file, "w", encoding="utf-8") as f:
            f.write(generated_code)

        typer.echo(f"Generated output written to: {file}")