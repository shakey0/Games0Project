from Games0App.models.log import Log
from Games0App.classes.question_sorter import question_sorter

def test_validate_blank_added(test_app):
    assert question_sorter.validate_blank_added('8a92jj2', ['test', 'test'], 'This is a test ____') == True
    assert question_sorter.validate_blank_added('8a92jj2', ['test', 'test'], 'This is a test') == False
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 0
    assert logs[0].ip_address == ''
    assert logs[0].function_name == 'validate_blank_added'
    assert logs[0].log_type == 'blank_error'
    assert logs[0].timestamp != None
    assert logs[0].data == {'error': "ERROR: Blank not added for question ID 8a92jj2 in ['test', 'test']"}
    assert not logs[0].issue_id

def test_validate_answer_has_no_numbers(test_app):
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], 'test') == True
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], 'test1') == False
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], '1test') == False
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], '1test1') == False
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], '1') == False
    assert question_sorter.validate_answer_has_no_numbers('8a92jj2', ['test', 'test'], '1'*100) == False
    logs = Log.query.all()
    assert len(logs) == 5
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 0
    assert logs[0].ip_address == ''
    assert logs[0].function_name == 'validate_answer_has_no_numbers'
    assert logs[0].log_type == 'number_in_answer'
    assert logs[0].timestamp != None
    assert logs[0].data == {'error': "ERROR: Answer contains numbers for question ID 8a92jj2 in ['test', 'test']"}
    assert not logs[0].issue_id

def test_sort_fill_blank_facts_questions(test_app):

    question_package = [
        {'ID': '8a92jj2', 'fact': 'This is a test', 'blanks': ['This']},
        {'ID': '8a92jj3', 'fact': 'This is a test', 'blanks': ['test']},
        {'ID': '8a92jj4', 'fact': 'This is a test', 'blanks': ['This', 'test']}
    ]
    possible_results = [[
        ['8a92jj2', '____ is a test', 'This'],
        ['8a92jj3', 'This is a ____', 'test'],
        ['8a92jj4', 'This is a ____', 'test']
    ], [
        ['8a92jj2', '____ is a test', 'This'],
        ['8a92jj3', 'This is a ____', 'test'],
        ['8a92jj4', '____ is a test', 'This']
    ]]
    assert question_sorter.sort_fill_blank_facts_questions(question_package, ['test', 'test']) in possible_results
    logs = Log.query.all()
    assert len(logs) == 0

    question_package = [
        {'ID': '8a92jj2', 'fact': 'This is a test', 'blanks': ['this']},
        {'ID': '8a92jj3', 'fact': 'This is a test', 'blanks': ['test']},
        {'ID': '8a92jj4', 'fact': 'This is a test', 'blanks': ['This']}
    ]
    assert question_sorter.sort_fill_blank_facts_questions(question_package, ['test', 'test']) == [
        ['8a92jj3', 'This is a ____', 'test'],
        ['8a92jj4', '____ is a test', 'This']
    ]
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 0
    assert logs[0].ip_address == ''
    assert logs[0].function_name == 'validate_blank_added'
    assert logs[0].log_type == 'blank_error'
    assert logs[0].timestamp != None
    assert logs[0].data == {'error': "ERROR: Blank not added for question ID 8a92jj2 in ['test', 'test']"}
    assert not logs[0].issue_id

    question_package = [
        {'ID': '8a92jj2', 'fact': 'This is a test 2000', 'blanks': ['2000']},
        {'ID': '8a92jj3', 'fact': 'This is a test', 'blanks': ['test']},
        {'ID': '8a92jj4', 'fact': 'This is a test', 'blanks': ['This']}
    ]
    assert question_sorter.sort_fill_blank_facts_questions(question_package, ['test', 'test']) == [
        ['8a92jj3', 'This is a ____', 'test'],
        ['8a92jj4', '____ is a test', 'This']
    ]
    logs = Log.query.all()
    assert len(logs) == 2
    assert logs[1].id == 2
    assert logs[1].unique_id[0] == 'S'
    assert logs[1].user_id == 0
    assert logs[1].ip_address == ''
    assert logs[1].function_name == 'validate_answer_has_no_numbers'
    assert logs[1].log_type == 'number_in_answer'
    assert logs[1].timestamp != None
    assert logs[1].data == {'error': "ERROR: Answer contains numbers for question ID 8a92jj2 in ['test', 'test']"}
    assert not logs[1].issue_id

