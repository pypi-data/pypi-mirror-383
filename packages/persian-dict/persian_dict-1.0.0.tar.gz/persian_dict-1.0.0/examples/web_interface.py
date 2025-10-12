from flask import Flask, render_template, request, jsonify
from persian_dict import (
    PersianDictionary,
    SearchEngine,
    RandomWordGenerator,
    DataFormatter,
)

app = Flask(__name__)

# بارگذاری دیکشنری
print("در حال بارگذاری دیکشنری...")
dictionary = PersianDictionary("data/ata")
search_engine = SearchEngine(dictionary)
random_gen = RandomWordGenerator(dictionary)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def search():
    word = request.args.get("word", "")
    category = request.args.get("category", "")

    if not word:
        return jsonify({"error": "کلمه برای جستجو وارد نشده"})

    results = search_engine.search_word(word, category if category else None)

    return jsonify(
        {"results": [word.to_dict() for word in results], "count": len(results)}
    )


@app.route("/api/random")
def random_words():
    count = int(request.args.get("count", 5))
    category = request.args.get("category", "")

    words = random_gen.get_random_words(count, category if category else None)

    return jsonify({"words": [word.to_dict() for word in words], "count": len(words)})


@app.route("/api/categories")
def categories():
    return jsonify({"categories": dictionary.get_categories()})


@app.route("/api/statistics")
def statistics():
    stats = dictionary.get_statistics()
    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True)
