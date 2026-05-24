import json
import secrets
from flask import request, make_response, session


def parse_cart_cookie(cookie_value):
    if not cookie_value:
        return {}
    try:
        raw = json.loads(cookie_value)
    except (ValueError, TypeError):
        return {}
    cart = {}
    for product_id, quantity in raw.items():
        try:
            cart[int(product_id)] = max(0, int(quantity))
        except (ValueError, TypeError):
            continue
    return {product_id: quantity for product_id, quantity in cart.items() if quantity > 0}


def get_cart_from_request():
    return parse_cart_cookie(request.cookies.get("cart"))


def cart_response(response, cart):
    if cart:
        response.set_cookie(
            "cart",
            json.dumps(cart),
            max_age=30 * 24 * 60 * 60,
            httponly=True,
            samesite="Lax",
        )
    else:
        response.delete_cookie("cart")
    return response


def get_cart_item_count():
    cart = parse_cart_cookie(request.cookies.get("cart"))
    return sum(cart.values())


def generate_csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(16)
        session["csrf_token"] = token
    return token


def validate_csrf_token(token):
    return bool(token and token == session.get("csrf_token"))
