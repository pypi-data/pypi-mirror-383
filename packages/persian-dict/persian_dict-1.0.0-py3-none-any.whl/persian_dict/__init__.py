from .core import PersianDictionary
from .search import SearchEngine
from .randomizer import RandomWordGenerator
from .utils import DataFormatter, TextProcessor
from .exceptions import (
    DictionaryError,
    CategoryNotFoundError,
    LetterNotFoundError,
    WordNotFoundError,
    DataLoadError,
    InvalidSearchParameterError,
)
from .data_models import WordEntry, CategoryInfo

__version__ = "1.0.0"
__author__ = "Ehsan Fazli"
__email__ = "ehsanfazlinejad@gmail.com"

__all__ = [
    "PersianDictionary",
    "SearchEngine",
    "RandomWordGenerator",
    "DataFormatter",
    "TextProcessor",
    "DictionaryError",
    "CategoryNotFoundError",
    "LetterNotFoundError",
    "WordNotFoundError",
    "DataLoadError",
    "InvalidSearchParameterError",
    "WordEntry",
    "CategoryInfo",
]
