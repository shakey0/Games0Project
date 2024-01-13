import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
import html
import csv


def get_last_id():
    with open(f'Games0App/static/quiz_data/trivia_madness.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        last_id = 0
        for row in reader:
            if row[0].isdigit():
                last_id = int(row[0])
    return last_id

print("1. Add jokes from API Ninjas to CSV")
write_questions = input("Choose the number of your CSV and API: ")
if write_questions == '1':
    api = 'https://opentdb.com/api.php?amount=50&type=multiple'
else:
    print("Invalid input.")
    exit()

last_id = get_last_id()
if write_questions == '1':
    response = requests.get(api)
response = json.loads(response.text)
print(response)

for item in response["results"]:

    os.system('clear')

    category = html.unescape(item['category'].lower())
    if not category:
        category = 'all'
    if ": " in category:
        category = category.split(": ")[1]
    if " & " in category:
        category = category.replace(" & ", "_and_")
    if " " in category:
        category = category.replace(" ", "_")
    question = html.unescape(item['question'].strip())
    answer = item['correct_answer'].strip()
    
    other_answers = []
    while True:
        print('CATEGORY:', category)
        print('QUESTION:', question)
        print('ANSWER:', answer)
        print('OTHER ANSWERS:', other_answers)
        print()
        choice = input('Enter=add, A=edit_answer, Q=edit_question, Z=discard, O=add_other_answer: ')
        if choice.lower() == 'a':
            answer = input('Enter answer: ')
        elif choice.lower() == 'q':
            question = input('Enter question: ')
        elif choice.lower() == 'z' or choice == '':
            break
        elif choice.lower() == 'o':
            other_answer = input('Enter other answer: ')
            other_answers.append(other_answer)
    if choice.lower() == 'z':
        continue

    last_id += 1
    if not other_answers:
        other_answers = ['!']
    with open(f'Games0App/static/quiz_data/trivia_madness.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([last_id, category, question, answer, *other_answers])
