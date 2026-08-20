from flask import Flask, request, redirect
import sqlite3
import string
import random

app = Flask(__name__)

DATABASE = "urls.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def generate_short_code():
    characters = string.ascii_letters + string.digits

    while True:
        short_code = ''.join(
            random.choice(characters)
            for _ in range(6)
        )

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM urls WHERE short_code = ?",
            (short_code,)
        )

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return short_code


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        original_url = request.form["url"]

        short_code = generate_short_code()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO urls (original_url, short_code)
            VALUES (?, ?)
            """,
            (original_url, short_code)
        )

        conn.commit()
        conn.close()

        short_url = request.host_url + short_code

        return f"""
        <html>
        <head>
            <title>URL Shortener</title>
        </head>

        <body style="font-family: Arial; text-align: center; margin-top: 100px;">

            <h1>URL Shortener</h1>

            <p>Your shortened URL is:</p>

            <a href="{short_url}" target="_blank">
                {short_url}
            </a>

            <br><br>

            <a href="/">Shorten another URL</a>

        </body>
        </html>
        """

    return """
    <html>
    <head>
        <title>URL Shortener</title>
    </head>

    <body style="font-family: Arial; text-align: center; margin-top: 100px;">

        <h1>URL Shortener</h1>

        <p>Enter a long URL to create a short link.</p>

        <form method="POST">

            <input
                type="url"
                name="url"
                placeholder="Enter your long URL"
                required
                style="width: 400px; padding: 10px;"
            >

            <br><br>

            <button
                type="submit"
                style="padding: 10px 20px;"
            >
                Shorten URL
            </button>

        </form>

    </body>
    </html>
    """


@app.route("/<short_code>")
def redirect_url(short_code):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)