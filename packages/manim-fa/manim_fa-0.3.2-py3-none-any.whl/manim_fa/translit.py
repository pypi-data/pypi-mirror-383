import json
from pathlib import Path

LATIN_TO_PERSIAN = {
    "kh": "خ", "gh": "غ", "ch": "چ", "sh": "ش", "th": "ث",
    "a": "ا", "b": "ب", "c": "ک", "d": "د", "e": "ِ", "f": "ف", "g": "گ",
    "h": "ه", "i": "ی", "j": "ج", "k": "ک", "l": "ل", "m": "م", "n": "ن",
    "o": "و", "p": "پ", "q": "ق", "r": "ر", "s": "س", "t": "ت", "u": "و",
    "v": "و", "w": "و", "x": "کس", "y": "ی", "z": "ز",
}

DEFAULT_WORD_DICT = {
    "salam": "سلام",
    "chetori": "چطوری",
    "manim": "مانیم",
    "farsi": "فارسی",
    "khoda": "خدا",
    "mamnun": "ممنون",
    "khub": "خوب",
    "to": "تو"
}

def _load_dictionary(dict_path: str | None = None) -> dict:
    if dict_path:
        path = Path(dict_path)
    else:
        path = Path(__file__).parent / "dictionary.json"

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[manim-fa] 📘 Dictionary loaded from {path.name} ({len(data)} words).")
                return data
        except Exception as e:
            print(f"[manim-fa] ⚠️ Error loading dictionary ({e}). Using default words.")
    return DEFAULT_WORD_DICT

def translit_to_fa(text: str, dict_path: str | None = None) -> str:
    result = text.lower()
    word_dict = _load_dictionary(dict_path)
    for latin_word, persian_word in word_dict.items():
        result = result.replace(latin_word, persian_word)
    for latin, persian in sorted(LATIN_TO_PERSIAN.items(), key=lambda x: -len(x[0])):
        result = result.replace(latin, persian)
    return result
