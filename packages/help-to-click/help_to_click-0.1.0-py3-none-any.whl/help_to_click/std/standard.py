"""Standard HelpToClick implementation"""
from dataclasses import dataclass
from collections.abc import Callable

from help_to_click.core import HelpToClick
from help_to_click.core.helper import H2CCmdSplitter
from help_to_click.core.config import H2CConfig, Callback
from help_to_click.std.parser import StandardH2CParser


@dataclass(init=False)
class StandardHelpToClick(HelpToClick):
    """Standard implementation with default cleanup and parser"""
    
    def __init__(
        self, 
        rawHelpStr: str, 
        cleanUpHelpers: list[Callable[[str], str]] = None,
        config: H2CConfig = None
    ):
        """
        Create StandardHelpToClick instance
        
        Args:
            rawHelpStr: Raw help text from CLI tool
            cleanUpHelpers: Optional custom cleanup functions. If None, uses defaults.
            config: Optional H2CConfig for controlling behavior. If None, uses defaults.
        """
        if cleanUpHelpers is None:
            cleanUpHelpers = [
                self._extract_commands_section,
                self._remove_usage_lines,
            ]
        
        if config is None:
            config = H2CConfig()
        
        super().__init__(
            rawHelpStr=rawHelpStr,
            cleanUpHelpers=cleanUpHelpers,
            cmdSplitter=H2CCmdSplitter(config=config),
            cmdParser=StandardH2CParser(config=config),
            config=config
        )
    
    @staticmethod
    def _extract_commands_section(text: str) -> str:
        """Extract just the commands section from help text"""
        markers = ['Commands:', 'Commands :', 'COMMANDS:', 'Available commands:']
        
        for marker in markers:
            if marker in text:
                idx = text.find(marker)
                start = idx + len(marker)
                return text[start:].strip()
        
        return text.strip()
    
    @staticmethod
    def _remove_usage_lines(text: str) -> str:
        """Remove usage/example lines"""
        lines = text.splitlines()
        filtered_lines = []
        
        skip_keywords = ['usage:', 'example:', '<command>', 'dnconsole']
        
        for line in lines:
            lower = line.lower().strip()
            if any(keyword in lower for keyword in skip_keywords):
                continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @classmethod
    def fromProcess(cls, command: str, callback: Callback = None, config: H2CConfig = None) -> 'StandardHelpToClick':
        """
        Create StandardHelpToClick instance by running a command to get its help text
        
        Args:
            command: Command to run to get help text (e.g., "mycli --help")
            callback: Callback to use as default_callback (optional)
            config: Base H2CConfig to use (optional, creates default if None)
            
        Returns:
            StandardHelpToClick instance configured with the specified callback
        """
        from help_to_click.utils import get_help_text_from_process, create_config_with_callback
        
        # Get help text
        help_text = get_help_text_from_process(command)
        
        # Create config with callback
        final_config = create_config_with_callback(callback, config)
        
        return cls(
            rawHelpStr=help_text,
            config=final_config
        )
