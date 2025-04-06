# Module: text_analysis.py
def count_consonant_words(text):
    """Count words starting with a lowercase consonant.
    
    Args:
        text (str): Input string.
    
    Returns:
        int: Number of words starting with a lowercase consonant.
    """
    consonants = set("bcdfghjklmnpqrstvwxyz")
    words = text.split()
    count = sum(1 for word in words if word and word[0].lower() in consonants)
    return count
def analyze_string(text):
    """Analyze string for minimal length words, words before period, and longest word ending with 'r'.
    
    Args:
        text (str): Input string.
    
    Returns:
        tuple: (count of min-length words, list of words before period, longest word ending with 'r')
    """
    import string
    words = [word.strip(string.punctuation) for word in text.split()]
    
    # a) Count words with minimal length
    if words:
        min_length = min(len(word) for word in words if word)
        count_min_length = sum(1 for word in words if len(word) == min_length)
    else:
        count_min_length = 0
    
    # b) Words followed by a period
    words_before_period = [word for word in text.split() if word.endswith('.')]
    
    # c) Longest word ending with 'r'
    words_ending_r = [word for word in words if word.lower().endswith('r')]
    longest_r = max(words_ending_r, key=len, default="None")
    
    return count_min_length, words_before_period, longest_r