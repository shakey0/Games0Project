from spellchecker import SpellChecker
spell = SpellChecker()
import re


def spell_check_sentence(sentence):
    spell_check_sentence = sentence.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(';', '').replace(':', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '')
    split_sentence = spell_check_sentence.split()
    split_sentence = [word for word in split_sentence if not word[0].isupper()]
    wrong_words = spell.unknown(split_sentence)
    if wrong_words:
        if all('.' in word for word in wrong_words):
            return True
        return False
    return True


def format_answer(answer):
    replace_chars = [' ', '-', '&', "'", '"', '(', ')', ',', '.', '?', '!', ':', ';', '$', '£', '€',
                    '%', '+', '=', '/', '\'', '*', '@', '#', '~', '<', '>']
    for char in replace_chars:
        answer = answer.replace(char, '')
    return answer


def normalise_answer(answer):
    digit_to_word = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three',
        '4': 'four', '5': 'five', '6': 'six', '7': 'seven',
        '8': 'eight', '9': 'nine'
    }
    answer = answer.lower().strip()
    answer = ''.join(digit_to_word.get(char, char) for char in answer)

    if '&' in answer:
        answer = answer.replace('&', '')
    if 'and' in answer:
        answer = answer.replace('and', '')

    for article in ['the ', 'a ', 'an ']:
        if answer.startswith(article):
            answer = answer[len(article):]
            break

    return format_answer(answer)


def is_close_match(str1, str2):
    # Check if the strings are the same or differ by only one character
    len_str1, len_str2 = len(str1), len(str2)
    if len_str1 > len_str2 + 1 or len_str1 + 1 < len_str2:
        return False

    i, j, diff = 0, 0, 0
    while i < len_str1 and j < len_str2:
        if str1[i] != str2[j]:
            if diff:
                return False
            diff = 1
            if len_str1 > len_str2:
                i += 1
            elif len_str1 < len_str2:
                j += 1
            else:
                i += 1
                j += 1
        else:
            i += 1
            j += 1
    return True


def number_to_words(n):
    if n == 0:
        return 'zero'

    units = ['','one','two','three','four','five','six','seven','eight','nine']
    teens = ['','eleven','twelve','thirteen','fourteen','fifteen','sixteen', 'seventeen','eighteen','nineteen']
    tens = ['','ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    thousands = ['','thousand','million','billion']

    def word_chunk(chunk):
        if chunk == 0:
            return ''
        elif chunk < 10:
            return units[chunk]
        elif chunk < 20:
            return teens[chunk-10]
        elif chunk < 100:
            return tens[chunk//10] + ('' if chunk % 10 == 0 else ' ' + units[chunk % 10])
        else:
            return units[chunk//100] + ' hundred' + ('' if chunk % 100 == 0 else ' and ' + word_chunk(chunk % 100))

    words = []
    for i, chunk in enumerate(reversed(str(n).zfill(12))):
        chunk = int(chunk)
        if chunk or i % 3 == 0:
            words.append(word_chunk(chunk) + ('' if i == 0 else ' ' + thousands[i//3]))
    
    return ' '.join(reversed(words)).strip()


def find_and_convert_numbers(text):
    # Regular expression to find full numbers, including those with commas
    numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*\b', text)
    
    # Convert each number to words and build a dictionary
    converted = {num: number_to_words(int(num.replace(',', ''))) for num in numbers}

    # Replace each number in the text with its word representation
    for num, words in converted.items():
        text = text.replace(num, words)

    return text
