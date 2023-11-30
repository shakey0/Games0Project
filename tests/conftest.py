import pytest, sys, py, os
from flask import Flask
from Games0App import db
from Games0App.config import TestingConfig
from Games0App.models.test_table import RunTable
from tests.seed_data import init_user
from playwright.sync_api import sync_playwright
from xprocess import ProcessStarter

@pytest.fixture(scope='function')
def test_app():
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def seed_test_database_for_test(test_app):
    with test_app.app_context():
        db.session.add(RunTable(name='first_record'))
        db.session.commit()

@pytest.fixture(scope='function')
def seed_test_database(test_app):
    with test_app.app_context():
        init_user(db)

@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()

@pytest.fixture(scope='session')
def flask_server(xprocess):
    python_executable = sys.executable
    app_file = py.path.local(__file__).dirpath("../run.py").realpath()
    class Starter(ProcessStarter):
        pattern = "Running on http://127.0.0.1:5000"
        env = {"PORT": str(5000), "FLASK_ENV": "testing", **os.environ}
        args = [python_executable, app_file]

    xprocess.ensure('flask_app', Starter)

    yield f"http://localhost:5000/"

    xprocess.getinfo('flask_app').terminate()
