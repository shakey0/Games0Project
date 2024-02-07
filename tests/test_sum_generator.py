from Games0App.classes.sum_generator import sum_generator

def test_sum_generator(test_app):

    for _ in range(300):

        result = sum_generator.create_sums_for_question("easy")
        assert len(result) == 3
        assert 'Which of the following sums equates to' in result[0]
        assert len([result[1]] + result[2]) == 4
        for answer in [result[1]] + result[2]:
            assert all(char.isdigit() or char in ['+', '-', '(', ')', ' '] for char in answer)
        value = eval(result[1].replace("÷", "/"))
        assert type(value) == int
        assert 10 <= value <= 99
        all_choices_values = []
        for answer in [result[1]] + result[2]:
            all_choices_values.append(eval(answer.replace("÷", "/")))
            assert len(all_choices_values) == len(set(all_choices_values)), "There are duplicate values in the list"
    
        result = sum_generator.create_sums_for_question("medium")
        assert len(result) == 3
        assert 'Which of the following sums equates to' in result[0]
        assert len([result[1]] + result[2]) == 4
        for answer in [result[1]] + result[2]:
            assert all(char.isdigit() or char in ['+', '-', "*", "÷", '(', ')', ' '] for char in answer)
        value = eval(result[1].replace("÷", "/"))
        assert type(value) == int or type(value) == float
        assert 25 <= value <= 249
        all_choices_values = []
        for answer in [result[1]] + result[2]:
            all_choices_values.append(eval(answer.replace("÷", "/")))
            assert len(all_choices_values) == len(set(all_choices_values)), "There are duplicate values in the list"

        result = sum_generator.create_sums_for_question("hard")
        assert len(result) == 3
        assert 'Which of the following sums equates to' in result[0]
        assert len([result[1]] + result[2]) == 4
        for answer in [result[1]] + result[2]:
            assert all(char.isdigit() or char in ['+', '-', "*", "÷", '(', ')', ' '] for char in answer)
        value = eval(result[1].replace("÷", "/"))
        assert type(value) == int or type(value) == float
        assert 50 <= value <= 499
        all_choices_values = []
        for answer in [result[1]] + result[2]:
            all_choices_values.append
            assert len(all_choices_values) == len(set(all_choices_values)), "There are duplicate values in the list"
