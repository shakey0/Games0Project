from flask import Blueprint, render_template, redirect, request, session, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from Games0App.extensions import db
from Games0App.mailjet_api import send_email
from Games0App.models.user import User
from Games0App.views.auth_functions import redirect_to_scoreboard, get_auth_types, get_stage, \
    do_stage_1, do_stage_2, complete_password_change
from Games0App.classes.auth_token_manager import AuthTokenManager
auth_token_manager = AuthTokenManager()
from Games0App.classes.auth_validator import AuthValidator
auth_validator = AuthValidator()
from Games0App.classes.logger import Logger
logger = Logger()
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
    user = User(username=request.form.get('username').lower(), email=request.form.get('email'),
                password_hashed=hashed_password, last_50_questions={})
    
    try:
        db.session.add(user)
        db.session.commit()

        login_user(user)

        send_email(user.email, user.username, 'sign_up_confirmation')

        return jsonify(success=True, message=f'Account created! Welcome, {user.username}!')
    
    except IntegrityError as e:
        db.session.rollback()
        if 'email' in str(e.orig):
            errors['email'] = 'An account with this email already exists.'
        elif 'username' in str(e.orig):
            errors['username'] = 'Username taken.'
        else:
            log_register_error('IntegrityError', str(e.orig))
            errors['error'] = 'Something went wrong. Please try again.'
        return jsonify(success=False, errors=errors)
    
    except Exception as e:
        db.session.rollback()
        log_register_error('UnknownError', str(e))
        return jsonify(success=False, errors={'error': 'Something went wrong. Please try again.'})

def log_register_error(error_type, error):
    json_log = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'error_type': error_type,
        'error': error
    }
    unique_id = logger.log_event(json_log, 'register', 'sign_up_error')
    print("\n\n" + error_type + "\n\n" + error + "\n")
    print('USER SIGN UP ERROR: ' + unique_id)


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
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hashed):
            login_user(user)
            return jsonify(success=True, message=f'Welcome, {user.username}!')
        
    if not auth_token_manager.check_login_password_attempt(credential):
        return jsonify(success=False, error="Too many attempts! Please wait 2 minutes.")
    
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
    
    if not auth_token_manager.check_reset_password_attempt():
        flash('For security reasons, please wait 1 hour before attempting this action.', 'error')
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
        
    send_email(current_user.email, current_user.username, 'change_email_confirmation')

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
        return jsonify(success=False, error="This email address is not registered.")
    
    if not auth_token_manager.attempt_check('reset_password_email_first', user.id):
        return jsonify(success=True, message="Please check your inbox.")
    
    if not auth_token_manager.attempt_check('reset_password_email', user.id):
        return jsonify(success=False, error="Too many attempts! Please wait 10 minutes.")
    
    reset_password_link = auth_token_manager.get_reset_password_link_token(user.id)

    print('RESET PASSWORD LINK:', f'localhost:5000/reset_password/{reset_password_link}')
    send_email(user.email, user.username, 'reset_password_link', reset_token=reset_password_link)

    return jsonify(success=True, message="Reset password link sent.")


@auth.route('/reset_password/<reset_token>')
def reset_password(reset_token):

    user_id = auth_token_manager.verify_reset_password_link_token(reset_token)
    if not user_id:
        flash('Link expired.', 'error')
        return redirect('/')
    
    auth_type_2, auth_type_3 = get_auth_types('reset', 'password', start_from=2)
    stage_token_1 = auth_token_manager.get_new_stage_token('reset_password', 1, parsed_user_id=user_id)
    stage_token_2 = auth_token_manager.get_new_stage_token('reset_password', 2, parsed_user_id=user_id)

    return render_template('auth.html', reset_token=reset_token, auth_type=auth_type_2,
                            stage_token_1=stage_token_1, stage_token_2=stage_token_2)


@auth.route('/reset_password', methods=['POST'])
def reset_password_():

    reset_token = request.form.get('reset_token') # AFTER TESTING CONSIDER WHETHER AN ABSENCE OF THIS SHOULD BE LOGGED
    choice = request.form.get('submit_button')
    if not reset_token or choice != 'Confirm':
        return redirect('/')
    
    user_id = auth_token_manager.verify_reset_password_link_token(reset_token)
    if not user_id:
        flash('It looks like your link probably expired. Please try again.', 'error')
        return redirect('/')
    
    stage_token_1 = request.form.get('stage_token_1')
    stage_token_2 = request.form.get('stage_token_2')
    result_1 = auth_token_manager.verify_stage_token('reset_password', 1, stage_token_1, parsed_user_id=user_id)
    result_2 = auth_token_manager.verify_stage_token('reset_password', 2, stage_token_2, parsed_user_id=user_id)
    if result_1 != True or result_2 != True:
        if result_1 == 'expired_token' or result_2 == 'expired_token':
            flash('It looks like your link probably reached its expiry. Please try again.', 'error')
        return redirect('/')
    
    auth_type_2, auth_type_3 = get_auth_types('reset', 'password', start_from=2)

    password_check = auth_validator.validate_new_password()
    if password_check != True:
        flash(password_check[0], 'error')
        return render_template('auth.html', reset_token=reset_token, auth_type=auth_type_2,
                                stage_token_1=stage_token_1, stage_token_2=stage_token_2)
    
    auth_token_manager.delete_reset_password_link_token(reset_token)

    hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash('Something certainly didn\'t look right there.', 'error')
        return redirect('/')
    user.password_hashed = hashed_password
    db.session.commit()

    return complete_password_change(user, auth_type_3)


@auth.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    
    if request.method == 'GET':

        issue_id = request.args.get('issue_id')
        if issue_id is None:
            issue_id = ''

        log = logger.get_log_by_unique_id(issue_id) if issue_id else None

        user_id = log.user_id if log else current_user.id if current_user.is_authenticated else 0
        if user_id == 0:
            flash('Please log in or follow a link sent via email to report an issue.', 'error')
            return redirect('/')
        
        date_time = log.timestamp if log else ''
        if date_time:
            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
            # MAKE FUNCTION TO FORMAT DATE AND TIME APPROPRIATELY
            pass

        values = {
            'user_id': user_id,
            'issue_id': issue_id,
            'date_time': date_time,
            'stage': 1
        }
        auth_token = auth_token_manager.get_new_auth_token(values)
        
        return render_template('report_issue.html', token=auth_token, values=values)

    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')

    value_names = ['user_id', 'issue_id', 'date_time', 'stage']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()):
        return redirect('/')
    
    if values['stage'] == '1':

        values['stage'] = 2

        issue_type = request.form.get('issue_type')
        values['issue'] = issue_type
        issue_titles = {
            'password_change': 'Unauthorised Password Change',
            'security_alert': 'Security Alert',
            'other_problem': 'Problem'
        }
        values['title'] = issue_titles[issue_type]

        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('report_issue.html', token=auth_token, values=values)
    
    value_names = ['user_id', 'issue_id', 'date_time', 'stage', 'issue', 'title']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()):
        return redirect('/')

    if values['stage'] == '2':

        values['stage'] = 3

        if not values['issue_id']:
            issue_id = request.form.get('issue_id')
            values['issue_id'] = issue_id

        description = request.form.get('description')
        values['description'] = description

        unique_id = logger.log_event(values, 'report_issue', values['issue'] + '_ISSUE_REPORTED')
        print(values['title'].upper() + ' REPORTED: ', unique_id)

        auth_token_manager.delete_auth_token(auth_token)

        return render_template('report_issue.html', token=auth_token, values=values)

    return redirect('/')
