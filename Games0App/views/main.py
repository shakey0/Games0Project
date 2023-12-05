from flask import Blueprint
from Games0App.extensions import db
from Games0App.models.user import User
from flask import render_template, request
import requests
import os
import random
import string

main = Blueprint('main', __name__)

class GamePlay:
    def __init__(self, name, intro_message, param="", api_variable=""):
        self.name = name
        lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
        self.image = lower_name + '.png'
        self.intro_message = intro_message
        self.param = param
        if api_variable == "trivia":
            self.api_url = 'https://api.api-ninjas.com/v1/trivia?category={}&limit=30'
        elif api_variable == "facts" or api_variable == "jokes":
            self.api_url = 'https://api.api-ninjas.com/v1/{}?limit=30'.format(api_variable)
        else:
            self.api_url = ""
        # self.api_url = 'https://api.api-ninjas.com/v1/trivia?category={}&limit=30'.format(self.variable.lower())
        self.question_numbers = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}
        self.question_number = 1
        self.current_question = ""
        self.current_answer = ""

    def update_question_number(self, number):
        self.question_number = self.question_numbers[number]

    def update_current_category(self, category):
        self.current_category = category

    def update_stored_questions(self):
        pass # CONTACT API AND STORE IN REDIS

    def get_question(self):
        # LOGIC TO GET QUESTION (+ANSWER) FROM REDIS
        self.current_question = "Question from Redis"
        self.current_answer = "Answer from Redis"
        return self.current_question
    
    def get_answer(self):
        return self.current_answer
    
        

games = [
    GamePlay("Fill in the Blank - Facts",
            "You will be given 10 facts and need to fill in the blank word for each one.",
            param="fill_blank_facts", api_variable="facts"),
    GamePlay("Fill in the Blank - Jokes",
            "You will be given 10 jokes and need to fill in the blank word for each one.",
            param="fill_blank_jokes", api_variable="jokes"),
    GamePlay("Trivia Madness - Choose Your Category",
            "You will be given 10 questions from your chosen category.",
            param="trivia_madness", api_variable="trivia"),
    GamePlay("Countries & Cultures - Multiple Choice",
            "You will be given 10 questions about countries and cultures and need to select the correct answer for each one.",
            param="countries_cultures_mc"),
    GamePlay("Countries & Cultures - True or False",
            "You will be given 10 questions about countries and cultures and need to select whether each statement is true or false.",
            param="countries_cultures_tf"),
    GamePlay("Number to Reach",
            "DIFFERENT MESSAGE",
            param="number_to_reach")
]

@main.route('/')
def index():
    
    return render_template('index.html', games=games)


@main.route('/game', methods=['GET', 'POST'])
def game():

    game_type = request.args.get('game_type')
    game_play = next(game for game in games if game.param == game_type)

    in_game = request.args.get('in_game')
    if game_type == 'trivia_madness' and not in_game:
        in_game = "before"

        class Category:
            def __init__(self, name):
                self.name = name
        
        categories = [Category("Art & Literature"), Category("Language"), Category("Science & Nature"),
                    Category("General"), Category("Food & Drink"), Category("People & Places"),
                    Category("Geography"), Category("History & Holidays"), Category("Entertainment"),
                    Category("Toys & Games"), Category("Music"), Category("Mathematics"),
                    Category("Religion & Mythology"), Category("Sports & Leisure")]
        
        return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type)
    else:
        categories = []

    if request.method == 'POST':
        pass

    category = ""
    game_name = ""
    if game_type == "trivia_madness" and in_game == "intro":
        category = request.args.get('category')
        game_name = "Trivia Madness - " + category
    elif not in_game:
        in_game = "intro"
        game_name = game_play.name
        return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type,
                                game=game_play, game_name=game_name)
    elif game_type == "trivia_madness":
        category = request.args.get('category')

    timer = 0
    if in_game == "yes":
        timer = int(request.args.get('difficulty'))
        
    return render_template('game.html', in_game=in_game, categories=categories, game_type=game_type,
                            game=game_play, timer=timer, category=category, game_name=game_name)




    # class Game:

        # def __init__(self, name):
        #     self.name = name
        #     self.variable = name.title().replace(' ', '').replace('-', '').replace('&', '')
        #     self.api_url = 'https://api.api-ninjas.com/v1/trivia?category={}&limit=30'.format(self.variable.lower())
        #     # self.api_response = requests.get(self.api_url, headers={'X-Api-Key': os.getenv('API_KEY')})
        #     # self.question_numbers = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}
        #     self.question_number = 1
        #     self.current_category = ""
        #     self.current_question = ""
        #     self.current_answer = ""

        # def update_question_number(self, number):
        #     self.question_number = self.question_numbers[number]

        # def update_current_category(self, category):
        #     self.current_category = category

        # def update_stored_questions(self):
        #     pass # CONTACT API AND STORE IN REDIS

        # def get_question(self):
        #     # LOGIC TO GET QUESTION (+ANSWER) FROM REDIS
        #     self.current_question = "Question from Redis"
        #     self.current_answer = "Answer from Redis"
        #     return "Question"
        
        # def get_answer(self):
        #     return self.current_answer





"""
[
  {
    "category": "historyholidays",
    "question": "Three of the names of Santa's reindeer begin with the letter 'D'', name two of them ",
    "answer": "Dancer, Dasher, Donner"
  },
    {
    "category": "historyholidays",
    "question": "What pope died 33 days after his election ",
    "answer": "John Paul i"
  }
]
"""