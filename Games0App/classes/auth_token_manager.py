from flask import flash
from flask_login import current_user, logout_user
from Games0App.extensions import redis_client
import os


class AuthTokenManager:


    def check_reset_password_attempt(self):
        key_name = f'reset_password_attempt_{current_user.id}'
        key = redis_client.get(key_name)
        if not key:
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
                print('Invalid token - ALERT!')
                logout_user()
                flash("A security threat was detected. You've been logged out.", 'error')
                # Log this event
                return 'invalid_token'
        else:
            print('Token expired.')
            # Log this event
            return 'expired_token'
