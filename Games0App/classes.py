import os
import redis
production = os.environ.get('PRODUCTION', False)
if production:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
else:
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    redis_client = redis.Redis(host='localhost', port=6379, db=0, password=REDIS_PASSWORD)
import json


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
        # self.api_url = 'https://api.api-ninjas.com/v1/trivia?category={}&limit=30'.format(self.variable.lower())
        self.question_numbers = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "last"}

    def validate_answer(self, answer):
        if len(answer.split()) > 2:
            return False
        return True

    def update_stored_questions(self, url, redis_group, category=""):
        print(category)
        print(url)
        from Games0App.views.api import get_api_questions

        try:
            response = get_api_questions(url)
            response = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")

        if response:
            valid_questions = []
            for item in response:
                if category:
                    question = item['question']
                    answer = item['answer']
                    if self.validate_answer(answer.strip().lower()):
                        valid_questions.append((question, answer))
            # NEED TO ADD VALID QUESTIONS AND DECIDE ON NAME FOR SET !!!!!!!!!!
            

            # redis_client.mset({("trivia_{}_{}".format(category, i+1)): question for i, (question, answer, category, last_question_no) in enumerate(valid_questions)})


            # for i, question in enumerate(response):
            #     redis_client.set("trivia_{}_{}".format(category, i+1), question)
            # redis_client.sadd("myStrings", *response)

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
            question = redis_client.get(redis_string)
            if question is not None:
                print('Got question from Redis')
                return (last_question_no+1, question.decode('utf-8'))
            print('Trying to get question from Redis set')
            question = redis_client.spop(redis_group)  # NAME FOR SET !!!!!!!!!!
            if question is not None:
                print('Got question from Redis set')
                if category:
                    incremented_question_no = redis_client.incr("{}_{}_last_question_no".format(self.lower_name, category))
                    redis_client.set("{}_{}_{}".format(self.lower_name, category, incremented_question_no), question)
                return (incremented_question_no, question.decode('utf-8'))
            print('Triggering API call to get more questions')
            if category:
                self.update_stored_questions(self.api_url.format(category.lower()), redis_group, category.lower())
            else:
                self.update_stored_questions(self.api_url, redis_group)

        # LOGIC TO GET QUESTION (+ANSWER) FROM REDIS
        self.current_question = "Question from Redis"
        self.current_answer = "Answer from Redis"
        return (1, self.current_question)  # NEED TO RETURN TRACKER AND QUESTION IN TUPLE
    
    def get_answer(self, tracker):
        return "Answer from Redis"
    

class Category:
    def __init__(self, name):
        self.name = name
