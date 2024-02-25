from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import redis


db = SQLAlchemy()
migrate = Migrate()

production = os.environ.get('FLASK_ENV', 'development')
if production == 'production' or production == 'testing_in_actions':
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)


def count_words(s):
    if len(s.split()) == 1:
        return str(len(s.split())) + " word"
    return str(len(s.split())) + " words"


def format_date(date_str):
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    month, day = date_str.split('-')
    def get_day_suffix(day):
        if day in ("11", "12", "13"):
            return "th"
        elif day[-1] == "1":
            return "st"
        elif day[-1] == "2":
            return "nd"
        elif day[-1] == "3":
            return "rd"
        return "th"
    day_formatted = str(int(day)) + get_day_suffix(day)
    return f"{months[month]} {day_formatted}"
