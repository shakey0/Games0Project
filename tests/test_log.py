from Games0App import db
from Games0App.models.log import Log
from datetime import datetime
import pytest
from sqlalchemy.exc import IntegrityError


def test_log_creation(test_app):
        
    test_log = Log(
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    db.session.add(test_log)
    db.session.commit()

    log = Log.query.filter_by(unique_id='unique_id').first()
    assert log is not None
    assert log.id == 1
    assert log.unique_id == 'unique_id'
    assert log.user_id == 1
    assert log.ip_address == '198.51.100.1'
    assert log.function_name == 'test_function'
    assert log.log_type == 'test'
    assert log.timestamp == datetime(2021, 1, 1, 0, 0, 0)
    assert log.data == {'test_data': 'test_data'}
    assert log.issue_id == 'issue_id'


def test_log_creation_fail_non_unique_unique_id(test_app):
        
    test_log = Log(
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    db.session.add(test_log)
    db.session.commit()

    test_log = Log(
        unique_id='unique_id',
        user_id=2,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    db.session.add(test_log)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_log_instances_are_equal(test_app):
        
    log1 = Log(
        id=1,
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    log2 = Log(
        id=1,
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    assert log1 == log2


def test_log_instances_are_not_equal(test_app):
        
    log1 = Log(
        id=1,
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    log2 = Log(
        id=2,
        unique_id='unique_id',
        user_id=1,
        ip_address='198.51.100.1',
        function_name='test_function',
        log_type='test',
        timestamp=datetime(2021, 1, 1, 0, 0, 0),
        data={'test_data': 'test_data'},
        issue_id='issue_id'
    )
    assert log1 != log2
