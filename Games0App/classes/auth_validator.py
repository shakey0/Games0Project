from flask import request
from flask_login import current_user
from Games0App.mailjet_api import send_email
from Games0App.classes.auth_token_manager import auth_token_manager
from Games0App.classes.logger import logger
import bcrypt
from better_profanity import profanity


class AuthValidator:


    def validate_password_for_auth(self):
        password = request.form.get('password')
        if not password:
            return "Please enter your password."
        if not auth_token_manager.attempt_check('auth_password', current_user.id):
            return "This is not good! You'll have to wait 10 minutes."
        if not bcrypt.checkpw(password.encode('utf-8'), current_user.password_hashed):
            if not auth_token_manager.check_auth_password_attempt():
                json_log = {
                    'user_id': current_user.id
                }
                unique_id = logger.log_event(json_log, 'validate_password_for_auth', 'max_auth_password_attempts')
                print('ACCOUNT ALERT - Logged incorrect auth password attempt: ' + unique_id)
                send_email(current_user.email, current_user.username, 'auth_password_max_attempts', unique_id=unique_id)
                return "This is not good! You'll have to wait 10 minutes."
            return "Something didn\'t match! Please try again."
        return True


    def validate_new_user_name(self):
        username = request.form.get('username')
        if not username:
            return 'Please enter a username.'
        username = username.strip()
        if len(username) < 3:
            return 'Username must be at least 4 characters.'
        elif len(username) > 20:
            return 'Username must be max 20 characters.'
        elif any(char not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for char in username):
            return 'Username must only contain letters, numbers, underscores and hyphens.'
        return True


    def validate_new_email(self):
        email = request.form.get('email')
        if not email:
            return 'Please enter an email.'
        email = email.strip()
        if len(email) < 3:
            return 'Email must be at least 3 characters.'
        elif '@' not in email or ' ' in email or email.count('@') > 1:
            return 'Please enter a valid email.'
        return True
    

    def validate_new_password(self):
        password = request.form.get('password')
        if not password:
            return 'Please enter a password.', 'password'
        elif len(password) < 8:
            return 'Password must be at least 8 characters.', 'password'
        confirm_password = request.form.get('confirm_password')
        if not confirm_password:
            return 'Please confirm your password.', 'confirm_password'
        elif not password == confirm_password:
            return 'Passwords do not match.', 'confirm_password'
        return True
    

    def validate_victory_message(self):
        message = request.form.get('message')
        if not message:
            return True # Victory message is optional
        message = message.strip()
        if len(message) > 25:
            return "Max 25 characters."
        if profanity.contains_profanity(message):
            return "Contains bad language."
        return True


auth_validator = AuthValidator()
