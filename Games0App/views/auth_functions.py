from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from Games0App.mailjet_api import send_email
from Games0App.classes.auth_token_manager import AuthTokenManager
auth_token_manager = AuthTokenManager()
from Games0App.classes.auth_validator import AuthValidator
auth_validator = AuthValidator()
from Games0App.classes.logger import Logger
logger = Logger()


def redirect_to_scoreboard():
    return redirect(url_for('scoreboard.scoreboard_page', username=current_user.username))


def get_auth_types(word_1, word_2, start_from=1):

    title = f'{word_1.title()} {word_2.title()}'
    route = f'{word_1}_{word_2}'
    past = '' if word_1 == 'reset' else 'd'
    message = ['', '', f'Your new {word_2}:', f'{word_2.title()} successfully {word_1}{past}!']

    auth_types = []
    for i in range(start_from, 4):
        auth_types.append({'title': title, 'stage': i, 'route': route, 'message': message[i]})
    
    return auth_types


def get_stage(route):

    stage_token_1 = request.form.get('stage_token_1')
    
    token_check = auth_token_manager.verify_stage_token(route, 1, stage_token_1)
    if token_check == 'expired_token':
        flash('Sorry! You took too long. Please try again.', 'error')
    if token_check != True:
        return False, token_check
    
    stage_token_2 = request.form.get('stage_token_2')

    if not stage_token_2:
        return True, [stage_token_1]
    
    token_check = auth_token_manager.verify_stage_token(route, 2, stage_token_2)
    if token_check != True:
        return False, token_check
    
    return True, [stage_token_1, stage_token_2]


def do_stage_1(auth_type_1, route, stage_token_1=None):
    if not stage_token_1:
        stage_token_1 = auth_token_manager.get_new_stage_token(route, 1)
    return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)


def do_stage_2(route, stage_token_1, auth_type_1, auth_type_2):
    password_validation = auth_validator.validate_password_for_auth()
    if password_validation != True:
        flash(password_validation, 'error')
        return do_stage_1(auth_type_1, route, stage_token_1=stage_token_1)
    
    stage_token_2 = auth_token_manager.get_new_stage_token(route, 2)
    return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                            stage_token_2=stage_token_2)


def complete_password_change(user, auth_type_3):

    json_log = {
        'user_id': user.id,
        'username': user.username
    }
    unique_id = logger.log_event(json_log, 'complete_password_change', 'password_change')

    send_email(user.email, user.username, 'reset_password_confirmation', unique_id=unique_id)

    auth_token_manager.attempt_check('reset_password', user.id)

    return render_template('auth.html', auth_type=auth_type_3, user=current_user)
