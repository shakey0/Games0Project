from playwright.sync_api import expect
from Games0App.extensions import db, redis_client


def test_index_route(page, flask_server):
    page.goto("http://localhost:5000/")
    title = page.locator("h1")
    expect(title).to_have_text('What game do you want to play?')
    game_names = page.locator('.game-name')
    expect(game_names).to_have_text([
        "Fill in the Blank - Facts", "Fill in the Blank - Jokes",
        "Trivia Madness", "Trivia - Multiple Choice",
        "Trivia - True or False", "Number to Reach"
    ])


def test_game_setup_route(page, flask_server):
    page.goto("http://localhost:5000/")
    page.dispatch_event(".t-fill_blank_facts", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Fill in the Blank - Facts')
    instruction_text = page.locator(".instruction-text")
    expect(instruction_text).to_have_text("You will be given 10 facts and need to fill in the blank word for each one. Type your answer for each question. The quicker you answer, the more points you'll get.Good luck!")
    start_game_button = page.locator(".submit-game-btn")
    expect(start_game_button).to_have_text("Start Game")
    page.dispatch_event(".submit-game-btn", "click")


def test_game_setup_with_categories(page, flask_server):
    page.goto("http://localhost:5000/")
    page.dispatch_event(".t-trivia_madness_categories", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Welcome to Trivia Madness!')
    page.dispatch_event(".t-showbiz-hard", "click")
    title = page.locator("h1")
    expect(title).to_have_text('Trivia Madness - Showbiz - HARD')
    page.dispatch_event(".submit-game-btn", "click")
    