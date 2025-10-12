import re

def get_words(paragraph: str) -> list:
    """Return a list of words (lowercased, punctuation removed)."""
    return re.findall(r'\b\w+\b', paragraph.lower())

def get_word_count(paragraph: str) -> int:
    """Return total number of words in paragraph."""
    return len(get_words(paragraph))

def get_unique_words(paragraph: str) -> set:
    """Return a set of unique words."""
    return set(get_words(paragraph))

def get_sentence_count(paragraph: str) -> int:
    """Return number of sentences (split by ., !, ?)."""
    sentences = re.split(r'[.!?]+', paragraph)
    return len([s for s in sentences if s.strip()])

def get_average_word_length(paragraph: str) -> float:
    """Return average word length."""
    words = get_words(paragraph)
    return sum(len(w) for w in words) / len(words) if words else 0

def count_word(paragraph: str, target_word: str) -> int:
    """Return the count of a specific word (case-insensitive)."""
    return get_words(paragraph).count(target_word.lower())