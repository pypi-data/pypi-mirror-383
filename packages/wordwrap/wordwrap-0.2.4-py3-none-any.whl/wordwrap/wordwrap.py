from dataclasses import dataclass

BREAK_LINE = "\n"

def recurse_iter(func):
    """
    Decorador trampolín para funciones recursivas que devuelven lambdas.
    Permite simular tail call optimization (TCO) en Python, evitando desbordamiento de pila
    en recursiones profundas. Ejecuta la función recursiva y, mientras el resultado sea
    una función (callable), la sigue ejecutando hasta obtener el valor final.

    Ejemplo:
        def f(n):
            if n == 0:
                return 0
            return lambda: f(n-1)
        assert recurse_iter(f)(10000) == 0
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        while callable(result):
            result = result()
        return result
    return wrapper

def get_last_separator_index_within_width(text: str, line_width: int) -> int:
    """
    Returns the index after the last space within the given line width, or 0 if no space is found.
    """
    separators = (" ",)
    find_in_text = text[:line_width]
    sep_index = 0
    for separator in separators: # No son equivalentes
        sep_index = max(sep_index, find_in_text.rfind(separator) + 1)
        
    return sep_index

def adjust_line_width_to_avoid_separate_spaces(text: str, line_width: int) -> int:
    """
    Adjusts the line width to avoid splitting spaces at the end of the line.
    """
    while line_width < len(text) and text[line_width] in (" ", "\n"):
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
    def recursive_call_split_text_into_lines(text, max_line_width):
        #Uso de trampolin con acumulador, tomado como no local
        return lambda: split_text_into_lines(text, max_line_width, new_acc)
    
    if acc is None:
        acc = []
        
    if len(text) <= max_line_width:
        return acc + [text]
    
    adjusted_line_width = adjust_line_width_to_avoid_separate_spaces(text, max_line_width)

    position_break_line = text[:adjusted_line_width].rfind(BREAK_LINE)
    if position_break_line != -1:
        new_acc = acc + [text[:position_break_line]] 

        return recursive_call_split_text_into_lines(text[position_break_line + 1:], # Al poner + 1 eliminamos el "\n" que se añadirá en el join
                                                    max_line_width)
    
    
    split_position = get_last_separator_index_within_width(text, adjusted_line_width) or max_line_width

    new_acc = acc + [text[:split_position]]
    return recursive_call_split_text_into_lines(text[split_position:], 
                                         max_line_width)


def wrap(text: str, column_width: int) -> str:
    """
    Wraps the text into lines of length column_width and joins them with newlines.
    """
    validate_wrap_input(text, column_width)

    lines: list[str] = recurse_iter(split_text_into_lines)(text, column_width)
    if lines[-1] == "":
        lines.pop()
    return BREAK_LINE.join(lines)



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
    