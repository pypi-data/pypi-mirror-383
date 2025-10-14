"""
Utility functions module
"""

import platform
import json
from pathlib import Path
from typing import Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from rich.panel import Panel


def get_config_dir() -> Path:
    """Get configuration directory path"""
    home = Path.home()
    config_dir = home / ".scriptmate"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get configuration file path"""
    return get_config_dir() / "config.json"


def get_system_info() -> dict[str, str]:
    """Get system information"""
    return {
        "os": platform.system(),
        "arch": platform.machine(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


def is_dangerous_command(cmd: str) -> bool:
    """Check if command is dangerous"""
    dangerous_patterns = [
        "rm -rf",
        "sudo rm",
        "format",
        "mkfs",
        "dd if=",
        "shutdown",
        "reboot",
        "halt",
        "poweroff",
        "init 0",
        "init 6",
        ":(){ :|:& };:",  # fork bomb
        "chmod -R 777",
        "chown -R",
        "> /dev/",
        "curl | sh",
        "wget | sh",
    ]

    cmd_lower = cmd.lower()
    return any(pattern in cmd_lower for pattern in dangerous_patterns)


def format_command_output(cmd: str, reason: str) -> "Panel":
    """Format command output"""
    from rich.text import Text

    # Check if command is dangerous
    if is_dangerous_command(cmd):
        warning = Text(
            "⚠️  Warning: This is a potentially dangerous command!", style="bold red"
        )
        return Panel.fit(
            f"{warning}\n\nReasoning Process:\n{reason}\n\nGenerated Command:\n{cmd}",
            title="🤖 ScriptMate Generation Result",
            border_style="red",
        )
    else:
        return Panel.fit(
            f"Reasoning Process:\n{reason}\n\nGenerated Command:\n{cmd}",
            title="🤖 ScriptMate Generation Result",
            border_style="green",
        )


def save_json(data: dict[str, Any], file_path: Path) -> None:
    """Save JSON data to file"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Failed to save configuration file: {e}")


def load_json(file_path: Path) -> dict[str, Any] | None:
    """Load JSON data from file"""
    try:
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to read configuration file: {e}")


def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()


def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re

    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None
