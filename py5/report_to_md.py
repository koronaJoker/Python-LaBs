from orders import *

def build_md_report(entered_date_of_birth, date_in_days, day_of_week):
    return f"""
# Отчёт по данным даты рождения пользователя и заказам в магазине FIDESCO.

## 1. Дата пользователя

Пользователь указал дату `{entered_date_of_birth}`, это `{day_of_week}`, с того дня прошло `{date_in_days}` дней.

## 2. Заказы

1. Общая сумма заказа : `{total_income}`
2. средний доход по категориям : 
```py
 {mean_income_by_category.to_string(index = False)}
 ```
3. Уровень возврата заказа : `{level_of_return}`
4. Корреляция между скидкой и общей выручкой : `{correlation:.2f}, ({direction, level})`
5. Количество возможных перестановок в именах: 
```py
{df[['name', 'permutations']]}
```

## Топ 5 товаров:
```py
{top_5[["id", "product", "count", "total"]].to_string(index = False)}
```
"""

def make_md_report(entered_date_of_birth, date_in_days, day_of_week):
    text = build_md_report(entered_date_of_birth, date_in_days, day_of_week)
    with open("report.md", "w" ,encoding="utf-8") as file:
        file.write(text)
    return text
