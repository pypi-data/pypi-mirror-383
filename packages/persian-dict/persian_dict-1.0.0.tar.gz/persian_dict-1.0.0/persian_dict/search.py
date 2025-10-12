from typing import List, Dict, Optional, Set
from .core import PersianDictionary
from .data_models import WordEntry
from .exceptions import DictionaryError
import re


class SearchEngine:
    def __init__(self, dictionary: PersianDictionary):
        self.dictionary = dictionary
        self._build_search_index()

    def _build_search_index(self):
        """ساخت ایندکس جستجو برای عملکرد بهتر"""
        self.word_index = {}
        self.meaning_index = {}

        for word in self.dictionary.all_words:
            # ایندکس کلمات انگلیسی
            english_lower = word.english_word.lower()
            if english_lower not in self.word_index:
                self.word_index[english_lower] = []
            self.word_index[english_lower].append(word)

            # ایندکس معانی فارسی
            for meaning in word.meanings:
                meaning_lower = meaning.lower()
                if meaning_lower not in self.meaning_index:
                    self.meaning_index[meaning_lower] = []
                self.meaning_index[meaning_lower].append(word)

    def search_word(
        self,
        word: str,
        category: Optional[str] = None,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> List[WordEntry]:
        """جستجوی یک کلمه در دیکشنری"""
        if not case_sensitive:
            word = word.lower()

        results = []

        if exact_match:
            # جستجوی دقیق
            if word in self.word_index:
                candidates = self.word_index[word]
                if category:
                    results = [w for w in candidates if w.category == category]
                else:
                    results = candidates
        else:
            # جستجوی جزئی
            pattern = re.compile(
                re.escape(word), re.IGNORECASE if not case_sensitive else 0
            )
            for w in self.dictionary.all_words:
                if pattern.search(w.english_word):
                    if not category or w.category == category:
                        results.append(w)

        return results

    def search_meaning(
        self, meaning: str, category: Optional[str] = None, exact_match: bool = False
    ) -> List[WordEntry]:
        """جستجوی بر اساس معنی فارسی"""
        meaning = meaning.lower()
        results = []

        if exact_match:
            # جستجوی دقیق معنی
            if meaning in self.meaning_index:
                candidates = self.meaning_index[meaning]
                if category:
                    results = [w for w in candidates if w.category == category]
                else:
                    results = candidates
        else:
            # جستجوی جزئی معنی
            pattern = re.compile(re.escape(meaning))
            for word in self.dictionary.all_words:
                for m in word.meanings:
                    if pattern.search(m.lower()):
                        if not category or word.category == category:
                            results.append(word)
                            break

        return results

    def advanced_search(
        self,
        english_word: Optional[str] = None,
        persian_meaning: Optional[str] = None,
        category: Optional[str] = None,
        letter: Optional[str] = None,
        starts_with: Optional[str] = None,
        ends_with: Optional[str] = None,
        contains: Optional[str] = None,
        max_results: int = 50,
    ) -> List[WordEntry]:
        """جستجوی پیشرفته با چندین فیلتر"""
        results = []

        # تعیین داده‌های جستجو بر اساس فیلترها
        if category and letter:
            if (
                category not in self.dictionary.categories
                or letter not in self.dictionary.categories[category]
            ):
                return []
            data_to_search = self.dictionary.categories[category][letter]
        elif category:
            if category not in self.dictionary.categories:
                return []
            data_to_search = []
            for letter_words in self.dictionary.categories[category].values():
                data_to_search.extend(letter_words)
        else:
            data_to_search = self.dictionary.all_words

        # اعمال فیلترها
        for word in data_to_search:
            match = True

            # فیلتر کلمه انگلیسی
            if english_word:
                if english_word.lower() not in word.english_word.lower():
                    match = False

            # فیلتر معنی فارسی
            if persian_meaning:
                meaning_found = any(
                    persian_meaning.lower() in m.lower() for m in word.meanings
                )
                if not meaning_found:
                    match = False

            # فیلتر شروع با
            if starts_with:
                if not word.english_word.lower().startswith(starts_with.lower()):
                    match = False

            # فیلتر پایان با
            if ends_with:
                if not word.english_word.lower().endswith(ends_with.lower()):
                    match = False

            # فیلتر شامل
            if contains:
                if contains.lower() not in word.english_word.lower():
                    match = False

            if match:
                results.append(word)
                if len(results) >= max_results:
                    break

        return results

    def search_similar_words(self, word: str, max_distance: int = 2) -> List[WordEntry]:
        """جستجوی کلمات مشابه (برای املای اشتباه)"""
        word = word.lower()
        results = []

        for dict_word in self.dictionary.all_words:
            dict_word_lower = dict_word.english_word.lower()
            distance = self._levenshtein_distance(word, dict_word_lower)
            if distance <= max_distance:
                results.append((dict_word, distance))

        # مرتب‌سازی بر اساس فاصله
        results.sort(key=lambda x: x[1])
        return [word for word, _ in results]

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """محاسبه فاصله لون‌اشتاین بین دو رشته"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """دریافت پیشنهادات برای یک کلمه"""
        similar_words = self.search_similar_words(word)
        return [w.english_word for w in similar_words[:max_suggestions]]
