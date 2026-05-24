from functools import wraps
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from models import create_user, get_user_by_id, get_user_by_username, verify_user
from utils import generate_csrf_token, get_cart_item_count, validate_csrf_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)


@auth_bp.app_context_processor
def inject_user():
    return {
        "current_user": g.get("user"),
        "cart_item_count": get_cart_item_count(),
        "csrf_token": generate_csrf_token(),
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Пожалуйста, войдите в систему, чтобы продолжить.", "error")
            return redirect(url_for("products.products"))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Только администратор может перейти к этому разделу.", "error")
            return redirect(url_for("products.products"))
        if g.user["role"] != "admin":
            flash("У вас нет прав администратора.", "error")
            return redirect(url_for("products.products"))
        return view(*args, **kwargs)
    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not validate_csrf_token(request.form.get("csrf_token")):
            flash("Ошибка безопасности. Попробуйте снова.", "error")
            return redirect(url_for("auth.register"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        errors = []

        if len(username) < 3:
            errors.append("Имя пользователя должно содержать как минимум 3 символа.")
        if len(password) < 6:
            errors.append("Пароль должен быть не менее 6 символов.")
        if password != confirm:
            errors.append("Пароли не совпадают.")
        if get_user_by_username(username):
            errors.append("Пользователь с таким именем уже существует.")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("auth.register"))

        create_user(username, password, role="user")
        flash("Регистрация прошла успешно. Войдите в систему.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not validate_csrf_token(request.form.get("csrf_token")):
            flash("Ошибка безопасности. Попробуйте снова.", "error")
            return redirect(url_for("auth.login"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = verify_user(username, password)
        if user is None:
            flash("Неверное имя пользователя или пароль.", "error")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user["id"]
        next_page = request.args.get("next") or url_for("products.products")
        flash(f"Добро пожаловать, {user['username']}!", "success")
        return redirect(next_page)

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("products.products"))
