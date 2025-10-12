import pytest
import os
import tempfile
import json
from persian_dict import PersianDictionary, DictionaryError


class TestPersianDictionary:
    @pytest.fixture
    def sample_data(self):
        """ایجاد داده‌های نمونه برای تست"""
        return {
            "Group": "A",
            "Entries": 2,
            "Words": [
                {"EnglishWord": "apple", "Meanings": ["سیب"]},
                {"EnglishWord": "book", "Meanings": ["کتاب"]},
            ],
        }

    @pytest.fixture
    def temp_dictionary(self, sample_data):
        """ایجاد دیکشنری موقت برای تست"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # ساخت پوشه داده‌ها
            data_dir = os.path.join(temp_dir, "test_dict")
            os.makedirs(data_dir)

            # ساخت فایل نمونه
            test_file = os.path.join(data_dir, "A.json")
            with open(test_file, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, ensure_ascii=False)

            yield PersianDictionary(data_dir)

    def test_initialization(self, temp_dictionary):
        """تست مقداردهی اولیه دیکشنری"""
        assert len(temp_dictionary.categories) == 1
        assert "test_dict" in temp_dictionary.categories
        assert len(temp_dictionary.all_words) == 2

    def test_get_categories(self, temp_dictionary):
        """تست دریافت دسته‌بندی‌ها"""
        categories = temp_dictionary.get_categories()
        assert categories == ["test_dict"]

    def test_get_category_data(self, temp_dictionary):
        """تست دریافت داده‌های دسته‌بندی"""
        category_data = temp_dictionary.get_category_data("test_dict")
        assert "A" in category_data
        assert len(category_data["A"]) == 2

    def test_get_all_data(self, temp_dictionary):
        """تست دریافت تمام داده‌ها"""
        all_data = temp_dictionary.get_all_data()
        assert len(all_data) == 2
        assert all_data[0].english_word == "apple"

    def test_get_word_count(self, temp_dictionary):
        """تست دریافت تعداد کلمات"""
        assert temp_dictionary.get_word_count() == 2
        assert temp_dictionary.get_word_count("test_dict") == 2

    def test_invalid_category(self, temp_dictionary):
        """تست دسته‌بندی نامعتبر"""
        with pytest.raises(DictionaryError):
            temp_dictionary.get_category_data("invalid")

        with pytest.raises(DictionaryError):
            temp_dictionary.get_word_count("invalid")

    def test_search_by_prefix(self, temp_dictionary):
        """تست جستجو با پیشوند"""
        results = temp_dictionary.search_by_prefix("a")
        assert len(results) == 1
        assert results[0].english_word == "apple"

        results = temp_dictionary.search_by_prefix("b")
        assert len(results) == 1
        assert results[0].english_word == "book"

    def test_get_statistics(self, temp_dictionary):
        """تست دریافت آمار"""
        stats = temp_dictionary.get_statistics()
        assert stats["total_words"] == 2
        assert stats["total_categories"] == 1
        assert "test_dict" in stats["categories"]
