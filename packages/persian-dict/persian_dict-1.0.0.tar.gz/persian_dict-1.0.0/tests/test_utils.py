import pytest
import tempfile
import os
from persian_dict import PersianDictionary, DataFormatter, TextProcessor, WordEntry


class TestDataFormatter:
    @pytest.fixture
    def sample_word(self):
        """ایجاد کلمه نمونه برای تست"""
        return WordEntry(
            english_word="computer",
            meanings=["کامپیوتر", "رایانه"],
            category="computer",
            letter="C",
        )

    def test_format_word_entry(self, sample_word):
        """تست قالب‌بندی کلمه"""
        formatted = DataFormatter.format_word_entry(sample_word)
        assert "کلمه: computer" in formatted
        assert "معانی: کامپیوتر, رایانه" in formatted

    def test_format_word_entry_with_metadata(self, sample_word):
        """تست قالب‌بندی کلمه با متادیتا"""
        formatted = DataFormatter.format_word_entry(sample_word, show_metadata=True)
        assert "دسته‌بندی: computer" in formatted
        assert "حرف: C" in formatted

    def test_format_search_results(self, sample_word):
        """تست قالب‌بندی نتایج جستجو"""
        results = [sample_word]
        formatted = DataFormatter.format_search_results(results)
        assert "تعداد نتایج یافت شده: 1" in formatted
        assert "computer" in formatted

    def test_format_search_results_empty(self):
        """تست قالب‌بندی نتایج جستجوی خالی"""
        formatted = DataFormatter.format_search_results([])
        assert "هیچ نتیجه‌ای یافت نشد" in formatted

    def test_export_to_json(self, sample_word):
        """تست صادرات به JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            DataFormatter.export_to_json(sample_word, f.name)
            assert os.path.exists(f.name)
            # بررسی محتوای فایل
            with open(f.name, "r", encoding="utf-8") as file:
                content = file.read()
                assert "computer" in content
            os.unlink(f.name)

    def test_export_to_csv(self, sample_word):
        """تست صادرات به CSV"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            DataFormatter.export_to_csv([sample_word], f.name)
            assert os.path.exists(f.name)
            # بررسی محتوای فایل
            with open(f.name, "r", encoding="utf-8") as file:
                content = file.read()
                assert "computer" in content
            os.unlink(f.name)


class TestTextProcessor:
    def test_normalize_persian(self):
        """تست نرمال‌سازی متن فارسی"""
        text = "این یک متن ۱۲۳ است"
        normalized = TextProcessor.normalize_persian(text)
        assert normalized == "این یک متن 123 است"

    def test_extract_words_from_text(self):
        """تست استخراج کلمات از متن"""
        text = "این یک متن نمونه است."
        words = TextProcessor.extract_words_from_text(text)
        assert words == ["این", "یک", "متن", "نمونه", "است"]

    def test_calculate_similarity(self):
        """تست محاسبه شباهت"""
        similarity = TextProcessor.calculate_similarity("computer", "computre")
        assert similarity > 0.5  # باید شباهت بالایی وجود داشته باشد

        similarity = TextProcessor.calculate_similarity("computer", "book")
        assert similarity < 0.5  # باید شباهت کمی وجود داشته باشد
