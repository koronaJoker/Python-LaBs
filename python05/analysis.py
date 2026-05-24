import math
import pandas as pd


def load_and_clean_orders(file_path: str):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Ошибка чтения CSV: {e}")

    required_columns = [
        "order_id",
        "product",
        "category",
        "price",
        "quantity",
        "discount",
        "status",
        "order_date",
        "distance_km"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            "В CSV отсутствуют обязательные столбцы:\n" + ", ".join(missing)
        )

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    df["product"] = df["product"].fillna("Неизвестный товар")
    df["category"] = df["category"].fillna("Без категории")
    df["status"] = df["status"].fillna("Unknown")
    df["discount"] = df["discount"].fillna(0)

    df = df.dropna(subset=["price", "quantity", "distance_km", "order_date"])

    df = df[df["price"] >= 0]
    df = df[df["quantity"] > 0]
    df = df[df["discount"] >= 0]
    df = df[df["discount"] <= 1]
    df = df[df["distance_km"] >= 0]

    df = df.drop_duplicates()

    return df


def add_calculated_columns(df: pd.DataFrame):
    df = df.copy()

    df["total_price"] = df["price"] * df["quantity"]
    df["final_price"] = df["total_price"] * (1 - df["discount"])
    df["is_successful"] = df["status"].astype(str).str.lower().isin(
        ["delivered", "completed", "success"]
    )

    return df


def analyze_data(df: pd.DataFrame):
    successful_df = df[df["is_successful"]]

    total_income = successful_df["final_price"].sum()

    income_by_category = (
        successful_df.groupby("category")["final_price"]
        .sum()
        .sort_values(ascending=False)
    )

    top_products = (
        df.groupby("product")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    return_rate = (df["status"].astype(str).str.lower() == "returned").mean() * 100
    success_rate = df["is_successful"].mean() * 100 if len(df) > 0 else 0

    return {
        "total_income": total_income,
        "income_by_category": income_by_category,
        "top_products": top_products,
        "return_rate": return_rate,
        "success_rate": success_rate,
        "orders_count": len(df)
    }


def extra_math_calculations(df: pd.DataFrame):
    valid_df = df.dropna(subset=["final_price", "distance_km"]).copy()

    if valid_df.empty:
        return {
            "avg_delivery_time": 0,
            "avg_delivery_cost": 0,
            "avg_value_index": 0,
            "avg_order": 0,
            "median_order": 0,
            "std_dev": 0,
            "variation_coeff": 0,
            "correlation_distance_price": 0
        }

    delivery_times = []
    delivery_costs = []
    value_indexes = []

    for _, row in valid_df.iterrows():
        distance = row["distance_km"]
        final_price = row["final_price"]

        if math.isnan(distance) or math.isnan(final_price):
            continue

        delivery_time = distance / 40
        delivery_cost = 5 + distance * 0.8
        value_index = math.sqrt(final_price) if final_price >= 0 else 0

        delivery_times.append(delivery_time)
        delivery_costs.append(delivery_cost)
        value_indexes.append(value_index)

    avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
    avg_delivery_cost = sum(delivery_costs) / len(delivery_costs) if delivery_costs else 0
    avg_value_index = sum(value_indexes) / len(value_indexes) if value_indexes else 0

    avg_order = valid_df["final_price"].mean()
    median_order = valid_df["final_price"].median()
    std_dev = valid_df["final_price"].std()

    if pd.isna(std_dev):
        std_dev = 0

    variation_coeff = std_dev / avg_order if avg_order != 0 else 0

    correlation_distance_price = valid_df["distance_km"].corr(valid_df["final_price"])
    if pd.isna(correlation_distance_price):
        correlation_distance_price = 0

    return {
        "avg_delivery_time": avg_delivery_time,
        "avg_delivery_cost": avg_delivery_cost,
        "avg_value_index": avg_value_index,
        "avg_order": avg_order,
        "median_order": median_order,
        "std_dev": std_dev,
        "variation_coeff": variation_coeff,
        "correlation_distance_price": correlation_distance_price
    }


def generate_report(user_date, birth_week_day, age_in_days, analysis, extra_results):
    category_text = ""
    if len(analysis["income_by_category"]) == 0:
        category_text = "Нет данных\n"
    else:
        for category, income in analysis["income_by_category"].items():
            category_text += f"- {category}: {income:.2f}\n"

    top_products_text = ""
    if len(analysis["top_products"]) == 0:
        top_products_text = "Нет данных\n"
    else:
        for i, (product, qty) in enumerate(analysis["top_products"].items(), start=1):
            top_products_text += f"{i}. {product} — {qty} шт.\n"

    report = f"""
ОТЧЁТ ПО АНАЛИЗУ ЗАКАЗОВ ИНТЕРНЕТ-МАГАЗИНА

1. ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
Дата рождения: {user_date}
День недели рождения: {birth_week_day}
Возраст в днях: {age_in_days}

2. ОСНОВНЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА
Количество заказов: {analysis["orders_count"]}
Общий доход: {analysis["total_income"]:.2f}
Уровень возвратов: {analysis["return_rate"]:.2f}%
Процент успешных заказов: {analysis["success_rate"]:.2f}%

Доход по категориям:
{category_text}

Топ-5 товаров:
{top_products_text}

3. ДОПОЛНИТЕЛЬНЫЕ МАТЕМАТИЧЕСКИЕ РАСЧЁТЫ
Среднее время доставки: {extra_results["avg_delivery_time"]:.2f} ч
Средняя стоимость доставки: {extra_results["avg_delivery_cost"]:.2f}
Средний индекс выгодности заказа: {extra_results["avg_value_index"]:.2f}

4. СТАТИСТИЧЕСКИЕ ПОКАЗАТЕЛИ
Средний чек: {extra_results["avg_order"]:.2f}
Медиана заказа: {extra_results["median_order"]:.2f}
Стандартное отклонение: {extra_results["std_dev"]:.2f}
Коэффициент вариации: {extra_results["variation_coeff"]:.2f}
Корреляция между расстоянием и стоимостью заказа: {extra_results["correlation_distance_price"]:.2f}

5. КРАТКИЕ ВЫВОДЫ
- Средний чек показывает среднюю стоимость одного заказа.
- Медиана показывает типичную стоимость заказа без сильного влияния выбросов.
- Стандартное отклонение характеризует разброс стоимости заказов.
- Коэффициент вариации показывает относительный разброс по сравнению со средним чеком.
- Корреляция помогает понять, существует ли связь между расстоянием доставки и стоимостью заказа.
""".strip()

    return report