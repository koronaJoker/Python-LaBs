from datetime import datetime
import calendar
import re


days_in_russian = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]
def validate_data(date):
    pattern = r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    if (not re.match(pattern, date)):
        return False

    try:
        datetime.strptime(date, r"%Y-%m-%d")
    except ValueError:
        return False

    return True

def get_data(date_text):
    date = datetime.strptime(date_text, r"%Y-%m-%d")
    date_in_days = (datetime.now() - date).days
    day_of_week = days_in_russian[calendar.weekday(date.year, date.month, date.day)]
    return [date_text, date_in_days, day_of_week]

        
    









