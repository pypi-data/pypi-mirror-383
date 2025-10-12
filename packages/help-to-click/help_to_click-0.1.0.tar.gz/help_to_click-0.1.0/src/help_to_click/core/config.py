
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class Callback:
    """Config for callbacks"""
    cli_path_target: str = None
    """Path to the CLI executable to invoke"""
    
    callback_func: Callable[[dict], Any] = None
    """Custom callback function that receives parsed kwargs and returns result"""
    
    callback_funcsrc : str = None
    """Source code of the custom callback function (for reference)"""

    is_query: bool = False
    """If True, command is read-only and doesn't modify state"""
    
    post_callback_handling: Callable[[Any], None] = None
    """Optional function to handle the callback result"""


@dataclass
class TypeInferenceConfig:
    """Type inference settings"""
    
    infer_int_from_keywords: bool = True
    """Infer int type from keywords"""
    
    infer_bool_from_keywords: bool = True
    """Infer bool type from keywords"""
    
    infer_float_from_keywords: bool = True
    """Infer float type from keywords"""
    
    infer_path_from_keywords: bool = True
    """Infer path type from keywords"""
    
    infer_tuple_from_comma: bool = True
    """Infer tuple type when value contains comma"""
    
    infer_int_from_range: bool = True
    """Infer int type from range indicators"""
    
    int_keywords: list[str] = field(default_factory=lambda: [
        'num', 'number', 'int', 'count', 'id', 'idx', 'index'
    ])
    """Keywords that indicate an integer type"""
    
    bool_keywords: list[str] = field(default_factory=lambda: [
        'bool', 'flag', 'enable', 'disable'
    ])
    """Keywords that indicate a boolean type"""
    
    float_keywords: list[str] = field(default_factory=lambda: [
        'float', 'rate', 'percent'
    ])
    """Keywords that indicate a float type"""
    
    path_keywords: list[str] = field(default_factory=lambda: [
        'path', 'file', 'dir', 'directory', 'folder'
    ])
    """Keywords that indicate a path type"""
    
    default_string_type: str = "string"
    """Default type when inference is disabled or no pattern matches"""


@dataclass
class ParserConfig:
    """Parser behavior settings"""
    
    allow_empty_commands: bool = False
    """Allow commands with no options or arguments"""
    
    skip_parse_errors: bool = True
    """Skip commands that fail to parse instead of raising exceptions"""
    
    preserve_option_case: bool = False
    """Preserve original case in option names (default: lowercase)"""
    
    verbose_warnings: bool = False
    """Print detailed warnings during parsing"""


@dataclass
class ClickConfig:
    """Click generation settings"""
    
    add_help_option: bool = True
    """Add --help option to generated commands"""
    
    use_short_options: bool = False
    """Generate short options (-n) in addition to long options (--name)"""
    
    validate_mutually_exclusive: bool = True
    """Add validation for mutually exclusive options"""


@dataclass
class H2CConfig:
    """
    Configuration for help_to_click parsing and generation behavior
    
    Controls type inference, parsing behavior, and Click generation options
    """

    # Callback Configuration
    default_callback: Callback = field(default_factory=lambda: Callback())
    """Default callback for commands without specific callback"""
    
    regex_callbacks: dict[str, Callback] = field(default_factory=dict)
    """Regex pattern -> Callback mapping for pattern-based command matching"""
    
    override_callbacks: dict[str, Callback] = field(default_factory=dict)
    """Exact command name -> Callback mapping for specific command overrides"""

    # Sub-configs
    type_inference: TypeInferenceConfig = field(default_factory=TypeInferenceConfig)
    """Type inference configuration"""
    
    parser: ParserConfig = field(default_factory=ParserConfig)
    """Parser behavior configuration"""
    
    click: ClickConfig = field(default_factory=ClickConfig)
    """Click generation configuration"""
    
    @classmethod
    def minimal(cls) -> 'H2CConfig':
        """
        Create a minimal config with most inference disabled
        Only basic parsing, no smart type detection
        """
        return cls(
            type_inference=TypeInferenceConfig(
                infer_int_from_keywords=False,
                infer_bool_from_keywords=False,
                infer_float_from_keywords=False,
                infer_path_from_keywords=False,
                infer_tuple_from_comma=False,
                infer_int_from_range=False,
            )
        )
    
    @classmethod
    def aggressive(cls) -> 'H2CConfig':
        """
        Create an aggressive config with maximum inference
        All features enabled, verbose output
        """
        return cls(
            type_inference=TypeInferenceConfig(
                infer_int_from_keywords=True,
                infer_bool_from_keywords=True,
                infer_float_from_keywords=True,
                infer_path_from_keywords=True,
                infer_tuple_from_comma=True,
                infer_int_from_range=True,
            ),
            parser=ParserConfig(
                verbose_warnings=True,
            ),
            click=ClickConfig(
                validate_mutually_exclusive=True,
            )
        )
    
    @classmethod
    def default(cls) -> 'H2CConfig':
        """Create default config (same as using the constructor with no args)"""
        return cls()