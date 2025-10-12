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

def test_zero_column_width():
    """Test case 20: Column width of 0 should raise exception"""
    with pytest.raises(ValueError):
        wrap("test", 0)

def test_negative_column_width():
    """Test case 21: Negative column width should raise exception"""
    with pytest.raises(ValueError):
        wrap("test", -1)