from mailjet_rest import Client
import os


def send_email(user_email, username, reset_token=None):

	api_key = os.environ.get('MAILJET_API_KEY')
	api_secret = os.environ.get('MAILJET_SECRET_KEY')
	mailjet = Client(auth=(api_key, api_secret), version='v3.1')

	if not reset_token:
		name_type = 'GamesZero Confirmation'
		subject = 'Welcome to GamesZero!'
		text_part = f'Hello {username},\n\nWelcome to GamesZero!\n\nPlease enjoy these wonderful games/quizzes and have fun!\n\nAll the best,\nshakey0'
		html_part = f'<h3>Hello {username},</h3><br /><br /><h3>Welcome to GamesZero!</h3><br /><br /><h3>Please enjoy these wonderful games/quizzes and have fun!</h3><br /><br />All the best,<br />shakey0'
	else:
		name_type = 'GamesZero Password Reset'
		subject = 'Reset Password'
		text_part = f'To reset your password, link on the following link and follow the instructions:\n\ngames0-by-shakey0.onrender.com/{reset_token}\n\nIf you did not make this request, please ignore this email and no changes will be made.\n\nAll the best,\nshakey0'
		html_part = f'<h3>To reset your password, link on the following link and follow the instructions:</h3><br /><br /><a href="games0-by-shakey0.onrender.com/{reset_token}">games0-by-shakey0.onrender.com/{reset_token}</a><br /><br /><h3>If you did not make this request, please ignore this email and no changes will be made.</h3><br /><br />All the best,<br />shakey0'

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

	result = mailjet.send.create(data=data)
	print(result.status_code)
	print(result.json())
