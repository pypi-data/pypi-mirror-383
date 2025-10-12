

# wordwrap

Wordwrap is a Python library for wrapping text to a fixed column width, designed for easy import and use in your own projects.

## Installation

Install from source (local):

```bash
pip install .
```

## Usage as a library

Import and use the main API:

```python
from wordwrap import WordWrap

result = WordWrap.wrap_text("This is a long line of text.", 10)
if result.is_success():
   print(result.value)  # Wrapped text with lines <= 10 chars
else:
   print(f"Error: {result.error}")
```

## API


# wordwrap

Wordwrap is a Python library for wrapping text to a fixed column width, designed for easy import and robust error handling.

## Installation

Install from PyPI:

```bash
pip install wordwrap
```

Or from source (local):

```bash
pip install .
```

## Usage

Import and use the main API:

```python
from wordwrap import WordWrap

result = WordWrap.wrap_text("This is a long line of text.", 10)
if result.is_success():
    print(result.value)  # Wrapped text with lines <= 10 chars
else:
    print(f"Error: {result.error}")
```

## API Reference

### WordWrap.wrap_text(text: str, column_width: int) -> Result

- Returns a `Result` object:
  - `.value`: Wrapped text (string)
  - `.error`: Error message (string)
- Input validation:
  - `text` must be a string
  - `column_width` must be a positive integer

## Features
- Wraps text to a specified column width, preserving words
- Handles long words and whitespace correctly
- Returns a Result object for error handling
- Python 3.8+

## Examples

```python
from wordwrap import WordWrap

# Example 1: Short text
result = WordWrap.wrap_text("word", 10)
print(result.value)  # "word"

# Example 2: Text exactly the column width
result = WordWrap.wrap_text("word123456", 10)
print(result.value)  # "word123456"

# Example 3: Text that requires splitting
result = WordWrap.wrap_text("a long line of text", 10)
print(result.value)  # "a long \nline of \ntext"

# Example 4: Long words
result = WordWrap.wrap_text("word superlongword text", 9)
print(result.value)  # "word \nsuperlong\nword text"

# Example 5: Multiple spaces
result = WordWrap.wrap_text("word    with   spaces", 10)
print(result.value)  # "word    \nwith   \nspaces"
```

## License
MIT

---

### Background

This library is inspired by the Word Wrap kata by Robert C. Martin (Uncle Bob).