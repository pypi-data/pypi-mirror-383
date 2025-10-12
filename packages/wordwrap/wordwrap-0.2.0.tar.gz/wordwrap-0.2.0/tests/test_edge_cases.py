import pytest
from src.wordwrap import WordWrap


def generate_long_text(word, lines):
    return (word + ' ') * lines


def test_wrap_text_many_lines():
    # 1200 lines, each word fits in column width
    text = generate_long_text('word', 1200)
    width = 4
    result = WordWrap.wrap_text(text, width)
    assert result.is_success()
    output_lines = result.value.split('\n')
    assert len(output_lines) == 1200
    for line in output_lines:
        assert line == 'word '


def test_wrap_text_long_paragraph():
    # 1500 words, column width 10, should split into 1500 lines
    text = generate_long_text('palabra', 1500)
    width = 10
    result = WordWrap.wrap_text(text, width)
    assert result.is_success()
    output_lines = result.value.split('\n')
    assert len(output_lines) == 1500
    for line in output_lines:
        assert line == 'palabra '


def test_wrap_text_large_block():
    # 2000 words, column width 20, should split into 2000 lines
    text = generate_long_text('testword', 2000)
    width = 20
    result = WordWrap.wrap_text(text, width)
    assert result.is_success()
    output_lines = result.value.split('\n')
    assert len(output_lines) == 1000
    for line in output_lines:
        assert line == 'testword testword '
