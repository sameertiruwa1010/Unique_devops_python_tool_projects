"""
cmd_ai/main.py
--------------
Main CLI entry point using Click.
This is what runs when you type: cmd-ai "your query"
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.prompt import Confirm

from cmd_ai.ai_engine import get_suggestion, get_explanation
from cmd_ai.database import fuzzy_lookup, list_all, add_entry
from cmd_ai.executor import execute_with_confirmation, is_dangerous

console = Console()


def print_banner():
    banner = Text()
    banner.append("  cmd-ai", style="bold green")
    banner.append("  —  AI-powered Linux command assistant\n", style="dim")
    banner.append("  Describe what you want. Get the command.", style="italic green")
    console.print(Panel(banner, border_style="green", padding=(0, 1)))


def print_command_result(query: str, command: str, source: str = "AI"):
    """Display the suggested command in a formatted panel."""
    content = Text()
    content.append(f"  {command}", style="bold bright_green")

    label = "🤖 AI Suggested" if source == "AI" else "📦 From local database"
    console.print(
        Panel(
            content,
            title=f"[green]{label}[/green]",
            border_style="green",
            padding=(0, 1),
        )
    )
    console.print(f"  [dim]Query:[/dim]  [white]{query}[/white]")
    console.print(f"  [dim]Run:[/dim]    [yellow]{command}[/yellow]\n")


# ──────────────────────────────────────────────
# Main CLI group
# ──────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.argument("query", required=False)
@click.option("--explain", "-e", is_flag=True, help="Explain the suggested command")
@click.option("--run", "-r", is_flag=True, help="Execute the suggested command after confirmation")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt (use with --run)")
@click.option("--ollama", is_flag=True, help="Use local Ollama AI instead of OpenAI")
@click.option("--model", "-m", default=None, help="Specify AI model to use")
@click.option("--no-db", is_flag=True, help="Skip local database lookup, go straight to AI")
@click.pass_context
def cli(ctx, query, explain, run, yes, ollama, model, no_db):
    """
    \b
    cmd-ai — Linux Command AI Assistant

    Describe what you want to do in plain English.
    cmd-ai will suggest the right Linux command.

    \b
    EXAMPLES:
      cmd-ai "find large files"
      cmd-ai "kill process on port 3000"
      cmd-ai "compress a folder" --run
      cmd-ai "show disk usage" --explain
      cmd-ai --interactive
    """
    if ctx.invoked_subcommand is not None:
        return

    if not query:
        print_banner()
        click.echo(ctx.get_help())
        return

    print_banner()
    console.print(f"  [dim]→ Looking up:[/dim] [white]{query}[/white]\n")

    command = None
    source = "AI"

    # ── Step 1: Try local database first ──────
    if not no_db:
        db_result = fuzzy_lookup(query)
        if db_result:
            source = "DB"
            command = db_result
            console.print(f"  [dim]✓ Found in local database[/dim]\n")

    # ── Step 2: Fall back to AI ────────────────
    if not command:
        console.print(f"  [dim]⠹ Asking AI...[/dim]")
        try:
            command = get_suggestion(query, use_ollama=ollama, model=model)
        except EnvironmentError as e:
            console.print(f"\n  [red]✗ Error:[/red] {e}")
            console.print(
                f"  [dim]Set your key:[/dim] [yellow]export OPENAI_API_KEY=sk-...[/yellow]\n"
            )
            raise SystemExit(1)
        except Exception as e:
            console.print(f"\n  [red]✗ AI Error:[/red] {e}\n")
            raise SystemExit(1)

    # ── Step 3: Display result ─────────────────
    print_command_result(query, command, source=source)

    # ── Step 4: Explain if requested ──────────
    if explain:
        console.print("  [dim]⠹ Getting explanation...[/dim]")
        try:
            explanation = get_explanation(command)
            console.print(
                Panel(
                    explanation,
                    title="[cyan]Explanation[/cyan]",
                    border_style="cyan",
                    padding=(0, 1),
                )
            )
        except Exception as e:
            console.print(f"  [red]Could not get explanation: {e}[/red]")

    # ── Step 5: Execute if requested ──────────
    if run:
        if is_dangerous(command) and not yes:
            console.print("\n  [bold red]⚠  WARNING: This command may be destructive![/bold red]")

        execute_with_confirmation(command, skip_confirm=yes)


# ──────────────────────────────────────────────
# Subcommand: interactive
# ──────────────────────────────────────────────

@cli.command("interactive")
@click.option("--ollama", is_flag=True, help="Use local Ollama AI")
def interactive_mode(ollama):
    """Launch interactive REPL session."""
    print_banner()
    console.print("  [bold cyan]Interactive Mode[/bold cyan] — type a description, press Enter.")
    console.print("  [dim]Commands: 'exit' to quit | 'explain <cmd>' | 'run <description>'[/dim]\n")

    while True:
        try:
            query = click.prompt("  cmd-ai", prompt_suffix="> ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n  [dim]Goodbye![/dim]\n")
            break

        query = query.strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            console.print("\n  [dim]Goodbye![/dim]\n")
            break

        # Parse inline modifiers
        run_it = query.startswith("run ")
        if run_it:
            query = query[4:].strip()

        db_result = fuzzy_lookup(query)
        if db_result:
            command = db_result
            print_command_result(query, command, source="DB")
        else:
            try:
                console.print("  [dim]⠹ Thinking...[/dim]")
                command = get_suggestion(query, use_ollama=ollama)
                print_command_result(query, command, source="AI")
            except Exception as e:
                console.print(f"  [red]Error: {e}[/red]\n")
                continue

        if run_it:
            execute_with_confirmation(command)


# ──────────────────────────────────────────────
# Subcommand: list
# ──────────────────────────────────────────────

@cli.command("list")
@click.option("--search", "-s", default=None, help="Filter entries by keyword")
def list_commands(search):
    """List all commands in the local database."""
    db = list_all()

    table = Table(
        title="Local Command Database",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold green",
        show_lines=True,
    )
    table.add_column("Description", style="white", min_width=30)
    table.add_column("Command", style="bright_green")

    for desc, cmd in sorted(db.items()):
        if search and search.lower() not in desc.lower():
            continue
        table.add_row(desc, cmd)

    console.print(table)
    console.print(f"\n  [dim]{len(db)} commands total[/dim]\n")


# ──────────────────────────────────────────────
# Subcommand: add
# ──────────────────────────────────────────────

@cli.command("add")
@click.argument("description")
@click.argument("command")
def add_command(description, command):
    """Add a custom command to the local database.

    \b
    EXAMPLE:
      cmd-ai add "backup home folder" "tar -czf ~/backup.tar.gz ~/"
    """
    add_entry(description, command)
    console.print(f"\n  [green]✓ Added:[/green] [white]{description}[/white] → [bright_green]{command}[/bright_green]\n")


# ──────────────────────────────────────────────
# Subcommand: explain
# ──────────────────────────────────────────────

@cli.command("explain")
@click.argument("command")
def explain_command(command):
    """Explain what a Linux command does.

    \b
    EXAMPLE:
      cmd-ai explain "find / -size +100M -type f 2>/dev/null"
    """
    console.print(f"\n  [dim]⠹ Explaining:[/dim] [yellow]{command}[/yellow]\n")
    try:
        explanation = get_explanation(command)
        console.print(
            Panel(
                explanation,
                title="[cyan]Command Explanation[/cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
    except Exception as e:
        console.print(f"  [red]Error: {e}[/red]\n")


if __name__ == "__main__":
    cli()
