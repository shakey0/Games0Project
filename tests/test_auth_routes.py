from playwright.sync_api import expect
from Games0App.extensions import redis_client


def test_register_route(page, flask_server, test_app):
    redis_client.flushall()
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


def test_logout_login_routes(page, flask_server, test_app):
    redis_client.flushall()
    
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
    
    page.click("text='Menu'")
    page.click("text='Log out'")
    page.wait_for_timeout(1000)
    
    page.goto("http://localhost:5000/")
    page.click("text='Menu'")
    page.click("text='Log in'")
    page.wait_for_timeout(1000)
    page.fill('#login-box input[name="username"]', "testemail@email.com")
    page.fill('#login-box input[name="password"]', "testpassword")
    page.dispatch_event(".login-btn", "click")
    page.wait_for_timeout(1000)
    username_link = page.locator(".nav-username-link")
    expect(username_link).to_have_text("testuser")


def test_change_email_route(page, flask_server, test_app):
    redis_client.flushall()
    
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
    
    page.click("text='testuser'")
    title = page.locator("h1")
    expect(title).to_have_text('Account Management')
    current_email = page.locator(".email-profile-info")
    expect(current_email).to_have_text('testemail@email.com')
    page.click("text='Change Email'")
    page.fill('input[name="password"]', "testpassword")
    page.click("text='Confirm'")
    page.fill('input[name="email"]', "newtestemail@test.com")
    page.click("text='Confirm'")
    page.click("text='Return to Profile'")
    current_email = page.locator(".email-profile-info")
    expect(current_email).to_have_text('newtestemail@test.com')
    