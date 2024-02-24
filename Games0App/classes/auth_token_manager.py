from flask_login import current_user
from Games0App.extensions import redis_client
from Games0App.classes.logger import logger
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
        elif type == 'send_contact_message':
            redis_timeout = os.environ.get('REDIS_TIMEOUT', 60)
            key_name = f'send_contact_message_attempt_{marker}'
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
        

    def get_reset_password_link_token(self, user_id):
        redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
        token = os.urandom(16).hex()
        redis_client.set(token, user_id, ex=redis_timeout)
        return token
    
    def verify_reset_password_link_token(self, token):
        user_id = redis_client.get(token)
        if user_id:
            return int(user_id.decode('utf-8'))
        return None
    
    def delete_reset_password_link_token(self, token):
        redis_client.delete(token)


    def get_new_auth_token(self, values_to_add):

        if 'route' in values_to_add:
            json_log = {
                'user_id': values_to_add['user_id'],
                'username': values_to_add['username'],
                'route': values_to_add['route']
            }
            unique_id = logger.log_event(json_log, 'get_new_auth_token', f'init_{values_to_add["route"]}')
            if 'title' in values_to_add:
                print(f'INIT {values_to_add["title"].upper()}: ' + unique_id)

        redis_timeout = os.environ.get('REDIS_TIMEOUT', 600)
        token = os.urandom(16).hex()
        redis_client.hset(token, mapping=values_to_add)
        redis_client.expire(token, redis_timeout)
        return token
    
    def add_values_to_auth_token(self, token, values_to_add):
        redis_client.hset(token, mapping=values_to_add)
    
    def get_values_from_auth_token(self, token, value_names):
        values = redis_client.hmget(token, value_names)
        results = {}
        for i in range(len(value_names)):
            value = values[i]
            if value is not None:
                results[value_names[i]] = value.decode('utf-8')
            else:
                results[value_names[i]] = None
        return results
    
    def delete_auth_token(self, token):
        redis_client.delete(token)


auth_token_manager = AuthTokenManager()
