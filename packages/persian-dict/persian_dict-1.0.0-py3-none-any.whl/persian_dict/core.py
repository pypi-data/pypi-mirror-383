import os
import json
import time
from typing import Dict, List, Optional, Set
from .data_models import WordEntry, CategoryInfo
from .exceptions import DictionaryError


class PersianDictionary:
    def __init__(self, data_path: str = "data/ata", use_cache: bool = True):
        self.data_path = data_path
        self.use_cache = use_cache
        self.categories: Dict[str, Dict[str, List[WordEntry]]] = {}
        self.all_words: List[WordEntry] = []
        self.category_info: Dict[str, CategoryInfo] = {}
        self.cache_dir = "data/cache"

        if use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self._load_data()

    def _load_data(self):
        """بارگذاری تمام داده‌های دیکشنری"""
        start_time = time.time()

        if not os.path.exists(self.data_path):
            raise DictionaryError(f"مسیر داده‌ها وجود ندارد: {self.data_path}")

        # تلاش برای بارگذاری از کش
        if self.use_cache:
            cached_data = self._load_from_cache()
            if cached_data:
                self.categories = cached_data.get("categories", {})
                self.all_words = cached_data.get("all_words", [])
                self.category_info = cached_data.get("category_info", {})
                print(
                    f"داده‌ها از کش بارگذاری شدند در {time.time() - start_time:.2f} ثانیه"
                )
                return

        # بارگذاری از فایل‌های JSON
        print("بارگذاری داده‌ها از فایل‌های JSON...")
        for category_name in os.listdir(self.data_path):
            category_path = os.path.join(self.data_path, category_name)
            if os.path.isdir(category_path):
                self.categories[category_name] = {}
                word_count = 0
                word_count_by_letter = {}
                letters = []

                for file_name in os.listdir(category_path):
                    if file_name.endswith(".json") and file_name != "readme.md":
                        file_path = os.path.join(category_path, file_name)
                        letter = file_name.replace(".json", "")
                        letters.append(letter)

                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                                # تبدیل داده‌ها به مدل WordEntry
                                words = []
                                for word_data in data.get("Words", []):
                                    word_entry = WordEntry(
                                        english_word=word_data["EnglishWord"],
                                        meanings=word_data["Meanings"],
                                        category=category_name,
                                        letter=letter,
                                    )
                                    words.append(word_entry)
                                    self.all_words.append(word_entry)

                                self.categories[category_name][letter] = words
                                word_count += len(words)
                                word_count_by_letter[letter] = len(words)

                        except Exception as e:
                            print(f"خطا در بارگذاری فایل {file_path}: {e}")

                # ایجاد اطلاعات دسته‌بندی
                self.category_info[category_name] = CategoryInfo(
                    name=category_name,
                    letters=letters,
                    total_words=word_count,
                    word_count_by_letter=word_count_by_letter,
                )

        # ذخیره در کش
        if self.use_cache:
            self._save_to_cache()

        print(f"بارگذاری کامل شد در {time.time() - start_time:.2f} ثانیه")
        print(f"تعداد کل کلمات: {len(self.all_words)}")
        print(f"تعداد دسته‌بندی‌ها: {len(self.categories)}")

    def _load_from_cache(self) -> Optional[Dict]:
        """بارگذاری داده‌ها از کش"""
        cache_file = os.path.join(self.cache_dir, "dictionary_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"خطا در بارگذاری کش: {e}")
        return None

    def _save_to_cache(self):
        """ذخیره داده‌ها در کش"""
        cache_file = os.path.join(self.cache_dir, "dictionary_cache.json")
        try:
            cache_data = {
                "categories": self.categories,
                "all_words": self.all_words,
                "category_info": self.category_info,
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
            print("داده‌ها در کش ذخیره شدند")
        except Exception as e:
            print(f"خطا در ذخیره کش: {e}")

    def get_categories(self) -> List[str]:
        """دریافت لیست تمام دسته‌بندی‌ها"""
        return list(self.categories.keys())

    def get_category_data(self, category: str) -> Dict[str, List[WordEntry]]:
        """دریافت داده‌های یک دسته‌بندی خاص"""
        if category not in self.categories:
            raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
        return self.categories[category]

    def get_all_data(self) -> List[WordEntry]:
        """دریافت تمام کلمات دیکشنری"""
        return self.all_words

    def get_word_count(self, category: Optional[str] = None) -> int:
        """دریافت تعداد کلمات در یک دسته‌بندی یا کل دیکشنری"""
        if category:
            if category not in self.category_info:
                raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
            return self.category_info[category].total_words
        return len(self.all_words)

    def get_letters_in_category(self, category: str) -> List[str]:
        """دریافت لیست حروف موجود در یک دسته‌بندی"""
        if category not in self.category_info:
            raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
        return self.category_info[category].letters

    def get_category_info(self, category: str) -> CategoryInfo:
        """دریافت اطلاعات کامل یک دسته‌بندی"""
        if category not in self.category_info:
            raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
        return self.category_info[category]

    def get_words_by_letter(self, category: str, letter: str) -> List[WordEntry]:
        """دریافت کلمات یک حرف خاص در یک دسته‌بندی"""
        if category not in self.categories:
            raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
        if letter not in self.categories[category]:
            raise DictionaryError(f"حرف '{letter}' در دسته‌بندی '{category}' یافت نشد")
        return self.categories[category][letter]

    def search_by_prefix(
        self, prefix: str, category: Optional[str] = None
    ) -> List[WordEntry]:
        """جستجوی کلمات با پیشوند خاص"""
        prefix = prefix.lower()
        results = []

        if category:
            if category not in self.categories:
                raise DictionaryError(f"دسته‌بندی '{category}' یافت نشد")
            for letter_words in self.categories[category].values():
                for word in letter_words:
                    if word.english_word.lower().startswith(prefix):
                        results.append(word)
        else:
            for word in self.all_words:
                if word.english_word.lower().startswith(prefix):
                    results.append(word)

        return results

    def get_statistics(self) -> Dict:
        """دریافت آمار کلی دیکشنری"""
        stats = {
            "total_words": len(self.all_words),
            "total_categories": len(self.categories),
            "categories": {},
        }

        for category_name, info in self.category_info.items():
            stats["categories"][category_name] = {
                "total_words": info.total_words,
                "letters": len(info.letters),
                "most_common_letter": (
                    max(info.word_count_by_letter.items(), key=lambda x: x[1])[0]
                    if info.word_count_by_letter
                    else None
                ),
            }

        return stats
