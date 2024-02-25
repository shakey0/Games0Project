from playwright.sync_api import expect
from Games0App.extensions import redis_client
import json


ordinals = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7, "8th": 8, "9th": 9, "10th": 10, "11th": 11, "12th": 12, "13th": 13, "14th": 14, "15th": 15, "16th": 16, "17th": 17, "18th": 18, "19th": 19, "20th": 20, "21st": 21, "22nd": 22, "23rd": 23, "24th": 24, "25th": 25, "26th": 26, "27th": 27, "28th": 28, "29th": 29, "30th": 30, "31st": 31}

def test_reveal_letter_route(page, flask_server, test_app):
    for num in range(30):
        redis_client.flushall()
        
        # Start a game and click the reveal letter button
        page.goto("http://localhost:5000/")
        if num == 0:
            page.click("text='Continue to Website'")
        page.dispatch_event(".t-fill_blank_facts", "click")
        page.dispatch_event("#easy", "click")
        page.dispatch_event(".submit-game-btn", "click")
        game_title = page.locator(".game-title-tag")
        expect(game_title).to_have_text("Fill in the Blank - Facts")
        page.dispatch_event(".reveal-letter-btn", "click")
        
        # Check the revealed letter against the answer
        question_value = redis_client.hget("fillintheblankfacts_hash", "fillintheblankfacts_1")
        question = json.loads(question_value.decode("utf-8"))
        page.wait_for_timeout(100)
        hint_messages = page.text_content(".hint-messages")
        position = 0
        for item in ordinals:
            if item in hint_messages:
                position = ordinals[item]
                break
        assert question[2][position-1] == hint_messages.split(" ")[-1][0]
        # page.screenshot(path="tests/screenshots/capture.png")


def test_reveal_length_route(page, flask_server, test_app):
    for num in range(30):
        redis_client.flushall()
        
        # Start a game and click the reveal length button
        page.goto("http://localhost:5000/")
        if num == 0:
            page.click("text='Continue to Website'")
        page.dispatch_event(".t-fill_blank_facts", "click")
        page.dispatch_event("#easy", "click")
        page.dispatch_event(".submit-game-btn", "click")
        game_title = page.locator(".game-title-tag")
        expect(game_title).to_have_text("Fill in the Blank - Facts")
        page.dispatch_event(".reveal-length-btn", "click")
        
        # Check the revealed length against the answer
        question_value = redis_client.hget("fillintheblankfacts_hash", "fillintheblankfacts_1")
        question = json.loads(question_value.decode("utf-8"))
        page.wait_for_timeout(100)
        hint_messages = page.text_content(".hint-messages")
        length, digit_found = "", False
        for char in hint_messages:
            if char.isdigit():
                length += char
                digit_found = True
            elif digit_found:
                break
        assert len(question[2]) == int(length)
        # page.screenshot(path="tests/screenshots/capture.png")


def test_remove_higher_route(page, flask_server, test_app):
    for num in range(30):
        redis_client.flushall()
        
        # Start a game and click the remove higher button
        page.goto("http://localhost:5000/")
        if num == 0:
            page.click("text='Continue to Website'")
        page.dispatch_event(".t-trivia_mc_categories", "click")
        page.dispatch_event(".t-generalknowledge", "click")
        page.dispatch_event("#hard", "click")
        page.dispatch_event("#medium2", "click")
        page.dispatch_event(".submit-game-btn", "click")
        game_title = page.locator(".game-title-tag")
        expect(game_title).to_have_text("Trivia - Multiple Choice - General Knowledge")
        page.dispatch_event(".remove-higher-btn", "click")
        page.wait_for_timeout(100)
        
        # Get the answers and check if one of the higher answers has been removed (display: none)
        answers = page.locator(".answer-selector")
        first_element_display = answers.nth(0).evaluate("element => getComputedStyle(element).display")
        second_element_display = answers.nth(1).evaluate("element => getComputedStyle(element).display")
        assert first_element_display == 'none' or second_element_display == 'none'
        # page.screenshot(path="tests/screenshots/capture.png")
        

def test_remove_lower_route(page, flask_server, test_app):
    for num in range(30):
        redis_client.flushall()
        
        # Start a game and click the remove lower button
        page.goto("http://localhost:5000/")
        if num == 0:
            page.click("text='Continue to Website'")
        page.dispatch_event(".t-trivia_mc_categories", "click")
        page.dispatch_event(".t-generalknowledge", "click")
        page.dispatch_event("#hard", "click")
        page.dispatch_event("#medium2", "click")
        page.dispatch_event(".submit-game-btn", "click")
        game_title = page.locator(".game-title-tag")
        expect(game_title).to_have_text("Trivia - Multiple Choice - General Knowledge")
        page.dispatch_event(".remove-lower-btn", "click")
        page.wait_for_timeout(100)
        
        # Get the answers and check if one of the lower answers has been removed (display: none)
        answers = page.locator(".answer-selector")
        third_element_display = answers.nth(2).evaluate("element => getComputedStyle(element).display")
        fourth_element_display = answers.nth(3).evaluate("element => getComputedStyle(element).display")
        assert third_element_display == 'none' or fourth_element_display == 'none'
        # page.screenshot(path="tests/screenshots/capture.png")
