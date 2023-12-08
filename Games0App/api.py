import requests
import os

def get_api_questions(url):
    API_KEY = os.environ.get('API_KEY')
    response = requests.get(url, headers={'X-Api-Key': API_KEY})
    if response.status_code == requests.codes.ok:
        print(response.text)
        return response.text
    else:
        print("Error:", response.status_code, response.text)
        return None
