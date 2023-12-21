import requests
import os


def get_api_questions_from_ninjas(url):
    API_KEY = os.environ.get('NINJA_API_KEY')
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


# def get_trivia_questions(amount=10, category=None, difficulty=None, type='boolean'):
#     url = "https://opentdb.com/api.php"
#     params = {
#         'amount': amount,
#         'type': type
#     }
#     if category:
#         params['category'] = category
#     if difficulty:
#         params['difficulty'] = difficulty

#     print("Sending request to:", url)
#     response = requests.get(url, params=params)
#     print(response)
#     if response.status_code == requests.codes.ok:
#         print(response.text)
#         return response.json()
#     else:
#         print("Error:", response.status_code, response.text)
#         return None
    
# get_trivia_questions()
