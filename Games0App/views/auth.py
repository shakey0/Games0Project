from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required
from Games0App.extensions import db
from Games0App.mailjet_api import send_email
from Games0App.models.user import User
from Games0App.classes.auth_token_manager import auth_token_manager
from Games0App.classes.auth_validator import auth_validator
from Games0App.classes.logger import logger
from Games0App.utils import format_datetime
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
    user = User(username=request.form.get('username').lower().strip(), email=request.form.get('email').strip(),
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
        'username': request.form.get('username').lower().strip(),
        'email': request.form.get('email').strip(),
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


def redirect_to_scoreboard():
    return redirect(url_for('scoreboard.scoreboard_page', username=current_user.username))


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    if not auth_token_manager.attempt_check('route', 'change_email'):
        flash('Something seems odd here. Please wait 1 minute before trying again.', 'error')
        return redirect_to_scoreboard()
    if not auth_token_manager.check_reset_password_attempt():
        flash('For security reasons, please wait 1 hour before attempting this action.', 'error')
        return redirect_to_scoreboard()

    if request.method == 'GET':
        
        values = {
            'user_id': current_user.id,
            'username': current_user.username,
            'current_email': current_user.email,
            'stage': 1,
            'route': 'change_email',
            'title': 'Change Email',
            'message': ''
        }
        auth_token = auth_token_manager.get_new_auth_token(values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect_to_scoreboard()
    
    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')
    
    value_names = ['user_id', 'username', 'current_email', 'stage', 'route', 'title', 'message']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()) or not values:
        flash('Sorry! You took too long. Please try again.', 'error')
        return redirect_to_scoreboard()
    if int(values['user_id']) != current_user.id:
        flash('Sorry! Something seems odd here.', 'error')
        return redirect_to_scoreboard()
    
    if values['stage'] == '1':
        values['stage'] = 1
        
        password_validation = auth_validator.validate_password_for_auth()
        if password_validation != True:
            flash(password_validation, 'error')
            return render_template('auth.html', token=auth_token, values=values)
        
        values['stage'] = 2
        values['message'] = 'Your new email address:'
        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if values['stage'] == '2':
        values['stage'] = 2
        
        email_check = auth_validator.validate_new_email()
        if email_check != True:
            flash(email_check, 'error')
            return render_template('auth.html', token=auth_token, values=values)

        try:
            current_user.email = request.form.get('email').strip()
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if 'email' in str(e.orig):
                flash('An account with this email already exists.', 'error')
                return render_template('auth.html', token=auth_token, values=values)
            
        values['stage'] = 3
        values['message'] = 'Email successfully changed!'
        values['new_email'] = request.form.get('email').strip()

        json_log = {
            'user_id': current_user.id,
            'username': current_user.username,
            'old_email': values['current_email'],
            'new_email': values['new_email']
        }
        unique_id = logger.log_event(json_log, 'change_email', 'email_changed')
        print('EMAIL CHANGED: ', unique_id)
        send_email(values['new_email'], current_user.username, 'changed_email_confirmation',
                    unique_id=unique_id)
        send_email(values['current_email'], current_user.username, 'changed_email_notification',
                    unique_id=unique_id, new_email=values['new_email'])

        auth_token_manager.delete_auth_token(auth_token)

        return render_template('auth.html', token=auth_token, values=values)
    
    return redirect('/')


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not auth_token_manager.attempt_check('route', 'change_password'):
        flash('Something seems odd here. Please wait 1 minute before trying again.', 'error')
        return redirect_to_scoreboard()

    if request.method == 'GET':
        
        values = {
            'user_id': current_user.id,
            'username': current_user.username,
            'stage': 1,
            'route': 'change_password',
            'title': 'Change Password',
            'message': ''
        }
        auth_token = auth_token_manager.get_new_auth_token(values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect_to_scoreboard()
    
    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')
    
    value_names = ['user_id', 'username', 'stage', 'route', 'title', 'message']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()) or not values:
        flash('Sorry! You took too long. Please try again.', 'error')
        return redirect_to_scoreboard()
    if int(values['user_id']) != current_user.id:
        flash('Sorry! Something seems odd here.', 'error')
        return redirect_to_scoreboard()
    
    if values['stage'] == '1':
        values['stage'] = 1
        
        password_validation = auth_validator.validate_password_for_auth()
        if password_validation != True:
            flash(password_validation, 'error')
            return render_template('auth.html', token=auth_token, values=values)
        
        values['stage'] = 2
        values['message'] = 'Your new password:'
        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if values['stage'] == '2':
        values['stage'] = 2
        
        password_check = auth_validator.validate_new_password()
        if password_check != True:
            flash(password_check[0], 'error')
            return render_template('auth.html', token=auth_token, values=values)

        hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        current_user.password_hashed = hashed_password
        db.session.commit()

        values['stage'] = 3
        values['message'] = 'Password successfully changed!'
        
        json_log = {
            'user_id': current_user.id,
            'username': current_user.username
        }
        unique_id = logger.log_event(json_log, 'change_password', 'password_changed')
        print('PASSWORD CHANGED: ', unique_id)
        send_email(current_user.email, current_user.username, 'changed_password_confirmation',
                    unique_id=unique_id)

        auth_token_manager.attempt_check('reset_password', current_user.id)

        auth_token_manager.delete_auth_token(auth_token)

        return render_template('auth.html', token=auth_token, values=values)
    
    return redirect('/')


@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if not auth_token_manager.attempt_check('route', 'change_email'):
        flash('Something seems odd here. Please wait 1 minute before trying again.', 'error')
        return redirect_to_scoreboard()
    if not auth_token_manager.check_reset_password_attempt():
        flash('For security reasons, please wait 1 hour before attempting this action.', 'error')
        return redirect_to_scoreboard()
    
    if request.method == 'GET':
            
        values = {
            'user_id': current_user.id,
            'username': current_user.username,
            'stage': 0,
            'route': 'delete_account',
            'title': 'Delete Account',
            'message': ''
        }
        auth_token = auth_token_manager.get_new_auth_token(values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect_to_scoreboard()
    
    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')
    
    value_names = ['user_id', 'username', 'stage', 'route', 'title', 'message']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()) or not values:
        flash('Sorry! You took too long. Please try again.', 'error')
        return redirect_to_scoreboard()
    if int(values['user_id']) != current_user.id:
        flash('Sorry! Something seems odd here.', 'error')
        return redirect_to_scoreboard()
    
    if values['stage'] == '0':
        values['stage'] = 1

        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if values['stage'] == '1':
        values['stage'] = 1

        password_validation = auth_validator.validate_password_for_auth()
        if password_validation != True:
            flash(password_validation, 'error')
            return render_template('auth.html', token=auth_token, values=values)
        
        values['stage'] = 2
        values['message'] = 'Are you absolutely sure you want to delete your account? This cannot be undone!'
        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if values['stage'] == '2':
        values['stage'] = 3

        db.session.delete(current_user)
        db.session.commit()
        session.clear()

        values['message'] = 'Account successfully deleted!'

        json_log = {
            'user_id': values['user_id'],
            'username': values['username']
        }
        unique_id = logger.log_event(json_log, 'delete_account', 'account_deleted')
        print('ACCOUNT DELETED: ', unique_id)

        auth_token_manager.delete_auth_token(auth_token)

        return render_template('auth.html', token=auth_token, values=values)
    
    return redirect('/')


@auth.route('/send_reset_password_link', methods=['POST'])
def send_reset_password_link():
    
    email = request.form.get('email')
    if not email:
        return jsonify(success=False, error="Please enter your email address.")
    email = email.strip()
    
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


@auth.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):

    user_id = auth_token_manager.verify_reset_password_link_token(reset_token)
    if not user_id:
        flash('Link expired. Please request a new link.', 'error')
        return redirect('/')

    if request.method == 'GET':
            
        username = User.query.filter_by(id=user_id).first().username
        if not username:
            flash('Something certainly didn\'t look right there.', 'error')
            return redirect('/')
        
        values = {
            'user_id': user_id,
            'username': username,
            'stage': 2,
            'route': f'reset_password/{reset_token}',
            'title': 'Reset Password',
            'message': 'Your new password:'
        }
        auth_token = auth_token_manager.get_new_auth_token(values)

        return render_template('auth.html', token=auth_token, values=values)
    
    if request.form.get('submit_button') != 'Confirm':
        return redirect('/')
    
    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')
    
    value_names = ['user_id', 'username', 'stage', 'route', 'title', 'message']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()) or not values:
        flash('Sorry! You took too long. Please try again.', 'error')
        return redirect('/')
    if int(values['user_id']) != user_id:
        flash('Sorry! Something seems odd here.', 'error')
        return redirect('/')
    
    if values['stage'] == '2':
        values['stage'] = 2

        password_check = auth_validator.validate_new_password()
        if password_check != True:
            flash(password_check[0], 'error')
            return render_template('auth.html', token=auth_token, values=values)
        
        values['stage'] = 3
        
        auth_token_manager.delete_reset_password_link_token(reset_token)

        hashed_password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        user = User.query.filter_by(id=user_id).first()
        if not user:
            flash('Something certainly didn\'t look right there.', 'error')
            return redirect('/')
        user.password_hashed = hashed_password
        db.session.commit()

        values['message'] = 'Password successfully reset!'

        json_log = {
            'user_id': user.id,
            'username': user.username,
            'reset_token': reset_token
        }
        unique_id = logger.log_event(json_log, 'reset_password', 'password_reset')
        print('PASSWORD RESET: ', unique_id)
        send_email(user.email, user.username, 'reset_password_confirmation', unique_id=unique_id)

        auth_token_manager.delete_auth_token(auth_token)

        auth_token_manager.attempt_check('reset_password', user.id)

        return render_template('auth.html', token=auth_token, values=values)
    
    return redirect('/')


