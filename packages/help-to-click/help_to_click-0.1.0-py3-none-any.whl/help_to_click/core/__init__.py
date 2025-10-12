
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
import inspect

import click

from help_to_click.core.helper import H2CCmdSplitter, H2CParser, H2CClickBuilder
from help_to_click.core.spec import H2CCommand, H2COption
from help_to_click.core.config import H2CConfig, Callback


@dataclass
class HelpToClick:
    rawHelpStr : str
    cleanUpHelpers : list[Callable[[str], str]]
    cmdSplitter : H2CCmdSplitter
    cmdParser : H2CParser
    config: H2CConfig = field(default_factory=H2CConfig)

    @cached_property
    def rawHelpStrCleaned(self) -> str:
        cleanedStr = self.rawHelpStr
        for helper in self.cleanUpHelpers:
            cleanedStr = helper(cleanedStr)
        return cleanedStr

    def __post_init__(self):
        self.rawHelpStrCleaned
        
        # Pass config to all sub-components
        if hasattr(self.cmdSplitter, 'config'):
            self.cmdSplitter.config = self.config
        if hasattr(self.cmdParser, 'config'):
            self.cmdParser.config = self.config

    def generateCmdContexts(self) -> list[H2CCommand]:
        """Generate list of H2CCommand objects from help text"""
        # Split into individual command strings
        cmd_strings = self.cmdSplitter.split_commands(self.rawHelpStrCleaned)
        
        # Parse each command string
        commands = []
        for cmd_str in cmd_strings:
            try:
                cmd = self.cmdParser.parse(cmd_str)
                commands.append(cmd)
            except Exception as e:
                # Skip commands that fail to parse
                print(f"Warning: Failed to parse command: {e}")
                continue
        
        return commands
    
    def generateClickGroup(self, group_name: str, appendGroup: click.Group = None) -> click.Group:
        """
        Generate a Click command group from parsed commands
        
        Args:
            group_name: Name for the Click group
            appendGroup: Optional existing Click group to append commands to
            
        Returns:
            click.Group with all commands added, organized by their group field
        """
        # Get all parsed commands
        commands = self.generateCmdContexts()
        
        # Create or use existing group
        if appendGroup is None:
            main_group = click.Group(name=group_name, help=f"Commands for {group_name}")
        else:
            main_group = appendGroup
        
        # Create a builder for converting H2CCommand to click.Command
        builder = H2CClickBuilder(config=self.config)
        
        # Organize commands by their group field
        # Groups are separated by dots, e.g., "database.user" means nested groups
        grouped_commands = {}
        ungrouped_commands = []
        
        for cmd in commands:
            if cmd.group:
                if cmd.group not in grouped_commands:
                    grouped_commands[cmd.group] = []
                grouped_commands[cmd.group].append(cmd)
            else:
                ungrouped_commands.append(cmd)
        
        # Add ungrouped commands directly to main group
        for cmd in ungrouped_commands:
            click_cmd = builder.build(cmd)
            main_group.add_command(click_cmd)
        
        # Handle grouped commands
        # Support nested groups like "database.user" -> database group -> user subgroup
        for group_path, group_cmds in grouped_commands.items():
            # Split group path by dots
            group_parts = group_path.split('.')
            
            # Navigate/create nested groups
            current_group = main_group
            for part in group_parts:
                # Check if subgroup exists
                existing_cmd = current_group.commands.get(part)
                
                if existing_cmd is None:
                    # Create new subgroup
                    subgroup = click.Group(name=part, help=f"{part} commands")
                    current_group.add_command(subgroup)
                    current_group = subgroup
                elif isinstance(existing_cmd, click.Group):
                    # Use existing subgroup
                    current_group = existing_cmd
                else:
                    # Conflict: name already used for command
                    print(f"Warning: Group name '{part}' conflicts with existing command")
                    continue
            
            # Add commands to the final group
            for cmd in group_cmds:
                click_cmd = builder.build(cmd)
                current_group.add_command(click_cmd)
        
        return main_group
    
    def generateClickFile(self, file_path: str, group_name: str = "cli"):
        """Generate a standalone Python file with Click CLI"""
        commands = self.generateCmdContexts()
        builder = H2CClickBuilder(config=self.config)
        
        lines = []
        lines.append("#!/usr/bin/env python3")
        lines.append('"""Generated CLI from help text"""')
        lines.append("import click")
        lines.append("")
        
        # Collect all callback functions that need to be included
        callback_funcs = set()
        for cmd in commands:
            callback = builder._resolve_callback(cmd.name)
            if callback and callback.callback_func:
                callback_funcs.add(callback.callback_func)
            if callback and callback.post_callback_handling:
                callback_funcs.add(callback.post_callback_handling)
        
        # Add callback function source code
        for func in callback_funcs:
            try:
                source = inspect.getsource(func)
                lines.append(source)
                lines.append("")
            except Exception:
                pass
        
        # Generate main group
        lines.append("@click.group()")
        lines.append("def cli():")
        lines.append(f'    """Commands for {group_name}"""')
        lines.append("    pass")
        lines.append("")
        
        # Generate commands
        for cmd in commands:
            callback = builder._resolve_callback(cmd.name)
            
            # Command decorator
            lines.append(f"@cli.command(name='{cmd.name}')")
            
            # Add options
            for opt_name, opt in cmd.options.items():
                opt_flags = [f"--{opt_name}"]
                opt_args = []
                
                if opt.isRequired:
                    opt_args.append("required=True")
                if opt.isFlag:
                    opt_args.append("is_flag=True")
                else:
                    type_map = {
                        'int': 'int',
                        'float': 'float', 
                        'bool': 'bool',
                        'string': 'str',
                        'path': 'click.Path()',
                        'tuple': 'str'
                    }
                    type_str = type_map.get(opt.typeOfVar, 'str')
                    opt_args.append(f"type={type_str}")
                
                args_str = ", ".join(opt_args)
                lines.append(f"@click.option({', '.join(repr(f) for f in opt_flags)}, {args_str})")
            
            # Add arguments
            for arg in (cmd.args or []):
                lines.append(f"@click.argument('{arg}')")
            
            # Function definition
            params = []
            for opt_name in cmd.options.keys():
                params.append(opt_name)
            for arg in (cmd.args or []):
                params.append(arg)
            
            lines.append(f"def {cmd.name}({', '.join(params)}):")
            lines.append(f'    """Command: {cmd.name}"""')
            
            # Build kwargs dict
            lines.append("    kwargs = {")
            for p in params:
                lines.append(f"        '{p}': {p},")
            lines.append("    }")
            
            # Call callback or default action
            if callback and callback.callback_func:
                func_name = callback.callback_func.__name__
                lines.append(f"    result = {func_name}(kwargs)")
                if callback.post_callback_handling:
                    post_func_name = callback.post_callback_handling.__name__
                    lines.append(f"    {post_func_name}(result)")
            else:
                lines.append(f"    print(f'Executing command: {cmd.name}')")
                lines.append("    print(f'Arguments: {kwargs}')")
            
            lines.append("")
        
        # Main entry point
        lines.append("if __name__ == '__main__':")
        lines.append("    cli()")
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return file_path
        
    def generatePlainCallers(self, file_path: str):
        """Generate plain Python functions with type checking and callback execution"""
        commands = self.generateCmdContexts()
        builder = H2CClickBuilder(config=self.config)
        
        lines = []
        lines.append("#!/usr/bin/env python3")
        lines.append('"""Generated plain caller functions from help text"""')
        lines.append("")
        
        # Analyze what we need to generate
        needs_utils = False
        cli_wrappers_needed = {}  # cli_path -> (is_query, post_callback_func)
        callback_funcs = set()
        post_funcs = set()
        
        for cmd in commands:
            callback = builder._resolve_callback(cmd.name)
            if callback:
                if callback.cli_path_target and not callback.callback_func:
                    # Need CLI wrapper function
                    cli_wrappers_needed[callback.cli_path_target] = (
                        callback.is_query, 
                        callback.post_callback_handling
                    )
                    needs_utils = True
                elif callback.callback_func:
                    # Need to embed callback function
                    callback_funcs.add(callback.callback_func)
                
                if callback.post_callback_handling:
                    post_funcs.add(callback.post_callback_handling)
        
        # Import utils if needed
        if needs_utils:
            lines.append("from help_to_click.utils.generated import invoke_cli")
            lines.append("")
        
        # Generate CLI wrapper functions for each unique cli_path_target
        for cli_path, (is_query, post_func) in cli_wrappers_needed.items():
            safe_name = cli_path.replace('-', '_').replace('.', '_').replace('/', '_')
            wrapper_name = f"_cli_wrapper_{safe_name}"
            
            lines.append(f"def {wrapper_name}(command_name, kwargs):")
            lines.append(f'    """Generated CLI wrapper for {cli_path}"""')
            lines.append(f"    result = invoke_cli('{cli_path}', command_name, kwargs, detached={not is_query})")
            
            if post_func:
                post_func_name = post_func.__name__
                lines.append("    if result is not None:")
                lines.append(f"        {post_func_name}(result)")
            
            lines.append("    return result")
            lines.append("")
        
        # Embed callback function source code
        for func in callback_funcs:
            try:
                source = inspect.getsource(func)
                lines.append(source)
                lines.append("")
            except Exception:
                pass
        
        # Embed post callback function source code
        for func in post_funcs:
            try:
                source = inspect.getsource(func)
                lines.append(source)
                lines.append("")
            except Exception:
                pass
        
        # Generate function for each command
        for cmd in commands:
            callback = builder._resolve_callback(cmd.name)
            
            # Function signature - required params first, then optional
            required_params = []
            optional_params = []
            
            for opt_name, opt in cmd.options.items():
                type_hint = self._get_python_type(opt.typeOfVar)
                if opt.isRequired:
                    required_params.append(f"{opt_name}: {type_hint}")
                else:
                    default_val = self._get_default_value(opt)
                    optional_params.append(f"{opt_name}: {type_hint} = {default_val}")
            
            # Arguments are always required
            for arg in (cmd.args or []):
                required_params.append(f"{arg}: str")
            
            # Combine: required first, then optional
            params = required_params + optional_params
            
            func_name = cmd.name.replace('-', '_')
            lines.append(f"def {func_name}({', '.join(params)}):")
            lines.append('    """')
            lines.append(f'    Command: {cmd.name}')
            if cmd.options:
                lines.append('    ')
                lines.append('    Options:')
                for opt_name, opt in cmd.options.items():
                    desc = opt.description or "No description"
                    lines.append(f'        {opt_name}: {desc}')
            lines.append('    """')
            
            # Type validation
            for opt_name, opt in cmd.options.items():
                if opt.typeOfVar == 'int':
                    lines.append(f"    if not isinstance({opt_name}, int):")
                    lines.append(f"        raise TypeError(f'{opt_name} must be int, got {{type({opt_name}).__name__}}')")
                elif opt.typeOfVar == 'float':
                    lines.append(f"    if not isinstance({opt_name}, (int, float)):")
                    lines.append(f"        raise TypeError(f'{opt_name} must be float, got {{type({opt_name}).__name__}}')")
                elif opt.typeOfVar == 'bool':
                    lines.append(f"    if not isinstance({opt_name}, bool):")
                    lines.append(f"        raise TypeError(f'{opt_name} must be bool, got {{type({opt_name}).__name__}}')")
                elif opt.typeOfVar == 'path':
                    lines.append(f"    if not isinstance({opt_name}, str):")
                    lines.append(f"        raise TypeError(f'{opt_name} must be str (path), got {{type({opt_name}).__name__}}')")
                elif opt.typeOfVar == 'tuple':
                    lines.append(f"    if not isinstance({opt_name}, (tuple, list)):")
                    lines.append(f"        raise TypeError(f'{opt_name} must be tuple or list, got {{type({opt_name}).__name__}}')")
            
            # Required field validation
            for opt_name, opt in cmd.options.items():
                if opt.isRequired:
                    if opt.typeOfVar == 'string':
                        lines.append(f"    if not {opt_name}:")
                        lines.append(f"        raise ValueError(f'{opt_name} is required')")
            
            # Build kwargs dict
            lines.append("    ")
            lines.append("    kwargs = {")
            all_params = list(cmd.options.keys()) + (cmd.args or [])
            for param in all_params:
                lines.append(f"        '{param}': {param},")
            lines.append("    }")
            lines.append("    ")
            
            # Execute callback based on configuration
            if callback and callback.callback_func:
                # Use custom callback function
                func_name = callback.callback_func.__name__
                lines.append(f"    result = {func_name}(kwargs)")
                
                # Apply post-callback handling if present
                if callback.post_callback_handling:
                    post_func_name = callback.post_callback_handling.__name__
                    lines.append(f"    {post_func_name}(result)")
                    lines.append("    return result")
                else:
                    lines.append("    return result")
                    
            elif callback and callback.cli_path_target:
                # Use generated CLI wrapper function
                cli_path = callback.cli_path_target
                safe_name = cli_path.replace('-', '_').replace('.', '_').replace('/', '_')
                wrapper_name = f"_cli_wrapper_{safe_name}"
                lines.append(f"    return {wrapper_name}('{cmd.name}', kwargs)")
                
            else:
                # Default behavior - just return kwargs
                lines.append("    return kwargs")
            
            lines.append("")
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return file_path
    
    def _get_python_type(self, type_of_var: str) -> str:
        """Map H2COption type to Python type hint"""
        type_map = {
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'string': 'str',
            'path': 'str',
            'tuple': 'tuple'
        }
        return type_map.get(type_of_var, 'str')
    
    def _get_default_value(self, opt: H2COption) -> str:
        """Get default value for option"""
        if opt.default is not None:
            if opt.typeOfVar == 'string' or opt.typeOfVar == 'path':
                return f"'{opt.default}'"
            elif opt.typeOfVar == 'bool':
                return str(opt.default).lower()
            else:
                return str(opt.default)
        
        # Type-based defaults
        if opt.isFlag:
            return 'False'
        elif opt.typeOfVar == 'int':
            return '0'
        elif opt.typeOfVar == 'float':
            return '0.0'
        elif opt.typeOfVar == 'bool':
            return 'False'
        elif opt.typeOfVar == 'tuple':
            return '()'
        else:
            return 'None'

    @classmethod
    def fromProcess(cls, command: str, callback: Callback = None, config: H2CConfig = None) -> 'HelpToClick':
        """
        Create HelpToClick instance by running a command to get its help text
        
        Args:
            command: Command to run to get help text (e.g., "mycli --help")
            callback: Callback to use as default_callback (optional)
            config: Base H2CConfig to use (optional, creates default if None)
            
        Returns:
            HelpToClick instance configured with the specified callback
        """
        from help_to_click.utils import get_help_text_from_process, create_config_with_callback
        
        # Get help text
        help_text = get_help_text_from_process(command)
        
        # Create config with callback
        final_config = create_config_with_callback(callback, config)
        
        return cls(
            rawHelpStr=help_text,
            cleanUpHelpers=[],  # Let the subclass handle cleanup
            cmdSplitter=H2CCmdSplitter(config=final_config),
            cmdParser=H2CParser(config=final_config),
            config=final_config
        )