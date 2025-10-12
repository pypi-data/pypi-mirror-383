from persian_dict import PersianDictionary, SearchEngine, DataFormatter


def main():
    print("=== جستجوی پیشرفته دیکشنری ===")

    # ایجاد نمونه دیکشنری
    dictionary = PersianDictionary("data/ata")
    search_engine = SearchEngine(dictionary)

    while True:
        print("\n--- منوی جستجوی پیشرفته ---")
        print("1. جستجوی ساده")
        print("2. جستجوی پیشرفته")
        print("3. جستجوی کلمات مشابه")
        print("4. دریافت پیشنهادات")
        print("5. خروج")

        choice = input("انتخاب کنید: ")

        if choice == "1":
            # جستجوی ساده
            word = input("کلمه برای جستجو: ")
            results = search_engine.search_word(word)
            print(DataFormatter.format_search_results(results))

        elif choice == "2":
            # جستجوی پیشرفته
            print("\n--- فیلترهای جستجو ---")
            english_word = input("کلمه انگلیسی (خالی بگذارید برای نادیده گرفتن): ")
            persian_meaning = input("معنی فارسی (خالی بگذارید برای نادیده گرفتن): ")
            category = input("دسته‌بندی (خالی بگذارید برای همه): ")
            starts_with = input("شروع با: ")
            contains = input("شامل: ")

            results = search_engine.advanced_search(
                english_word=english_word or None,
                persian_meaning=persian_meaning or None,
                category=category or None,
                starts_with=starts_with or None,
                contains=contains or None,
            )

            print(DataFormatter.format_search_results(results))

        elif choice == "3":
            # جستجوی کلمات مشابه
            word = input("کلمه برای یافتن کلمات مشابه: ")
            similar_words = search_engine.search_similar_words(word)
            print(f"کلمات مشابه با '{word}':")
            for i, word_entry in enumerate(similar_words[:5], 1):
                print(
                    f"{i}. {word_entry.english_word} - {', '.join(word_entry.meanings)}"
                )

        elif choice == "4":
            # دریافت پیشنهادات
            word = input("کلمه برای دریافت پیشنهادات: ")
            suggestions = search_engine.get_suggestions(word)
            print(f"پیشنهادات برای '{word}':")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"{i}. {suggestion}")

        elif choice == "5":
            print("خداحافظ!")
            break

        else:
            print("انتخاب نامعتبر!")


if __name__ == "__main__":
    main()