@auth.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    
    issues = {
        'password_change': {'title': 'Unauthorised Password Change', 'message': 'My password was changed and I did NOT do it.'},
        'email_change': {'title': 'Unauthorised Email Change', 'message': 'My email was changed and I did NOT do it.'},
        'security_alert': {'title': 'Security Alert', 'message': 'I received a security alert via email.'},
        'other_problem': {'title': 'Problem', 'message': 'An error occurred and I\'d like to report it.'}
    }

    if request.method == 'GET':

        issue_id = request.args.get('issue_id')
        if issue_id is None:
            issue_id = ''

        log = logger.get_log_by_unique_id(issue_id) if issue_id else None

        user_id = log.user_id if log else current_user.id if current_user.is_authenticated else 0
        if user_id == 0:
            flash('Please log in or follow a link sent via email to report an issue.', 'error')
            return redirect('/')
        
        date_time_issue_occurred = log.timestamp if log else ''
        if date_time_issue_occurred:
            date_time_issue_occurred = format_datetime(date_time_issue_occurred)

        values = {
            'user_id': user_id,
            'issue_id': issue_id,
            'issue': '',
            'title': '',
            'date_time_issue_occurred': date_time_issue_occurred,
            'stage': 1
        }
        auth_token = auth_token_manager.get_new_auth_token(values)
        
        return render_template('report_issue.html', token=auth_token, values=values, issues=issues)

    auth_token = request.form.get('auth_token')
    if not auth_token:
        return redirect('/')

    value_names = ['user_id', 'issue_id', 'date_time_issue_occurred', 'stage', 'issue', 'title']
    values = auth_token_manager.get_values_from_auth_token(auth_token, value_names)
    if any(v is None for v in values.values()) or not values:
        return redirect('/')
    
    if values['stage'] == '1':
        values['stage'] = 2

        issue_type = request.form.get('issue_type')
        values['issue'] = issue_type
        values['title'] = issues[issue_type]['title']

        auth_token_manager.add_values_to_auth_token(auth_token, values)

        return render_template('report_issue.html', token=auth_token, values=values)

    if values['stage'] == '2':
        values['stage'] = 3

        if not values['issue_id']:
            issue_id = request.form.get('issue_id')
            values['issue_id'] = issue_id

        description = request.form.get('issue_description')
        values['description'] = description

        json_log = {
            'user_id': values['user_id'],
            'issue_id': values['issue_id'],
            'date_time_issue_occurred': values['date_time_issue_occurred'],
            'description': description
        }
        unique_id = logger.log_event(json_log, 'report_issue', values['issue'] + '_ISSUE_REPORTED')
        print(values['title'].upper() + ' REPORTED: ', unique_id)
        user = User.query.filter_by(id=values['user_id']).first()
        if user:
            send_email(user.email, user.username, 'issue_report_confirmation', unique_id=unique_id, issue_title=values['title'])

        auth_token_manager.delete_auth_token(auth_token)

        return render_template('report_issue.html', token=auth_token, values=values)

    return redirect('/')
