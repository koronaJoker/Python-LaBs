import sqlite3
from datetime import datetime
from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        conn.row_factory = sqlite3.Row
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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
        )

        product_columns = {row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()}
        if "created_at" not in product_columns:
            conn.execute("ALTER TABLE products ADD COLUMN created_at TEXT")
            conn.execute(
                "UPDATE products SET created_at = ? WHERE created_at IS NULL",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),),
            )

        for category in ("Сладости", "Напитки", "Выпечка", "Фрукты"):
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))

        admin_username = current_app.config["ADMIN_USERNAME"]
        admin_password = current_app.config["ADMIN_PASSWORD"]
        if admin_username and admin_password:
            existing_admin = conn.execute(
                "SELECT id FROM users WHERE username = ?", (admin_username,)
            ).fetchone()
            if existing_admin is None:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                    (admin_username, generate_password_hash(admin_password)),
                )

        conn.commit()


def get_categories():
    conn = get_db()
    return conn.execute("SELECT * FROM categories ORDER BY name").fetchall()


def resolve_category(conn, category_id, new_category):
    if new_category:
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (new_category,))
        row = conn.execute("SELECT id FROM categories WHERE name = ?", (new_category,)).fetchone()
        return row["id"]
    return category_id


def get_products(category_id=None, sort="new", search=None, min_price=None, max_price=None):
    order_by = {
        "new": "p.created_at DESC",
        "name": "p.name ASC",
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "stock": "p.stock DESC",
    }
    query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
    """
    conditions = []
    params = []
    if category_id:
        conditions.append("p.category_id = ?")
        params.append(category_id)
    if search:
        conditions.append("LOWER(p.name) LIKE ?")
        params.append(f"%{search.lower()}%")
    if min_price is not None:
        try:
            min_price_val = float(min_price)
            conditions.append("p.price >= ?")
            params.append(min_price_val)
        except (ValueError, TypeError):
            pass
    if max_price is not None:
        try:
            max_price_val = float(max_price)
            conditions.append("p.price <= ?")
            params.append(max_price_val)
        except (ValueError, TypeError):
            pass
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY {order_by.get(sort, 'p.created_at DESC')}"
    conn = get_db()
    return conn.execute(query, params).fetchall()


def get_price_bounds():
    conn = get_db()
    row = conn.execute("SELECT COALESCE(MIN(price), 0) AS min_price, COALESCE(MAX(price), 0) AS max_price FROM products").fetchone()
    return row["min_price"], row["max_price"]


def get_product(product_id):
    conn = get_db()
    return conn.execute(
        """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.id = ?
        """,
        (product_id,),
    ).fetchone()


def get_products_by_ids(product_ids):
    if not product_ids:
        return []
    placeholders = ",".join("?" for _ in product_ids)
    conn = get_db()
    return conn.execute(
        f"SELECT * FROM products WHERE id IN ({placeholders}) ORDER BY name",
        tuple(product_ids),
    ).fetchall()


def create_product(name, price, stock, category_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO products (name, price, stock, category_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, price, stock, category_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()


def update_product(product_id, name, price, stock, category_id):
    conn = get_db()
    conn.execute(
        "UPDATE products SET name = ?, price = ?, stock = ?, category_id = ? WHERE id = ?",
        (name, price, stock, category_id, product_id),
    )
    conn.commit()


def delete_product(product_id):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()


def get_user_by_username(username):
    conn = get_db()
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id):
    conn = get_db()
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(username, password, role="user"):
    conn = get_db()
    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    conn.commit()


def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def create_order(user_id, cart):
    conn = get_db()
    products = get_products_by_ids(list(cart.keys()))
    total = 0
    for product in products:
        quantity = cart.get(product["id"], 0)
        total += product["price"] * quantity

    cursor = conn.execute(
        "INSERT INTO orders (user_id, created_at, total) VALUES (?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total),
    )
    order_id = cursor.lastrowid
    for product in products:
        quantity = cart.get(product["id"], 0)
        conn.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, product["id"], quantity, product["price"]),
        )
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product["id"]),
        )
    conn.commit()
    return order_id


def get_inventory_summary():
    conn = get_db()
    return conn.execute(
        """
        SELECT
            COUNT(*) AS total_products,
            COALESCE(SUM(stock), 0) AS total_stock,
            COALESCE(AVG(price), 0) AS avg_price,
            COALESCE(SUM(price * stock), 0) AS inventory_value
        FROM products
        """
    ).fetchone()


def get_category_statistics():
    conn = get_db()
    return conn.execute(
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
