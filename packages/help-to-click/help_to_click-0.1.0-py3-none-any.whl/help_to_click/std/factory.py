"""Factory functions for creating standard HelpToClick instances"""
from help_to_click.core import HelpToClick
from help_to_click.core.helper import H2CCmdSplitter
from help_to_click.std.parser import StandardH2CParser


def create_standard_help_to_click(
    raw_help_str: str,
    cleanup_helpers: list = None
) -> HelpToClick:
    """
    Create a HelpToClick instance with standard parser and splitter
    
    Args:
        raw_help_str: Raw help text from CLI tool
        cleanup_helpers: Optional list of cleanup functions to apply
        
    Returns:
        Configured HelpToClick instance
    """
    if cleanup_helpers is None:
        cleanup_helpers = [
            remove_header_lines,
            remove_usage_lines,
        ]
    
    return HelpToClick(
        rawHelpStr=raw_help_str,
        cleanUpHelpers=cleanup_helpers,
        cmdSplitter=H2CCmdSplitter(),
        cmdParser=StandardH2CParser()
    )


def remove_header_lines(text: str) -> str:
    """Remove header lines (lines before 'Commands:')"""
    if 'Commands' in text:
        # Find the Commands section
        commands_idx = text.find('Commands')
        # Find the next line after Commands:
        newline_idx = text.find('\n', commands_idx)
        if newline_idx != -1:
            return text[newline_idx + 1:]
    return text


def remove_usage_lines(text: str) -> str:
    """Remove usage/example lines"""
    lines = text.splitlines()
    filtered_lines = []
    
    skip_keywords = ['usage:', 'example:', 'usage', '<command>', 'dnconsole']
    
    for line in lines:
        lower = line.lower().strip()
        # Skip lines that look like usage examples
        if any(keyword in lower for keyword in skip_keywords):
            continue
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def extract_commands_section(text: str) -> str:
    """
    Extract just the commands section from help text
    
    Looks for 'Commands:' or 'Commands :' and returns everything after
    """
    # Try different variations
    markers = ['Commands:', 'Commands :', 'COMMANDS:', 'Available commands:']
    
    for marker in markers:
        if marker in text:
            idx = text.find(marker)
            # Skip past the marker and any following whitespace/newlines
            start = idx + len(marker)
            return text[start:].strip()
    
    # If no marker found, return the whole text
    return text.strip()
