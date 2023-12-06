class GamePlay:
    def __init__(self, name, intro_message, param="", api_variable=""):
        self.name = name
        lower_name = name.lower().replace(' ', '').replace('-', '').replace('&', '')
        self.image = lower_name + '.png'
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



    def update_stored_questions(self):
        pass # CONTACT API AND STORE IN REDIS

    def get_question(self, last_question_no):
        # LOGIC TO GET QUESTION (+ANSWER) FROM REDIS
        self.current_question = "Question from Redis"
        self.current_answer = "Answer from Redis"
        return (1, self.current_question)  # NEED TO RETURN TRACKER AND QUESTION IN TUPLE
    
    def get_answer(self, tracker):
        return "Answer from Redis"
    

class Category:
    def __init__(self, name):
        self.name = name
