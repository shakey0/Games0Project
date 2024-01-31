from Games0App.classes.digit_to_word_converter import DigitToWordConverter
digit_to_word_converter = DigitToWordConverter()
from Games0App.classes.logger import Logger
logger = Logger()
import random


class QuestionSorter:


    def validate_blank_added(self, id, load_route, question):
        if not '____' in question:
            error = f'ERROR: Blank not added for question ID {id} in {load_route}'
            print(error)
            json_log = {'error': error}
            logger.log_event(json_log, 'validate_blank_added', 'blank_error')
            return False
        return True


    def validate_answer_has_no_numbers(self, id, load_route, answer):
        if any(char.isdigit() for char in answer):
            error = f'ERROR: Answer contains numbers for question ID {id} in {load_route}'
            print(error)
            json_log = {'error': error}
            logger.log_event(json_log, 'validate_answer_has_no_numbers', 'number_in_answer')
            return False
        return True


    def sort_fill_blank_facts_questions(self, question_package, load_route):
        valid_questions = []
        for item in question_package:
            id = item['ID']
            answer = random.choice(item['blanks'])
            question = item['fact'].replace(answer, '____')
            if not self.validate_blank_added(id, load_route, question):
                continue
            if not self.validate_answer_has_no_numbers(id, load_route, answer):
                continue
            valid_questions.append([id, question, answer])
        return valid_questions


    def sort_fill_blank_jokes_questions(self, question_package, load_route):
        valid_questions = []
        for item in question_package:
            id = item['ID']
            answer = random.choice(item['blanks'])
            full_joke = item['joke'] + ' ' + item['punchline']
            question = full_joke.replace(answer, '____')
            if not self.validate_blank_added(id, load_route, question):
                continue
            if not self.validate_answer_has_no_numbers(id, load_route, answer):
                continue
            valid_questions.append([id, question, answer])
        return valid_questions


    def sort_trivia_madness_questions(self, question_package, load_route):
        valid_questions = []
        for item in question_package:
            id = item['ID']
            question = item['question']
            answer = item['answer']
            answer = digit_to_word_converter.find_and_convert_numbers(answer)
            if not self.validate_answer_has_no_numbers(id, load_route, answer):
                continue
            valid_questions.append([id, question, answer])
        return valid_questions


    def sort_trivia_mc_questions(self, question_package, load_route):
        valid_questions = []
        for item in question_package:
            id = item['id']
            question = item['question'].strip()
            if len(question) > 100:
                continue
            answer = item['correctAnswer'].strip()
            wrong_answers = [wrong_answer.strip() for wrong_answer in item['incorrectAnswers']]
            is_valid = True
            for item in [answer] + wrong_answers:
                if len(item) > 30:
                    is_valid = False
                    break
            if not is_valid:
                continue
            # There is currently nothing to validate, therefore load_route is not used
            valid_questions.append([id, question, answer, wrong_answers])
        return valid_questions


    def sort_trivia_tf_questions(self, question_package, load_route):
        valid_questions = []
        for item in question_package:
            id = item['ID']
            random_option = random.choice(item['options'])
            question = item['statement'].replace('____', random_option)
            if '____' in question:
                error = f'ERROR: Option ({random_option}) not added for question ID {id} in {load_route}'
                print(error)
                json_log = {'error': error}
                logger.log_event(json_log, 'sort_trivia_tf_questions', 'blank_not_added')
                continue
            answer = item['statement'].replace('____', item['answer'])
            if '____' in answer:
                error = f'ERROR: Answer not added for question ID {id} in {load_route}'
                print(error)
                json_log = {'error': error}
                logger.log_event(json_log, 'sort_trivia_tf_questions', 'blank_not_added')
                continue
            valid_questions.append([id, question, answer])
        return valid_questions
