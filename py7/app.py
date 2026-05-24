from datetime import datetime
from pathlib import Path
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "lab7-secret-key"

DB_NAME = "database.db"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / DB_NAME


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0,
                category_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            """
        )

        product_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(products)").fetchall()
        }
        if "created_at" not in product_columns:
            conn.execute("ALTER TABLE products ADD COLUMN created_at TEXT")
            conn.execute(
                "UPDATE products SET created_at = ? WHERE created_at IS NULL",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),),
            )

        for category in ("Сладости", "Напитки", "Выпечка", "Фрукты"):
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        conn.commit()


def get_categories():
    with get_db() as conn:
        return conn.execute("SELECT * FROM categories ORDER BY name").fetchall()


def validate_product_form(form):
    errors = []
    name = form.get("name", "").strip()
    price_raw = form.get("price", "").strip()
    stock_raw = form.get("stock", "").strip()
    category_id_raw = form.get("category_id", "").strip()
    new_category = form.get("new_category", "").strip()

    if not name:
        errors.append("Название товара не может быть пустым.")
    elif len(name) < 2:
        errors.append("Название должно содержать минимум 2 символа.")

    try:
        price = float(price_raw)
        if price < 0:
            errors.append("Цена не может быть отрицательной.")
    except ValueError:
        price = None
        errors.append("Цена должна быть числом.")

    try:
        stock = int(stock_raw)
        if stock < 0:
            errors.append("Количество не может быть отрицательным.")
    except ValueError:
        stock = None
        errors.append("Количество должно быть целым числом.")

    category_id = None
    if category_id_raw:
        try:
            category_id = int(category_id_raw)
        except ValueError:
            errors.append("Категория выбрана некорректно.")

    if new_category and len(new_category) < 2:
        errors.append("Название новой категории должно содержать минимум 2 символа.")

    return {
        "errors": errors,
        "name": name,
        "price": price,
        "stock": stock,
        "category_id": category_id,
        "new_category": new_category,
    }


def resolve_category(conn, category_id, new_category):
    if new_category:
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (new_category,))
        row = conn.execute(
            "SELECT id FROM categories WHERE name = ?",
            (new_category,),
        ).fetchone()
        return row["id"]
    return category_id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/items")
@app.route("/products")
def products():
    category_id = request.args.get("category_id", type=int)
    sort = request.args.get("sort", "new")
    order_by = {
        "new": "p.created_at DESC",
        "name": "p.name ASC",
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "stock": "p.stock DESC",
    }.get(sort, "p.created_at DESC")

    query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
    """
    params = []
    if category_id:
        query += " WHERE p.category_id = ?"
        params.append(category_id)
    query += f" ORDER BY {order_by}"

    with get_db() as conn:
        items = conn.execute(query, params).fetchall()

    return render_template(
        "products.html",
        products=items,
        categories=get_categories(),
        selected_category=category_id,
        sort=sort,
    )


@app.route("/items/<int:product_id>")
@app.route("/products/<int:product_id>")
def product_detail(product_id):
    with get_db() as conn:
        product = conn.execute(
            """
            SELECT p.*, c.name AS category_name
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (product_id,),
        ).fetchone()

    if product is None:
        return render_template("404.html"), 404
    return render_template("product_detail.html", product=product)


@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        data = validate_product_form(request.form)
        if data["errors"]:
            for error in data["errors"]:
                flash(error, "error")
        else:
            with get_db() as conn:
                category_id = resolve_category(
                    conn,
                    data["category_id"],
                    data["new_category"],
                )
                conn.execute(
                    """
                    INSERT INTO products (name, price, stock, category_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        data["name"],
                        data["price"],
                        data["stock"],
                        category_id,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()
            flash("Товар успешно добавлен.", "success")
            return redirect(url_for("products"))

    return render_template("product_form.html", categories=get_categories(), product=None)


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    with get_db() as conn:
        product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if product is None:
        return render_template("404.html"), 404

    if request.method == "POST":
        data = validate_product_form(request.form)
        if data["errors"]:
            for error in data["errors"]:
                flash(error, "error")
        else:
            with get_db() as conn:
                category_id = resolve_category(
                    conn,
                    data["category_id"],
                    data["new_category"],
                )
                conn.execute(
                    """
                    UPDATE products
                    SET name = ?, price = ?, stock = ?, category_id = ?
                    WHERE id = ?
                    """,
                    (
                        data["name"],
                        data["price"],
                        data["stock"],
                        category_id,
                        product_id,
                    ),
                )
                conn.commit()
            flash("Товар обновлен.", "success")
            return redirect(url_for("product_detail", product_id=product_id))

    return render_template(
        "product_form.html",
        categories=get_categories(),
        product=product,
    )


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    flash("Товар удален.", "success")
    return redirect(url_for("products"))


@app.route("/stats")
def stats():
    with get_db() as conn:
        summary = conn.execute(
            """
            SELECT
                COUNT(*) AS total_products,
                COALESCE(SUM(stock), 0) AS total_stock,
                COALESCE(AVG(price), 0) AS avg_price,
                COALESCE(SUM(price * stock), 0) AS inventory_value
            FROM products
            """
        ).fetchone()
        by_category = conn.execute(
            """
            SELECT
                COALESCE(c.name, 'Без категории') AS category_name,
                COUNT(p.id) AS product_count,
                COALESCE(SUM(p.stock), 0) AS stock_count
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            GROUP BY c.id, c.name
            ORDER BY product_count DESC, category_name ASC
            """
        ).fetchall()

    return render_template("stats.html", summary=summary, by_category=by_category)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


init_db()


if __name__ == "__main__":
    app.run(debug=True)
