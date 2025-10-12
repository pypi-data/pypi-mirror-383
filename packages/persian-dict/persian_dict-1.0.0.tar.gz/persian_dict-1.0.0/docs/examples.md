# مثال‌های استفاده از کتابخانه دیکشنری پارسی

## مثال 1: استفاده پایه

```python
from persian_dict import PersianDictionary, SearchEngine, RandomWordGenerator

# ایجاد دیکشنری
dictionary = PersianDictionary("data/ata")

# دریافت اطلاعات کلی
print(f"تعداد کل کلمات: {dictionary.get_word_count()}")
print(f"دسته‌بندی‌ها: {dictionary.get_categories()}")

# جستجوی کلمه
search_engine = SearchEngine(dictionary)
results = search_engine.search_word("computer")
for word in results:
    print(f"{word.english_word}: {', '.join(word.meanings)}")

# کلمات تصادفی
random_gen = RandomWordGenerator(dictionary)
random_words = random_gen.get_random_words(3)
for word in random_words:
    print(f"کلمه تصادفی: {word.english_word}")