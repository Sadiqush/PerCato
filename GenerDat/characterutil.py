import json
from enum import IntFlag
from typing import Union, Dict
import random
from timeit import timeit


class Character:
    def __init__(self, character, description=None, unicode=-1):
        self.unicode = unicode
        self.description = description
        self.character = character

    def __str__(self):
        return self.character

    def __repr__(self):
        return str(self.__dict__)


class PersianLetterSide(IntFlag):
    NONE = 0
    BACK = 1
    FRONT = 2
    BOTH = BACK | FRONT


class PersianLetter(Character):

    def __init__(self, character, description=None, unicode=-1,
                 initial_form=None, medial_form=None, final_form=None, isolated_form=None):
        super().__init__(character, description, unicode)
        self.initial_form = initial_form
        self.medial_form = medial_form
        self.final_form = final_form
        self.isolated_form = isolated_form

    def get_connected_form(self, side_flag: Union[PersianLetterSide, int]) -> str:
        if side_flag == PersianLetterSide.BOTH and self.medial_form:
            return self.medial_form
        if side_flag & PersianLetterSide.BACK:
            return self.final_form
        if side_flag & PersianLetterSide.FRONT and self.initial_form:
            return self.initial_form
        return self.isolated_form

    def can_connect(self, side_flag: Union[PersianLetterSide, int]) -> bool:
        if PersianLetterSide.BACK & side_flag and not self.final_form:
            return False
        if PersianLetterSide.FRONT & side_flag and not self.initial_form:
            return False
        return True


class CharacterManager:
    def __init__(self, json_path: str = "letters.json"):
        self._letters_map: Dict[str, PersianLetter] = self.load_persian_letters(json_path)

    def get_persian_letters(self, as_dict=False):
        return self._letters_map.copy() if as_dict else list(self._letters_map)

    @staticmethod
    def get_persian_letters_ugly(view=False):
        """Create an alphabet that consists of all forms of letters, in ugly way."""
        letters = ['ﺍ', 'ﺎ', 'ﺏ', 'ﺐ', 'ﺑ', 'ﺒ', 'ﺕ', 'ﺖ', 'ﺗ', 'ﺘ', 'ﺙ',
                   'ﺚ', 'ﺛ', 'ﺜ', 'ﺝ', 'ﺞ', 'ﺟ', 'ﺠ', 'ﺡ', 'ﺢ', 'ﺣ', 'ﺤ',
                   'ﺥ', 'ﺦ', 'ﺧ', 'ﺨ', 'ﺩ', 'ﺪ', 'ﺫ', 'ﺬ', 'ﺭ', 'ﺮ', 'ﺯ',
                   'ﺰ', 'ﺱ', 'ﺲ', 'ﺳ', 'ﺴ', 'ﺵ', 'ﺶ', 'ﺷ', 'ﺸ', 'ﺹ', 'ﺺ',
                   'ﺻ', 'ﺼ', 'ﺽ', 'ﺾ', 'ﺿ', 'ﻀ', 'ﻁ', 'ﻂ', 'ﻅ', 'ﻆ', 'ﻉ',
                   'ﻊ', 'ﻋ', 'ﻌ', 'ﻍ', 'ﻎ', 'ﻏ', 'ﻐ', 'ﻑ', 'ﻒ', 'ﻓ', 'ﻔ',
                   'ﻕ', 'ﻖ', 'ﻗ', 'ﻘ', 'ﮎ', 'ﻚ', 'ﻛ', 'ﻜ', 'ﻝ', 'ﻞ', 'ﻟ',
                   'ﻠ', 'ﻡ', 'ﻢ', 'ﻣ', 'ﻤ', 'ﻥ', 'ﻦ', 'ﻧ', 'ﻨ', 'ﻩ', 'ﻪ',
                   'ﻫ', 'ﻬ', 'ﻭ', 'ﻮ', 'ﯼ', 'ﭖ', 'ﭗ', 'ﭘ', 'ﭙ', 'ﭺ', 'ﭻ',
                   'ﭼ', 'ﭽ', 'ژ', 'ﮋ', 'ﮒ', 'ﮓ', 'ﮔ', 'ﮕ', 'ﺃ', 'ﺋ', 'ﺊ',
                   'ﺌ', 'ﺉ', 'ﺁ', 'ؤ', 'لا']
        if view:
            print("the alphabet is a total of %s:" % len(letters))
            for i in letters:
                print(f"{i}\t", end="")

        return letters

    @staticmethod
    def load_persian_letters(json_path):
        with open('letters.json', 'r', encoding="utf-8") as file:
            letters_dict_list = json.load(file)["letters"]
        letters = {}
        for letter_dict in letters_dict_list:
            letter = PersianLetter('\0')
            letter.__dict__ = letter_dict
            letters[letter.character] = letter
        return letters

    def fix_letters(self, string: str, reject_unknown=False):
        fixed = []
        for i, c in enumerate(string):
            if c in self._letters_map:
                c = self.get_letter_form(string, i)
            elif reject_unknown:
                raise Exception(f"Unknown letter '{c}' in \"{string}\".")
            fixed.append(c)
        return "".join(fixed)

    def get_letter_form(self, string: str, index: int) -> str:
        flag = 0
        c = string[index]
        if index < len(string) - 1:
            cf = string[index + 1]
            if cf in self._letters_map and \
                    self._letters_map[c].can_connect(PersianLetterSide.FRONT) and \
                    self._letters_map[cf].can_connect(PersianLetterSide.BACK):
                flag |= PersianLetterSide.FRONT
        if index > 0:
            cb = string[index - 1]
            if cb in self._letters_map and \
                    self._letters_map[c].can_connect(PersianLetterSide.BACK) and \
                    self._letters_map[cb].can_connect(PersianLetterSide.FRONT):
                flag |= PersianLetterSide.BACK
        return self._letters_map[c].get_connected_form(flag)

    def get_equal_words(self, length: int, batch: int, ugly=True):
        """Generate random words with equal weight (probability) for letters"""
        if ugly:
            letters = self.get_persian_letters_ugly()
        else:
            letters = [letter.character for letter in self._letters_map.values()]

        words = []
        random.seed(42)
        for i in range(batch):
            word = ''.join(random.choices(letters, k=length, weights=[1] * len(letters)))
            words.append(word)
        # print(words)

        return words

    @property
    def letters_map(self):
        return self._letters_map


if __name__ == '__main__':
    cm = CharacterManager()
    x = cm.fix_letters('صادق')
    print(list(x))
