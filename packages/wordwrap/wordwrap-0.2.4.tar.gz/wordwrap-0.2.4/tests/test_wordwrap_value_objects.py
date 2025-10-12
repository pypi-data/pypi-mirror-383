
import pytest
from wordwrap.wordwrap import WordWrap, Result

def test_wrap_simple_result():
	result = WordWrap.wrap_text("hello world", 5)
	assert isinstance(result, Result)
	assert result.is_success()
	assert result.value == "hello \nworld"

def test_wrap_with_long_word_result():
	result = WordWrap.wrap_text("helloworld", 5)
	assert result.is_success()
	assert result.value == "hello\nworld"

def test_wrap_multiple_spaces_result():
	result = WordWrap.wrap_text("hello   world", 5)
	assert result.is_success()
	assert result.value == "hello   \nworld"

def test_wrap_empty_string_result():
	result = WordWrap.wrap_text("", 5)
	assert result.is_success()
	assert result.value == ""

def test_wrap_exact_length_result():
	result = WordWrap.wrap_text("abcde", 5)
	assert result.is_success()
	assert result.value == "abcde"


def test_wrap_error_none_text():
	result = WordWrap.wrap_text(None, 5)
	assert not result.is_success()
	assert result.error == "Input text must be a string"
	assert result.value is None

def test_wrap_error_invalid_length():
	result = WordWrap.wrap_text("hello world", 0)
	assert not result.is_success()
	assert result.error == "Width must be a positive integer"
	assert result.value is None

# Ejemplo de API explícita de gestión de errores
def test_result_api_error_handling():
	result = WordWrap.wrap_text(None, 5)
	if result.is_error():
		assert result.error == "Input text must be a string"
		assert result.value is None
	else:
		pytest.fail("Se esperaba un error pero el resultado fue exitoso")
