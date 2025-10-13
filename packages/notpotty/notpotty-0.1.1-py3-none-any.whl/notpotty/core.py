import re
from .words import censored_words_rus

class NotPotty:

    word_list = '|'.join(re.escape(word) for word in censored_words_rus)
    CENSOR_PATTERN = re.compile(rf'\b(?:{word_list})\b', re.IGNORECASE)

    def ffirstone(self, text):
        """Метод для поиска нецензурного слова"""
        match = self.CENSOR_PATTERN.search(text)
        if match:
            return match.group()
        return None

    @staticmethod
    def ffirst_one(text):
        """Метод для поиска нецензурного слова"""
        match = NotPotty.CENSOR_PATTERN.search(text)
        if match:
            return match.group()
        return None


    def pfirstone(self, text):
        """Метод для поиска нецензурного слова и вывода"""
        match = self.CENSOR_PATTERN.search(text)
        message = "Нецензурных слов нет"
        if match:
            message =f"Найдено нецензурное слово: {match.group()}"
            return message
        return message


    def sensor(self, text):
        """Метод сканирования нецензурного слова"""
        match = self.CENSOR_PATTERN.search(text)
        if match:
            return True
        return False
