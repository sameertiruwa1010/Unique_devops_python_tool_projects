"""
cmd_ai/ai_engine.py
-------------------
Handles AI-powered command suggestion via OpenAI API.
Also supports Ollama (local AI) as a fallback.
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert Linux system administrator.
Your ONLY job is to convert a plain English description into the best Linux/Unix shell command.

Rules:
- Output ONLY the raw command — no explanation, no markdown, no code blocks
- Use pipes and combinations when appropriate
- Add 2>/dev/null to suppress errors where sensible
- For destructive operations, add a safe confirmation flag
- If multiple steps are needed, chain with && or show a pipeline
- Never wrap in backticks or quotes
"""


def ask_openai(query: str, model: str = "gpt-4o-mini") -> str:
    """
    Send query to OpenAI and return the suggested command.
    Requires OPENAI_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set. Run: export OPENAI_API_KEY=your_key_here"
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        max_tokens=200,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def ask_ollama(query: str, model: str = "mistral") -> str:
    """
    Send query to a local Ollama instance and return the suggested command.
    Requires Ollama to be running: https://ollama.ai
    """
    try:
        import requests

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": f"{SYSTEM_PROMPT}\n\nUser: {query}\nCommand:",
                "stream": False,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except ImportError:
        raise ImportError("Install requests: pip install requests")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}. Is Ollama running?")


def get_suggestion(query: str, use_ollama: bool = False, model: str = None) -> str:
    """
    Main entry point. Returns AI-suggested command for the given query.
    Falls back gracefully with helpful error messages.
    """
    if use_ollama:
        return ask_ollama(query, model=model or "mistral")
    else:
        return ask_openai(query, model=model or "gpt-4o-mini")


def get_explanation(command: str) -> str:
    """
    Ask the AI to explain what a command does, part by part.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a Linux expert. Explain the given shell command clearly and concisely. Break down each part/flag. Use plain English. Keep it brief.",
            },
            {
                "role": "user",
                "content": f"Explain this command: {command}",
            },
        ],
        max_tokens=400,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
