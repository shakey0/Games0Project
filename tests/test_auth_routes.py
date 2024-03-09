from playwright.sync_api import expect
from Games0App.extensions import redis_client
from Games0App.models.user import User
from Games0App.models.log import Log


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


def test_reset_password_route(page, flask_server, test_app):
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
    
    # Go to reset password box
    page.goto("http://localhost:5000/")
    page.click("text='Menu'")
    page.click("text='Log in'")
    page.click("text='Forgot password?'")
    page.wait_for_timeout(1000)
    
    # Send reset password link with no email
    page.click("text='Send reset password link'")
    message = page.locator(".forgotten-password-error-message")
    expect(message).to_have_text("Please enter your email address.")
    
    # Send reset password link
    page.fill('input[name="email"]', "testemail@email.com")
    page.click("text='Send reset password link'")
    message = page.locator(".forgotten-password-success-message")
    expect(message).to_have_text("Reset password link sent.")
    page.click("text='Send reset password link'")
    message = page.locator(".forgotten-password-success-message")
    expect(message).to_have_text("Please check your inbox.")
    
    # Check and get the logs
    logs = Log.query.all()
    assert len(logs) == 3
    assert logs[0].log_type == 'account_created'
    assert logs[1].log_type == 'successful_login'
    assert logs[2].log_type == 'reset_password_email_sent'
    reset_token = logs[2].data['reset_token']
    
    page.goto(f"http://localhost:5000/reset_password/{reset_token}")
    
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
    page.click("text='Return to Home'")
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


def test_report_issue_route_from_contact(page, flask_server, test_app):
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
    
    # Go to report_issue route
    page.click("text='Menu'")
    page.click("text='Contact'")
    page.click("text='Report an Issue'")
    title = page.locator("h1")
    expect(title).to_have_text('Report Issue')
    stage_title = page.locator(".report-issue-form-title1")
    expect(stage_title).to_have_text('What kind of issue are you reporting?')
    
    # Click Next without selecting an issue
    page.click("text='Next'")
    stage_title = page.locator(".report-issue-form-title1")
    expect(stage_title).to_have_text('What kind of issue are you reporting?')
    
    # Select an issue and click Next
    page.click("text='An error occurred and I'd like to report it.'")
    page.click("text='Next'")
    stage_title = page.locator(".report-issue-form-title2")
    expect(stage_title).to_have_text('Details of issue:')
    
    # Click Report Issue without entering any details
    page.click("text='Report Issue'")
    error = page.locator(".error-message")
    expect(error).to_have_text("Please include a case number or a description.")
    
    # Enter a case number and click Report Issue
    page.fill('input[name="issue_id"]', "123")
    page.click("text='Report Issue'")
    reported_message = page.locator(".t-reported-message")
    expect(reported_message).to_have_text("Thank you for reporting this issue.")
    page.click("text='Return to Home'")
    
    # Enter a description and click Report Issue
    page.click("text='Menu'")
    page.click("text='Contact'")
    page.click("text='Report an Issue'")
    page.click("text='An error occurred and I'd like to report it.'")
    page.click("text='Next'")
    page.fill('.issue-description', "123")
    page.click("text='Report Issue'")
    reported_message = page.locator(".t-reported-message")
    expect(reported_message).to_have_text("Thank you for reporting this issue.")
    page.click("text='Return to Home'")
    
    # Enter a case number and a description and click Report Issue
    page.click("text='Menu'")
    page.click("text='Contact'")
    page.click("text='Report an Issue'")
    page.click("text='An error occurred and I'd like to report it.'")
    page.click("text='Next'")
    page.fill('input[name="issue_id"]', "123")
    page.fill('.issue-description', "123")
    page.click("text='Report Issue'")
    reported_message = page.locator(".t-reported-message")
    expect(reported_message).to_have_text("Thank you for reporting this issue.")
    page.click("text='Return to Home'")
    
    # Check the logs
    logs = Log.query.all()
    assert len(logs) == 5
    assert logs[0].log_type == 'account_created'
    assert logs[1].log_type == 'successful_login'
    assert logs[2].log_type == 'other_problem_ISSUE_REPORTED'
    assert logs[3].log_type == 'other_problem_ISSUE_REPORTED'
    assert logs[4].log_type == 'other_problem_ISSUE_REPORTED'


def test_report_issue_route_after_password_change(page, flask_server, test_app):
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
    
    # Change password
    page.click("text='testuser'")
    title = page.locator("h1")
    expect(title).to_have_text('Account Management')
    page.click("text='Change Password'")
    page.fill('input[name="password"]', "testpassword")
    page.click("text='Confirm'")
    page.fill('input[name="password"]', "newpassword")
    page.fill('input[name="confirm_password"]', "newpassword")
    page.click("text='Confirm'")
    page.click("text='Return to Profile'")
    page.click("text='Menu'")
    page.click("text='Log out'")
    
    # Check and get the logs
    logs = Log.query.all()
    assert len(logs) == 4
    assert logs[0].log_type == 'account_created'
    assert logs[1].log_type == 'successful_login'
    assert logs[2].log_type == 'init_change_password'
    assert logs[3].log_type == 'password_changed'
    unique_id = logs[3].unique_id
    
    # Go to report_issue route
    page.goto("http://localhost:5000/report_issue?issue_id=" + unique_id)
    title = page.locator("h1")
    expect(title).to_have_text('Report Issue')
    stage_title = page.locator(".report-issue-form-title1")
    expect(stage_title).to_have_text('What kind of issue are you reporting?')
    
    # Click Next without selecting an issue
    page.click("text='Next'")
    stage_title = page.locator(".report-issue-form-title1")
    expect(stage_title).to_have_text('What kind of issue are you reporting?')
    
    # Select an issue and click Next
    page.click("text='My password was changed and I did NOT do it.'")
    page.click("text='Next'")
    stage_title = page.locator(".report-issue-form-title2")
    expect(stage_title).to_have_text('Details of issue:')
    
    # Click Report Issue
    page.click("text='Report Issue'")
    reported_message = page.locator(".t-reported-message")
    expect(reported_message).to_have_text("Thank you for reporting this issue.")
    
    # Send reset password link
    page.click("text='Reset Password'")
    page.fill('input[name="email"]', "testemail@email.com")
    page.click("text='Send reset password link'")
    page.wait_for_timeout(100)
    
    # Check the logs
    logs = Log.query.all()
    assert len(logs) == 6
    assert logs[4].log_type == 'password_change_ISSUE_REPORTED'
    assert logs[5].log_type == 'reset_password_email_sent'
