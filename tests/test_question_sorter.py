from Games0App.models.log import Log
from Games0App.classes.question_sorter import question_sorter


def test_validate_blank_added(test_app):
    assert question_sorter.validate_blank_added(1, ['test', 'test'], 'This is a test ____') == True
    assert question_sorter.validate_blank_added(1, ['test', 'test'], 'This is a test') == False
    logs = Log.query.all()
    assert len(logs) == 1

