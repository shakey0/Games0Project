from flask import Blueprint, redirect, request, jsonify
from flask_login import login_user, logout_user
from Games0App.extensions import db
from Games0App.models.user import User
from sqlalchemy.exc import IntegrityError
import bcrypt


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    errors = {}
    username = request.form.get('username')
    if not username:
        errors['username'] = 'Please enter a username.'
    elif len(username) < 3:
        errors['username'] = 'Username must be at least 4 characters.'
    elif len(username) > 20:
        errors['username'] = 'Username must be max 20 characters.'
    email = request.form.get('email')
    if not email:
        errors['email'] = 'Please enter an email.'
    elif len(email) < 3:
        errors['email'] = 'Email must be at least 4 characters.'
    password = request.form.get('password')
    if not password:
        errors['password'] = 'Please enter a password.'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters.'
    confirm_password = request.form.get('confirm_password')
    if not confirm_password:
        errors['confirm_password'] = 'Please confirm your password.'
    if not password == confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'
    if errors:
        return jsonify(success=False, errors=errors)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # NEED TO GET GAMES PLAYED AND GAMES TRACKER FROM CLIENT COOKIE SESSION
    user = User(username=request.form.get('username'), email=request.form.get('email'), password_hashed=hashed_password,
                games_played={}, games_tracker={})
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
def logout():
    logout_user()
    return redirect('/')
