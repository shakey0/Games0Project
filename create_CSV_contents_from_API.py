import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
import csv


def get_last_id(word):
    with open(f'Games0App/static/{word}s.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        last_id = 0
        for row in reader:
            if row[0].isdigit():
                last_id = int(row[0])
    return last_id

print("1. Add jokes from API Ninjas to CSV")
print("2. Add jokes from Official Joke API to CSV")
print("3. Add facts from API Ninjas to CSV")
write_questions = input("Choose the number of your CSV and API: ")
if write_questions == '1':
    api = 'https://api.api-ninjas.com/v1/jokes?limit=30'
    word = 'joke'
elif write_questions == '2':
    api = 'https://official-joke-api.appspot.com/jokes/ten'
    word = 'joke'
elif write_questions == '3':
    api = 'https://api.api-ninjas.com/v1/facts?limit=30'
    word = 'fact'
else:
    print("Invalid input.")
    exit()

last_id = get_last_id(word)
API_KEY = os.environ.get('NINJA_API_KEY')
if write_questions == '1':
    response = requests.get("https://api.api-ninjas.com/v1/jokes?limit=30", headers={'X-Api-Key': API_KEY})
elif write_questions == '2':
    response = requests.get('https://official-joke-api.appspot.com/jokes/ten')
elif write_questions == '3':
    response = requests.get('https://api.api-ninjas.com/v1/facts?limit=30', headers={'X-Api-Key': API_KEY})
response = json.loads(response.text)
print(response)

for item in response:
    os.system('clear')
    if write_questions == '1':
        if len(item['joke']) > 100 or '?' not in item['joke'] or len(item['joke'].split('? ')) < 2:
            continue
        main_part = item['joke'].split('? ')[0] + '?'
        answer_part = item['joke'].split('? ')[1]
    elif write_questions == '2':
        main_part = item['setup']
        answer_part = item['punchline']
    elif write_questions == '3':
        if len(item['fact']) > 100:
            continue
        main_part = item['fact']
        answer_part = 'NONE'
    is_okay = input(f"Is this {word} okay? (y/n)\n{word.upper()} QUESTION: {main_part}\n{word.upper()} ANSWER: {answer_part}\n")
    if is_okay.lower() == 'y':
        blank_words = []
        while True:
            print('Blank words so far:', blank_words)
            blank_word = input("Enter a word that can be a blank or Q to stop adding: ")
            if blank_word.lower() == 'q':
                break
            elif len(blank_word) >= 3:
                blank_words.append(blank_word)
            else:
                print("Word too short.")
    else:
        continue
    supposed_id = last_id + 1
    if word == 'joke':
        entry_to_add = {"id": supposed_id, "joke": main_part, "answer": answer_part, "blanks": blank_words}
    elif word == 'fact':
        entry_to_add = {"id": supposed_id, "fact": main_part, "blanks": blank_words}
    os.system('clear')
    print(f"FINAL {word.upper()}:", entry_to_add)
    abandon = False
    while True:
        is_okay = input(f"Add {word} to CSV? (y/n) ")
        if is_okay.lower() == 'y':
            break
        elif is_okay.lower() == 'n':
            abandon = True
            break
    if not abandon:
        last_id += 1
        if word == 'joke':
            output_file_path = 'Games0App/static/jokes.csv'
        elif word == 'fact':
            output_file_path = 'Games0App/static/facts.csv'
        with open(output_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            if word == 'joke':
                writer.writerow([str(entry_to_add["id"]), entry_to_add['joke'], entry_to_add['answer'],
                                ', '.join(entry_to_add['blanks'])])
            elif word == 'fact':
                writer.writerow([str(entry_to_add["id"]), entry_to_add['fact'], ', '.join(entry_to_add['blanks'])])
        print("Joke added to CSV.")