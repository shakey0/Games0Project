from flask import Blueprint
from Games0App.extensions import db
from Games0App.models.user import User
from flask import render_template
import random
import string

main = Blueprint('main', __name__)

@main.route('/')
def index():

    class Game:
        def __init__(self, name):
            self.name = name
            self.image = '/static/images/' + name + '.png'
            self.link = '/games/' + name.lower().replace(' ', '').replace('-', '').replace('&', '')
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

@main.route('/games/triviamadnesschooseyourcategory')
def TriviaMadnessChooseYourCategory():
    return render_template('triviamadness.html')

@main.route('/games/countriesculturesmultiplechoice')
def CountriesCulturesMultipleChoice():
    return render_template('countriesculturesmc.html')

@main.route('/games/countriesculturestrueorfalse')
def CountriesCulturesTrueOrFalse():
    return render_template('countriesculturestf.html')

@main.route('/games/numbertoreach')
def NumberToReach():
    return render_template('numbertoreach.html')
