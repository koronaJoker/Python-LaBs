import pandas as pd
import random
import math

SPEED = 60

#connect
df = pd.read_csv('orders.csv')

cols = ["id", "price", "weight", "count", "discount"]
df[cols] = df[cols].apply(pd.to_numeric, errors = "coerce")

df = df.dropna(subset = cols)
df = df.fillna("Unknown")

df = df[df["price"] >= 0]

df = df[
    (df["discount"] >= 0)
    & (df["discount"] <= 100)
    & (~df["discount"].apply(math.isnan))
]



# new_file for new records
df["amount"] = df["count"] * df["price"]
df["total"] = df["amount"] + (df["distance"] * 100) * df["discount"] / 100 + df["weight"]*df["count"]*5

df["success"] = df["id"].apply(lambda x: random.choice([True, False]))

df["aprx_time"] = SPEED / df["distance"] 


total_income = math.fsum(df[df["returned"]==False]["total"])
mean_income_by_category = df.groupby("category")["price"].agg(["sum", "mean", "count"])
correlation = df["total"].corr(df["discount"])
level_of_return = df["returned"].mean() * 100 # len(returned)/len(total)
df["permutations"] = df["name"].apply(
    lambda x: math.factorial(len(str(x)))
)
top_5 = df.sort_values(by="count",ascending=False).head(5)


strength = math.fabs(correlation)

if strength >= 0.7:
    level = "Сильная"
elif strength >= 0.5:
    level = "Выше среднего"
elif strength >= 0.3:
    level = "Средняя"
elif strength > 0:
    level = "Слабая"
else:
    level = "Отсутствует"

if correlation > 0:
    direction = "прямая"
elif correlation < 0:
    direction = "обратная"
else:
    direction = ""

result = f"{direction} {level} корреляция".strip()

df.to_csv("handled_orders.csv", index = False)

 