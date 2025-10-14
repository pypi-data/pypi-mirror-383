"""
Command executor module
"""

import subprocess
import click
from typing import Any

from .utils import is_dangerous_command


class CommandExecutor:
    """Command executor"""

    def __init__(self):
        self.last_command: str | None = None
        self.last_result: dict[str, Any] | None = None

    def execute_with_confirmation(self, cmd: str, reason: str) -> bool:
        """Execute command with confirmation"""
        # Display generated command and reasoning
        self._display_result(cmd, reason)

        # Check for dangerous commands
        if is_dangerous_command(cmd):
            click.echo("\n⚠️  Warning: Potentially dangerous command detected!")
            if not click.confirm(
                "Are you sure you want to execute this command?", default=False
            ):
                click.echo("❌ Command execution cancelled")
                return False

        # User confirmation
        if not click.confirm("\nExecute this command?", default=True):
            click.echo("❌ Command execution cancelled")
            return False

        # Execute command
        return self._execute_command(cmd)

    def _display_result(self, cmd: str, reason: str) -> None:
        """Display generation result"""
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax

        console = Console()

        # Reasoning process
        console.print("\n💭 Reasoning Process:", style="bold blue")
        console.print(reason, style="dim")

        # Generated command
        console.print("\n🔧 Generated Command:", style="bold green")

        # Syntax highlighting
        cmd_syntax = Syntax(cmd, "bash", theme="monokai", line_numbers=False)
        console.print(Panel(cmd_syntax, border_style="green"))

        # Dangerous command warning
        if is_dangerous_command(cmd):
            console.print(
                "⚠️  Warning: This is a potentially dangerous command!", style="bold red"
            )

    def _execute_command(self, cmd: str) -> bool:
        """Execute command"""
        try:
            click.echo(f"\n🚀 Executing command: {cmd}")
            click.echo("-" * 50)

            # Save command history
            self.last_command = cmd

            # Execute command using subprocess with real-time output
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Display output in real-time
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    output_lines.append(output.strip())

            # Get return code
            return_code = process.poll()

            click.echo("-" * 50)

            if return_code == 0:
                click.echo("✅ Command executed successfully")
                self.last_result = {
                    "success": True,
                    "return_code": return_code,
                    "output": "\n".join(output_lines),
                }
                return True
            else:
                click.echo(f"❌ Command execution failed (return code: {return_code})")
                self.last_result = {
                    "success": False,
                    "return_code": return_code,
                    "output": "\n".join(output_lines),
                }
                return False

        except KeyboardInterrupt:
            click.echo("\n⏹️  Command execution interrupted by user")
            return False
        except Exception as e:
            click.echo(f"❌ Error occurred while executing command: {e}")
            self.last_result = {"success": False, "error": str(e)}
            return False

    def get_last_result(self) -> dict[str, Any] | None:
        """Get last execution result"""
        return self.last_result

    def get_last_command(self) -> str | None:
        """Get last executed command"""
        return self.last_command


# Global executor instance
executor = CommandExecutor()
