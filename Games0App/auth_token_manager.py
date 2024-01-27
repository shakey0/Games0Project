from flask import flash
from flask_login import current_user, logout_user
from Games0App.extensions import redis_client
import os


class AuthTokenManager:


    def attempt_check(self, type, marker):

        if type == 'auth_password':
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
            return False
        else:
            redis_client.incr(key_name)
            redis_client.expire(key_name, redis_timeout)
            return True


    def get_new_change_token(self, auth_type, stage):
        redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
        key_name = f'change_token_{auth_type}_{current_user.id}_{stage}'
        token = os.urandom(16).hex()
        redis_client.set(key_name, token, ex=redis_timeout)
        return token


    def verify_change_token(self, auth_type, stage, token):
        key_name = f'change_token_{auth_type}_{current_user.id}_{stage}'
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
            return 'token_expired'
