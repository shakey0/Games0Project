from flask import Blueprint, render_template, redirect, request, session, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from Games0App.extensions import db
from Games0App.mailjet_api import send_email
from Games0App.models.user import User
from Games0App.views.auth_functions import redirect_to_scoreboard, get_auth_types, get_stage, \
    do_stage_1, do_stage_2, do_stage_2_reset_password, complete_password_change
from Games0App.classes.auth_token_manager import AuthTokenManager
auth_token_manager = AuthTokenManager()
from Games0App.classes.auth_validator import AuthValidator
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

        # send_email(user.email, user.username) # - DISABLED FOR NOW

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


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():

    if not auth_token_manager.attempt_check('route', 'change_email'):
        return redirect_to_scoreboard()
    
    auth_type_1, auth_type_2, auth_type_3 = get_auth_types('change', 'email')

    if request.method == 'GET':
        return do_stage_1(auth_type_1, 'change_email')
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect_to_scoreboard()
    
    result, stage_data = get_stage('change_email')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    elif stage_data == 'invalid_token':
        return redirect('/')
    if result != True:
        return redirect_to_scoreboard()

    if len(stage_data) == 1:
        return do_stage_2('change_email', stage_data[0], auth_type_1, auth_type_2)
        
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
        return do_stage_1(auth_type_1, 'change_password')
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect_to_scoreboard()
    
    result, stage_data = get_stage('change_password')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    elif stage_data == 'invalid_token':
        return redirect('/')
    if result != True:
        return redirect_to_scoreboard()

    if len(stage_data) == 1:
        return do_stage_2('change_password', stage_data[0], auth_type_1, auth_type_2)
        
    stage_token_1, stage_token_2 = stage_data
        
    password_check = auth_validator.validate_new_password()
    if password_check != True:
        flash(password_check[0], 'error')
        return render_template('auth.html', auth_type=auth_type_2, stage_token_1=stage_token_1,
                                stage_token_2=stage_token_2)
    
    hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    current_user.password_hashed = hashed_password
    db.session.commit()

    return complete_password_change(current_user, auth_type_3)


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():

    if not auth_token_manager.attempt_check('route', 'delete_account'):
        return redirect_to_scoreboard()
    
    if not auth_token_manager.check_reset_password_attempt():
        flash('For security reasons, please wait 1 hour before attempting this action.', 'error')
        print('DELETE ACCOUNT DENIED')
        return redirect_to_scoreboard()
    
    auth_type_0, auth_type_1, auth_type_2, auth_type_3 = get_auth_types('delete', 'account', start_from=0)

    if request.method == 'GET':
        return render_template('auth.html', auth_type=auth_type_0)

    choice = request.form.get('submit_button')
    if choice == 'Yes':
        return do_stage_1(auth_type_1, 'delete_account')
    elif choice != 'Confirm':
        return redirect_to_scoreboard()
    
    result, stage_data = get_stage('delete_account')

    if stage_data == 'expired_token':
        return redirect_to_scoreboard()
    elif stage_data == 'invalid_token':
        return redirect('/')
    if result != True:
        return redirect_to_scoreboard()

    if len(stage_data) == 1:
        return do_stage_2('delete_account', stage_data[0], auth_type_1, auth_type_2)
            
    db.session.delete(current_user)
    db.session.commit()

    session.clear()

    return render_template('auth.html', auth_type=auth_type_3)


@auth.route('/send_reset_password_link', methods=['POST'])
def send_reset_password_link():
    
    email = request.form.get('email')
    if not email:
        return jsonify(success=False, error="Please enter your email address.")
    
    user = User.query.filter_by(email=email).first()
    if not user:
        print('EMAIL NOT FOUND:', email)
        return jsonify(success=False, error="This email address is not registered.")
    
    if not auth_token_manager.attempt_check('reset_password_email_first', user.id):
        return jsonify(success=True, message="Please check your inbox.")
    
    if not auth_token_manager.attempt_check('reset_password_email', user.id):
        return jsonify(success=False, error="Too many attempts! Please wait 10 minutes.")
    
    reset_password_link = auth_token_manager.get_reset_password_link_token(user.id)

    print('RESET PASSWORD LINK:', f'localhost:5000/reset_password/{reset_password_link}')

    # send_email(user.email, user.username, reset_token=reset_password_link) # - DISABLED FOR NOW

    return jsonify(success=True, message="Reset password link sent.")


@auth.route('/reset_password/<reset_token>')
def reset_password(reset_token):

    user_id = auth_token_manager.verify_reset_password_link_token(reset_token)
    if not user_id:
        flash('Link expired.', 'error')
        return redirect('/')
    
    return do_stage_2_reset_password(reset_token, user_id, revert=False)


@auth.route('/security/<reset_token>')
def reverse_reset_password(reset_token):

    user_id = auth_token_manager.verify_reset_password_link_token(reset_token, revert=True)
    if not user_id:
        flash('Link expired.', 'error')
        return redirect('/')
    
    return do_stage_2_reset_password(reset_token, user_id, revert=True)


@auth.route('/reset_password', methods=['POST'])
def reset_password_():

    reset_token = request.form.get('reset_token')
    choice = request.form.get('submit_button')
    if not reset_token or choice != 'Confirm':
        return redirect('/')
    
    revert = True if request.form.get('revert') == 'revert' else False
    user_id = auth_token_manager.verify_reset_password_link_token(reset_token, revert=revert)
    if not user_id:
        flash('It looks like your link probably expired. Please try again.', 'error')
        return redirect('/')
    
    stage_token_1 = request.form.get('stage_token_1')
    stage_token_2 = request.form.get('stage_token_2')
    result_1 = auth_token_manager.verify_change_token('reset_password', 1, stage_token_1, parsed_user_id=user_id)
    result_2 = auth_token_manager.verify_change_token('reset_password', 2, stage_token_2, parsed_user_id=user_id)
    if result_1 != True or result_2 != True:
        flash('Something certainly didn\'t look right there.', 'error')
        return redirect('/')
    
    auth_type_2, auth_type_3 = get_auth_types('reset', 'password', start_from=2)

    password_check = auth_validator.validate_new_password()
    if password_check != True:
        flash(password_check[0], 'error')
        return render_template('auth.html', reset_token=reset_token, auth_type=auth_type_2,
                                stage_token_1=stage_token_1, stage_token_2=stage_token_2, revert=revert)
    
    auth_token_manager.delete_reset_password_link_token(reset_token)

    hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash('Something certainly didn\'t look right there.', 'error')
        return redirect('/')
    user.password_hashed = hashed_password
    db.session.commit()

    return complete_password_change(user, auth_type_3)
