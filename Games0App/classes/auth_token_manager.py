from flask import flash
from flask_login import current_user, logout_user
from Games0App.extensions import redis_client
from Games0App.mailjet_api import send_email
from Games0App.models.user import User
from Games0App.classes.logger import Logger
logger = Logger()
import os


class AuthTokenManager:


    def check_reset_password_attempt(self):
        key_name = f'reset_password_attempt_{current_user.id}'
        key = redis_client.get(key_name)
        if not key:
            return True
        return False
    

    def check_auth_password_attempt(self):
        key_name = f'auth_password_attempt_{current_user.id}'
        key = redis_client.get(key_name)
        if not key:
            return False
        elif int(key.decode('utf-8')) < 3:
            return True
        return False
    

    def check_login_password_attempt(self, credential):
        key_name = f'login_password_attempt_{credential}'
        key = redis_client.get(key_name)
        if not key:
            return False
        elif int(key.decode('utf-8')) < 5:
            return True
        return False


    def attempt_check(self, type, marker):
        
        if type == 'reset_password':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 3600)
            key_name = f'reset_password_attempt_{marker}'
            limit = 1
        elif type == 'reset_password_email_first':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 30)
            key_name = f'reset_password_email_first_attempt_{marker}'
            limit = 1
        elif type == 'reset_password_email':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
            key_name = f'reset_password_email_attempt_{marker}'
            limit = 3
        elif type == 'auth_password':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
            key_name = f'auth_password_attempt_{marker}'
            limit = 3
        elif type == 'login_password':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 120)
            key_name = f'login_password_attempt_{marker}'
            limit = 5
        elif type == 'route':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 60)
            key_name = f'route_attempt_{current_user.id}_{marker}'
            limit = 10

        key = redis_client.get(key_name)
        if not key:
            redis_client.set(key_name, 1, ex=redis_timeout)
            return True
        elif int(key.decode('utf-8')) >= limit:
            if type == 'reset_password_email':
                redis_client.delete(f'reset_password_email_first_attempt_{marker}')
            return False
        else:
            redis_client.incr(key_name)
            redis_client.expire(key_name, redis_timeout)
            return True
        

    def get_reset_password_link_token(self, user_id, revert=False):
        cache_time = 86400 if revert else 600
        redis_timeout = os.environ.get('REDIS_TIMEOUT', cache_time)
        token = os.urandom(16).hex()
        reset_type = 'revert' if revert else 'reset'
        redis_client.set(token, f'{user_id}_{reset_type}', ex=redis_timeout)
        return token
    

    def verify_reset_password_link_token(self, token, revert=False):
        result = redis_client.get(token)
        if result:
            user_id, reset_type = result.decode('utf-8').split('_')
            if revert:
                if reset_type == 'revert':
                    return int(user_id)
                return None
            else:
                if reset_type == 'reset':
                    return int(user_id)
                return None
        return None
    

    def delete_reset_password_link_token(self, token):
        redis_client.delete(token)


    def get_new_change_token(self, auth_type, stage, parsed_user_id=None):
        redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
        user_id = current_user.id if not parsed_user_id else parsed_user_id
        key_name = f'change_token_{auth_type}_{user_id}_{stage}'
        token = os.urandom(16).hex()
        redis_client.set(key_name, token, ex=redis_timeout)
        return token


    def verify_change_token(self, auth_type, stage, token, parsed_user_id=None):
        user_id = current_user.id if not parsed_user_id else parsed_user_id
        key_name = f'change_token_{auth_type}_{user_id}_{stage}'
        key = redis_client.get(key_name)
        if key:
            if key.decode('utf-8') == token:
                return True
            else:
                json_log = {
                    'user_id': user_id,
                    'auth_type': auth_type,
                    'stage': stage,
                    'token': token,
                    'cache_token': key.decode('utf-8')
                }
                unique_id = logger.log_event(json_log, 'verify_change_token', 'invalid_change_token')
                print('INVALID TOKEN: ' + unique_id + ' - ALERT!')
                flash("A security threat was detected. You've been logged out.", 'error')
                flash(f'If you wish to contact me, please quote this case number: {unique_id}', 'error')
                flash('An email has been sent to you regarding the issue. You may reply to it.', 'error')
                flash('You may also consider changing your password.', 'error')
                if current_user.is_authenticated:
                    send_email(current_user.email, current_user.username, unique_id=unique_id)
                    logout_user()
                else:
                    user = User.query.filter_by(id=user_id).first()
                    if user:
                        send_email(user.email, user.username, unique_id=unique_id)
                return 'invalid_token'
        else:
            return 'expired_token'
