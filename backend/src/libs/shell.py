"""
Shell command utilities for KVTM Auto
Provides utilities for building and executing shell commands
"""

import json
from pathlib import Path
from typing import List, Optional

from ..models.script import GameOptions


class Shell:
    """Shell command utilities for KVTM Auto"""
    
    @staticmethod
    def escape_arg(arg: str) -> str:
        """Escape a shell argument"""
        escaped = arg.replace('"', '\\"')
        return f'"{escaped}"'
    
    @staticmethod
    def build_simple_command(command: str, *args: str) -> List[str]:
        """Build a simple shell command"""
        return ["sh", "-c", f"{command} {' '.join(args)}"]
    
    @staticmethod
    def build_script_execution_command(
        device_id: str,
        script_id: str,
        script_path: Path,
        game_options: GameOptions,
        open_game_path: Optional[Path] = None
    ) -> List[str]:
        """Build a complete script execution command with optional game opening"""
        builder = ShellCommandBuilder()
        
        # Add open game command if needed
        if game_options.open_game and open_game_path:
            builder.add_echo("Running open-game script...")
            builder.add_python_script(open_game_path, device_id, game_options)
        
        # Build main script command
        options_json = json.dumps(game_options.model_dump())
        main_command = f'python "{script_path}" --device-id "{device_id}" --options \'{options_json}\''
        
        # Use loop builder for complex looping
        loop_commands = builder.build_with_loop(
            max_loops=game_options.max_loops,
            loop_delay=game_options.loop_delay,
            loop_command=main_command,
            script_id=script_id
        )
        return loop_commands


class ShellCommandBuilder:
    """Builder for shell commands with loop support"""
    
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
    
    def add_python_script(
        self, 
        script_path: Path, 
        device_id: str, 
        game_options: GameOptions,
        loop_index: Optional[str] = None
    ) -> "ShellCommandBuilder":
        """Add a Python script execution command"""
        options_json = json.dumps(game_options.model_dump())
        cmd = f'python "{script_path}" --device-id "{device_id}" --options \'{options_json}\''
        
        if loop_index:
            cmd += f' --loop-index {loop_index}'
            
        self.commands.append(cmd)
        return self
    
    def build_with_loop(
        self,
        max_loops: int,
        loop_delay: float,
        loop_command: str,
        script_id: str
    ) -> List[str]:
        """Build a looped command structure"""
        if max_loops == 1:
            self.commands.append(f'echo "Executing script {script_id}..."')
            self.commands.append(loop_command)
        else:
            loop_script = f'''
for i in $(seq 1 {max_loops}); do
    echo "Loop $i/{max_loops} - Executing script {script_id}..."
    {loop_command} --loop-index $((i-1))
    if [ $? -ne 0 ]; then
        echo "Script failed on loop $i"
        exit 1
    fi
    if [ $i -lt {max_loops} ] && [ "{loop_delay}" != "0" ] && [ "{loop_delay}" != "0.0" ]; then
        echo "Waiting {loop_delay}s before next loop..."
        sleep {loop_delay}
    fi
done
echo "Script {script_id} completed after {max_loops} loop(s)"
'''
            self.commands.append(loop_script)
        
        return self.build()
    
    def build(self) -> List[str]:
        """Build the final shell command"""
        if not self.commands:
            return ["true"]  # No-op command
        
        full_command = " && ".join(self.commands)
        return ["sh", "-c", full_command]