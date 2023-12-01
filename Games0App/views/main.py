from flask import Blueprint
from Games0App.extensions import db
from Games0App.models.user import User
from flask import render_template, request
import random
import string

main = Blueprint('main', __name__)

@main.route('/')
def index():

    class Game:
        def __init__(self, name):
            self.name = name
            lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
            self.image = lower_name + '.png'
            self.link = '/games/' + lower_name
            self.route = name.title().replace(' ', '').replace('-', '').replace('&', '')
            print(self.route)
    
    games = [Game("Fill in the Blank - Facts"), Game("Fill in the Blank - Jokes"),
             Game("Trivia Madness - Choose Your Category"), Game("Countries & Cultures - Multiple Choice"),
             Game("Countries & Cultures - True or False"), Game("Number to Reach")]
    
    return render_template('index.html', games=games)

@main.route('/games/fillintheblankfacts')
def FillInTheBlankFacts():
    return render_template('fillintheblankfacts.html')

@main.route('/games/fillintheblankjokes')
def FillInTheBlankJokes():
    return render_template('fillintheblankjokes.html')


@main.route('/games/triviamadnesschooseyourcategory', methods=['GET', 'POST'])
def TriviaMadnessChooseYourCategory():

    class Category:

        def __init__(self, name):
            self.name = name
            self.variable = name.title().replace(' ', '').replace('-', '').replace('&', '')
            # self.api = ""
            self.question_number = "one"

        def get_question(self):
            return "Test question"
        
        def get_answer(self):
            return "Test answer"
    
    categories = [Category("Art & Literature"), Category("Language"), Category("Science & Nature"),
                Category("General"), Category("Food & Drink"), Category("People & Places"),
                Category("Geography"), Category("History & Holidays"), Category("Entertainment"),
                Category("Toys & Games"), Category("Music"), Category("Mathematics"),
                Category("Religion & Mythology"), Category("Sports & Leisure")]

    in_game = "no"

    if request.method == 'POST':
        pass

    category = request.args.get('category')
    if category:
        for item in categories:
            if item.variable == category:
                game_category = item
                in_game = "intro"
                break
    else:
        game_category = None

    in_game_request = request.args.get('in_game')
    if in_game_request == "yes":
        in_game = "yes"
        for category in categories:
            if category.variable == request.args.get('category'):
                game_category = category
                break



    return render_template('triviamadness.html', in_game=in_game, game_category=game_category, categories=categories)


@main.route('/games/countriesculturesmultiplechoice')
def CountriesCulturesMultipleChoice():
    return render_template('countriesculturesmc.html')

@main.route('/games/countriesculturestrueorfalse')
def CountriesCulturesTrueOrFalse():
    return render_template('countriesculturestf.html')

@main.route('/games/numbertoreach')
def NumberToReach():
    return render_template('numbertoreach.html')




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