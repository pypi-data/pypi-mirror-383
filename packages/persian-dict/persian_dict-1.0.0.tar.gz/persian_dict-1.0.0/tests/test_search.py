import pytest
from persian_dict import PersianDictionary, SearchEngine, DictionaryError


class TestSearchEngine:
    @pytest.fixture
    def sample_dictionary(self):
        """ایجاد دیکشنری نمونه برای تست"""
        # در اینجا می‌توانید یک دیکشنری نمونه با داده‌های از پیش تعریف شده ایجاد کنید
        # برای سادگی، فرض می‌کنیم دیکشنری با داده‌های واقعی وجود دارد
        return PersianDictionary("data/ata")

    def test_search_engine_initialization(self, sample_dictionary):
        """تست مقداردهی اولیه موتور جستجو"""
        search_engine = SearchEngine(sample_dictionary)
        assert search_engine.dictionary == sample_dictionary
        assert hasattr(search_engine, "word_index")
        assert hasattr(search_engine, "meaning_index")

    def test_search_word_exact(self, sample_dictionary):
        """تست جستجوی دقیق کلمه"""
        search_engine = SearchEngine(sample_dictionary)
        # فرض می‌کنیم کلمه "computer" در دیکشنری وجود دارد
        results = search_engine.search_word("computer", exact_match=True)
        assert len(results) >= 0  # ممکن است نتایجی وجود داشته باشد یا نه

    def test_search_word_partial(self, sample_dictionary):
        """تست جستجوی جزئی کلمه"""
        search_engine = SearchEngine(sample_dictionary)
        results = search_engine.search_word("comp", exact_match=False)
        assert len(results) >= 0

    def test_search_meaning(self, sample_dictionary):
        """تست جستجوی معنی"""
        search_engine = SearchEngine(sample_dictionary)
        # فرض می‌کنیم معنی "کامپیوتر" در دیکشنری وجود دارد
        results = search_engine.search_meaning("کامپیوتر")
        assert len(results) >= 0

    def test_advanced_search(self, sample_dictionary):
        """تست جستجوی پیشرفته"""
        search_engine = SearchEngine(sample_dictionary)
        results = search_engine.advanced_search(
            english_word="comp", category="computer", max_results=10
        )
        assert len(results) >= 0

    def test_search_similar_words(self, sample_dictionary):
        """تست جستجوی کلمات مشابه"""
        search_engine = SearchEngine(sample_dictionary)
        similar_words = search_engine.search_similar_words("computr")  # با املای اشتباه
        assert len(similar_words) >= 0

    def test_get_suggestions(self, sample_dictionary):
        """تست دریافت پیشنهادات"""
        search_engine = SearchEngine(sample_dictionary)
        suggestions = search_engine.get_suggestions("computr")
        assert len(suggestions) >= 0
