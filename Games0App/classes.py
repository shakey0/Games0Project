import os
import redis
production = os.environ.get('PRODUCTION', False)
if production:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)
from Games0App.utils import spell_check_sentence, find_and_convert_numbers
from Games0App.lists import blank_words_to_avoid
import json
import csv
import random


class GamePlay:
    def __init__(self, name, intro_message, default=True, categories=[], param="", api_source="", api_variable=""):
        self.name = name
        self.lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
        self.image = self.lower_name + '.png'
        self.intro_message = intro_message
        self.default = default
        self.categories = categories
        self.param = param
        self.api_source = api_source
        self.api_variable = api_variable
        if categories and api_source == "ninjas":
            self.api_url = 'https://api.api-ninjas.com/v1/{}?category={}&limit=30'
        elif api_source == "ninjas":
            self.api_url = 'https://api.api-ninjas.com/v1/{}?limit=30'
        elif categories and api_source == "trivia":
            self.api_url = "https://the-trivia-api.com/api/questions?limit=30&categories={}&difficulty={}"
        elif api_source == "trivia":
            self.api_url = "https://the-trivia-api.com/api/questions?limit=30&difficulty={}"
        else:
            self.api_url = ""
        self.question_numbers = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}


    def create_fill_blank_answer(self, sentence):
        punctuation = ['.', ',', '!', '?', ';', ':', '(', ')', '[', ']', '{', '}', '"', "'"]
        split_sentence = sentence.split()
        count = 0
        while count < 100:
            if not spell_check_sentence(sentence):
                return None
            count += 1
            random_word = random.choice(split_sentence)
            if not random_word[1:-1].isalpha():
                continue
            for punct in punctuation:
                random_word = random_word.replace(punct, '')
            if random_word.lower() in blank_words_to_avoid:
                continue
            if not random_word.isalpha():
                continue
            if len(random_word) < 4 or len(random_word) > 8:
                continue
            if not sentence[-1] in ['.', '!', '?']:
                sentence += '.'
            return [sentence.replace(random_word, '____'), random_word]
        return None

    def validate_trivia_madness_question(self, question, answer):
        if len(answer.split()) > 2 or len(answer) > 15 or len(answer.split()[0]) > 10:
            return False
        if len(answer.split()) == 2 and len(answer.split()[1]) > 10:
            return False
        if not spell_check_sentence(question):
            print('QUESTION SPELLING ERROR\n', question)
            return False
        if not spell_check_sentence(answer):
            print('ANSWER SPELLING ERROR\n', answer)
            return False
        if any(c.isalpha() for c in answer) and any(c.isdigit() for c in answer):
            return False
        return True

    def update_stored_questions(self, url, redis_group):
        print(url)
        from Games0App.foreign_api import get_api_questions_from_ninjas, get_api_questions_from_trivia

        try:
            if self.api_source == "ninjas":
                response = get_api_questions_from_ninjas(url)
            elif self.api_source == "trivia":
                response = get_api_questions_from_trivia(url)
            else:
                response = None
            response = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")

        if response:
            valid_questions = []
            answers = []
            for item in response:

                if "trivia_madness" in self.param:
                    question = item['question'].strip()
                    answer = item['answer'].strip()
                    if ',' in answer or '.' in answer or '_' in answer or len(answer.split()) > 2:
                        continue
                    if len(question) > 100:
                        continue
                    answer = find_and_convert_numbers(answer)
                    if self.validate_trivia_madness_question(question, answer):
                        if not question[-1] in ['.', '!', '?']:
                            question += '?'
                        if answer.lower().replace(' ', '').replace('-', '').replace('&', '') in answers:
                            continue
                        answers.append(answer.lower().replace(' ', '').replace('-', '').replace('&', ''))
                        valid_questions.append([question, answer])
                
                elif "fill_blank" in self.param:
                    sentence = item['fact'] if 'fact' in item else item['joke']
                    if len(sentence) > 100:
                        continue
                    fill_in_the_blank = self.create_fill_blank_answer(sentence)
                    if fill_in_the_blank:
                        valid_questions.append(fill_in_the_blank)

                elif "trivia_mc" in self.param:
                    question = item['question'].strip()
                    answer = item['correctAnswer'].strip()
                    if len(question) > 100:
                        continue
                    wrong_answers = [wrong_answer.strip() for wrong_answer in item['incorrectAnswers']]
                    is_valid = True
                    for item in [answer] + wrong_answers:
                        if len(item) > 30:
                            is_valid = False
                            break
                    if not is_valid:
                        continue
                    valid_questions.append([question, answer, wrong_answers])
            
            if valid_questions:
                print('VALID QUESTIONS:\n', valid_questions)
                serialized_questions = [json.dumps(question) for question in valid_questions]
                redis_client.sadd(redis_group, *serialized_questions)
                print('Added questions to Redis set')
                return True
            return False
        return False


    def update_stored_statements(self, file_path, redis_group, category=""):

        all_items = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                item = {'category': row['category'], 'statement': row['statement'], 'answer': row['answer'], 'options': row['options'].split(', ')}
                if category:
                    if item['category'].strip().lower() == category.strip().lower():
                        all_items.append(item)
                else:
                    all_items.append(item)

        random_items = random.sample(all_items, min(30, len(all_items)))

        constructed_statements = []
        for item in random_items:
            random_option = random.choice(item['options'])
            statement = item['statement'].replace('____', random_option)
            answer = item['statement'].replace('____', item['answer'])
            constructed_statements.append([statement, answer])

        if constructed_statements:
            print('VALID QUESTIONS:\n', constructed_statements)
            serialized_questions = [json.dumps(question) for question in constructed_statements]
            redis_client.sadd(redis_group, *serialized_questions)
            print('Added questions to Redis set')
            return True
        return False


    def generate_numbers_and_ops(self, difficulty):
        while True:
            if difficulty == "easy":
                low, high = 1, 9
                ops = ["+", "-"]
                target_number = random.randint(10, 99)
            elif difficulty == "hard":
                low, high = 2, 19
                ops = ["+", "-", "*", "÷"]
                target_number = random.randint(50, 499)
            else: # difficulty == "medium"
                low, high = 3, 9
                ops = ["+", "-", "*", "÷"]
                target_number = random.randint(25, 249)
            
            numbers = [random.randint(low, high) for _ in range(4)]
            ops = [random.choice(ops) for _ in range(2)]

            if ops[0] == "÷":
                numbers[0] *= 10
                numbers[0] += random.randint(1, 9)
                if numbers[0] % numbers[1] != 0:
                    continue
            if ops[1] == "÷":
                numbers[2] *= 10
                numbers[2] += random.randint(1, 9)
                if numbers[2] % numbers[3] != 0:
                    continue

            return numbers, ops, target_number

    def create_sums_for_question(self, difficulty):

        max_end_no = 20 if difficulty == "easy" else 200 if difficulty == "hard" else 100 # If difficulty is medium

        all_choices = []
        for _ in range(4):

            while True:
                sum_numbers, ops, target_number = self.generate_numbers_and_ops(difficulty)
                for item in all_choices:
                    if target_number == item[1]: # MUST TEST FOR DUPLICATE TARGET NUMBERS
                        continue
                exp_part1 = f"({sum_numbers[0]} {ops[0]} {sum_numbers[1]})".replace("÷", "/")
                exp_part2 = f"({sum_numbers[2]} {ops[1]} {sum_numbers[3]})".replace("÷", "/")
                if difficulty == "easy" or difficulty == "medium":
                    if eval(exp_part1) < 1 or eval(exp_part1) > 99 or eval(exp_part2) < 1 or eval(exp_part2) > 99:
                        continue
                expression = f"({sum_numbers[0]} {ops[0]} {sum_numbers[1]}) {random.choice(['+', '-'])} ({sum_numbers[2]} {ops[1]} {sum_numbers[3]})"

                try:
                    value = eval(expression.replace("÷", "/"))
                except ZeroDivisionError:
                    continue
            
                if type(value) == float:
                    if value.is_integer():
                        value = int(value)
                    else:
                        continue
                if value < 0 or value == target_number:
                    continue
                
                if target_number - max_end_no <= value <= target_number + max_end_no:
                    break
                
            if target_number - value > 0:
                corrected_sum = expression + " + " + str(target_number - value)
            else:
                corrected_sum = expression + " - " + str(value - target_number)

            all_choices.append([corrected_sum, target_number])

        # print('ALL TARGET NUMBERS:\n', [item[1] for item in all_choices])
        selected_target = random.choice(all_choices)
        question = f"Which of the following sums equates to {selected_target[1]}?"
        answer = selected_target[0]
        wrong_answers = [item[0] for item in all_choices if item[0] != answer]
        return [question, answer, wrong_answers]
        
    def update_stored_sums(self, redis_group, difficulty):

        valid_questions = []

        for _ in range(30):
            question, answer, wrong_answers = self.create_sums_for_question(difficulty)
            if question and answer and wrong_answers:
                valid_questions.append([question, answer, wrong_answers])

        if valid_questions:
            print('VALID QUESTIONS:\n', valid_questions)
            serialized_questions = [json.dumps(question) for question in valid_questions]
            redis_client.sadd(redis_group, *serialized_questions)
            print('Added questions to Redis set')
            return True
        return False


    def get_question_from_redis_set(self, redis_group, category, difficulty):
        question = redis_client.spop(redis_group)
        if question is not None:
            print('Got question from Redis set')

            base_string = self.create_base_string(category, difficulty)

            redis_question_no_string = base_string + "_last_question_no"
            incremented_question_no = redis_client.incr(redis_question_no_string)

            field = base_string + "_" + str(incremented_question_no)
            hash_name = base_string + "_hash"

            redis_client.hset(hash_name, field, question)

            if redis_client.ttl(hash_name) == -1:
                redis_client.expire(hash_name, 3600)
                redis_client.expire(redis_question_no_string, 3600)

            question = json.loads(question.decode('utf-8'))
            if len(question) == 2:
                return {"last_question_no": incremented_question_no, "question": question[0], "answer": question[1]}
            elif len(question) == 3:
                return {"last_question_no": incremented_question_no, "question": question[0], "answer": question[1], "wrong_answers": question[2]}
            else:
                return None


    def get_question_from_redis(self, last_question_no, redis_string, category, difficulty):
        base_string = self.create_base_string(category, difficulty)
        hash_name = base_string + "_hash"

        question = redis_client.hget(hash_name, redis_string)
        if question is not None:
            print('Got question from Redis')
            question = json.loads(question.decode('utf-8'))
            if len(question) == 2:
                return {"last_question_no": last_question_no+1, "question": question[0], "answer": question[1]}
            elif len(question) == 3:
                return {"last_question_no": last_question_no+1, "question": question[0], "answer": question[1], "wrong_answers": question[2]}
            else:
                return None


    def get_question(self, last_question_no, category="", difficulty=""):
        if category:
            if self.api_source == "ninjas":
                category = category.lower().replace(' ', '').replace('-', '').replace('&', '')
            else:
                category = category.lower().replace(' ', '_').replace('&', 'and')
        
        base_string = self.create_base_string(category, difficulty)
        redis_string = base_string + "_" + str(last_question_no+1)
        redis_group = base_string + "_collection"
        
        print('Trying to get question from Redis')
        question = self.get_question_from_redis(last_question_no, redis_string, category, difficulty)
        if question is not None:
            return question
        
        print('Trying to get question from Redis set')
        question = self.get_question_from_redis_set(redis_group, category, difficulty)
        if question is not None:
            return question
            
        if self.api_source:
            print('Triggering API call to get more questions')
            count = 0
            while count < 3:
                count += 1
                if self.api_variable:  # For ninjas API
                    if category:
                        print("CATEGORY: ", category)
                        result = self.update_stored_questions(self.api_url.format(self.api_variable, category), redis_group)
                    else:
                        result = self.update_stored_questions(self.api_url.format(self.api_variable), redis_group)
                else:  # For trivia API
                    if category:
                        print("CATEGORY: ", category)
                        result = self.update_stored_questions(self.api_url.format(category, difficulty), redis_group)
                    else:
                        result = self.update_stored_questions(self.api_url.format(difficulty), redis_group)
                if result:
                    print('Trying to get question from Redis set')
                    question = self.get_question_from_redis_set(redis_group, category, difficulty)
                    if question is not None:
                        return question
            print('Failed to get question from API')
            return None
        
        elif "_tf" in self.param:
            print('Loading questions from file')
            if category:
                result = self.update_stored_statements('Games0App/static/true_or_false_trivia.csv', redis_group, category)
            else:
                result = self.update_stored_statements('Games0App/static/true_or_false_trivia.csv', redis_group)
            if result:
                print('Trying to get question from Redis set')
                question = self.get_question_from_redis_set(redis_group, category, difficulty)
                if question is not None:
                    return question
            print('Failed to get question from file')
            return None
        
        elif "number" in self.param:
            print('Generating sums')
            result = self.update_stored_sums(redis_group, difficulty)
            if result:
                print('Trying to get question from Redis set')
                question = self.get_question_from_redis_set(redis_group, category, difficulty)
                if question is not None:
                    return question
            print('Failed to generate sums')
            return None


    def create_base_string(self, category, difficulty):
        base_string = self.lower_name
        if category:
            base_string += "_" + category
        if difficulty:
            base_string += "_" + difficulty
        return base_string
