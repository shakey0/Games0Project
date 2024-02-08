import pytest, sys, random, py, os
from Games0App.__init__ import create_app
from Games0App import db
from Games0App.models.test_table import RunTable
# from tests.seed_data import init_user
from playwright.sync_api import sync_playwright
from xprocess import ProcessStarter


@pytest.fixture(scope='function')
def test_app():
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def seed_test_database_for_test(test_app):
    with test_app.app_context():
        db.session.add(RunTable(name='first_record'))
        db.session.commit()


# @pytest.fixture(scope='function')
# def seed_test_database(test_app):
#     with test_app.app_context():
#         init_user(db)


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            yield page
        finally:
            browser.close()


@pytest.fixture(scope='session')
def flask_server(xprocess):
    python_executable = sys.executable
    app_file = py.path.local(__file__).dirpath("../run.py").realpath()
    port = str(random.randint(4000, 4999))
    class Starter(ProcessStarter):
        env = {"PORT": port, "FLASK_ENV": "testing", **os.environ}
        pattern = "Debugger PIN"
        args = [python_executable, app_file]

    xprocess.ensure('flask_app', Starter)

    yield f"localhost:{port}"

    xprocess.getinfo('flask_app').terminate()


@pytest.fixture()
def web_client(test_app):
    test_app.config['TESTING'] = True # This gets us better errors
    with test_app.test_client() as client:
        yield client
