class DictionaryError(Exception):
    """پایه استثناهای مربوط به دیکشنری"""

    pass


class CategoryNotFoundError(DictionaryError):
    """استثنا برای زمانی که دسته‌بندی یافت نشود"""

    def __init__(self, category_name: str):
        self.category_name = category_name
        super().__init__(f"دسته‌بندی '{category_name}' یافت نشد")


class LetterNotFoundError(DictionaryError):
    """استثنا برای زمانی که حرف مورد نظر یافت نشود"""

    def __init__(self, letter: str, category: str = None):
        self.letter = letter
        self.category = category
        if category:
            super().__init__(f"حرف '{letter}' در دسته‌بندی '{category}' یافت نشد")
        else:
            super().__init__(f"حرف '{letter}' یافت نشد")


class WordNotFoundError(DictionaryError):
    """استثنا برای زمانی که کلمه مورد نظر یافت نشود"""

    def __init__(self, word: str):
        self.word = word
        super().__init__(f"کلمه '{word}' یافت نشد")


class DataLoadError(DictionaryError):
    """استثنا برای خطا در بارگذاری داده‌ها"""

    def __init__(self, message: str):
        super().__init__(f"خطا در بارگذاری داده‌ها: {message}")


class InvalidSearchParameterError(DictionaryError):
    """استثنا برای پارامترهای جستجوی نامعتبر"""

    def __init__(self, parameter: str, message: str):
        self.parameter = parameter
        super().__init__(f"پارامتر جستجوی '{parameter}' نامعتبر است: {message}")
