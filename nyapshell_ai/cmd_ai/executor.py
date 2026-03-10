
import subprocess


DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -f",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",
    "> /dev/sda",
    "chmod -R 777 /",
    "chown -R",
    "sudo rm",
    "wget -O- | sh",
    "curl | sh",
    "curl | bash",
]


def is_dangerous(command: str) -> bool:
    """Check if a command matches known dangerous patterns."""
    lower = command.lower()
    return any(pattern in lower for pattern in DANGEROUS_PATTERNS)


def confirm_execution(command: str, force_warn: bool = False) -> bool:
    """Ask the user to confirm before executing a command."""
    if force_warn or is_dangerous(command):
        print(f"\n  ⚠️  WARNING: This command may be destructive!")
        print(f"  Please review carefully before confirming.\n")

    print(f"  Command to execute:  {command}\n")
    answer = input("  Run this command? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def run_command(command: str) -> int:
    """Execute the shell command. Returns the exit code."""
    print()
    try:
        result = subprocess.run(command, shell=True, text=True)
        return result.returncode
    except KeyboardInterrupt:
        print("\n  Interrupted.")
        return 130
    except Exception as e:
        print(f"\n  Error executing command: {e}")
        return 1


def execute_with_confirmation(command: str, skip_confirm: bool = False) -> None:
    """Full workflow: confirm → execute → show result."""
    if skip_confirm:
        run_command(command)
        return

    confirmed = confirm_execution(command)
    if confirmed:
        exit_code = run_command(command)
        if exit_code == 0:
            print("\n  ✓ Command completed successfully.")
        else:
            print(f"\n  ✗ Command exited with code {exit_code}.")
    else:
        print("\n  Cancelled. Command was not executed.")
