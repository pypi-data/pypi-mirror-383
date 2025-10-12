from dataclasses import dataclass

def recurse_iter(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        while callable(result):
            result = result()
        return result
    return wrapper

def get_last_space_index_within_width(text: str, line_width: int) -> int:
    """
    Returns the index after the last space within the given line width, or 0 if no space is found.
    """
    return text[:line_width].rfind(" ") + 1

def adjust_line_width_to_avoid_separate_spaces(text: str, line_width: int) -> int:
    """
    Adjusts the line width to avoid splitting spaces at the end of the line.
    """
    while line_width < len(text) and text[line_width] == " ":
        line_width += 1
    return line_width


def validate_wrap_input(text: str, max_line_width: int) -> None:
    """
    Validates input for text wrapping. Raises ValueError if invalid.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")
    if max_line_width < 1:
        raise ValueError("Width must be a positive integer")

def split_text_into_lines(text: str, max_line_width: int, acc=None) -> list[str]:
    """
    Splits the text into lines of maximum length max_line_width, keeping words whole.
    """
    if acc is None:
        acc = []
    if len(text) <= max_line_width:
        return acc + [text]
    
    adjusted_line_width = adjust_line_width_to_avoid_separate_spaces(text, max_line_width)
    
    split_position = get_last_space_index_within_width(text, adjusted_line_width) or max_line_width
    
    return lambda: split_text_into_lines(text[split_position:], 
                                         max_line_width, 
                                         acc + [text[:split_position]])


def wrap(text: str, column_width: int) -> str:
    """
    Wraps the text into lines of length column_width and joins them with newlines.
    """
    validate_wrap_input(text, column_width)

    lines: list[str] = recurse_iter(split_text_into_lines)(text, column_width)
    if lines[-1] == "":
        lines.pop()
    return '\n'.join(lines)

@dataclass(frozen=True)
class Result:
    """
    Represents the result of an operation, with value if successful or error if failed.
    """
    value: str | None = None
    error: str | None = None

    def is_success(self):
        """
        Returns True if the result is successful (value is not None).
        """
        return self.value is not None
    
    def is_error(self):
        """
        Returns True if the result is an error (error is not None).
        """
        return self.error is not None
    

class WordWrap:
    """
    Provides the static method wrap_text to wrap text into fixed-width lines.
    """
    def __init__(self):
        """
        WordWrap cannot be instantiated directly.
        """
        raise TypeError("WordWrap is a utility class and cannot be instantiated.")

    @staticmethod
    def wrap_text(text: str, column_width: int) -> Result:
        """
        Wraps the text into lines of length column_width. Returns a Result.
        """
        try:
            return Result(value = wrap(text, column_width))
        except ValueError as e:
            return Result(error = str(e))
    