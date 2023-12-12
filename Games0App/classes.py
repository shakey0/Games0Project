import os
import redis
production = os.environ.get('PRODUCTION', False)
if production:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)
from Games0App.utils import spell_check_sentence
import json
import random


class GamePlay:
    def __init__(self, name, intro_message, param="", api_variable=""):
        self.name = name
        self.lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
        self.image = self.lower_name + '.png'
        self.intro_message = intro_message
        self.param = param
        if api_variable == "trivia":
            self.api_url = 'https://api.api-ninjas.com/v1/trivia?category={}&limit=30'
        elif api_variable == "facts" or api_variable == "jokes":
            self.api_url = 'https://api.api-ninjas.com/v1/{}?limit=30'.format(api_variable)
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
            if not random_word.isalpha():
                continue
            if len(random_word) < 5 or len(random_word) > 10:
                continue
            if not sentence[-1] in ['.', '!', '?']:
                sentence += '.'
            return [sentence.replace(random_word, '__________'), random_word]
        return None

    def validate_trivia_question(self, question, answer):
        if not spell_check_sentence(question):
            return False
        if not spell_check_sentence(answer):
            return False
        if ',' in answer or '.' in answer or '_' in answer or len(answer.split()) > 2:
            return False
        if any(c.isalpha() for c in answer) and any(c.isdigit() for c in answer):
            return False
        return True

    def update_stored_questions(self, url, redis_group, category=""):
        print(category)
        print(url)
        from Games0App.foreign_api import get_api_questions

        try:
            response = get_api_questions(url)
            response = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")

        if response:
            valid_questions = []
            for item in response:
                if category:
                    question = item['question'].strip()
                    answer = item['answer'].strip()
                    if self.validate_trivia_question(question, answer):
                        # NEED TO AMEND THE ANSWER TO CUT OUT WORDS LIKE 'THE' AND 'A' AND 'AN'
                        if not question[-1] in ['.', '!', '?']:
                            question += '?'
                        valid_questions.append([question, answer])
                else:
                    sentence = item['fact'] if 'fact' in item else item['joke']
                    fill_in_the_blank = self.create_fill_blank_answer(sentence)
                    if fill_in_the_blank:
                        valid_questions.append(fill_in_the_blank)
            
            if valid_questions:
                serialized_questions = [json.dumps(question) for question in valid_questions]
                redis_client.sadd(redis_group, *serialized_questions)
                print('Added questions to Redis set')
                return True
            return False
        return False


    def get_question_from_redis_set(self, redis_group, category):
        question = redis_client.spop(redis_group)
        if question is not None:
            print('Got question from Redis set')
            print(self.lower_name)
            if category:
                redis_question_no_string = "{}_{}_last_question_no".format(self.lower_name, category)
                incremented_question_no = redis_client.incr(redis_question_no_string)
                field = "{}_{}_{}".format(self.lower_name, category, incremented_question_no)
                hash_name = "{}_{}_hash".format(self.lower_name, category)
            else:
                redis_question_no_string = "{}_last_question_no".format(self.lower_name)
                incremented_question_no = redis_client.incr(redis_question_no_string)
                field = "{}_{}".format(self.lower_name, incremented_question_no)
                hash_name = "{}_hash".format(self.lower_name)

            redis_client.hset(hash_name, field, question)
            if redis_client.ttl(hash_name) == -1:
                redis_client.expire(hash_name, 3600)
                redis_client.expire(redis_question_no_string, 3600)

            return (incremented_question_no, json.loads(question.decode('utf-8')))


    def get_question_from_redis(self, last_question_no, redis_string, category):
        hash_name = "{}_{}_hash".format(self.lower_name, category) if category else "{}_hash".format(self.lower_name)
        question = redis_client.hget(hash_name, redis_string)
        if question is not None:
            print('Got question from Redis')
            return (last_question_no+1, json.loads(question.decode('utf-8')))


    def get_question(self, last_question_no, category=""):
        # return "ANSWER FROM REDIS"
        if self.api_url:
            if category:
                category = category.lower().replace(' ', '').replace('-', '').replace('&', '')
                redis_string = "{}_{}_{}".format(self.lower_name, category, last_question_no+1)
                redis_group = "{}_{}_collection".format(self.lower_name, category)
            else:
                redis_string = "{}_{}".format(self.lower_name, last_question_no+1)
                redis_group = self.lower_name + "_collection"
            
            print('Trying to get question from Redis')
            question = self.get_question_from_redis(last_question_no, redis_string, category)
            if question is not None:
                return question
            
            print('Trying to get question from Redis set')
            question = self.get_question_from_redis_set(redis_group, category)
            if question is not None:
                return question
            
            print('Triggering API call to get more questions')
            count = 0
            while count < 3:
                count += 1
                if category:
                    print("CATEGORY: ", category)
                    result = self.update_stored_questions(self.api_url.format(category), redis_group, category)
                else:
                    result = self.update_stored_questions(self.api_url, redis_group)
                if result:
                    print('Trying to get question from Redis set')
                    question = self.get_question_from_redis_set(redis_group, category)
                    if question is not None:
                        return question
            print('Failed to get question from API')
            return None
    

class Category:
    def __init__(self, name):
        self.name = name
