from typing import List, Dict, Any
from .data_models import WordEntry, CategoryInfo
from .core import PersianDictionary


class DataFormatter:
    @staticmethod
    def format_word_entry(word_entry: WordEntry, show_metadata: bool = False) -> str:
        """قالب‌بندی یک ورودی کلمه برای نمایش"""
        result = f"کلمه: {word_entry.english_word}\n"
        result += f"معانی: {', '.join(word_entry.meanings)}\n"

        if show_metadata:
            result += f"دسته‌بندی: {word_entry.category or 'N/A'}\n"
            result += f"حرف: {word_entry.letter or 'N/A'}\n"

        return result

    @staticmethod
    def format_category_summary(dictionary: PersianDictionary, category: str) -> str:
        """قالب‌بندی خلاصه یک دسته‌بندی"""
        if category not in dictionary.category_info:
            return f"دسته‌بندی '{category}' یافت نشد"

        info = dictionary.category_info[category]
        result = f"دسته‌بندی: {category}\n"
        result += f"تعداد کلمات: {info.total_words}\n"
        result += f"تعداد حروف: {len(info.letters)}\n"
        result += f"حروف موجود: {', '.join(sorted(info.letters))}\n"

        if info.word_count_by_letter:
            most_common = max(info.word_count_by_letter.items(), key=lambda x: x[1])
            result += f"پرکاربردترین حرف: {most_common[0]} ({most_common[1]} کلمه)\n"

        return result

    @staticmethod
    def format_search_results(results: List[WordEntry], max_display: int = 10) -> str:
        """قالب‌بندی نتایج جستجو"""
        if not results:
            return "هیچ نتیجه‌ای یافت نشد"

        result = f"تعداد نتایج یافت شده: {len(results)}\n"
        if len(results) > max_display:
            result += f"نمایش {max_display} نتیجه اول از {len(results)} نتیجه:\n\n"
        else:
            result += f"نمایش تمام {len(results)} نتیجه:\n\n"

        for i, entry in enumerate(results[:max_display], 1):
            result += f"{i}. {entry.english_word}\n"
            result += f"   معانی: {', '.join(entry.meanings)}\n"
            if entry.category:
                result += f"   دسته‌بندی: {entry.category}\n"
            result += "\n"

        return result

    @staticmethod
    def format_statistics(stats: Dict) -> str:
        """قالب‌بندی آمار دیکشنری"""
        result = f"آمار دیکشنری:\n"
        result += f"{'='*30}\n"
        result += f"تعداد کل کلمات: {stats['total_words']:,}\n"
        result += f"تعداد دسته‌بندی‌ها: {stats['total_categories']}\n\n"

        result += "جزئیات دسته‌بندی‌ها:\n"
        result += f"{'-'*50}\n"

        for category, info in stats["categories"].items():
            result += f"{category}:\n"
            result += f"  - کلمات: {info['total_words']:,}\n"
            result += f"  - حروف: {info['letters']}\n"
            result += f"  - پرکاربردترین حرف: {info['most_common_letter'] or 'N/A'}\n\n"

        return result

    @staticmethod
    def export_to_json(data: Any, filename: str):
        """صادرات داده‌ها به فایل JSON"""
        import json

        def default_converter(obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=default_converter)

    @staticmethod
    def export_to_csv(words: List[WordEntry], filename: str):
        """صادرات کلمات به فایل CSV"""
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["English Word", "Meanings", "Category", "Letter"])

            for word in words:
                writer.writerow(
                    [
                        word.english_word,
                        "|".join(word.meanings),
                        word.category or "",
                        word.letter or "",
                    ]
                )


class TextProcessor:
    @staticmethod
    def normalize_persian(text: str) -> str:
        """نرمال‌سازی متن فارسی"""
        # تبدیل اعداد فارسی به انگلیسی
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
        english_numbers = "0123456789"
        translation_table = str.maketrans(persian_numbers, english_numbers)

        text = text.translate(translation_table)

        # حذف فاصله‌های اضافی
        text = " ".join(text.split())

        return text

    @staticmethod
    def extract_words_from_text(text: str) -> List[str]:
        """استخراج کلمات از متن"""
        import re

        # حذف علائم نگارشی
        text = re.sub(r"[^\w\s]", "", text)

        # تقسیم به کلمات
        words = text.split()

        return words

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """محاسبه شباهت بین دو متن"""
        from difflib import SequenceMatcher

        return SequenceMatcher(None, text1, text2).ratio()
