"""
Core Pig Latin conversion functions.

Pig Latin rules:
1. For words beginning with consonant sounds, move the consonant(s) to the end and add "ay"
   Example: "hello" -> "ellohay", "string" -> "ingstray"
2. For words beginning with vowel sounds, just add "way" to the end
   Example: "apple" -> "appleway", "eat" -> "eatway"
3. Preserve capitalization and punctuation
"""

import re
from typing import List

VOWELS = set('aeiouAEIOU')


def word_to_pig_latin(word: str) -> str:
    """
    Convert a single word to Pig Latin.

    Args:
        word: A single word to convert

    Returns:
        The word converted to Pig Latin

    Examples:
        >>> word_to_pig_latin("hello")
        'ellohay'
        >>> word_to_pig_latin("apple")
        'appleway'
        >>> word_to_pig_latin("String")
        'Ingstray'
    """
    if not word:
        return word

    # Extract any leading/trailing punctuation
    leading_punct = ""
    trailing_punct = ""

    # Find leading punctuation
    i = 0
    while i < len(word) and not word[i].isalpha():
        leading_punct += word[i]
        i += 1

    # Find trailing punctuation
    j = len(word) - 1
    while j >= 0 and not word[j].isalpha():
        trailing_punct = word[j] + trailing_punct
        j -= 1

    # Extract the actual word
    if i > j:
        return word  # No alphabetic characters

    clean_word = word[i:j+1]

    if not clean_word:
        return word

    # Check if first letter is uppercase
    is_capitalized = clean_word[0].isupper()
    # For single letter words, treat as capitalized not all caps
    is_all_caps = clean_word.isupper() and len(clean_word) > 1

    # Work with lowercase for easier processing
    lower_word = clean_word.lower()

    # Apply Pig Latin rules
    if lower_word[0] in VOWELS:
        # Starts with vowel: add "way"
        pig_latin = lower_word + "way"
    else:
        # Starts with consonant(s): move consonant cluster to end and add "ay"
        # 'y' acts as a vowel when it comes after consonants
        consonant_cluster = ""
        idx = 0

        # Collect consonant cluster
        while idx < len(lower_word):
            current_char = lower_word[idx]

            # Stop at a regular vowel
            if current_char in VOWELS:
                break

            # 'y' acts as a vowel if it's not at the start and comes after consonants
            # BUT only if there are other letters after it OR if it's the only "vowel" sound
            if current_char == 'y' and idx > 0:
                # Check if there's anything after 'y'
                if idx + 1 < len(lower_word):
                    # 'y' acts as a vowel when it's in the middle/acts as vowel sound
                    break
                # If 'y' is at the end, treat it as a vowel
                break

            consonant_cluster += current_char
            idx += 1

            # Special case: 'qu' should stay together as a consonant cluster
            if consonant_cluster and consonant_cluster[-1] == 'q' and idx < len(lower_word) and lower_word[idx] == 'u':
                consonant_cluster += lower_word[idx]
                idx += 1

        # If we consumed the entire word, just add "ay"
        if idx >= len(lower_word):
            pig_latin = lower_word + "ay"
        else:
            pig_latin = lower_word[idx:] + consonant_cluster + "ay"

    # Restore capitalization
    if is_all_caps:
        pig_latin = pig_latin.upper()
    elif is_capitalized:
        pig_latin = pig_latin[0].upper() + pig_latin[1:]

    return leading_punct + pig_latin + trailing_punct


def to_pig_latin(text: str) -> str:
    """
    Convert a string of text to Pig Latin.

    This function processes an entire string, converting each word to Pig Latin
    while preserving spacing, punctuation, and capitalization.

    Args:
        text: The text to convert to Pig Latin

    Returns:
        The text converted to Pig Latin

    Examples:
        >>> to_pig_latin("Hello world")
        'Ellohay orldway'
        >>> to_pig_latin("The quick brown fox")
        'Ethay ickquay ownbray oxfay'
        >>> to_pig_latin("I love Python!")
        'Iway ovelay Ythonpay!'
    """
    if not text:
        return text

    # Split text into words while preserving whitespace
    # Use regex to split on whitespace but keep the whitespace
    parts = re.split(r'(\s+)', text)

    result = []
    for part in parts:
        if part and not part.isspace():
            # Check if part contains apostrophe (contractions)
            if "'" in part:
                # Split on apostrophe and convert each part separately
                subparts = re.split(r"(')", part)
                converted_subparts = []
                for subpart in subparts:
                    if subpart == "'":
                        converted_subparts.append(subpart)
                    elif subpart:
                        converted_subparts.append(word_to_pig_latin(subpart))
                result.append(''.join(converted_subparts))
            else:
                # It's a regular word, convert it
                result.append(word_to_pig_latin(part))
        else:
            # It's whitespace, preserve it
            result.append(part)

    return ''.join(result)
