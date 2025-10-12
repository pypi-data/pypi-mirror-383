from txtanalyze.core import (
    get_words,
    get_word_count,
    get_unique_words,
    get_sentence_count,
    get_average_word_length,
    count_word
)

def test_functions():
    text = "Hello world! Hello Python. Python is fun."

    assert get_words(text) == ['hello', 'world', 'hello', 'python', 'python', 'is', 'fun']
    assert get_word_count(text) == 7
    assert get_unique_words(text) == {'hello', 'world', 'python', 'is', 'fun'}
    assert get_sentence_count(text) == 3
    assert round(get_average_word_length(text), 2) == 4.0
    assert count_word(text, "python") == 2