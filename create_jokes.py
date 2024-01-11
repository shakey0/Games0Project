import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
import csv


def get_last_id():
    with open('Games0App/static/jokes.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        last_id = 0
        for row in reader:
            if row[0].isdigit():
                last_id = int(row[0])
    return last_id

last_id = get_last_id()
print("Last ID:", last_id)
write_questions = input("Do you want to write questions to the CSV? (y/n) ")
if write_questions.lower() == 'y':
    API_KEY = os.environ.get('NINJA_API_KEY')
    # response = requests.get("https://api.api-ninjas.com/v1/jokes?limit=30", headers={'X-Api-Key': API_KEY})
    response = requests.get('https://official-joke-api.appspot.com/jokes/ten', headers={'X-Api-Key': API_KEY})
    response = json.loads(response.text)
    print(response)

    for item in response:
        os.system('clear')
        # if len(item['joke']) > 100 or '?' not in item['joke'] or len(item['joke'].split('? ')) < 2:
        #     continue
        # joke_question = item['joke'].split('? ')[0] + '?'
        # joke_answer = item['joke'].split('? ')[1]
        joke_question = item['setup']
        joke_answer = item['punchline']
        is_okay = input(f"Is this joke okay? (y/n)\nJOKE QUESTION: {joke_question}\nJOKE ANSWER: {joke_answer}\n")
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
        joke_to_add = {"id": supposed_id, "joke": joke_question, "answer": joke_answer, "blanks": blank_words}
        os.system('clear')
        print("FINAL JOKE:", joke_to_add)
        abandon = False
        while True:
            is_okay = input("Add joke to CSV? (y/n) ")
            if is_okay.lower() == 'y':
                break
            elif is_okay.lower() == 'n':
                abandon = True
                break
        if not abandon:
            last_id += 1
            output_file_path = 'Games0App/static/jokes.csv'
            with open(output_file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow([str(joke_to_add["id"]), joke_to_add['joke'], joke_to_add['answer'],
                                ', '.join(joke_to_add['blanks'])])
            print("Joke added to CSV.")