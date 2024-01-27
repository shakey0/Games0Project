from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
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


def get_auth_type(title, stage, route, message):
    return {'title': title, 'stage': stage, 'route': route, 'message': message}


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():

    if not auth_token_manager.attempt_check('route', 'change_email'):
        return redirect(url_for('scoreboard.scoreboard_page', username=current_user.username))

    auth_type_1 = get_auth_type('Change Email', 1, 'change_email', '')
    auth_type_2 = get_auth_type('Change Email', 2, 'change_email', 'Your new email address:')
    auth_type_3 = get_auth_type('Change Email', 3, 'change_email', 'Email address successfully changed!')

    if request.method == 'GET':
        stage_token_1 = auth_token_manager.get_new_change_token('change_email', 1)
        return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
    
    stage_token_1 = request.form.get('stage_token_1')
    if not stage_token_1:
        print("MISSING TOKEN")
        return redirect(url_for('scoreboard.scoreboard', username=current_user.username))
    
    stage_token_2 = request.form.get('stage_token_2')

    if stage_token_1 and not stage_token_2:
        if auth_token_manager.verify_change_token('change_email', 1, stage_token_1):

            password_validation = auth_validator.validate_password_for_auth()
            if password_validation != True:
                flash(password_validation, 'error')
                return render_template('auth.html', auth_type=auth_type_1, stage_token_1=stage_token_1)
            
            stage_token_2 = auth_token_manager.get_new_change_token('change_email', 2)
            return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                    stage_token_2=stage_token_2)
        else:
            print("INVALID TOKEN - ALERT!!!")
            logout_user()
            flash("A security threat was detected. You've been logged out.", 'error')
            # Log this event
            return redirect('/')
        
    elif stage_token_1 and stage_token_2:
        if auth_token_manager.verify_change_token('change_email', 1, stage_token_1) and \
            auth_token_manager.verify_change_token('change_email', 2, stage_token_2):
            
            email_check = auth_validator.validate_new_email()
            if email_check != True:
                flash(email_check, 'error')
                return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                        stage_token_2=stage_token_2)
            
            current_user.email = request.form.get('email')
            db.session.commit()

            return render_template('auth.html', auth_type=auth_type_3, user=current_user)
        
        else:
            print("INVALID TOKEN - ALERT!!!")
            logout_user()
            flash("A security threat was detected. You've been logged out.", 'error')
            # Log this event
            return redirect('/')


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'GET':
        stage_token_1 = auth_token_manager.get_new_change_token('change_email', 1)
        auth_type = {'title': 'Change Password', 'stage': 0, 'route': 'change_password', 'message': ''}
        return render_template('auth.html', auth_type=auth_type, stage_token_1=stage_token_1)


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'GET':
        stage_token_1 = auth_token_manager.get_new_change_token('change_email', 1)
        auth_type = {'title': 'Delete Account', 'stage': 0, 'route': 'delete_account', 'message': ''}
        return render_template('auth.html', auth_type=auth_type, stage_token_1=stage_token_1)
