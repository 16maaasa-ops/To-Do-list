import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

import sheets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


@app.route("/")
def index():
    todos = sheets.get_all_todos()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        due_date = request.form["due_date"]
        if not title:
            flash("タイトルは必須です。", "error")
            return render_template("add.html")
        sheets.add_todo(title, content, due_date)
        flash("Todoを追加しました。", "success")
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/edit/<todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo, _ = sheets.get_todo(todo_id)
    if todo is None:
        flash("Todoが見つかりませんでした。", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        due_date = request.form["due_date"]
        if not title:
            flash("タイトルは必須です。", "error")
            return render_template("edit.html", todo=todo)
        sheets.update_todo(todo_id, title, content, due_date)
        flash("Todoを更新しました。", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", todo=todo)


@app.route("/toggle/<todo_id>", methods=["POST"])
def toggle(todo_id):
    sheets.toggle_status(todo_id)
    return redirect(url_for("index"))


@app.route("/delete/<todo_id>", methods=["POST"])
def delete(todo_id):
    sheets.delete_todo(todo_id)
    flash("Todoを削除しました。", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
