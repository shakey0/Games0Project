from mailjet_rest import Client
from Games0App.extensions import db
from Games0App.models.email_log import EmailLog
from Games0App.classes.logger import Logger
logger = Logger()
import os
from datetime import datetime


def send_email(user_email, username, reset_token='', not_user_token='', auth_password=False, unique_id=''):

	api_key = os.environ.get('MAILJET_API_KEY')
	api_secret = os.environ.get('MAILJET_SECRET_KEY')
	mailjet = Client(auth=(api_key, api_secret), version='v3.1')

	if not reset_token and not not_user_token and not auth_password and not unique_id:
		email_log_type = 'sign_up_confirmation'
		email_info = ''
		name_type = 'GamesZero Confirmation'
		subject = 'Welcome to GamesZero!'
		text_part = f'Hello {username},\n\nWelcome to GamesZero!\n\nPlease enjoy these wonderful games/quizzes and have fun!\n\nAll the best,\nshakey0'
		html_part = f'<h3>Hello {username},</h3><h3>Welcome to GamesZero!</h3><h3>Please enjoy these wonderful games/quizzes and have fun!</h3><h3>All the best,</h3><h3>shakey0</h3>'
	elif reset_token:
		email_log_type = 'reset_password_request'
		email_info = reset_token
		name_type = 'GamesZero Password Reset'
		subject = 'Your Reset Password Link'
		text_part = f'To reset your password, click on the following link and follow the instructions:\n\nhttps://games0-by-shakey0.onrender.com/reset_password/{reset_token} \n\nIf you did not make this request, please ignore this email and no changes will be made.\n\nAll the best,\nshakey0'
		html_part = f'<h3>To reset your password, click on the following link and follow the instructions:</h3><a href="https://games0-by-shakey0.onrender.com/reset_password/{reset_token}">games0-by-shakey0.onrender.com/reset_password/{reset_token}</a><br /><h3>If you did not make this request, please ignore this email and no changes will be made.</h3><h3>All the best,</h3><h3>shakey0</h3>'
	elif not_user_token:
		email_log_type = 'reset_password_confirmation'
		email_info = not_user_token
		name_type = 'GamesZero Password Reset'
		subject = 'Password Reset'
		text_part = f'Hi {username},\n\nYour GamesZero password has been reset.\n\nIf you did this, that\'s fantastic and you don\'t need to do anything. However, if you didn\'t do this, please click on the link below and follow the instructions.\n\nhttps://games0-by-shakey0.onrender.com/security/{not_user_token} \n\nAll the best,\nshakey0'
		html_part = f'<h3>Hi {username},</h3><h3>Your GamesZero password has been reset.</h3><h3>If you did this, that\'s fantastic and you don\'t need to do anything. However, if you didn\'t do this, please click on the link below and follow the instructions.</h3><a href="https://games0-by-shakey0.onrender.com/security/{not_user_token}">games0-by-shakey0.onrender.com/security/{not_user_token}</a><br /><h3>All the best,</h3><h3>shakey0</h3>'
	elif auth_password and unique_id:
		email_log_type = 'auth_password_max_attempts'
		email_info = ''
		name_type = 'GamesZero Security'
		subject = 'Security Alert - ' + unique_id
		text_part = f'Hi {username},\n\nAn incorrect password was recently entered 3 times while trying to make adjustments to your account. If you did not initiate this action, please contact me immediately. You can reply to this email to contact me. You may also consider changing your password.\n\nAll the best,\nshakey0'
		html_part = f'<h3>Hi {username},</h3><h3>An incorrect password was recently entered 3 times while trying to make adjustments to your account. If you did not initiate this action, please contact me immediately. You can reply to this email to contact me. You may also consider changing your password.</h3><h3>All the best,</h3><h3>shakey0</h3>'
	elif unique_id:
		email_log_type = 'security_alert'
		email_info = unique_id
		name_type = 'GamesZero Security'
		subject = 'Security Alert - ' + unique_id
		text_part = f'Hi {username},\n\nYou were recently logged out of your account due to a security issue. If you did not initiate this action, please contact me immediately. You can reply to this email to contact me.\nYou may also consider changing your password.\n\nAll the best,\nshakey0'
		html_part = f'<h3>Hi {username},</h3><h3>You were recently logged out of your account due to a security issue. If you did not initiate this action, please contact me immediately. You can reply to this email to contact me.</h3><h3>You may also consider changing your password.</h3><h3>All the best,</h3><h3>shakey0</h3>'
	else:
		json_log = {
			'user_email': user_email,
			'username': username,
			'reset_token': reset_token,
			'not_user_token': not_user_token,
			'auth_password': auth_password,
			'unique_id': unique_id
		}
		unique_log_id = logger.log_event(json_log, 'send_email', 'invalid_parameters')
		print('Send_email function called with invalid parameters: ', user_email, username, reset_token, not_user_token, auth_password, unique_id)
		print('EMAIL ERROR: ' + unique_log_id)
		return

	data = {
		'Messages': [
			{
				"From": {
					"Email": os.environ.get('MY_EMAIL_ADDRESS'),
					"Name": name_type
				},
				"To": [
					{
						"Email": user_email,
						"Name": user_email
					}
				],
				"Subject": subject,
				"TextPart": text_part,
				"HTMLPart": html_part
			}
		]
	}

	class Result: # FOR TESTING PURPOSES
		def __init__(self, status_code, json):
			self.status_code = status_code
			self.json = json
	result = Result(200, {'success': True})
	# result = mailjet.send.create(data=data) # DISABLED TO PREVENT EMAILS BEING SENT
	# print(result.status_code)
	# print(result.json())
	
	email_log = EmailLog(
		user_email=user_email,
		username=username,
		email_type=email_log_type,
		info=email_info,
		status_code=result.status_code,
		json_response=result.json,
		timestamp=datetime.utcnow()
	)
	db.session.add(email_log)
	db.session.commit()
