import re


class DigitToWordConverter:


    def word_chunk(self, chunk):
        units = ['','one','two','three','four','five','six','seven','eight','nine']
        teens = ['','eleven','twelve','thirteen','fourteen','fifteen','sixteen', 'seventeen','eighteen','nineteen']
        tens = ['','ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']

        if chunk == 0:
            return ''
        elif chunk < 10:
            return units[chunk]
        elif chunk < 20:
            return teens[chunk-10]
        elif chunk < 100:
            return tens[chunk//10] + ('' if chunk % 10 == 0 else ' ' + units[chunk % 10])
        else:
            return units[chunk//100] + ' hundred' + ('' if chunk % 100 == 0 else ' and ' + self.word_chunk(chunk % 100))


    def number_to_words(self, n):
        if n == 0:
            return 'zero'
        
        thousands = ['','thousand','million','billion']
        
        words = []
        str_n = str(n).zfill(12)
        for i in range(0, 12, 3):
            chunk = int(str_n[9-i:12-i])
            if chunk:
                words.append(self.word_chunk(chunk) + ' ' + thousands[i//3])

        return ' '.join(filter(None, reversed(words))).strip()


    def find_and_convert_numbers(self, text):
        numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*(?!\d)|\b\d+\b', text)
        # print("NUMBERS: ", numbers)
        converted = {num: self.number_to_words(int(num.replace(',', ''))) for num in numbers}
        for num, words in converted.items():
            text = text.replace(num, words)
        # print("TEXT: ", text)
        return text
