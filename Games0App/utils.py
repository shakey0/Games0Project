def format_answer(answer):
    replace_chars = [' ', '-', '&', "'", '"', '(', ')', ',', '.', '?', '!', ':', ';', '$', '£', '€',
                    '%', '+', '=', '/', '\'', '*', '@', '#', '~', '<', '>']
    for char in replace_chars:
        answer = answer.replace(char, '')
    return answer

def normalise_answer(answer):
    answer = answer.lower().strip()

    if ' & ' in answer:
        answer = answer.replace('&', '')
    if ' and ' in answer:
        answer = answer.replace('and', '')

    for article in ['the ', 'a ', 'an ', 'some ', 'my ', 'your ', 'he ', 'his ', 'she ', 'her ', 'hers ', 'it ', 'its ', 'we ', 'our ', 'they ', 'their ', 'it\'s ', 'they\'re', 'he\'s', 'she\'s']:
        if answer.startswith(article):
            answer = answer[len(article):]
            break

    return format_answer(answer)


def is_close_match(user_answer, real_answer):
    if real_answer.lower() in user_answer.lower(): # NEEDS TESTING - MAY BE TOO LENIENT
        return True
    
    # Check if the strings are the same or differ by only one character
    len_u_answer, len_r_answer = len(user_answer), len(real_answer)
    if len_u_answer > len_r_answer + 1 or len_u_answer + 1 < len_r_answer:
        return False

    i, j, diff = 0, 0, 0
    while i < len_u_answer and j < len_r_answer:
        if user_answer[i] != real_answer[j]:
            if diff:
                return False
            diff = 1
            if len_u_answer > len_r_answer:
                i += 1
            elif len_u_answer < len_r_answer:
                j += 1
            else:
                i += 1
                j += 1
        else:
            i += 1
            j += 1
    return True


def format_datetime(dt):

    suffixes = {1: 'ˢᵗ', 2: 'ⁿᵈ', 3: 'ʳᵈ'}
    
    day = dt.day
    suffix = suffixes.get(day if 10 <= day % 100 <= 20 else day % 10, 'ᵗʰ')
    
    formatted_date_time = dt.strftime(f'%d{suffix} %b at %H:%M').replace(f'{day}{suffix}', f'{day}{suffix}')
    formatted_date_time = formatted_date_time.lstrip("0")
    
    return formatted_date_time


conversion_dict = {
    'A': 'n', 'B': '1', 'C': 'Y', 'D': 'g', 'E': '5', 'F': 'L', 'G': 'b', 'H': '9', 'I': 'r', 'J': 'w',
    'K': '0', 'L': 'Q', 'M': 'u', 'N': 'D', 'O': '2', 'P': 'z', 'Q': 'H', 'R': 'S', 'S': 'e', 'T': 'T',
    'U': 'o', 'V': '3', 'W': 'm', 'X': 'F', 'Y': 'k', 'Z': 'A', 
    'a': 'V', 'b': 'j', 'c': 'X', 'd': 'E', 'e': '6', 'f': 'M', 'g': 'i', 'h': 'P', 'i': 't', 'j': 's',
    'k': 'G', 'l': 'J', 'm': '8', 'n': 'l', 'o': '4', 'p': 'B', 'q': 'Z', 'r': 'C', 's': 'q', 't': 'W',
    'u': 'd', 'v': 'I', 'w': 'K', 'x': 'R', 'y': 'p', 'z': 'v',
    '0': 'h', '1': 'c', '2': 'x', '3': 'N', '4': 'O', '5': '7', '6': 'U', '7': 'y', '8': 'a', '9': 'f'
}

def convert_scrambled_name(scrambled_name):
    unscrambled_name = ""
    scrambled_name = scrambled_name.replace("%20", " ")
    for char in scrambled_name:
        unscrambled_name += [key for key, value in conversion_dict.items() if value == char][0] if char != " " else " "
    return unscrambled_name


# from spellchecker import SpellChecker
# spell = SpellChecker()
# import os
# from openai import OpenAI
# openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


# def check_blank_answer_for_alternative(user_answer, real_answer, sentence):
#     if not re.match("^[a-zA-Z0-9]+$", user_answer):
#         return False
#     if spell.unknown([user_answer]):  # Names will be unknown, needs testing
#         return False
#     print("Sending request to OpenAI")
#     print("USER ANSWER: ", user_answer)
#     print("REAL ANSWER: ", real_answer)
#     print("SENTENCE: ", sentence.replace('____', real_answer))
#     completion = openai_client.chat.completions.create(model="gpt-3.5-turbo-1106",
#     messages=[{"role": "user",
#     "content": f"Does '{user_answer}' provide the same meaning as '{real_answer}' in the sentence '{sentence.replace('____', real_answer)}'? Answer with 'Yes' or 'No' only."}])
#     response_text = completion.choices[0].message.content
#     print(completion)
#     print("RESPONSE TEXT: ", response_text)
#     return "Yes" in response_text


# check_blank_answer_for_alternative("yellow", "invented", "An ear trumpet was used before the hearing aid was ____ by people who had difficulty hearing.")