def test_sort_fill_blank_jokes_questions(test_app):

    question_package = [
        {'ID': '8a92jj2', 'joke': 'This is a test?', 'punchline': 'You fell for it', 'blanks': ['This']},
        {'ID': '8a92jj3', 'joke': 'This is a test?', 'punchline': 'Fooled you!', 'blanks': ['Fooled']},
        {'ID': '8a92jj4', 'joke': 'This is a test?', 'punchline': 'Another test joke', 'blanks': ['test', 'joke']}
    ]
    possible_results = [[
        ['8a92jj2', '____ is a test? You fell for it', 'This'],
        ['8a92jj3', 'This is a test? ____ you!', 'Fooled'],
        ['8a92jj4', 'This is a ____? Another ____ joke', 'test']
    ], [
        ['8a92jj2', '____ is a test? You fell for it', 'This'],
        ['8a92jj3', 'This is a test? ____ you!', 'Fooled'],
        ['8a92jj4', 'This is a test? Another test ____', 'joke']
    ]]
    assert question_sorter.sort_fill_blank_jokes_questions(question_package, ['test', 'test']) in possible_results
    logs = Log.query.all()
    assert len(logs) == 0

    question_package = [
        {'ID': '8a92jj2', 'joke': 'This is a test?', 'punchline': 'You fell for it', 'blanks': ['This']},
        {'ID': '8a92jj3', 'joke': 'This is a test?', 'punchline': 'Fooled you!', 'blanks': ['fooled']},
        {'ID': '8a92jj4', 'joke': 'This is a test?', 'punchline': 'Another test joke', 'blanks': ['test']}
    ]
    assert question_sorter.sort_fill_blank_jokes_questions(question_package, ['test', 'test']) == [
        ['8a92jj2', '____ is a test? You fell for it', 'This'],
        ['8a92jj4', 'This is a ____? Another ____ joke', 'test']
    ]
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 0
    assert logs[0].ip_address == ''
    assert logs[0].function_name == 'validate_blank_added'
    assert logs[0].log_type == 'blank_error'
    assert logs[0].timestamp != None
    assert logs[0].data == {'error': "ERROR: Blank not added for question ID 8a92jj3 in ['test', 'test']"}
    assert not logs[0].issue_id

    question_package = [
        {'ID': '8a92jj2', 'joke': 'This is a test 2000?', 'punchline': 'You fell for it', 'blanks': ['2000']},
        {'ID': '8a92jj3', 'joke': 'This is a test?', 'punchline': 'Fooled you!', 'blanks': ['fooled']},
        {'ID': '8a92jj4', 'joke': 'This is a test?', 'punchline': 'Another test joke', 'blanks': ['test']}
    ]
    assert question_sorter.sort_fill_blank_jokes_questions(question_package, ['test', 'test']) == [
        ['8a92jj4', 'This is a ____? Another ____ joke', 'test']
    ]
    logs = Log.query.all()
    assert len(logs) == 3
    assert logs[1].id == 2
    assert logs[1].unique_id[0] == 'S'
    assert logs[1].user_id == 0
    assert logs[1].ip_address == ''
    assert logs[1].function_name == 'validate_answer_has_no_numbers'
    assert logs[1].log_type == 'number_in_answer'
    assert logs[1].timestamp != None
    assert logs[1].data == {'error': "ERROR: Answer contains numbers for question ID 8a92jj2 in ['test', 'test']"}
    assert not logs[1].issue_id
    assert logs[2].id == 3
    assert logs[2].unique_id[0] == 'S'
    assert logs[2].user_id == 0
    assert logs[2].ip_address == ''
    assert logs[2].function_name == 'validate_blank_added'
    assert logs[2].log_type == 'blank_error'
    assert logs[2].timestamp != None
    assert logs[2].data == {'error': "ERROR: Blank not added for question ID 8a92jj3 in ['test', 'test']"}
    assert not logs[2].issue_id

def test_sort_trivia_madness_questions(test_app):
    question_package = [
        {'ID': '8a92jj2', 'question': 'What is the capital of France?', 'answer': 'Paris'},
        {'ID': '8a92jj3', 'question': 'What is the capital of Germany?', 'answer': 'Berlin'},
        {'ID': '8a92jj4', 'question': 'About how many people live in the United Kingdom?', 'answer': '66 million'}
    ]
    assert question_sorter.sort_trivia_madness_questions(question_package, ['test', 'test']) == [
        ['8a92jj2', 'What is the capital of France?', 'Paris'],
        ['8a92jj3', 'What is the capital of Germany?', 'Berlin'],
        ['8a92jj4', 'About how many people live in the United Kingdom?', 'sixty six million']
    ]

