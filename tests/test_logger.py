from Games0App.classes.logger import logger

def test_log_event_get_log_by_unique_id(test_app):

    json_log = {'test': 'test'}
    function_name = 'test'
    log_type = 'test'
    result = logger.log_event(json_log, function_name, log_type)
    assert result[0] == 'S'
    assert len(result) == 9
    log = logger.get_log_by_unique_id(result)
    assert log.id == 1
    assert log.unique_id == result
    assert log.user_id == 0
    assert log.ip_address == ''
    assert log.function_name == 'test'
    assert log.log_type == 'test'
    assert log.timestamp != None
    assert log.data == {'test': 'test'}
    assert log.issue_id == ''
    
    json_log = {'user_id': 1, 'test': 'test', 'issue_id': 'S9A3E9C25'}
    function_name = 'test'
    log_type = 'init_change_email'
    result = logger.log_event(json_log, function_name, log_type)
    assert result[0] == 'R'
    assert len(result) == 9
    log = logger.get_log_by_unique_id(result)
    assert log.id == 2
    assert log.unique_id == result
    assert log.user_id == 1
    assert log.ip_address == 'unknown'
    assert log.function_name == 'test'
    assert log.log_type == 'init_change_email'
    assert log.timestamp != None
    assert log.data == {'test': 'test'}
    assert log.issue_id == 'S9A3E9C25'

    json_log = {'test': 'test'}
    function_name = 'test'
    log_type = 'init_reset_password/37af50ff6d950090772f8cbd335b21ac'
    result = logger.log_event(json_log, function_name, log_type)
    assert result[0] == 'S'
    assert len(result) == 9
    log = logger.get_log_by_unique_id(result)
    assert log.id == 3
    assert log.unique_id == result
    assert log.user_id == 0
    assert log.ip_address == 'unknown'
    assert log.function_name == 'test'
    assert log.log_type == 'init_reset_password/37af50ff6d950090772f8cbd335b21ac'
    assert log.timestamp != None
    assert log.data == {'test': 'test'}
    assert log.issue_id == ''
