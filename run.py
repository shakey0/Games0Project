from dotenv import load_dotenv
load_dotenv()

from Games0App import create_app
app = create_app()

import os
state = os.environ.get('FLASK_ENV', 'development')
if __name__ == '__main__':
    print(os.environ['SQLALCHEMY_DATABASE_URI'])
    if state == 'production':
        app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', 5000)))
    elif state == 'testing' or state == 'testing_in_actions':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=True, port=int(os.environ.get('PORT', 5000)))
