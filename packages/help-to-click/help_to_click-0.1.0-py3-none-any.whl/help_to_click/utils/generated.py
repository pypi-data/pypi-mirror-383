"""Utility functions for generated plain callers"""
import subprocess
from typing import Any


def invoke_cli(cli_path: str, command_name: str, kwargs: dict, detached: bool = False) -> Any:
    """
    Invoke CLI tool with subprocess
    
    Args:
        cli_path: Path to the CLI executable
        command_name: Command name to invoke
        kwargs: Arguments to pass to the command
        detached: If True, run detached without waiting for result
        
    Returns:
        subprocess.CompletedProcess result or None if detached
    """
    # Build command line arguments
    cmd_args = [cli_path, command_name]
    
    for key, value in kwargs.items():
        if value is not None:
            # Handle boolean flags
            if isinstance(value, bool):
                if value:
                    cmd_args.append(f"--{key}")
            else:
                cmd_args.append(f"--{key}")
                cmd_args.append(str(value))
    
    # Execute the command
    if detached:
        # Run detached (fire and forget)
        subprocess.Popen(
            cmd_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return None
    else:
        # Run and wait for result
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return output if present
        if result.stdout:
            return result.stdout.strip()
        
        return result
