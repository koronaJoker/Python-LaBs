from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for, g
from auth import login_required
from models import create_order, get_product, get_products_by_ids
from utils import cart_response, get_cart_from_request, validate_csrf_token

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart")
@login_required
def view_cart():
    cart = get_cart_from_request()
    products = get_products_by_ids(list(cart.keys()))
    cart_items = []
    total = 0

    for product in products:
        quantity = cart.get(product["id"], 0)
        subtotal = quantity * product["price"]
        total += subtotal
        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render_template("cart.html", cart_items=cart_items, total=total)


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Ошибка безопасности. Попробуйте снова.", "error")
        return redirect(request.referrer or url_for("products.products"))

    product = get_product(product_id)
    if product is None:
        flash("Товар не найден.", "error")
        return redirect(request.referrer or url_for("products.products"))

    try:
        quantity = max(1, int(request.form.get("quantity", 1)))
    except ValueError:
        quantity = 1

    cart = get_cart_from_request()
    current_quantity = cart.get(product_id, 0)
    if current_quantity + quantity > product["stock"]:
        flash("Нельзя добавить в корзину больше, чем есть на складе.", "error")
        return redirect(request.referrer or url_for("products.products"))

    cart[product_id] = current_quantity + quantity
    response = make_response(redirect(request.referrer or url_for("products.products")))
    return cart_response(response, cart)


@cart_bp.route("/cart/update", methods=["POST"])
def update_cart():
    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Ошибка безопасности. Попробуйте снова.", "error")
        return redirect(url_for("cart.view_cart"))

    product_id = request.form.get("product_id", type=int)
    if product_id is None:
        flash("Неверный товар для обновления.", "error")
        return redirect(url_for("cart.view_cart"))

    product = get_product(product_id)
    if product is None:
        flash("Товар не найден.", "error")
        return redirect(url_for("cart.view_cart"))

    try:
        quantity = int(request.form.get("quantity", 0))
    except ValueError:
        quantity = 0

    cart = get_cart_from_request()
    if quantity <= 0:
        cart.pop(product_id, None)
    elif quantity > product["stock"]:
        flash("Нельзя заказать больше, чем есть на складе.", "error")
        return redirect(url_for("cart.view_cart"))
    else:
        cart[product_id] = quantity

    response = make_response(redirect(url_for("cart.view_cart")))
    return cart_response(response, cart)


@cart_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Ошибка безопасности. Попробуйте снова.", "error")
        return redirect(url_for("cart.view_cart"))

    cart = get_cart_from_request()
    cart.pop(product_id, None)
    response = make_response(redirect(url_for("cart.view_cart")))
    return cart_response(response, cart)


@cart_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Ошибка безопасности. Попробуйте снова.", "error")
        return redirect(url_for("cart.view_cart"))

    cart = get_cart_from_request()
    if not cart:
        flash("Корзина пуста.", "error")
        return redirect(url_for("cart.view_cart"))

    products = get_products_by_ids(list(cart.keys()))
    errors = []
    for product in products:
        quantity = cart.get(product["id"], 0)
        if quantity > product["stock"]:
            errors.append(f"Товар '{product['name']}' доступен только в количестве {product['stock']}.")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("cart.view_cart"))

    create_order(g.user["id"], cart)
    flash("Заказ оформлен. Спасибо!", "success")
    response = make_response(redirect(url_for("products.products")))
    return cart_response(response, {})
