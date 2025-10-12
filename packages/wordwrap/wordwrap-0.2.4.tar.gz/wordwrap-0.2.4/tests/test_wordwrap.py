import pytest
from wordwrap.wordwrap import wrap


def test_empty_string():
    """Test case 1: Empty string should return empty string"""
    result = wrap("", 10)
    assert result == ""

def test_single_word_shorter_than_column_width():
    """Test case 2: Single word shorter than column width"""
    result = wrap("palabra", 10)
    assert result == "palabra"

def test_single_word_exactly_column_width():
    """Test case 3: Single word exactly the column width"""
    result = wrap("palabra123", 10)
    assert result == "palabra123"

def test_single_word_longer_than_column_width():
    """Test case 4: Single word longer than column width should break"""
    result = wrap("palabralarga", 5)
    assert result == "palab\nralar\nga"

def test_two_words_that_fit_in_one_line():
    """Test case 5: Two words that fit in one line"""
    result = wrap("hola mundo", 15)
    assert result == "hola mundo"

def test_two_words_requiring_line_break():
    """Test case 6: Two words requiring line break"""
    result = wrap("hola mundo", 8)
    assert result == "hola \nmundo"

def test_multiple_words_complex_wrapping():
    """Test case 7: Multiple words with complex wrapping"""
    result = wrap("una linea larga de texto", 10)
    assert result == "una linea \nlarga de \ntexto"
def test_wrap_width_one():
    """Test: wrap with width 1 should not enter infinite loop"""
    text = "abcde"
    result = wrap(text, 1)
    # Esperado: cada letra en una línea
    assert result == "a\nb\nc\nd\ne"

def test_long_word_breaks_correctly():
    """Test case 8: Long word breaks at exact column width"""
    result = wrap("palabra superlarga texto", 9)
    assert result == "palabra \nsuperlarg\na texto"

def test_multiple_spaces_preserved():
    """Test case 9: Multiple spaces should be preserved"""
    result = wrap("palabra    con       espacios", 10)
    assert result == "palabra    \ncon       \nespacios"

def test_spaces_at_end_of_line_preserved():
    """Test case 10: Spaces at end of line should be preserved"""
    result = wrap("word   more", 7)
    assert result == "word   \nmore"

def test_multiple_consecutive_spaces():
    """Test case 11: Multiple consecutive spaces in middle"""
    result = wrap("a     b", 5)
    assert result == "a     \nb"

def test_text_with_trailing_spaces():
    """Test case 12: Text with trailing spaces"""
    result = wrap("hello   ", 10)
    assert result == "hello   "

def test_text_with_leading_spaces():
    """Test case 13: Text with leading spaces"""
    result = wrap("   hello", 10)
    assert result == "   hello"

def test_very_long_word_multiple_breaks():
    """Test case 14: Very long word requiring multiple breaks"""
    result = wrap("supercalifragilisticoexpialidoso", 10)
    assert result == "supercalif\nragilistic\noexpialido\nso"

def test_mix_normal_and_long_words():
    """Test case 15: Mix of normal and long words"""
    result = wrap("normal supercalifragilistico word", 10)
    assert result == "normal \nsupercalif\nragilistic\no word"

def test_single_character_column_width():
    """Test case 16: Column width of 1"""
    result = wrap("abc", 1)
    assert result == "a\nb\nc"

def test_only_spaces():
    """Test case 17: String with only spaces"""
    result = wrap("     ", 3)
    assert result == "     "

def test_words_separated_by_single_space():
    """Test case 18: Normal case with single spaces"""
    result = wrap("the quick brown fox", 8)
    assert result == "the \nquick \nbrown \nfox"

def test_edge_case_word_exactly_fills_line_with_space():
    """Test case 19: Word + space exactly fills line"""
    result = wrap("word next", 5)
    assert result == "word \nnext"

def test_wrap_with_newlines_in_text():
    """Test: wrap debe romper por salto de línea si cae entre el último espacio y el ancho de columna"""
    text = "The Zen of Python, by Tim Peters\n\nBeautiful is better than ugly.\n"
    result = wrap(text, 12)
    # El resultado esperado debe tener saltos de línea donde corresponda
    expected = "The Zen of \nPython, by \nTim Peters\n\nBeautiful is \nbetter than \nugly.\n"
    assert result == expected

def test_zero_column_width():
    """Test case 20: Column width of 0 should raise exception"""
    with pytest.raises(ValueError):
        wrap("test", 0)

def test_negative_column_width():
    """Test case 21: Negative column width should raise exception"""
    with pytest.raises(ValueError):
        wrap("test", -1)

def test_newline_at_end():
    text = "Termina con salto\n"
    result = wrap(text, 10)
    expected = "Termina \ncon salto\n"
    assert result == expected


def test_only_spaces():
    text = "     "
    width = 2
    expected = "     "
    assert wrap(text, width) == expected

# --- TESTS ESPECIALES: manejo de saltos de línea ya presentes en el texto ---

class TestWrapWithExistingNewlines:
    """
    Tests para verificar que los saltos de línea existentes en el texto se respetan y no se insertan saltos adicionales en la misma posición.
    El salto de línea debe considerarse como corte y la línea resultante debe ser <= column_width.
    """
    def test_newline_before_limit(self):
        text = "Los\nElefantes son maravillosos"
        result = wrap(text, 13)
        expected = "Los\nElefantes son \nmaravillosos"
        assert result == expected

    def test_newline_before_limit_with_last_long_word(self):
        text = "Los\nElefantes son maravillosisimos"
        result = wrap(text, 13)
        expected = "Los\nElefantes son \nmaravillosisi\nmos"
        assert result == expected

    def test_newline_after_limit(self):
        text = "Los Elefantes\nson maravillosos"
        result = wrap(text, 12)
        expected = "Los \nElefantes\nson \nmaravillosos"
        assert result == expected

    def test_newline_in_limit(self):
        text = "Los Elefantes\nson maravillosos"
        result = wrap(text, 13)
        expected = "Los Elefantes\nson \nmaravillosos"
        assert result == expected

    def test_multiple_newlines(self):
        text = "Uno\nDos\nTres Cuatro Cinco"
        result = wrap(text, 10)
        expected = "Uno\nDos\nTres \nCuatro \nCinco"
        assert result == expected

    def test_newline_at_start(self):
        text = "\nEmpieza con salto"
        result = wrap(text, 10)
        expected = "\nEmpieza \ncon salto"
        assert result == expected

    def test_spaces_at_start_and_end(self):
        text = "   hola mundo   "
        width = 5
        expected = "\n".join([
            "   ",
            "hola ",
            "mundo   "
        ])
        assert wrap(text, width) == expected