def test_sort_mc_questions(test_app):
    
    question_package = [
        {'id': '8a92jj2', 'question': 'What is the capital of France?', 'correctAnswer': 'Paris', 'incorrectAnswers': ['London', 'Berlin', 'Madrid']},
        {'id': '8a92jj3', 'question': 'What is the capital of Germany?', 'correctAnswer': 'Berlin', 'incorrectAnswers': ['London', 'Paris', 'Madrid']},
        {'id': '8a92jj4', 'question': 'About how many people live in the United Kingdom?', 'correctAnswer': '66 million', 'incorrectAnswers': ['60 million', '70 million', '80 million']}
    ]
    assert question_sorter.sort_trivia_mc_questions(question_package, ['test', 'test']) == [
        ['8a92jj2', 'What is the capital of France?', 'Paris', ['London', 'Berlin', 'Madrid']],
        ['8a92jj3', 'What is the capital of Germany?', 'Berlin', ['London', 'Paris', 'Madrid']],
        ['8a92jj4', 'About how many people live in the United Kingdom?', '66 million', ['60 million', '70 million', '80 million']]
    ]

    question_package = [
        {'id': '8a92jj2', 'question': 'What is the capital of France?', 'correctAnswer': 'Paris', 'incorrectAnswers': ['London', 'Berlin', 'Madrid']},
        {'id': '8a92jj3', 'question': 'What is the capital of Germany?', 'correctAnswer': 'Berlin', 'incorrectAnswers': ['London', 'Paris', 'Madrid']},
        {'id': '8a92jj4', 'question': 'About how many people live in the United Kingdom?', 'correctAnswer': '66 million', 'incorrectAnswers': ['60 million', '70 million', '80 million']},
        {'id': '8a92jj5', 'question': 'What is the capital of Italy?', 'correctAnswer': 'Rome is the wonderful captial of Italy', 'incorrectAnswers': ['London', 'Berlin', 'Madrid']},
        {'id': '8a92jj6', 'question': 'What is the capital of Spain?', 'correctAnswer': 'Madrid', 'incorrectAnswers': ['London', 'Berlin is certainly not the capital of Spain', 'Paris']}
    ]
    assert question_sorter.sort_trivia_mc_questions(question_package, ['test', 'test']) == [
        ['8a92jj2', 'What is the capital of France?', 'Paris', ['London', 'Berlin', 'Madrid']],
        ['8a92jj3', 'What is the capital of Germany?', 'Berlin', ['London', 'Paris', 'Madrid']],
        ['8a92jj4', 'About how many people live in the United Kingdom?', '66 million', ['60 million', '70 million', '80 million']]
    ]

def test_sort_trivia_tf_questions(test_app):

    question_package = [
        {'ID': '8a92jj2', 'statement': 'The capital of France is ____.', 'answer': 'Paris', 'options': ['Paris', 'London']}
    ]
    assert question_sorter.sort_trivia_tf_questions(question_package, ['test', 'test']) == [
        ['8a92jj2', 'The capital of France is Paris.', 'The capital of France is Paris.']
    ] or [
        ['8a92jj2', 'The capital of France is London.', 'The capital of France is Paris.']
    ]
    logs = Log.query.all()
    assert len(logs) == 0

    question_package = [
        {'ID': '8a92jj2', 'statement': 'The capital of France is ___.', 'answer': 'Paris', 'options': ['Paris', 'London']}
    ]
    assert question_sorter.sort_trivia_tf_questions(question_package, ['test', 'test']) == []
    logs = Log.query.all()
    assert len(logs) == 1
    assert logs[0].id == 1
    assert logs[0].unique_id[0] == 'S'
    assert logs[0].user_id == 0
    assert logs[0].ip_address == ''
    assert logs[0].function_name == 'sort_trivia_tf_questions'
    assert logs[0].log_type == 'option_not_added'
    assert logs[0].timestamp != None
    possible_results = [
        {'error': 'ERROR: Option (London) not added for question ID 8a92jj2 in [\'test\', \'test\']'},
        {'error': 'ERROR: Option (Paris) not added for question ID 8a92jj2 in [\'test\', \'test\']'}
    ]
    assert logs[0].data in possible_results
    assert not logs[0].issue_id
