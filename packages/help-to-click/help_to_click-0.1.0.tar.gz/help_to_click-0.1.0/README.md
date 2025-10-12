# help_to_click

> Parse CLI help text → Generate Click commands

## What it does

```python
from help_to_click.std.standard import StandardHelpToClick

help_text = """
Commands:
greet --name <person>
  Say hello
"""

h2c = StandardHelpToClick(help_text)
cli = h2c.generateClickGroup("myapp")

if __name__ == '__main__':
    cli()
```

That's it. Your help text is now a working Click CLI.

## Install

```bash
pip install help-to-click
```

## Basic Usage

```python
# 1. Parse help text
h2c = StandardHelpToClick(help_text)

# 2. Get structured commands
commands = h2c.generateCmdContexts()

# 3. Generate Click CLI
cli = h2c.generateClickGroup("myapp")

# 4. Generate standalone files
h2c.generateClickFile("cli.py")      # Click CLI with decorators
h2c.generatePlainCallers("funcs.py")  # Plain functions with type checking
```

## Type Inference

The parser automatically detects types from descriptions:

```
--id <item_id>    → int    (has "id")
--file <path>     → path   (has "path")
--count <num>     → int    (has "num")
--rate <percent>  → float  (has "percent")
```

## Custom Behavior

```python
from help_to_click.core.config import H2CConfig, Callback

def my_handler(kwargs):
    print(f"Hello {kwargs['name']}!")

config = H2CConfig(
    override_callbacks={
        'greet': Callback(callback_func=my_handler)
    }
)

h2c = StandardHelpToClick(help_text, config=config)
```

## Config Presets

```python
# No type inference
config = H2CConfig.minimal()

# Maximum inference
config = H2CConfig.aggressive()

# Custom
config = H2CConfig(
    type_inference=TypeInferenceConfig(
        infer_int_from_keywords=True,
        infer_path_from_keywords=False
    )
)
```

## Examples

See `examples/` folder (15 examples):
- `01_basic.py` - Simplest example
- `05_callback.py` - Custom behavior
- `11_generate_file.py` - Generate Click CLI
- `12_plain_callers.py` - Generate plain functions
- `13_from_process.py` - New fromProcess API
- See `examples/README.md` for full list

## Documentation

See `docs/` folder for detailed guides.

## Tests

```bash
pytest tests/ -v
```

34 tests, all passing.

## License

MIT
