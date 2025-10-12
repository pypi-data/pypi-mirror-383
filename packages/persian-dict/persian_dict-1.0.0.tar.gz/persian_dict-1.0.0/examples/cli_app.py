import argparse
from persian_dict import (
    PersianDictionary,
    SearchEngine,
    RandomWordGenerator,
    DataFormatter,
)


def main():
    parser = argparse.ArgumentParser(description="دیکشنری انگلیسی به فارسی")
    parser.add_argument("--data-path", default="data/ata", help="مسیر داده‌های دیکشنری")
    parser.add_argument("--search", help="جستجوی کلمه")
    parser.add_argument("--meaning", help="جستجوی معنی")
    parser.add_argument("--category", help="فیلتر دسته‌بندی")
    parser.add_argument("--random", type=int, help="تعداد کلمات تصادفی برای نمایش")
    parser.add_argument("--stats", action="store_true", help="نمایش آمار دیکشنری")
    parser.add_argument(
        "--categories", action="store_true", help="نمایش لیست دسته‌بندی‌ها"
    )
    parser.add_argument("--export-json", help="صادرات نتایج به فایل JSON")
    parser.add_argument("--export-csv", help="صادرات نتایج به فایل CSV")

    args = parser.parse_args()

    try:
        # ایجاد نمونه دیکشنری
        dictionary = PersianDictionary(args.data_path)

        if args.categories:
            print("دسته‌بندی‌های موجود:")
            for i, category in enumerate(dictionary.get_categories(), 1):
                info = dictionary.get_category_info(category)
                print(f"{i}. {category} ({info.total_words:,} کلمه)")

        if args.stats:
            stats = dictionary.get_statistics()
            print(DataFormatter.format_statistics(stats))

        if args.search:
            search_engine = SearchEngine(dictionary)
            results = search_engine.search_word(args.search, args.category)
            output = DataFormatter.format_search_results(results)
            print(output)

            if args.export_json:
                DataFormatter.export_to_json(results, args.export_json)
                print(f"نتایج در {args.export_json} ذخیره شد")

            if args.export_csv:
                DataFormatter.export_to_csv(results, args.export_csv)
                print(f"نتایج در {args.export_csv} ذخیره شد")

        if args.meaning:
            search_engine = SearchEngine(dictionary)
            results = search_engine.search_meaning(args.meaning, args.category)
            output = DataFormatter.format_search_results(results)
            print(output)

            if args.export_json:
                DataFormatter.export_to_json(results, args.export_json)
                print(f"نتایج در {args.export_json} ذخیره شد")

            if args.export_csv:
                DataFormatter.export_to_csv(results, args.export_csv)
                print(f"نتایج در {args.export_csv} ذخیره شد")

        if args.random:
            random_gen = RandomWordGenerator(dictionary)
            words = random_gen.get_random_words(args.random, args.category)

            print(f"{args.random} کلمه تصادفی:")
            for i, word in enumerate(words, 1):
                print(f"{i}. {word.english_word} - {', '.join(word.meanings)}")

            if args.export_json:
                DataFormatter.export_to_json(words, args.export_json)
                print(f"نتایج در {args.export_json} ذخیره شد")

            if args.export_csv:
                DataFormatter.export_to_csv(words, args.export_csv)
                print(f"نتایج در {args.export_csv} ذخیره شد")

        # اگر هیچ آرگومانی ارائه نشده باشد
        if not any(vars(args).values()):
            parser.print_help()

    except Exception as e:
        print(f"خطا: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main()
