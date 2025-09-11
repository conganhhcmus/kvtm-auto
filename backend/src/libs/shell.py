"""
Shell command utilities for KVTM Auto
Provides basic shell utilities (script execution now handled by direct imports)
"""

from typing import List


class Shell:
    """Basic shell command utilities for KVTM Auto"""
    
    @staticmethod
    def escape_arg(arg: str) -> str:
        """Escape a shell argument"""
        escaped = arg.replace('"', '\\"')
        return f'"{escaped}"'
    
    @staticmethod
    def build_simple_command(command: str, *args: str) -> List[str]:
        """Build a simple shell command"""
        return ["sh", "-c", f"{command} {' '.join(args)}"]


class ShellCommandBuilder:
    """Basic builder for shell commands (legacy support)"""
    
    def __init__(self):
        self.commands = []
    
    def add_command(self, command: str) -> "ShellCommandBuilder":
        """Add a shell command"""
        self.commands.append(command)
        return self
    
    def add_echo(self, message: str) -> "ShellCommandBuilder":
        """Add an echo command"""
        self.commands.append(f'echo "{message}"')
        return self
    
    def build(self) -> List[str]:
        """Build the final shell command"""
        if not self.commands:
            return ["true"]  # No-op command
        
        full_command = " && ".join(self.commands)
        return ["sh", "-c", full_command]