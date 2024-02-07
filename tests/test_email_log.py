from Games0App import db
from Games0App.models.email_log import EmailLog
from datetime import datetime


def test_email_log_creation(test_app):
            
    test_email_log = EmailLog(
        user_email='test_email',
        username='test_username',
        email_type='test',
        info={'test_info': 'test_info'},
        unique_id='unique_id',
        status_code=200,
        json_response={'test_response': 'test_response'},
        timestamp=datetime(2021, 1, 1, 0, 0, 0)
    )
    db.session.add(test_email_log)
    db.session.commit()

    email_log = EmailLog.query.filter_by(unique_id='unique_id').first()
    assert email_log is not None
    assert email_log.id == 1
    assert email_log.user_email == 'test_email'
    assert email_log.username == 'test_username'
    assert email_log.email_type == 'test'
    assert email_log.info == {'test_info': 'test_info'}
    assert email_log.unique_id == 'unique_id'
    assert email_log.status_code == 200
    assert email_log.json_response == {'test_response': 'test_response'}
    assert email_log.timestamp == datetime(2021, 1, 1, 0, 0, 0)


def test_email_log_instances_are_equal(test_app):
    email_log1 = EmailLog(
        id=1,
        user_email='test_email',
        username='test_username',
        email_type='test',
        info={'test_info': 'test_info'},
        unique_id='unique_id',
        status_code=200,
        json_response={'test_response': 'test_response'},
        timestamp=datetime(2021, 1, 1, 0, 0, 0)
    )
    email_log2 = EmailLog(
        id=1,
        user_email='test_email',
        username='test_username',
        email_type='test',
        info={'test_info': 'test_info'},
        unique_id='unique_id',
        status_code=200,
        json_response={'test_response': 'test_response'},
        timestamp=datetime(2021, 1, 1, 0, 0, 0)
    )
    assert email_log1 == email_log2


def test_email_log_instances_are_not_equal(test_app):
    email_log1 = EmailLog(
        id=1,
        user_email='test_email',
        username='test_username',
        email_type='test',
        info={'test_info': 'test_info'},
        unique_id='unique_id',
        status_code=200,
        json_response={'test_response': 'test_response'},
        timestamp=datetime(2021, 1, 1, 0, 0, 0)
    )
    email_log2 = EmailLog(
        id=2,
        user_email='test_email',
        username='test_username',
        email_type='test',
        info={'test_info': 'test_info'},
        unique_id='unique_id',
        status_code=200,
        json_response={'test_response': 'test_response'},
        timestamp=datetime(2021, 1, 1, 0, 0, 0)
    )
    assert email_log1 != email_log2
