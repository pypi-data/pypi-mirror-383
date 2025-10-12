from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class WordEntry:
    english_word: str
    meanings: List[str]
    category: Optional[str] = None
    letter: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "EnglishWord": self.english_word,
            "Meanings": self.meanings,
            "Category": self.category,
            "Letter": self.letter,
        }


@dataclass
class CategoryInfo:
    name: str
    letters: List[str]
    total_words: int
    word_count_by_letter: Dict[str, int]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "letters": self.letters,
            "total_words": self.total_words,
            "word_count_by_letter": self.word_count_by_letter,
        }
