from playwright.sync_api import expect
from Games0App.extensions import redis_client
from Games0App.models.high_score import HighScore
import json


def test_scoreboard_route_from_unauth(page, flask_server, test_app):
    redis_client.flushall()
    
    # Play a game to the end
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.dispatch_event(".t-trivia_tf_categories", "click")
    page.dispatch_event(".t-animals", "click")
    page.dispatch_event("#medium", "click")
    page.dispatch_event(".submit-game-btn", "click")
    for num in range(10):
        page.wait_for_timeout(100)
        question_value = redis_client.hget("triviatrueorfalse_animals_hash", "triviatrueorfalse_animals_{}".format(num+1))
        question = json.loads(question_value.decode("utf-8"))
        if question[1] == question[2]:
            page.dispatch_event("#True", "click")
        else:
            page.dispatch_event("#False", "click")
        page.dispatch_event(".submit-game-btn", "click")
        result = page.locator(".t-answer-result")
        expect(result).to_have_text("You are right!")
        page.dispatch_event(".submit-game-btn", "click")
    
    # Sign up as a new user
    page.wait_for_timeout(100)
    sign_up_link = page.locator(".t-sb-sign-up")
    expect(sign_up_link).to_have_text("Sign up")
    page.dispatch_event(".t-sb-sign-up", "click")
    page.wait_for_timeout(1000)
    page.fill('#register-box input[name="username"]', "testuser")
    page.fill('#register-box input[name="email"]', "testemail@email.com")
    page.fill('#register-box input[name="password"]', "testpassword")
    page.fill('#register-box input[name="confirm_password"]', "testpassword")
    page.click("text='I accept the Terms of Service.'")
    page.dispatch_event(".sign-up-btn", "click")
    page.wait_for_timeout(1000)
    username_link = page.locator(".nav-username-link")
    expect(username_link).to_have_text("testuser")
    add_score_title = page.locator("h1")
    expect(add_score_title).to_have_text("Add Your Score")
    
    # Add a score with a message that is too long
    page.fill('.message-input', "This is a message that is too long for the message input field. It is over 25 characters long and should not be accepted.")
    page.click("text='Add My Score'")
    page.wait_for_timeout(100)
    error = page.locator(".victory-message-error")
    expect(error).to_have_text("Max 25 characters.")
    
    # Add a score with a valid message
    page.fill('.message-input', "Great!")
    page.click("text='Add My Score'")
    page.wait_for_timeout(100)
    score_user_name = page.locator(".username-score-button")
    expect(score_user_name).to_have_text("testuser")
    score_message = page.locator(".score-message-container")
    expect(score_message).to_contain_text("Great!")
    
    # Like the score
    likes_count = page.locator(".likes-count")
    expect(likes_count).to_have_text("0")
    page.dispatch_event(".like-thumbsup", "click")
    page.wait_for_timeout(100)
    likes_count = page.locator(".likes-count")
    expect(likes_count).to_have_text("1")
    page.dispatch_event(".liked-thumbsup", "click")
    page.wait_for_timeout(100)
    likes_count = page.locator(".likes-count")
    expect(likes_count).to_have_text("0")
    
    # Amend the score message with a message that is too long
    page.dispatch_event(".edit-score-button", "click")
    page.fill('input[name="message"]', "This is a message that is too long for the message input field. It is over 25 characters long and should not be accepted.")
    page.click("text='Confirm'")
    page.wait_for_timeout(100)
    error = page.locator(".victory-message-error")
    expect(error).to_have_text("Max 25 characters.")
    
    # Amend the score message with a valid message
    page.dispatch_event(".edit-score-button", "click")
    page.fill('input[name="message"]', "Great! I love this game!")
    page.click("text='Confirm'")
    score_message = page.locator(".score-message-container")
    expect(score_message).to_contain_text("Great! I love this game!")
    
    # Delete the score
    page.dispatch_event(".edit-score-button", "click")
    page.click("text='Remove Entire Entry'")
    
    page.wait_for_timeout(100)
    high_scores = HighScore.query.all()
    assert len(high_scores) == 0


def test_scoreboard_route_from_auth(page, flask_server, test_app):
    redis_client.flushall()
    
    # Create a user
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.click("text='Menu'")
    page.click("text='Sign up'")
    page.wait_for_timeout(1000)
    page.fill('#register-box input[name="username"]', "testuser")
    page.fill('#register-box input[name="email"]', "testemail@email.com")
    page.fill('#register-box input[name="password"]', "testpassword")
    page.fill('#register-box input[name="confirm_password"]', "testpassword")
    page.click("text='I accept the Terms of Service.'")
    page.dispatch_event(".sign-up-btn", "click")
    page.wait_for_timeout(1000)
    username_link = page.locator(".nav-username-link")
    expect(username_link).to_have_text("testuser")
    
    # Play a game to the end
    page.dispatch_event(".t-trivia_tf_categories", "click")
    page.dispatch_event(".t-animals", "click")
    page.dispatch_event("#medium", "click")
    page.dispatch_event(".submit-game-btn", "click")
    for num in range(10):
        page.wait_for_timeout(100)
        question_value = redis_client.hget("triviatrueorfalse_animals_hash", "triviatrueorfalse_animals_{}".format(num+1))
        question = json.loads(question_value.decode("utf-8"))
        if question[1] == question[2]:
            page.dispatch_event("#True", "click")
        else:
            page.dispatch_event("#False", "click")
        page.dispatch_event(".submit-game-btn", "click")
        result = page.locator(".t-answer-result")
        expect(result).to_have_text("You are right!")
        if num == 9:
            break
        page.dispatch_event(".submit-game-btn", "click")
    page.wait_for_timeout(100)
    
    # Add a score with a message that is too long
    page.fill('input[name="message"]', "This is a message that is too long for the message input field. It is over 25 characters long and should not be accepted.")
    page.click("text='Scoreboard'")
    page.wait_for_timeout(100)
    
    # Add a score with a valid message
    page.fill('input[name="message"]', "Great!")
    page.click("text='Scoreboard'")
    score_user_name = page.locator(".username-score-button")
    expect(score_user_name).to_have_text("testuser")
    score_message = page.locator(".score-message-container")
    expect(score_message).to_contain_text("Great!")
    
    page.wait_for_timeout(100)
    high_scores = HighScore.query.all()
    assert len(high_scores) == 1
