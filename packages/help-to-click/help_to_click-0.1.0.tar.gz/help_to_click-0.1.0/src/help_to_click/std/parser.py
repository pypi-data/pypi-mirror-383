"""Standard parser for common CLI help text formats"""
import re
from help_to_click.core.helper import H2CParser
from help_to_click.core.spec import H2CCommand, H2COption


class StandardH2CParser(H2CParser):
    """
    Parser for standard CLI help format like:
    
    command <--name value | --id value>
            [--option <value>]
            [--flag]
    """
    
    # Pattern to match options: --option or --option <value> (allowing nested angle brackets)
    OPTION_PATTERN = re.compile(r'--(\w+)(?:\s+(<[^>]+(?:\|[^>]+)?>|<[^>]+>|\w+))?')
    
    # Pattern to match choices: <val1 | val2 | val3>
    CHOICE_PATTERN = re.compile(r'<([^>]+\s*\|\s*[^>]+)>')
    
    # Pattern to detect numeric types
    NUMERIC_PATTERN = re.compile(r'^\d+$')
    
    def parse(self, command_string: str) -> H2CCommand:
        """
        Parse a single command string into H2CCommand
        
        Args:
            command_string: Full command text, potentially multi-line
            
        Returns:
            H2CCommand object with parsed options
        """
        lines = command_string.strip().splitlines()
        if not lines:
            raise ValueError("Empty command string")
        
        # First line contains command name
        first_line = lines[0]
        command_name = self._extract_command_name(first_line)
        
        # Parse all lines for options and arguments
        full_text = command_string
        args = self._extract_args(full_text)
        options = self._extract_options(full_text)
        
        return H2CCommand(
            name=command_name,
            args=args,
            options=options
        )
    
    def _extract_command_name(self, first_line: str) -> str:
        """Extract command name (first word) from first line"""
        parts = first_line.strip().split()
        if not parts:
            raise ValueError("Cannot extract command name from empty line")
        return parts[0]
    
    def _extract_args(self, text: str) -> list[str]:
        """
        Extract positional arguments (required parameters not starting with --)
        
        For now, we treat mutually exclusive required options as special
        and don't put them in args. Args would be for positional parameters.
        """
        args = []
        
        # Look for required parameters in <> that don't start with --
        # Example: <filename> or <command>
        required_pattern = re.compile(r'<(?!--)([\w_]+)>')
        
        for match in required_pattern.finditer(text):
            arg_name = match.group(1)
            # Skip if it looks like a value description for an option
            if not self._is_value_description(arg_name):
                args.append(arg_name)
        
        return args
    
    def _is_value_description(self, name: str) -> bool:
        """Check if this looks like a value description rather than an argument"""
        # Common value placeholders
        value_indicators = [
            'value', 'val', 'name', 'id', 'file', 'path', 'str', 
            'string', 'number', 'num', 'command', 'cmd'
        ]
        return any(indicator in name.lower() for indicator in value_indicators)
    
    def _extract_options(self, text: str) -> dict[str, H2COption]:
        """
        Extract all options from the command text
        
        Handles:
        - Required options: <--option value>
        - Optional options: [--option value] or [--option <value>]
        - Bare options: --option <value> (outside brackets)
        - Flags: [--flag] (no value)
        - Choices: [--option <val1 | val2>]
        """
        options = {}
        
        # Find all option patterns - look for --option followed by optional value
        # We'll scan the entire text for all --option patterns
        
        # Pattern for optional sections: [...--option...]
        # Use a more careful approach: find [] blocks and parse each
        optional_blocks = []
        i = 0
        while i < len(text):
            if text[i] == '[':
                # Find matching ]
                depth = 1
                start = i + 1
                i += 1
                while i < len(text) and depth > 0:
                    if text[i] == '[':
                        depth += 1
                    elif text[i] == ']':
                        depth -= 1
                    i += 1
                if depth == 0:
                    optional_blocks.append(text[start:i-1])
            else:
                i += 1
        
        # Pattern for required sections: <...--option...>
        required_blocks = []
        i = 0
        while i < len(text):
            if text[i] == '<':
                # Find matching >
                depth = 1
                start = i + 1
                i += 1
                while i < len(text) and depth > 0:
                    if text[i] == '<':
                        depth += 1
                    elif text[i] == '>':
                        depth -= 1
                    i += 1
                if depth == 0 and '--' in text[start:i-1]:
                    required_blocks.append(text[start:i-1])
            else:
                i += 1
        
        # Parse optional options
        for block in optional_blocks:
            self._parse_option_section(block, options, is_required=False)
        
        # Parse required options
        for block in required_blocks:
            self._parse_option_section(block, options, is_required=True)
        
        # Also find "bare" options that are outside of brackets/angles
        # These appear after the command name and bracket groups
        # Look for --option patterns in the remaining text
        # Create a version of text with brackets/angles removed to find bare options
        text_without_blocks = text
        for block in optional_blocks + required_blocks:
            text_without_blocks = text_without_blocks.replace(f'[{block}]', '')
            text_without_blocks = text_without_blocks.replace(f'<{block}>', '')
        
        # Now find any remaining --option patterns
        for match in self.OPTION_PATTERN.finditer(text_without_blocks):
            full_match = match.group(0)
            if full_match and '--' in full_match:
                # This is a bare option - treat as required (not in optional brackets)
                option = self._parse_single_option(full_match, is_required=True)
                if option and option.name not in options:
                    options[option.name] = option
        
        return options
    
    def _parse_option_section(self, section: str, options: dict, is_required: bool):
        """Parse a section of text for options"""
        
        # Check if this section contains mutually exclusive options at the top level
        # (not within angle brackets)
        # We need to distinguish between:
        #   --name value | --id value  (mutually exclusive options)
        #   --cores <1 | 2 | 4>        (single option with choices)
        
        # Quick check: if there are multiple -- at the same depth, it's mutually exclusive
        option_count = section.count('--')
        has_pipe_outside_angles = False
        
        # Check if | exists outside of < >
        depth = 0
        for i, char in enumerate(section):
            if char == '<':
                depth += 1
            elif char == '>':
                depth -= 1
            elif char == '|' and depth == 0:
                has_pipe_outside_angles = True
                break
        
        if option_count > 1 and has_pipe_outside_angles:
            # Handle mutually exclusive options: --name value | --id value
            alternatives = [alt.strip() for alt in section.split('|')]
            
            for alt in alternatives:
                if not alt.startswith('--'):
                    continue
                    
                option = self._parse_single_option(alt, is_required)
                if option:
                    options[option.name] = option
        else:
            # Single option (possibly with choices)
            if '--' in section:
                option = self._parse_single_option(section, is_required)
                if option:
                    options[option.name] = option
    
    def _parse_single_option(self, text: str, is_required: bool) -> H2COption:
        """Parse a single option like '--name <value>' or '--flag'"""
        
        match = self.OPTION_PATTERN.search(text)
        if not match:
            return None
        
        option_name = match.group(1)
        value_desc = match.group(2) if len(match.groups()) >= 2 else None
        
        # Clean up value_desc - remove angle brackets if present
        if value_desc and value_desc.startswith('<') and value_desc.endswith('>'):
            value_desc = value_desc[1:-1]
        
        # Determine if it's a flag (no value)
        is_flag = value_desc is None
        
        # Check for choices
        type_of_var = "string"  # default
        default = None
        description = None
        
        if value_desc:
            is_flag = False  # Has a value, so not a flag
            
            # Check if value contains choices
            if '|' in value_desc:
                choices = [c.strip() for c in value_desc.split('|')]
                description = f"Choices: {', '.join(choices)}"
                
                # Try to detect type from choices
                if all(self.NUMERIC_PATTERN.match(c) for c in choices):
                    type_of_var = "int"
                else:
                    type_of_var = "choice"
            else:
                # Try to infer type from value description
                type_of_var = self._infer_type(value_desc)
                description = value_desc
            
            # Check for default value (auto keyword)
            if 'auto' in value_desc.lower():
                default = "auto"
        
        return H2COption(
            name=option_name,
            description=description,
            default=default,
            typeOfVar=type_of_var,
            isFlag=is_flag,
            isRequired=is_required
        )
    
    def _infer_type(self, value_desc: str) -> str:
        """
        Infer the type from value description using config settings
        
        Args:
            value_desc: The value description string (e.g., "item_id", "file_path")
            
        Returns:
            Inferred type string: "int", "bool", "float", "path", "tuple", or "string"
        """
        if not value_desc:
            return self.config.type_inference.default_string_type
        
        lower = value_desc.lower()
        
        # Check for numeric indicators (if enabled)
        if self.config.type_inference.infer_int_from_keywords:
            if any(word in lower for word in self.config.type_inference.int_keywords):
                return "int"
        
        # Check for boolean indicators (if enabled)
        if self.config.type_inference.infer_bool_from_keywords:
            if any(word in lower for word in self.config.type_inference.bool_keywords):
                return "bool"
        
        # Check for range indicators (if enabled)
        if self.config.type_inference.infer_int_from_range:
            if '~' in lower or '-' in lower:
                return "int"
        
        # Check for float indicators (if enabled)
        if self.config.type_inference.infer_float_from_keywords:
            if any(word in lower for word in self.config.type_inference.float_keywords):
                return "float"
        
        # Check for path indicators (if enabled)
        if self.config.type_inference.infer_path_from_keywords:
            if any(word in lower for word in self.config.type_inference.path_keywords):
                return "path"
        
        # Check for coordinate patterns (if enabled)
        if self.config.type_inference.infer_tuple_from_comma:
            if ',' in lower:
                return "tuple"
        
        # Default to configured string type
        return self.config.type_inference.default_string_type
