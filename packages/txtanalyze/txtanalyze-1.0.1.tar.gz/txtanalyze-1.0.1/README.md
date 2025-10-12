# txtanalyze

`txtanalyze` is a modular Python package for analyzing text paragraphs.  
It provides a clean and simple API for word counts, sentence counts, unique words, average word length, and counting specific words.  
Designed for developers, writers, and data enthusiasts who need quick insights into text.

---

## Features

- Extract words from text (punctuation removed, lowercase)
- Count total and unique words
- Count sentences
- Calculate average word length
- Count specific words (case-insensitive)

---

## Installation

```bash
pip install txtanalyze
```

---

## Usage Examples

### Example 1 — Basic Text Analysis

```python
from txtanalyze import get_words, get_word_count, get_unique_words

text = "Hello world! Hello Python. Python is fun."

print(get_words(text))
print(get_word_count(text))
print(get_unique_words(text))
```

Output

```
['hello', 'world', 'hello', 'python', 'python', 'is', 'fun']
7
{'hello', 'world', 'python', 'is', 'fun'}
```

---

### Example 2 — Sentence and Word Metrics

```python
from txtanalyze import get_sentence_count, get_average_word_length, count_word

text = "Hello world! Hello Python. Python is fun."

print(get_sentence_count(text))
print(round(get_average_word_length(text), 2))
print(count_word(text, "Python"))
```

Output

```
3
4.57
2
```

---

## Testing

Run all tests with

```bash
pytest tests
```

---

## License

MIT License © 2025 Dimuth Sakya
