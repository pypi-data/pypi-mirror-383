
import click
import subprocess
import re
from typing import Any
from help_to_click.core.spec import H2CCommand, H2COption
from help_to_click.core.config import H2CConfig, Callback


class H2CCmdSplitter:
    def __init__(self, config: H2CConfig = None):
        """
        Initialize command splitter with configuration
        
        Args:
            config: H2CConfig instance for controlling behavior
        """
        self.config = config or H2CConfig()
    
    def split_commands(self, commands: str) -> list[str]:
        """
        Split multi-line command help text into individual commands.
        
        A new command starts when:
        - Line begins with a letter (no leading whitespace)
        - Line is not empty
        
        All subsequent indented lines belong to that command until
        the next command starts.
     
        """
        lines = commands.splitlines()
        
        cmd_lines = []
        current_cmd = []
        
        for line in lines:
            # Skip empty lines
            if line.strip() == "":
                continue
            
            # Check if this is the start of a new command
            # New command = first character is alphabetic AND no leading whitespace
            if line and line[0].isalpha() and not line.startswith(" "):
                # Save previous command if exists
                if current_cmd:
                    cmd_lines.append("\n".join(current_cmd))
                    current_cmd = []
                
                # Start new command
                current_cmd.append(line)
            else:
                # Continuation of current command (indented line)
                if current_cmd:
                    current_cmd.append(line)
        
        # Don't forget the last command
        if current_cmd:
            cmd_lines.append("\n".join(current_cmd))
        
        return cmd_lines
    
class H2CParser:
    def __init__(self, config: H2CConfig = None):
        """
        Initialize parser with configuration
        
        Args:
            config: H2CConfig instance for controlling parsing behavior
        """
        self.config = config or H2CConfig()
    
    def parse(self, string : str) -> H2CCommand:
        raise NotImplementedError()
    
class H2CClickBuilder:
    """Build Click commands from H2CCommand objects"""
    
    def __init__(self, config: H2CConfig = None):
        """
        Initialize Click builder with configuration
        
        Args:
            config: H2CConfig instance for controlling Click generation
        """
        self.config = config or H2CConfig()
    
    def build(self, command: H2CCommand) -> click.Command:
        """
        Build a Click command from H2CCommand specification
        
        Args:
            command: H2CCommand object with command specification
            
        Returns:
            click.Command object ready to be added to a group
        """
        # Determine which callback to use for this command
        callback = self._resolve_callback(command.name)
        
        # Create the command callback function
        def command_callback(**kwargs):
            """Generated command callback"""
            return self._execute_callback(command.name, callback, kwargs)
        
        # Build the command with decorators
        # We need to apply decorators in reverse order (bottom-up)
        cmd_func = command_callback
        cmd_func.__name__ = command.name.replace('-', '_')  # Click-safe name
        
        # Add positional arguments first (bottom decorators)
        for arg in reversed(command.args):
            cmd_func = self._add_argument(cmd_func, arg)
        
        # Add options (top decorators)  
        for opt_name, opt in reversed(list(command.options.items())):
            cmd_func = self._add_option(cmd_func, opt)
        
        # Wrap with @click.command() decorator
        cmd_func = click.command(name=command.name, help=f"Command: {command.name}")(cmd_func)
        
        return cmd_func
    
    def _resolve_callback(self, command_name: str) -> Callback:
        """
        Resolve which callback to use for a command
        
        Priority:
        1. Exact override match in override_callbacks
        2. Regex pattern match in regex_callbacks
        3. Default callback
        
        Args:
            command_name: Name of the command
            
        Returns:
            Callback instance to use
        """
        # Check for exact override
        if command_name in self.config.override_callbacks:
            return self.config.override_callbacks[command_name]
        
        # Check regex patterns
        for pattern, callback in self.config.regex_callbacks.items():
            if re.match(pattern, command_name):
                return callback
        
        # Use default callback
        return self.config.default_callback
    
    def _execute_callback(self, command_name: str, callback: Callback, kwargs: dict) -> Any:
        """
        Execute a callback for a command
        
        Args:
            command_name: Name of the command being executed
            callback: Callback configuration to use
            kwargs: Parsed command-line arguments
            
        Returns:
            Result from the callback execution
        """
        result = None
        
        # If custom callback function is provided, use it
        if callback.callback_func:
            result = callback.callback_func(kwargs)
        
        # If CLI path is provided, invoke the actual CLI tool
        elif callback.cli_path_target:
            result = self._invoke_cli(callback.cli_path_target, command_name, kwargs)
        
        # Otherwise, just echo what would be executed (placeholder behavior)
        else:
            click.echo(f"Executing command: {command_name}")
            click.echo(f"Arguments: {kwargs}")
            result = kwargs
        
        # Apply post-callback handling if provided
        if callback.post_callback_handling and result is not None:
            callback.post_callback_handling(result)
        
        return result
    
    def _invoke_cli(self, cli_path: str, command_name: str, kwargs: dict) -> Any:
        """
        Invoke the actual CLI tool with subprocess
        
        Args:
            cli_path: Path to the CLI executable
            command_name: Command name to invoke
            kwargs: Arguments to pass to the command
            
        Returns:
            subprocess.CompletedProcess result
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
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Echo output if present
            if result.stdout:
                click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            
            return result
        
        except subprocess.CalledProcessError as e:
            click.echo(f"Error executing command: {e}", err=True)
            if e.stdout:
                click.echo(e.stdout)
            if e.stderr:
                click.echo(e.stderr, err=True)
            raise click.ClickException(f"Command failed with exit code {e.returncode}")

    
    def _add_option(self, func, option: H2COption):
        """Add a Click option decorator to function"""
        
        # Build option parameters
        option_names = [f'--{option.name}']
        
        # Map our types to Click types
        click_type = self._map_type(option.typeOfVar)
        
        # Build decorator kwargs
        decorator_kwargs = {
            'type': click_type,
            'help': option.description or f'{option.name} option',
        }
        
        # Handle required/optional
        if option.isRequired:
            decorator_kwargs['required'] = True
        else:
            decorator_kwargs['default'] = option.default
        
        # Handle flags
        if option.isFlag:
            decorator_kwargs['is_flag'] = True
            decorator_kwargs.pop('type', None)  # Flags don't need type
            decorator_kwargs.pop('default', None)
        
        # Apply the decorator
        return click.option(*option_names, **decorator_kwargs)(func)
    
    def _add_argument(self, func, arg_name: str):
        """Add a Click argument decorator to function"""
        return click.argument(arg_name)(func)
    
    def _map_type(self, type_str: str) -> type:
        """Map our type strings to Click types"""
        type_mapping = {
            'int': int,
            'float': float,
            'bool': bool,
            'string': str,
            'choice': str,  # Choices are handled separately
            'path': click.Path(),
            'tuple': str,  # Tuples as strings for now
        }
        return type_mapping.get(type_str, str)