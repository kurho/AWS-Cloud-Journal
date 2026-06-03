from flask import Flask, request, redirect, render_template_string, flash, url_for
import pymysql
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-in-prod")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "cloudjournal")
S3_IMAGE_URL = os.getenv("S3_IMAGE_URL")

MAX_TITLE_LEN = 150
MAX_CONTENT_LEN = 5000


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        charset="utf8mb4",
    )


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Cloud Journal</title>
  <style>
    :root { --bg:#0f172a; --card:#1e293b; --accent:#38bdf8; --text:#e2e8f0; --muted:#94a3b8; }
    * { box-sizing: border-box; }
    body { margin:0; font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); }
    .wrap { max-width: 760px; margin: 0 auto; padding: 2rem 1rem; }
    h1 { margin:0 0 .25rem; font-size:2rem; }
    .lede { color:var(--muted); margin-top:0; }
    .hero { width:100%; max-height:280px; object-fit:cover; border-radius:12px; margin:1rem 0; }
    .card { background:var(--card); padding:1.25rem; border-radius:12px; margin-bottom:1rem; }
    h2 { margin-top:2rem; border-bottom:1px solid #334155; padding-bottom:.5rem; }
    label { display:block; margin:.75rem 0 .25rem; font-size:.9rem; color:var(--muted); }
    input, textarea { width:100%; padding:.6rem .75rem; border-radius:8px; border:1px solid #334155;
                       background:#0b1220; color:var(--text); font-size:1rem; font-family:inherit; }
    textarea { min-height:120px; resize:vertical; }
    button { margin-top:1rem; background:var(--accent); color:#0b1220; border:0; padding:.7rem 1.25rem;
             border-radius:8px; font-weight:600; cursor:pointer; }
    button:hover { filter:brightness(1.1); }
    .meta { color:var(--muted); font-size:.8rem; margin-top:.5rem; }
    .post-title { margin:0 0 .5rem; color:var(--accent); }
    .post-body { white-space:pre-wrap; margin:0; }
    .flash { padding:.6rem .9rem; border-radius:8px; margin-bottom:1rem; }
    .flash.error { background:#7f1d1d; }
    .flash.success { background:#14532d; }
    .empty { color:var(--muted); font-style:italic; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Cloud Journal</h1>
    <p class="lede">A portfolio project built with EC2, RDS, and S3 on AWS.</p>

    {% if image_url %}
      <img class="hero" src="{{ image_url }}" alt="Cloud Journal banner">
    {% endif %}

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, msg in messages %}
        <div class="flash {{ category }}">{{ msg }}</div>
      {% endfor %}
    {% endwith %}

    <div class="card">
      <h2 style="margin-top:0;border:0;padding:0;">Create Entry</h2>
      <form action="{{ url_for('submit') }}" method="post">
        <label for="title">Title</label>
        <input id="title" name="title" maxlength="{{ max_title }}" required>

        <label for="content">Content</label>
        <textarea id="content" name="content" maxlength="{{ max_content }}" required></textarea>

        <button type="submit">Publish</button>
      </form>
    </div>

    <h2>Journal Entries</h2>
    {% for post in posts %}
      <div class="card">
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-body">{{ post.content }}</p>
        <div class="meta">{{ post.created_at }}</div>
      </div>
    {% else %}
      <p class="empty">No entries yet — be the first to post.</p>
    {% endfor %}
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    posts = []
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT title, content, created_at FROM posts ORDER BY id DESC LIMIT 100"
            )
            posts = cursor.fetchall()
    except Exception as e:
        log.exception("DB read failed: %s", e)
        flash("Could not load entries right now.", "error")
    finally:
        if conn:
            conn.close()

    return render_template_string(
        HTML,
        posts=posts,
        image_url=S3_IMAGE_URL,
        max_title=MAX_TITLE_LEN,
        max_content=MAX_CONTENT_LEN,
    )


@app.route("/submit", methods=["POST"])
def submit():
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()

    if not title or not content:
        flash("Title and content are required.", "error")
        return redirect(url_for("index"))
    if len(title) > MAX_TITLE_LEN or len(content) > MAX_CONTENT_LEN:
        flash("Entry exceeds allowed length.", "error")
        return redirect(url_for("index"))

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO posts (title, content) VALUES (%s, %s)",
                (title, content),
            )
        conn.commit()
        flash("Entry published.", "success")
    except Exception as e:
        log.exception("DB write failed: %s", e)
        flash("Could not save your entry.", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("index"))


@app.route("/health")
def health():
    """Lightweight health check for ALB / target groups."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
