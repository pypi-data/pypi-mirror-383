from persian_dict import (
    PersianDictionary,
    SearchEngine,
    RandomWordGenerator,
    DataFormatter,
)


def main():
    print("=== دیکشنری انگلیسی به فارسی ===")

    # ایجاد نمونه دیکشنری
    print("در حال بارگذاری دیکشنری...")
    dictionary = PersianDictionary("data/ata")

    # دریافت اطلاعات کلی
    print(f"\nتعداد کل کلمات: {dictionary.get_word_count():,}")
    print(f"تعداد دسته‌بندی‌ها: {len(dictionary.get_categories())}")

    # نمایش دسته‌بندی‌ها
    print("\nدسته‌بندی‌های موجود:")
    for i, category in enumerate(dictionary.get_categories()[:10], 1):
        print(f"{i}. {category}")

    # ایجاد موتور جستجو
    search_engine = SearchEngine(dictionary)

    # جستجوی کلمه
    print("\n=== جستجوی کلمه ===")
    search_word = input("کلمه انگلیسی برای جستجو: ")
    results = search_engine.search_word(search_word)

    print(DataFormatter.format_search_results(results))

    # جستجوی معنی
    print("\n=== جستجوی معنی ===")
    search_meaning = input("معنی فارسی برای جستجو: ")
    results = search_engine.search_meaning(search_meaning)

    print(DataFormatter.format_search_results(results))

    # ایجاد تولیدکننده کلمات تصادفی
    random_gen = RandomWordGenerator(dictionary)

    # نمایش کلمات تصادفی
    print("\n=== کلمات تصادفی ===")
    random_gen.print_random_words(5, format_type="table")

    # نمایش آمار
    print("\n=== آمار دیکشنری ===")
    stats = dictionary.get_statistics()
    print(DataFormatter.format_statistics(stats))


if __name__ == "__main__":
    main()
