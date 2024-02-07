from Games0App.classes.sum_generator import sum_generator

def test_sum_generator(test_app):
    result = sum_generator.create_sums_for_question("easy")
    assert len(result) == 3
    assert 'Which of the following sums equates to' in result[0]
    assert all(char.isdigit() or char in ['+', '-', '(', ')', ' '] for char in result[1])