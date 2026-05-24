import re
import calendar
from datetime import datetime
from gtts import gTTS


def validate_birth_date(user_date: str):
    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, user_date):
        raise ValueError("Неверный формат даты. Используй YYYY-MM-DD")

    birth_date = datetime.strptime(user_date, "%Y-%m-%d")

    if not (datetime(1900, 1, 1) <= birth_date <= datetime.now()):
        raise ValueError("Дата должна быть не раньше 1900-01-01 и не позже сегодняшнего дня")

    days = [
        "Понедельник", "Вторник", "Среда",
        "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]

    year, month, day = birth_date.year, birth_date.month, birth_date.day
    birth_week_day = days[calendar.weekday(year, month, day)]
    age_in_days = (datetime.now() - birth_date).days

    return birth_date, birth_week_day, age_in_days


def save_report_to_file(report_text: str, filename="report.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(report_text)


def save_report_to_mp3(report_text: str, lang="ru", filename="report.mp3"):
    if not report_text.strip():
        raise ValueError("Текст отчёта пустой, озвучивание невозможно")

    if lang not in ["ru", "en"]:
        raise ValueError("Поддерживаются только языки 'ru' и 'en'")

    try:
        tts = gTTS(text=report_text, lang=lang)
        tts.save(filename)
    except Exception as e:
        raise ValueError(f"Ошибка при создании mp3: {e}")