"""
Tests for the Pig Latin converter module.
"""

import pytest
from chainguard_pig_latin import to_pig_latin, word_to_pig_latin


class TestWordToPigLatin:
    """Tests for word_to_pig_latin function."""

    def test_consonant_words(self):
        """Test words starting with consonants."""
        assert word_to_pig_latin("hello") == "ellohay"
        assert word_to_pig_latin("world") == "orldway"
        assert word_to_pig_latin("python") == "ythonpay"
        assert word_to_pig_latin("string") == "ingstray"
        assert word_to_pig_latin("glove") == "oveglay"

    def test_vowel_words(self):
        """Test words starting with vowels."""
        assert word_to_pig_latin("apple") == "appleway"
        assert word_to_pig_latin("eat") == "eatway"
        assert word_to_pig_latin("igloo") == "iglooway"
        assert word_to_pig_latin("orange") == "orangeway"
        assert word_to_pig_latin("umbrella") == "umbrellaway"

    def test_capitalization_single_word(self):
        """Test that capitalization is preserved."""
        assert word_to_pig_latin("Hello") == "Ellohay"
        assert word_to_pig_latin("Apple") == "Appleway"
        assert word_to_pig_latin("HELLO") == "ELLOHAY"
        assert word_to_pig_latin("APPLE") == "APPLEWAY"

    def test_consonant_clusters(self):
        """Test words with consonant clusters."""
        assert word_to_pig_latin("three") == "eethray"
        assert word_to_pig_latin("school") == "oolschay"
        assert word_to_pig_latin("stretch") == "etchstray"
        assert word_to_pig_latin("throw") == "owthray"

    def test_qu_combination(self):
        """Test that 'qu' stays together."""
        assert word_to_pig_latin("queen") == "eenquay"
        assert word_to_pig_latin("quick") == "ickquay"
        assert word_to_pig_latin("quiet") == "ietquay"
        assert word_to_pig_latin("square") == "aresquay"

    def test_punctuation(self):
        """Test that punctuation is preserved."""
        assert word_to_pig_latin("hello!") == "ellohay!"
        assert word_to_pig_latin("world?") == "orldway?"
        assert word_to_pig_latin("(hello)") == "(ellohay)"
        assert word_to_pig_latin("'world'") == "'orldway'"
        assert word_to_pig_latin("hello...") == "ellohay..."

    def test_edge_cases(self):
        """Test edge cases."""
        assert word_to_pig_latin("") == ""
        assert word_to_pig_latin("a") == "away"
        assert word_to_pig_latin("I") == "Iway"
        assert word_to_pig_latin("b") == "bay"

    def test_single_consonant_words(self):
        """Test single consonant words."""
        assert word_to_pig_latin("by") == "ybay"
        assert word_to_pig_latin("my") == "ymay"
        assert word_to_pig_latin("to") == "otay"

    def test_all_consonants(self):
        """Test words with only consonants and y as vowel."""
        # 'xyz' has no vowel sound, but 'y' after 'x' acts as a vowel
        assert word_to_pig_latin("xyz") == "yzxay"
        # 'fly' - 'y' acts as the vowel sound
        assert word_to_pig_latin("fly") == "yflay"


class TestToPigLatin:
    """Tests for to_pig_latin function."""

    def test_simple_sentence(self):
        """Test converting simple sentences."""
        assert to_pig_latin("hello world") == "ellohay orldway"
        assert to_pig_latin("I love Python") == "Iway ovelay Ythonpay"
        assert to_pig_latin("I love Coding") == "Iway ovelay Odingcay"

    def test_sentence_with_punctuation(self):
        """Test sentences with punctuation."""
        assert to_pig_latin("Hello, world!") == "Ellohay, orldway!"
        assert to_pig_latin("What? No way!") == "Atwhay? Onay ayway!"
        assert to_pig_latin("It's a beautiful day.") == "Itway'say away eautifulbay ayday."

    def test_capitalization_in_sentence(self):
        """Test that capitalization is preserved in sentences."""
        # 'qu' moves together as a consonant cluster
        assert to_pig_latin("The Quick Brown Fox") == "Ethay Ickquay Ownbray Oxfay"
        assert to_pig_latin("HELLO WORLD") == "ELLOHAY ORLDWAY"

    def test_multiple_spaces(self):
        """Test that multiple spaces are preserved."""
        assert to_pig_latin("hello  world") == "ellohay  orldway"
        assert to_pig_latin("one   two    three") == "oneway   otway    eethray"

    def test_empty_string(self):
        """Test empty string."""
        assert to_pig_latin("") == ""

    def test_single_word(self):
        """Test single word strings."""
        assert to_pig_latin("hello") == "ellohay"
        assert to_pig_latin("apple") == "appleway"

    def test_real_sentences(self):
        """Test realistic example sentences."""
        # 'qu' moves together as a consonant cluster
        assert to_pig_latin("The quick brown fox jumps over the lazy dog") == \
            "Ethay ickquay ownbray oxfay umpsjay overway ethay azylay ogday"

        assert to_pig_latin("Python is an awesome programming language") == \
            "Ythonpay isway anway awesomeway ogrammingpray anguagelay"

    def test_mixed_content(self):
        """Test mixed content with numbers and special characters."""
        # Words are converted, but the function focuses on alphabetic characters
        assert to_pig_latin("Hello123") == "Ellohay123"

    def test_tabs_and_newlines(self):
        """Test that tabs and newlines are preserved."""
        assert to_pig_latin("hello\tworld") == "ellohay\torldway"
        # Note: newlines would typically be stripped in real usage

    def test_apostrophes_in_words(self):
        """Test words with apostrophes - each part is converted separately."""
        # Contractions are split on apostrophe and each part converted
        assert to_pig_latin("don't") == "onday'tay"
        assert to_pig_latin("it's") == "itway'say"
        assert to_pig_latin("I'm") == "Iway'may"


class TestExamplesFromDocstrings:
    """Test all examples from docstrings to ensure they work."""

    def test_word_to_pig_latin_docstring_examples(self):
        """Test examples from word_to_pig_latin docstring."""
        assert word_to_pig_latin("hello") == "ellohay"
        assert word_to_pig_latin("apple") == "appleway"
        assert word_to_pig_latin("String") == "Ingstray"

    def test_to_pig_latin_docstring_examples(self):
        """Test examples from to_pig_latin docstring."""
        assert to_pig_latin("Hello world") == "Ellohay orldway"
        # 'qu' moves together as a consonant cluster
        assert to_pig_latin("The quick brown fox") == "Ethay ickquay ownbray oxfay"
        assert to_pig_latin("I love Python!") == "Iway ovelay Ythonpay!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
