from spellchecker import SpellChecker
spell = SpellChecker()


def format_answer(answer):
    replace_chars = [' ', '-', '&', "'", '"', '(', ')', ',', '.', '?', '!', ':', ';', '$', '£', '€',
                    '%', '+', '=', '/', '\'', '*', '@', '#', '~', '<', '>']
    for char in replace_chars:
        answer = answer.replace(char, '')
    return answer.lower()


def spell_check_sentence(sentence):
    spell_check_sentence = sentence.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(';', '').replace(':', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '')
    wrong_words = spell.unknown(spell_check_sentence.split())
    if wrong_words:
        if all('.' in word for word in wrong_words):
            return True
        return False
    return True