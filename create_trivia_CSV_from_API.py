import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
import csv


def get_last_id(word):
    with open(f'Games0App/static/quiz_data/trivia_madness.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        last_id = 0
        for row in reader:
            if row[0].isdigit():
                last_id = int(row[0])
    return last_id