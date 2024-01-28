from Games0App.extensions import redis_client
from Games0App.classes.question_sorter import QuestionSorter
question_sorter = QuestionSorter()
from Games0App.classes.sum_generator import SumGenerator
sum_generator = SumGenerator()
import requests
import json
import csv
import random


class GamePlay:
    def __init__(self, name, intro_message, param, load_route, default=True, categories=[], has_difficulty=False):
        self.name = name
        self.lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
        self.image = self.lower_name + '.png'
        self.intro_message = intro_message
        self.param = param
        self.load_route = load_route
        self.default = default
        self.categories = categories
        self.has_difficulty = has_difficulty
        self.question_numbers = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
                                7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}


    def get_questions_from_api(self, category, difficulty):

        if category and difficulty:
            url = self.load_route[1].format(category, difficulty)
        elif category: # Currently not in use
            url = self.load_route[1].format(category)
        elif difficulty:
            url = self.load_route[1].format(difficulty)
        else: # Currently not in use
            url = self.load_route[1]
        print(url)

        try:
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                print(response.text)
                response = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            response = None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            response = None
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: {e}")
            response = None
        except:
            print("Error:", response.status_code, response.text)
            response = None

        if response:
            return response
        return None
    

    def get_questions_from_csv(self, category, difficulty):
        if category:
            category = category.replace('_and_', '_')

        all_items = []
        with open(f"Games0App/static/quiz_data/{self.load_route[1]}.csv", newline='') as csvfile:

            reader = csv.DictReader(csvfile, delimiter=';')
            headers = reader.fieldnames

            for row in reader:
                item = {header: row[header] for header in headers}
                if 'options' in item:
                    item['options'] = item['options'].split(', ')
                if 'blanks' in item:
                    item['blanks'] = item['blanks'].split(', ')
                if category and ('category' in item and item['category'].strip().lower() == category.strip().lower()):
                    all_items.append(item)
                elif not category:
                    all_items.append(item)
                # difficulty is not currently in use
        all_items = random.sample(all_items, min(30, len(all_items)))
        return all_items


    def get_questions_from_function(self, category, difficulty):
        valid_questions = []
        for _ in range(30):
            if self.load_route[1] == 'sum_generator':
                question, answer, wrong_answers = sum_generator.create_sums_for_question(difficulty)
                if question and answer and wrong_answers:
                    valid_questions.append([0, question, answer, wrong_answers])
            # Currently sum_generator is the only function that generates questions
            # category is not currently in use
        return valid_questions

    
    def update_stored_questions(self, questions, redis_group):
        if questions:
            print('VALID QUESTIONS:\n', questions)
            serialized_questions = [json.dumps(question) for question in questions]
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
            if len(question) == 3:
                return {"last_question_no": incremented_question_no, "ID": question[0],
                        "question": question[1], "answer": question[2]}
            elif len(question) == 4:
                return {"last_question_no": incremented_question_no, "ID": question[0],
                        "question": question[1], "answer": question[2], "wrong_answers": question[3]}
            return None
        return None


    def get_question_from_redis(self, last_question_no, redis_string, category, difficulty):
        base_string = self.create_base_string(category, difficulty)
        hash_name = base_string + "_hash"

        question = redis_client.hget(hash_name, redis_string)
        if question is not None:
            print('Got question from Redis')
            question = json.loads(question.decode('utf-8'))
            if len(question) == 3:
                return {"last_question_no": last_question_no+1, "ID": question[0],
                        "question": question[1], "answer": question[2]}
            elif len(question) == 4:
                return {"last_question_no": last_question_no+1, "ID": question[0],
                        "question": question[1], "answer": question[2], "wrong_answers": question[3]}
            return None
        return None


    def get_question(self, last_question_no, category="", difficulty=""):
        
        category = self.format_category_name(category)
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
            
        if self.load_route[0] == 'api':
            print('Triggering API call to get more questions')
            count = 0
            while count < 3:
                count += 1
                question_package = self.get_questions_from_api(category, difficulty)
                if not question_package:
                    continue
                if "the-trivia-api.com" in self.load_route[1]:
                    valid_questions = question_sorter.sort_trivia_mc_questions(question_package, self.load_route)
                else: # There are currently no other types of questions that come directly from APIs
                    continue
                result = self.update_stored_questions(valid_questions, redis_group)
                if result:
                    print('Trying to get question from Redis set')
                    question = self.get_question_from_redis_set(redis_group, category, difficulty)
                    if question is not None:
                        return question
            print('Failed to get question from API')
            return None
        
        elif self.load_route[0] == 'csv':
            print('Loading questions from file')
            question_package = self.get_questions_from_csv(category, difficulty)
            if self.load_route[1] == 'facts':
                valid_questions = question_sorter.sort_fill_blank_facts_questions(question_package, self.load_route)
            elif self.load_route[1] == 'jokes':
                valid_questions = question_sorter.sort_fill_blank_jokes_questions(question_package, self.load_route)
            elif self.load_route[1] == 'trivia_madness':
                valid_questions = question_sorter.sort_trivia_madness_questions(question_package, self.load_route)
            elif self.load_route[1] == 'true_or_false_trivia':
                valid_questions = question_sorter.sort_trivia_tf_questions(question_package, self.load_route)
            else:
                valid_questions = None
            result = self.update_stored_questions(valid_questions, redis_group)
            if result:
                print('Trying to get question from Redis set')
                question = self.get_question_from_redis_set(redis_group, category, difficulty)
                if question is not None:
                    return question
            print('Failed to get question from file')
            return None
        
        elif self.load_route[0] == 'function':
            print('Generating questions')
            valid_questions = self.get_questions_from_function(category, difficulty)
            result = self.update_stored_questions(valid_questions, redis_group)
            if result:
                print('Trying to get question from Redis set')
                question = self.get_question_from_redis_set(redis_group, category, difficulty)
                if question is not None:
                    return question
            print('Failed to generate sums')
            return None


    def format_category_name(self, category):
        if category:
            category = category.lower().replace(' - hard', '').replace(' & ', '_and_').replace(' ', '_')
        return category

    def create_base_string(self, category, difficulty):
        base_string = self.lower_name
        if category:
            base_string += "_" + category
        if difficulty:
            base_string += "_" + difficulty
        return base_string
