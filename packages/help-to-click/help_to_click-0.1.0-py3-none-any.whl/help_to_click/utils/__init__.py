"""Utilities for process-based help text extraction and CLI wrapping"""
import subprocess
from typing import Optional
from help_to_click.core.config import H2CConfig, Callback


def get_help_text_from_process(command: str) -> str:
    """
    Extract help text by running a command
    
    Args:
        command: Command to run (e.g., "mycli --help")
        
    Returns:
        Help text output from the command
        
    Raises:
        RuntimeError: If command fails to execute
    """
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            shell=True
        )
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get help text from '{command}': {e.stderr}") from e


def create_config_with_callback(callback: Optional[Callback] = None, base_config: Optional[H2CConfig] = None) -> H2CConfig:
    """
    Create H2CConfig with the specified callback as default
    
    Args:
        callback: Callback to use as default_callback (if None, uses empty Callback)
        base_config: Base config to copy settings from (if None, uses default H2CConfig)
        
    Returns:
        H2CConfig with callback configured as default
    """
    if base_config is None:
        config = H2CConfig()
    else:
        # Copy the base config
        config = H2CConfig(
            type_inference=base_config.type_inference,
            parser=base_config.parser,
            click=base_config.click,
            regex_callbacks=base_config.regex_callbacks.copy(),
            override_callbacks=base_config.override_callbacks.copy()
        )
    
    # Set the default callback
    config.default_callback = callback or Callback()
    
    return config


def extract_base_command(command: str) -> str:
    """
    Extract base command from a command string
    
    Args:
        command: Full command string (e.g., "git --help", "mycli --version")
        
    Returns:
        Base command (e.g., "git", "mycli")
    """
    return command.split()[0]