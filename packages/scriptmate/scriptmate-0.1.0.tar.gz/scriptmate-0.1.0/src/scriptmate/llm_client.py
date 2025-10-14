"""
LLM Client Module
"""

import json
import platform
import requests
from textwrap import dedent


class LLMClient:
    """LLM Client for generating shell commands"""

    def __init__(self, api_key: str, model_name: str, base_url: str):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        current_os = platform.system()
        current_arch = platform.machine()

        return dedent(
            f"""\
        You are a professional developer focused on generating Shell commands.
        Your task is to generate correct Shell commands based on user requests.

        Important guidelines:
        1. Always reply in the same language as the user's prompt.
        2. Current OS: {current_os}, Architecture: {current_arch}. Consider this information when generating commands.
        3. Ensure generated commands are safe, accurate, and suitable for the current system environment.

        Please reply in JSON format with the following fields:
        {{
            "reason": "Your thinking process and reasoning, explaining why you chose this command",
            "cmd": "Generated shell command (must be a directly executable string)"
        }}

        Notes:
        - The cmd field must be a directly executable shell command string
        - If multiple commands are needed, connect them with && or ;
        - Avoid generating dangerous commands that could harm the system
        - Prioritize cross-platform compatibility
        """
        )

    def generate_command(self, user_input: str) -> dict[str, str]:
        """Generate shell command based on user input"""
        try:
            # Build request data
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_input},
                ],
                "temperature": 0.1,
                "max_tokens": 1000,
            }

            # Send request
            response = self.session.post(
                f"{self.base_url}/chat/completions", json=data, timeout=30
            )

            # Check response status
            if response.status_code != 200:
                raise Exception(
                    f"API request failed: {response.status_code} - {response.text}"
                )

            # Parse response
            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise Exception("Invalid API response format: choices field not found")

            content = result["choices"][0]["message"]["content"].strip()

            # Try to parse JSON response
            try:
                # If content is wrapped in code blocks, extract JSON part first
                json_content = content
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    if end != -1:
                        json_content = content[start:end].strip()
                elif content.startswith("```") and content.endswith("```"):
                    json_content = content[3:-3].strip()

                parsed_result = json.loads(json_content)

                # Validate required fields
                if "cmd" not in parsed_result or "reason" not in parsed_result:
                    raise Exception("Response missing required fields (cmd or reason)")

                return {
                    "cmd": str(parsed_result["cmd"]).strip(),
                    "reason": str(parsed_result["reason"]).strip(),
                }

            except json.JSONDecodeError as e:
                # If not JSON format, try to extract from text
                print(f"JSON parsing failed: {e}")
                print(f"Original content: {content}")
                return self._extract_from_text(content)

        except requests.exceptions.Timeout:
            raise Exception("Request timeout, please check network connection")
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Connection failed, please check network connection and Base URL"
            )
        except Exception as e:
            raise Exception(f"Command generation failed: {str(e)}")

    def _extract_from_text(self, content: str) -> dict[str, str]:
        """Extract command and reasoning from text"""
        lines = content.split("\n")
        cmd = ""
        reason = ""
        in_code_block = False

        # Try to extract JSON information from text
        for line in lines:
            line = line.strip()

            # Skip code block markers
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # Find lines containing "cmd":
            if '"cmd":' in line:
                try:
                    # Extract command part
                    start = line.find('"cmd":') + 6
                    cmd_part = line[start:].strip()
                    if cmd_part.startswith('"'):
                        end = cmd_part.find('"', 1)
                        if end != -1:
                            cmd = cmd_part[1:end]
                except Exception:
                    pass

            # Find lines containing "reason":
            if '"reason":' in line:
                try:
                    # Extract reasoning part
                    start = line.find('"reason":') + 9
                    reason_part = line[start:].strip()
                    if reason_part.startswith('"'):
                        end = reason_part.rfind('"')
                        if end > 0:
                            reason = reason_part[1:end]
                except Exception:
                    pass

        # If still no command found, try more lenient matching
        if not cmd:
            for line in lines:
                line = line.strip()
                if line and not line.startswith(("#", "//", "```", '"')):
                    # Check if it looks like a command
                    common_commands = [
                        "ls",
                        "cd",
                        "pwd",
                        "cat",
                        "grep",
                        "find",
                        "ps",
                        "top",
                        "df",
                        "du",
                        "whoami",
                        "id",
                        "uname",
                        "who",
                        "w",
                        "users",
                        "last",
                        "history",
                    ]
                    if any(line.startswith(cmd_name) for cmd_name in common_commands):
                        cmd = line
                        break

        if not cmd:
            # If no command found, use entire content as reasoning and generate a generic command
            reason = content if not reason else reason
            cmd = "echo 'Unable to parse command, please provide more specific description'"

        if not reason:
            reason = "Command generated based on user description"

        return {"cmd": cmd, "reason": reason}

    def test_connection(self) -> bool:
        """Test connection to LLM API"""
        try:
            result = self.generate_command("test connection")
            return "cmd" in result and "reason" in result
        except Exception:
            return False

        if not reason:
            reason = "Command generated based on user description"

        return {"cmd": cmd, "reason": reason}

    def test_connection(self) -> bool:
        """Test connection to LLM API"""
        try:
            result = self.generate_command("test connection")
            return "cmd" in result and "reason" in result
        except Exception:
            return False
