from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from Games0App.extensions import db
from Games0App.models.user import User
from Games0App.auth_token_manager import AuthTokenManager
auth_token_manager = AuthTokenManager()
from Games0App.auth_validator import AuthValidator
auth_validator = AuthValidator()
from sqlalchemy.exc import IntegrityError
import bcrypt


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():

    errors = {}

    username_check = auth_validator.validate_new_user_name()
    if username_check != True:
        errors['username'] = username_check

    email_check = auth_validator.validate_new_email()
    if email_check != True:
        errors['email'] = email_check
        
    password_check = auth_validator.validate_new_password()
    if password_check != True:
        errors[password_check[1]] = password_check[0]
    
    if errors:
        return jsonify(success=False, errors=errors)
    
    hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    user = User(username=request.form.get('username'), email=request.form.get('email'),
                password_hashed=hashed_password, last_50_questions={})
    
    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify(success=True, message=f'Account created! Welcome, {user.username}!')
    
    except IntegrityError as e:
        db.session.rollback()
        if 'email' in str(e.orig):
            errors['email'] = 'An account with this email already exists.'
        elif 'username' in str(e.orig):
            errors['username'] = 'Username taken.'
        return jsonify(success=False, errors=errors)


@auth.route('/login', methods=['POST'])
def login():

    credential = request.form.get('username')
    if not credential:
        return jsonify(success=False, error="Please enter your email or username.")
    
    password = request.form.get('password')
    if not password:
        return jsonify(success=False, error="Please enter your password.")
    
    if not auth_token_manager.attempt_check('login_password', credential):
        return jsonify(success=False, error="Too many attempts! Please wait 2 minutes.")

    user = User.query.filter((User.email == credential) | (User.username == credential)).first()
    if user:
        print('USER FOUND')
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hashed):
            print('PASSWORD MATCHED')
            login_user(user)
            return jsonify(success=True, message=f'Welcome, {user.username}!')
        else:
            return jsonify(success=False, error="Something didn\'t match! Please try again.")
    else:
        return jsonify(success=False, error="Something didn\'t match! Please try again.")


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


def redirect_to_scoreboard():
    return redirect(url_for('scoreboard.scoreboard_page', username=current_user.username))


def get_auth_types(word_1, word_2, start_from=1):

    title = f'{word_1.title()} {word_2.title()}'
    route = f'{word_1}_{word_2}'
    message = ['', '', f'Your new {word_2}:', f'{word_2.title()} successfully {word_1}d!']

    auth_types = []
    for i in range(start_from, 4):
        auth_types.append({'title': title, 'stage': i, 'route': route, 'message': message[i]})
    
    return auth_types


def get_stage(route):

    stage_token_1 = request.form.get('stage_token_1')
    if not stage_token_1:
        print("No token sent with form - ALERT!")
        return 'invalid_token'
    token_check = auth_token_manager.verify_change_token(route, 1, stage_token_1)
    if token_check != True:
        return token_check
    
    stage_token_2 = request.form.get('stage_token_2')
    if not stage_token_2:
        return [stage_token_1]
    
    token_check = auth_token_manager.verify_change_token(route, 2, stage_token_2)
    if token_check != True:
        return token_check
    return [stage_token_1, stage_token_2]


def stage_1_validation(route, stage_token_1, auth_type_1, auth_type_2):
    password_validation = auth_validator.validate_password_for_auth()
    if password_validation != True:
        flash(password_validation, 'error')
        return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
    
    stage_token_2 = auth_token_manager.get_new_change_token(route, 2)
    return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                            stage_token_2=stage_token_2)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():

    if not auth_token_manager.attempt_check('route', 'change_email'):
        return redirect_to_scoreboard()
    
    auth_type_1, auth_type_2, auth_type_3 = get_auth_types('change', 'email')

    if request.method == 'GET':
        stage_token_1 = auth_token_manager.get_new_change_token('change_email', 1)
        return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
    
    choice = request.form.get('submit_button')
    if choice == 'Cancel':
        return redirect_to_scoreboard()
    
    stage_data = get_stage('change_email')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    elif stage_data == 'invalid_token':
        return redirect('/')

    elif len(stage_data) == 1 and choice == 'Confirm':
        return stage_1_validation('change_email', stage_data[0], auth_type_1, auth_type_2)
        
    elif len(stage_data) == 2 and choice == 'Confirm':
        stage_token_1, stage_token_2 = stage_data
            
        email_check = auth_validator.validate_new_email()
        if email_check != True:
            flash(email_check, 'error')
            return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                    stage_token_2=stage_token_2)
        
        try:
            current_user.email = request.form.get('email')
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if 'email' in str(e.orig):
                flash('An account with this email already exists.', 'error')
                return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                        stage_token_2=stage_token_2)

        return render_template('auth.html', auth_type=auth_type_3, user=current_user)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    if not auth_token_manager.attempt_check('route', 'change_password'):
        return redirect_to_scoreboard()
    
    auth_type_1, auth_type_2, auth_type_3 = get_auth_types('change', 'password')

    if request.method == 'GET':
        stage_token_1 = auth_token_manager.get_new_change_token('change_password', 1)
        return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
    
    choice = request.form.get('submit_button')
    if choice == 'Cancel':
        return redirect_to_scoreboard()
    
    stage_data = get_stage('change_password')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    elif stage_data == 'invalid_token':
        return redirect('/')

    elif len(stage_data) == 1 and choice == 'Confirm':
        return stage_1_validation('change_password', stage_data[0], auth_type_1, auth_type_2)
        
    elif len(stage_data) == 2 and choice == 'Confirm':
        stage_token_1, stage_token_2 = stage_data
            
        password_check = auth_validator.validate_new_password()
        if password_check != True:
            flash(password_check[0], 'error')
            return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                    stage_token_2=stage_token_2)
        
        hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        current_user.password_hashed = hashed_password
        db.session.commit()

        return render_template('auth.html', auth_type=auth_type_3, user=current_user)


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():

    if not auth_token_manager.attempt_check('route', 'change_password'):
        return redirect_to_scoreboard()
    
    auth_type_0, auth_type_1, auth_type_2, auth_type_3 = get_auth_types('delete', 'account', start_from=0)

    if request.method == 'GET':
        return render_template('auth.html', auth_type=auth_type_0)

    choice = request.form.get('submit_button')
    if choice == 'No' or choice == 'Cancel':
        return redirect_to_scoreboard()
    if choice == 'Yes':
        stage_token_1 = auth_token_manager.get_new_change_token('delete_account', 1)
        return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
    
    stage_data = get_stage('delete_account')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    
    elif stage_data == 'invalid_token':
        return redirect('/')

    elif len(stage_data) == 1 and choice == 'Confirm':
        return stage_1_validation('delete_account', stage_data[0], auth_type_1, auth_type_2)
    
    elif len(stage_data) == 2 and choice == 'Confirm':
            
        db.session.delete(current_user)
        db.session.commit()

        session.clear()

        return render_template('auth.html', auth_type=auth_type_3)
