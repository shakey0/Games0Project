from flask import Blueprint, render_template
from Games0App.extensions import db
from Games0App.models.user import User


user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/user/<username>')
def user_page(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user_page.html', user=user)
