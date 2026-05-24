from orders import *

def build_txt_report(entered_date_of_birth, date_in_days, day_of_week):
    return f"""
Отчёт по данным даты рождения пользователя и заказам в магазине FIDESCO.

1. Дата пользователя

Пользователь указал дату: {entered_date_of_birth}
Это: {day_of_week}
С того дня прошло: {date_in_days} дней

2. Заказы

1. Общая сумма заказа: {total_income}

2. Средний доход по категориям:
{mean_income_by_category.to_string(index=False)}

3. Уровень возврата заказа:
{level_of_return}

4. Корреляция между скидкой и общей выручкой:
{correlation:.2f} ({direction}, {level})

5. Количество возможных перестановок в именах:
{df[['name', 'permutations']].to_string(index=False)}

Топ 5 товаров:
{top_5[['id', 'product', 'count', 'total']].to_string(index=False)}
"""

def make_txt_report(entered_date_of_birth, date_in_days, day_of_week):
    text = build_txt_report(entered_date_of_birth, date_in_days, day_of_week)
    with open("report.txt", "w", encoding="utf-8") as file:
        file.write(text)
    return text
