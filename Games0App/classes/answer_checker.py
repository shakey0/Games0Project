from flask import request
from Games0App.extensions import redis_client
from Games0App.classes.digit_to_word_converter import digit_to_word_converter


class AnswerChecker:
    
    
    def format_answer(self, answer):
        replace_chars = [' ', '-', '&', "'", '"', '(', ')', ',', '.', '?', '!', ':', ';', '$', '£', '€',
                        '%', '+', '=', '/', '\'', '*', '@', '#', '~', '<', '>']
        for char in replace_chars:
            answer = answer.replace(char, '')
        return answer

    def normalise_answer(self, answer):
        answer = answer.lower().strip()

        if ' & ' in answer:
            answer = answer.replace('&', '')
        if ' and ' in answer:
            answer = answer.replace('and', '')

        for article in ["they're ", 'they ', 'their ', 'the ', 'an ', 'a ', 'some ', 'my ', 'your ', 'our ', 'hers ', 'her ', "he's a ", "he's ", 'he ', 'his ', "she's a ", "she's ", 'she ', "it's the ", "it's a ", "it's ", 'its ', 'it ', "we're", 'we ']:
            if answer.startswith(article):
                answer = answer[len(article):]
                break

        return self.format_answer(answer)


    def check_difference(self, user_answer, real_answer):
        # Check if the strings are the same or differ by only one character or contain minor order differences
        
        len_u_answer, len_r_answer = len(user_answer), len(real_answer)

        i, j, same, last_letter_user_a, last_letter_real_a = 0, 0, 0, '', ''
        while i < len_u_answer and j < len_r_answer:
            if user_answer[i] != real_answer[j] and \
                (real_answer[j] != last_letter_user_a or user_answer[i] != last_letter_real_a):
                if len_u_answer > len_r_answer:
                    try:
                        last_letter_user_a = user_answer[i]
                    except:
                        pass
                    i += 1
                elif len_u_answer < len_r_answer:
                    try:
                        last_letter_real_a = real_answer[j]
                    except:
                        pass
                    j += 1
                else:
                    try:
                        last_letter_user_a = user_answer[i]
                        last_letter_real_a = real_answer[j]
                    except:
                        pass
                    i += 1
                    j += 1
            else:
                same += 1
                try:
                    last_letter_user_a = user_answer[i]
                    last_letter_real_a = real_answer[j]
                except:
                    pass
                i += 1
                j += 1
        return same

    def is_close_match(self, user_answer, real_answer):
        if real_answer.lower() in user_answer.lower():
            return True
        same = self.check_difference(user_answer, real_answer)
        if same == len(real_answer) or same == len(real_answer) - 1 or same == len(real_answer) + 1:
            return True
        count = [0, len(real_answer) - 1]
        while count[1] <= len(user_answer):
            user_answer_section = user_answer[count[0]:count[1]]
            same = self.check_difference(real_answer, user_answer_section)
            if same == len(real_answer) or same == len(real_answer) - 1 \
                or same == len(real_answer) + 1:
                return True
            count[0] += 1
            count[1] += 1
        return False
    
    
    def check_answer(self, token, game):
        
        user_answer = request.form.get('answer')
        real_answer = redis_client.hget(token, 'answer').decode('utf-8')
        statement = False

        if user_answer and ("fill_blank" in game.param or "trivia_madness" in game.param):
            user_answer = digit_to_word_converter.find_and_convert_numbers(user_answer)
            correct = self.is_close_match(self.normalise_answer(user_answer), self.normalise_answer(real_answer))
            if '/' in real_answer and correct == False:
                real_answer_part_one = real_answer.split('/')[0]
                real_answer_part_two = real_answer.split('/')[1]
                if self.is_close_match(self.normalise_answer(user_answer), self.normalise_answer(real_answer_part_one)) \
                    or self.is_close_match(self.normalise_answer(user_answer), self.normalise_answer(real_answer_part_two)):
                    correct = True
            if ' and ' in user_answer and correct == False:
                answer_part_one = user_answer.split(' and ')[0]
                answer_part_two = user_answer.split(' and ')[1]
                user_answer = answer_part_two + ' and ' + answer_part_one
                correct = self.is_close_match(self.normalise_answer(user_answer), self.normalise_answer(real_answer))
            if ' & ' in user_answer and correct == False:
                answer_part_one = user_answer.split(' & ')[0]
                answer_part_two = user_answer.split(' & ')[1]
                user_answer = answer_part_two + ' & ' + answer_part_one
                correct = self.is_close_match(self.normalise_answer(user_answer), self.normalise_answer(real_answer))

        elif "number" in game.param:
            correct = user_answer == real_answer
            set_question = redis_client.hget(token, 'question').decode('utf-8')
            real_answer = f"{real_answer} = {set_question[39:-1]}"
            
        elif user_answer and "_mc" in game.param:
            correct = self.normalise_answer(user_answer) == self.normalise_answer(real_answer)

        elif "_tf" in game.param:
            set_question = redis_client.hget(token, 'question').decode('utf-8')
            if user_answer == "True" and set_question == real_answer:
                correct, statement = True, True
            elif user_answer == "False" and set_question != real_answer:
                correct, statement = True, False
            elif user_answer == "True" and set_question != real_answer:
                correct, statement = False, False
                user_answer = set_question
            elif user_answer == "False" and set_question == real_answer:
                correct, statement = False, True
            else:
                correct, statement = False, set_question == real_answer

        else:
            user_answer = "No answer given"
            correct = False
        
        return correct, statement, real_answer, user_answer
            

answer_checker = AnswerChecker()
