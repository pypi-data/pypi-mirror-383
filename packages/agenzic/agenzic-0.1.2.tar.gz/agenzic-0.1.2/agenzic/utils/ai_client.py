import os
import typer
import requests
from agenzic.utils.helpers import get_api_key,get_model

API_URL = "https://api.openai.com/v1/chat/completions"

def ask_ai(prompt: str) -> str:
    key = get_api_key()
    headers = {"Authorization":f"Bearer {key}",
               "Content-Type": "application/json"
    }
    model = get_model()
    payload = {
        "model":model,
        "messages": [{"role":"user","content":prompt}],
        "temperature":0.7
    }

    try:
        response = requests.post(API_URL,headers=headers,json=payload,timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        typer.echo(f"API CALL FAILER {e}")
        raise typer.Exit(1)