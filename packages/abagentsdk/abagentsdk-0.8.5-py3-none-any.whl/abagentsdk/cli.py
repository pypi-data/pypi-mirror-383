# abagentsdk/cli.py
from __future__ import annotations

import argparse
import os
import runpy
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from .utils.silence import install_silence
install_silence()

from . import Agent, Memory

console = Console()
BANNER = "[bold cyan]ABZ Agent SDK CLI[/] — type 'q' to quit."

# Load .env once at startup (no prompting anywhere)
load_dotenv()


def _require_key_or_die() -> None:
    """No prompt. Only accept GEMINI_API_KEY from env/.env; exit if missing."""
    if not os.getenv("GEMINI_API_KEY"):
        console.print(
            "[red]GEMINI_API_KEY not found.[/]\n"
            "Add it to your environment or a .env file (same folder), e.g.:\n"
            "  GEMINI_API_KEY=your_own_key\n"
            "Tip: run [cyan]abagentsdk setup[/] to scaffold a project and .env."
        )
        raise SystemExit(1)


def _run_script(path: str) -> int:
    file = Path(path)
    if not file.exists():
        console.print(f"[red]File not found:[/] {path}")
        return 1
    _require_key_or_die()
    runpy.run_path(str(file), run_name="__main__")
    return 0


def _repl(name: str, instructions: str, model: str, verbose: bool, max_iter: int) -> int:
    _require_key_or_die()
    agent = Agent(
        name=name or "CLI Agent",
        instructions=instructions or "Be concise and helpful.",
        model=model or "auto",
        memory=Memory(),
        verbose=verbose,          # iteration/tool logs only when True
        max_iterations=max_iter,
        # api_key is read from env in your SDK config
    )
    console.print(Panel(BANNER, expand=False))
    while True:
        try:
            msg = input(f"You ({agent.name}) > ").strip()
            if not msg:
                continue
            if msg.lower() in {"q", "quit", "exit"}:
                console.print("[green]Bye![/]")
                return 0
            res = agent.run(msg)
            console.print(Panel(res.content, title="Agent"))
        except KeyboardInterrupt:
            console.print("\n[green]Bye![/]")
            return 0
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")
            if verbose:
                raise


# ---------- Project scaffolding ----------
AGENT_FILE_TEMPLATE = """\
from dotenv import load_dotenv
import os

from abagentsdk import Agent, Memory

# Load .env to populate GEMINI_API_KEY
load_dotenv()

def main():
    # No prompting — fail fast if key missing
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY missing. Add it to .env or your environment.")

    agent = Agent(
        name={agent_name!r},
        instructions={instructions!r},
        model={model!r},
        memory=Memory(),
        verbose=False,
        # api_key NOT passed — Agent reads from env
    )

    print("==== {agent_name} (ABZ Agent SDK) ====")
    while True:
        user = input("You > ").strip()
        if not user:
            continue
        if user.lower() in {{'q', 'quit', 'exit'}}:
            print("Bye!")
            break
        res = agent.run(user)
        print("Agent >", res.content)

if __name__ == "__main__":
    main()
"""

README_SNIPPET = """\
# ABZ Agent SDK quickstart

## Setup

1) Ensure you have Python 3.10+ and a virtual environment.
2) Install the SDK:

```bash
pip install abagentsdk
"""