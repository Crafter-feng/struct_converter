import pytest
from c_parser.core.value_parser import ValueParser

@pytest.fixture
def parser():
    return ValueParser()

def test_parse_char_array(parser):
    test_value = "{'H', 'e', 'l', 'l', 'o'}"
    result = parser.parse_char_array(test_value)
    assert result == ['H', 'e', 'l', 'l', 'o']

def test_parse_string_literal(parser):
    test_value = '"Hello, World!"'
    result = parser.parse_string(test_value)
    assert result == "Hello, World!"

def test_parse_hex_value(parser):
    test_value = "0xFF"
    result = parser.parse_integer(test_value)
    assert result == 255

def test_parse_array_initialization(parser):
    test_value = "{1, 2, 3, 4, 5}"
    result = parser.parse_array(test_value)
    assert result == [1, 2, 3, 4, 5]

def test_parse_complex_data(parser):
    test_value = "{{1, 2}, {3, 4}}"
    result = parser.parse_nested_array(test_value)
    assert result == [[1, 2], [3, 4]] 