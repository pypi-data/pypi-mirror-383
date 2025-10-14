# translator.py
from .data import emoji_dict

def text_to_emoji(text: str) -> str:
    words = text.lower().split()
    result = []
    for word in words:
        result.append(emoji_dict.get(word, word))
    return ' '.join(result)
