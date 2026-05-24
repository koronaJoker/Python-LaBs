from flask import Blueprint, flash, redirect, render_template, request, url_for
from auth import admin_required, login_required
from models import (
    create_product,
    delete_product,
    get_categories,
    get_category_statistics,
    get_db,
    get_inventory_summary,
    get_price_bounds,
    get_product,
    get_products,
    get_products_by_ids,
    resolve_category,
    update_product,
)
from utils import validate_csrf_token

products_bp = Blueprint("products", __name__)


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


@products_bp.route("/")
def index():
    return render_template("index.html")


@products_bp.route("/items")
@products_bp.route("/products")
def products():
    category_id = request.args.get("category_id", type=int)
    sort = request.args.get("sort", "new")
    search = request.args.get("search", "").strip()
    # price filters from query params
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")
    products = get_products(
        category_id=category_id,
        sort=sort,
        search=search or None,
        min_price=price_min,
        max_price=price_max,
    )
    # bounds for slider UI
    price_bounds = get_price_bounds()
    return render_template(
        "products.html",
        products=products,
        categories=get_categories(),
        selected_category=category_id,
        sort=sort,
        search=search,
        price_min=price_min,
        price_max=price_max,
        price_bounds=price_bounds,
    )


@products_bp.route("/items/<int:product_id>")
@products_bp.route("/products/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    if product is None:
        return render_template("404.html"), 404
    return render_template("product_detail.html", product=product)


@products_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        if not validate_csrf_token(request.form.get("csrf_token")):
            flash("Ошибка безопасности. Попробуйте снова.", "error")
            return redirect(url_for("products.add_product"))

        data = validate_product_form(request.form)
        if data["errors"]:
            for error in data["errors"]:
                flash(error, "error")
        else:
            conn = get_db()
            category_id = resolve_category(
                conn,
                data["category_id"],
                data["new_category"],
            )
            create_product(data["name"], data["price"], data["stock"], category_id)
            flash("Товар успешно добавлен.", "success")
            return redirect(url_for("products.products"))

    form_data = {
        "name": request.form.get("name", ""),
        "price": request.form.get("price", ""),
        "stock": request.form.get("stock", ""),
        "category_id": request.form.get("category_id", ""),
        "new_category": request.form.get("new_category", ""),
    }
    return render_template("product_form.html", categories=get_categories(), product=None, form_data=form_data)


@products_bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = get_product(product_id)
    if product is None:
        return render_template("404.html"), 404

    if request.method == "POST":
        if not validate_csrf_token(request.form.get("csrf_token")):
            flash("Ошибка безопасности. Попробуйте снова.", "error")
            return redirect(url_for("products.edit_product", product_id=product_id))

        data = validate_product_form(request.form)
        if data["errors"]:
            for error in data["errors"]:
                flash(error, "error")
        else:
            conn = get_db()
            category_id = resolve_category(
                conn,
                data["category_id"],
                data["new_category"],
            )
            update_product(product_id, data["name"], data["price"], data["stock"], category_id)
            flash("Товар обновлен.", "success")
            return redirect(url_for("products.product_detail", product_id=product_id))

    form_data = {
        "name": request.form.get("name", product["name"]),
        "price": request.form.get("price", product["price"]),
        "stock": request.form.get("stock", product["stock"]),
        "category_id": request.form.get("category_id", product["category_id"] or ""),
        "new_category": request.form.get("new_category", ""),
    }
    return render_template("product_form.html", categories=get_categories(), product=product, form_data=form_data)


@products_bp.route("/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product_route(product_id):
    product = get_product(product_id)
    if product is None:
        return render_template("404.html"), 404
    delete_product(product_id)
    flash("Товар удален.", "success")
    return redirect(url_for("products.products"))


@products_bp.route("/stats")
@login_required
def stats():
    summary = get_inventory_summary()
    by_category = get_category_statistics()
    return render_template("stats.html", summary=summary, by_category=by_category)
