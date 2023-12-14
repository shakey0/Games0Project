import requests
import os


def get_api_questions_from_ninja(url):
    API_KEY = os.environ.get('API_KEY')
    response = requests.get(url, headers={'X-Api-Key': API_KEY})
    if response.status_code == requests.codes.ok:
        print(response.text)
        return response.text
    else:
        print("Error:", response.status_code, response.text)
        return None


def get_api_questions_from_trivia(url):
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        print(response.text)
        return response.text
    else:
        print("Error:", response.status_code, response.text)
        return None
    
# get_api_questions_from_trivia('https://the-trivia-api.com/api/questions?limit=30&categories=society_and_culture&difficulty=medium')