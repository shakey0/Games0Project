from playwright.sync_api import expect
from Games0App.extensions import redis_client
from Games0App.models.user import User


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


def test_register_route_errors(page, flask_server, test_app):
    redis_client.flushall()
    page.goto("http://localhost:5000/")
    page.click("text='Continue to Website'")
    page.click("text='Menu'")
    page.click("text='Sign up'")
    page.wait_for_timeout(1000)
    # Click the sign up button without entering any information
    page.dispatch_event(".sign-up-btn", "click")
    page.wait_for_timeout(100)
    username_error = page.locator(".register-username-error-message")
    email_error = page.locator(".register-email-error-message")
    password_error = page.locator(".register-password-error-message")
    policy_error = page.locator(".register-general-error-message")
    expect(username_error).to_have_text("Please enter a username.")
    expect(email_error).to_have_text("Please enter an email.")
    expect(password_error).to_have_text("Please enter a password.")
    expect(policy_error).to_have_text("Please agree to the Terms of Service.")
    page.fill('#register-box input[name="username"]', "testuser")
    page.fill('#register-box input[name="email"]', "testemail@email.com")
    page.fill('#register-box input[name="password"]', "testpassword")
    page.fill('#register-box input[name="confirm_password"]', "password") # Passwords do not match
    page.dispatch_event(".sign-up-btn", "click")
    page.wait_for_timeout(100)
    confirm_password_error = page.locator(".register-confirm_password-error-message")
    expect(confirm_password_error).to_have_text("Passwords do not match.")
    

def test_logout_login_routes_with_errors(page, flask_server, test_app):
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
    
    # Log out
    page.click("text='Menu'")
    page.click("text='Log out'")
    page.wait_for_timeout(1000)
    
    # Log in
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
    
    # Log out
    page.click("text='Menu'")
    page.click("text='Log out'")
    page.wait_for_timeout(1000)
    
    # Log in with errors
    page.goto("http://localhost:5000/")
    page.click("text='Menu'")
    page.click("text='Log in'")
    page.wait_for_timeout(1000)
    # Click the login button without entering any information
    page.dispatch_event(".login-btn", "click")
    page.wait_for_timeout(100)
    login_error = page.locator(".login-error-message")
    expect(login_error).to_have_text("Please enter your email or username.")
    
    page.fill('#login-box input[name="username"]', "testemail@email.com")
    page.fill('#login-box input[name="password"]', "password") # Incorrect password
    page.dispatch_event(".login-btn", "click")
    page.wait_for_timeout(100)
    login_error = page.locator(".login-error-message")
    expect(login_error).to_have_text("Something didn't match! Please try again.")


def test_change_email_route(page, flask_server, test_app):
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
    
    # Go to change_email route
    page.click("text='testuser'")
    title = page.locator("h1")
    expect(title).to_have_text('Account Management')
    current_email = page.locator(".email-profile-info")
    expect(current_email).to_have_text('testemail@email.com')
    page.click("text='Change Email'")
    
    # Enter incorrect password
    page.fill('input[name="password"]', "password")
    page.click("text='Confirm'")
    error = page.locator(".error")
    expect(error).to_have_text("Something didn't match! Please try again.")
    
    # Enter correct password
    page.fill('input[name="password"]', "testpassword")
    page.click("text='Confirm'")
    
    # Leave email field empty
    page.fill('input[name="email"]', "")
    page.click("text='Confirm'")
    error = page.locator(".error")
    expect(error).to_have_text("Please enter an email.")
    
    # Enter valid email
    page.fill('input[name="email"]', "newtestemail@test.com")
    page.click("text='Confirm'")
    page.click("text='Return to Profile'")
    current_email = page.locator(".email-profile-info")
    expect(current_email).to_have_text('newtestemail@test.com')
    
    
def test_change_password_route(page, flask_server, test_app):
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
    
    # Go to change_password route
    page.click("text='testuser'")
    title = page.locator("h1")
    expect(title).to_have_text('Account Management')
    page.click("text='Change Password'")
    
    # Enter incorrect password
    page.fill('input[name="password"]', "password")
    page.click("text='Confirm'")
    error = page.locator(".error")
    expect(error).to_have_text("Something didn't match! Please try again.")
    
    # Enter correct password
    page.fill('input[name="password"]', "testpassword")
    page.click("text='Confirm'")
    
    # Enter invalid password
    page.fill('input[name="password"]', "new")
    page.fill('input[name="confirm_password"]', "new")
    page.click("text='Confirm'")
    error = page.locator(".error")
    expect(error).to_have_text("Password must be at least 8 characters.")
    
    # Enter valid password and assert that it works
    page.fill('input[name="password"]', "newpassword")
    page.fill('input[name="confirm_password"]', "newpassword")
    page.click("text='Confirm'")
    page.click("text='Return to Profile'")
    page.click("text='Menu'")
    page.click("text='Log out'")
    page.wait_for_timeout(1000)
    page.goto("http://localhost:5000/")
    page.click("text='Menu'")
    page.click("text='Log in'")
    page.wait_for_timeout(1000)
    page.fill('#login-box input[name="username"]', "testemail@email.com")
    page.fill('#login-box input[name="password"]', "newpassword")
    page.dispatch_event(".login-btn", "click")
    page.wait_for_timeout(1000)
    username_link = page.locator(".nav-username-link")
    expect(username_link).to_have_text("testuser")
    
    
def test_delete_account_route(page, flask_server, test_app):
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
    
    # Go to delete_account route
    page.click("text='testuser'")
    title = page.locator("h1")
    expect(title).to_have_text('Account Management')
    page.click("text='Delete Account'")
    page.click("text='Confirm'")

    # Enter incorrect password
    page.fill('input[name="password"]', "password")
    page.click("text='Confirm'")
    error = page.locator(".error")
    expect(error).to_have_text("Something didn't match! Please try again.")
    
    # Enter correct password, confirm to delete account and assert that it works
    page.fill('input[name="password"]', "testpassword")
    page.click("text='Confirm'")
    page.click("text='Confirm'")
    page.click("text='Return to Home'")
    all_users = User.query.all()
    assert len(all_users) == 0
