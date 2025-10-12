import random
from typing import List, Dict, Optional
from .core import PersianDictionary
from .data_models import WordEntry
from .exceptions import DictionaryError


class RandomWordGenerator:
    def __init__(self, dictionary: PersianDictionary):
        self.dictionary = dictionary
        self._build_category_weights()

    def _build_category_weights(self):
        """ساخت وزن‌دهی برای دسته‌بندی‌ها بر اساس تعداد کلمات"""
        self.category_weights = {}
        total_words = len(self.dictionary.all_words)

        for category_name, info in self.dictionary.category_info.items():
            weight = info.total_words / total_words
            self.category_weights[category_name] = weight

    def get_random_word(
        self,
        category: Optional[str] = None,
        letter: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> WordEntry:
        """دریافت یک کلمه تصادفی"""
        if seed is not None:
            random.seed(seed)

        if category and category not in self.dictionary.categories:
            raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")

        if category and letter:
            if letter not in self.dictionary.categories[category]:
                raise DictionaryError(
                    f"حرف '{letter}' در دسته‌بندی '{category}' یافت نشد"
                )
            words = self.dictionary.categories[category][letter]
            return random.choice(words) if words else None

        if category:
            all_words = []
            for letter_words in self.dictionary.categories[category].values():
                all_words.extend(letter_words)
            return random.choice(all_words) if all_words else None

        return (
            random.choice(self.dictionary.all_words)
            if self.dictionary.all_words
            else None
        )

    def get_random_words(
        self,
        count: int = 10,
        category: Optional[str] = None,
        letter: Optional[str] = None,
        unique: bool = True,
        seed: Optional[int] = None,
    ) -> List[WordEntry]:
        """دریافت چندین کلمه تصادفی"""
        if seed is not None:
            random.seed(seed)

        words = []
        attempts = 0
        max_attempts = count * 10  # جلوگیری از حلقه بی‌نهایت

        while len(words) < count and attempts < max_attempts:
            word = self.get_random_word(category, letter)
            if word:
                if not unique or word not in words:
                    words.append(word)
            attempts += 1

        return words

    def get_random_words_by_weight(
        self, count: int = 10, seed: Optional[int] = None
    ) -> List[WordEntry]:
        """دریافت کلمات تصادفی با توجه به وزن دسته‌بندی‌ها"""
        if seed is not None:
            random.seed(seed)

        words = []
        categories = list(self.category_weights.keys())
        weights = list(self.category_weights.values())

        for _ in range(count):
            # انتخاب دسته‌بندی با احتمال وزنی
            category = random.choices(categories, weights=weights)[0]
            word = self.get_random_word(category=category)
            if word:
                words.append(word)

        return words

    def get_random_words_from_categories(
        self,
        categories: List[str],
        words_per_category: int = 1,
        seed: Optional[int] = None,
    ) -> Dict[str, List[WordEntry]]:
        """دریافت کلمات تصادفی از چندین دسته‌بندی"""
        if seed is not None:
            random.seed(seed)

        result = {}
        for category in categories:
            if category in self.dictionary.categories:
                words = self.get_random_words(
                    count=words_per_category, category=category
                )
                result[category] = words

        return result

    def print_random_words(
        self,
        count: int = 10,
        category: Optional[str] = None,
        letter: Optional[str] = None,
        show_meanings: bool = True,
        format_type: str = "simple",
    ):
        """چاپ کلمات تصادفی"""
        words = self.get_random_words(count, category, letter)

        if format_type == "simple":
            for i, word in enumerate(words, 1):
                print(f"{i}. {word.english_word}")
                if show_meanings:
                    print(f"   معانی: {', '.join(word.meanings)}")
                print()

        elif format_type == "table":
            print(f"{'#':<3} {'English Word':<20} {'Meanings':<30} {'Category':<15}")
            print("-" * 70)
            for i, word in enumerate(words, 1):
                meanings = ", ".join(word.meanings[:2])  # حداکثر 2 معنی
                if len(word.meanings) > 2:
                    meanings += "..."
                print(
                    f"{i:<3} {word.english_word:<20} {meanings:<30} {word.category or 'N/A':<15}"
                )

        elif format_type == "detailed":
            for i, word in enumerate(words, 1):
                print(f"کلمه {i}:")
                print(f"  انگلیسی: {word.english_word}")
                print(f"  فارسی: {', '.join(word.meanings)}")
                print(f"  دسته‌بندی: {word.category}")
                print(f"  حرف: {word.letter}")
                print()

    def get_random_quiz(
        self,
        count: int = 5,
        category: Optional[str] = None,
        question_type: str = "english_to_persian",
    ) -> List[Dict]:
        """ساخت آزمون تصادفی"""
        questions = []
        words = self.get_random_words(count, category)

        for word in words:
            if question_type == "english_to_persian":
                question = {
                    "question": word.english_word,
                    "answer": random.choice(word.meanings),
                    "options": [random.choice(word.meanings)],
                    "category": word.category,
                }

                # افزودن گزینه‌های اشتباه
                other_words = self.get_random_words(3, category)
                for other_word in other_words:
                    if other_word.english_word != word.english_word:
                        question["options"].append(random.choice(other_word.meanings))

                # مخلوط کردن گزینه‌ها
                random.shuffle(question["options"])
                questions.append(question)

            elif question_type == "persian_to_english":
                correct_meaning = random.choice(word.meanings)
                question = {
                    "question": correct_meaning,
                    "answer": word.english_word,
                    "options": [word.english_word],
                    "category": word.category,
                }

                # افزودن گزینه‌های اشتباه
                other_words = self.get_random_words(3, category)
                for other_word in other_words:
                    if other_word.english_word != word.english_word:
                        question["options"].append(other_word.english_word)

                # مخلوط کردن گزینه‌ها
                random.shuffle(question["options"])
                questions.append(question)

        return questions
