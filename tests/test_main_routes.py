from playwright.sync_api import expect
from Games0App.extensions import db, redis_client
import json


def test_index_route(page, flask_server, test_app):
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    title = page.locator("h1")
    expect(title).to_have_text('What game do you want to play?')
    game_names = page.locator('.game-name')
    expect(game_names).to_have_text([
        "Fill in the Blank - Facts", "Fill in the Blank - Jokes",
        "Trivia Madness", "Trivia - Multiple Choice",
        "Trivia - True or False", "Number to Reach"
    ])


def test_game_setup_route(page, flask_server, test_app):
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-fill_blank_facts", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Fill in the Blank - Facts')
    instruction_text = page.locator(".instruction-text")
    expect(instruction_text).to_have_text("You will be given 10 facts and need to fill in the blank word for each one. Type your answer for each question. The quicker you answer, the more points you'll get.Good luck!")
    start_game_button = page.locator(".submit-game-btn")
    expect(start_game_button).to_have_text("Start Game")
    page.dispatch_event(".submit-game-btn", "click")
    game_title = page.locator(".game-title-tag")
    expect(game_title).to_have_text("Fill in the Blank - Facts")


def test_game_setup_route_with_categories(page, flask_server, test_app):
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-trivia_madness_categories", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Welcome to Trivia Madness!')
    page.dispatch_event(".t-showbiz-hard", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Trivia Madness - Showbiz - HARD')
    page.dispatch_event(".submit-game-btn", "click")
    game_title = page.locator(".game-title-tag")
    expect(game_title).to_have_text("Trivia Madness - Showbiz - HARD")
    

def test_game_setup_route_with_difficulty(page, flask_server, test_app):
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-trivia_mc_categories", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Welcome to Trivia - Multiple Choice!')
    page.dispatch_event(".t-science", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Trivia - Multiple Choice - Science')
    page.dispatch_event("#easy", "click")
    page.dispatch_event("#hard2", "click")
    page.dispatch_event(".submit-game-btn", "click")
    game_title = page.locator(".game-title-tag")
    expect(game_title).to_have_text("Trivia - Multiple Choice - Science")


def test_game_play_route(page, flask_server, test_app):
    redis_client.flushall()
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-fill_blank_jokes", "click")
    page.dispatch_event("#hard", "click")
    page.dispatch_event(".submit-game-btn", "click")
    game_title = page.locator(".game-title-tag")
    expect(game_title).to_have_text("Fill in the Blank - Jokes")
    for num in range(10):
        page.wait_for_timeout(100)
        question_value = redis_client.hget("fillintheblankjokes_hash", "fillintheblankjokes_{}".format(num+1))
        question = json.loads(question_value.decode("utf-8"))
        question_text = page.locator(".func-in")
        expect(question_text).to_have_text(question[1])
        page.fill(".answer-input", question[2])
        page.dispatch_event(".submit-game-btn", "click")
        result = page.locator(".t-answer-result")
        expect(result).to_have_text("You are right!")
        page.dispatch_event(".submit-game-btn", "click")
        # page.screenshot(path="tests/screenshots/capture_{}.png".format(num+1))


def test_game_play_route_categories(page, flask_server, test_app):
    redis_client.flushall()
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-trivia_tf_categories", "click")
    page.dispatch_event(".t-animals", "click")
    page.dispatch_event("#medium", "click")
    page.dispatch_event(".submit-game-btn", "click")
    game_title = page.locator(".game-title-tag")
    expect(game_title).to_have_text("Trivia - True or False - Animals")
    for num in range(10):
        page.wait_for_timeout(100)
        question_value = redis_client.hget("triviatrueorfalse_animals_hash", "triviatrueorfalse_animals_{}".format(num+1))
        question = json.loads(question_value.decode("utf-8"))
        question_text = page.locator(".func-in")
        expect(question_text).to_have_text(question[1])
        if question[1] == question[2]:
            page.dispatch_event("#True", "click")
        else:
            page.dispatch_event("#False", "click")
        page.dispatch_event(".submit-game-btn", "click")
        result = page.locator(".t-answer-result")
        expect(result).to_have_text("You are right!")
        page.dispatch_event(".submit-game-btn", "click")
        # page.screenshot(path="tests/screenshots/capture_{}.png".format(num+1))