import pytest
from persian_dict import PersianDictionary, RandomWordGenerator, DictionaryError


class TestRandomWordGenerator:
    @pytest.fixture
    def sample_dictionary(self):
        """ایجاد دیکشنری نمونه برای تست"""
        return PersianDictionary("data/ata")

    def test_randomizer_initialization(self, sample_dictionary):
        """تست مقداردهی اولیه تولیدکننده کلمات تصادفی"""
        randomizer = RandomWordGenerator(sample_dictionary)
        assert randomizer.dictionary == sample_dictionary
        assert hasattr(randomizer, "category_weights")

    def test_get_random_word(self, sample_dictionary):
        """تست دریافت کلمه تصادفی"""
        randomizer = RandomWordGenerator(sample_dictionary)
        word = randomizer.get_random_word()
        assert word is not None
        assert hasattr(word, "english_word")
        assert hasattr(word, "meanings")

    def test_get_random_words(self, sample_dictionary):
        """تست دریافت چندین کلمه تصادفی"""
        randomizer = RandomWordGenerator(sample_dictionary)
        words = randomizer.get_random_words(5)
        assert len(words) == 5
        for word in words:
            assert hasattr(word, "english_word")

    def test_get_random_words_with_category(self, sample_dictionary):
        """تست دریافت کلمات تصادفی از یک دسته‌بندی خاص"""
        randomizer = RandomWordGenerator(sample_dictionary)
        categories = sample_dictionary.get_categories()
        if categories:
            words = randomizer.get_random_words(3, category=categories[0])
            assert len(words) == 3
            for word in words:
                assert word.category == categories[0]

    def test_get_random_words_by_weight(self, sample_dictionary):
        """تست دریافت کلمات تصادفی با وزن"""
        randomizer = RandomWordGenerator(sample_dictionary)
        words = randomizer.get_random_words_by_weight(5)
        assert len(words) == 5

    def test_get_random_quiz(self, sample_dictionary):
        """تست ساخت آزمون تصادفی"""
        randomizer = RandomWordGenerator(sample_dictionary)
        quiz = randomizer.get_random_quiz(3)
        assert len(quiz) == 3
        for question in quiz:
            assert "question" in question
            assert "answer" in question
            assert "options" in question
