import json
from enum import IntFlag
from typing import Union, Dict
import random
from copy import copy, deepcopy


class Character:
    def __init__(self, character, description=None, unicode=-1):
        self.unicode = unicode
        self.description = description
        self.character = character

    def __str__(self):
        return self.character

    def __repr__(self):
        return str(self.__dict__)


class PersianLetterForm(IntFlag):
    ISOLATED = 0
    INITIAL = 1
    FINAL = 2
    MEDIAL = 3


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

    def __copy__(self):
        c = PersianLetter('\0')
        c.__dict__ = self.__dict__.copy()
        return c


class CharacterManager:
    sadiq_letters = ['ﺎ', 'ﺐ', 'ﺒ', 'ﺑ', 'ﺖ', 'ﺘ', 'ﺗ', 'ﺚ', 'ﺛ', 'ﺞ', 'ﺟ',
                     'ﺢ', 'ﺣ', 'ﺦ', 'ﺧ', 'ﺪ', 'ﺩ', 'ﺬ', 'ﺮ', 'ﺰ', 'ﺲ',
                     'ﺳ', 'ﺶ', 'ﺷ', 'ﺺ', 'ﺻ', 'ﺾ', 'ﺿ', 'ﻂ',
                     'ﻆ', 'ﻉ', 'ﻊ', 'ﻋ', 'ﻌ', 'ﻍ', 'ﻎ', 'ﻏ', 'ﻐ',
                     'ﻒ', 'ﻔ', 'ﻓ', 'ﻖ', 'ﻗ', 'ﻘ', 'ﻚ', 'ﻛ', 'ﻞ',
                     'ﻟ', 'ﻠ', 'ﻢ', 'ﻣ', 'ﻡ', 'ﻦ', 'ﻨ', 'ﻧ', 'ﻩ', 'ﻪ', 'ﻫ',
                     'ﻬ', 'ﻮ', 'ﯼ', 'ﻴ', 'ﯾ', 'ﭗ', 'ﭘ', 'ﭻ', 'ﭼ', 'ﮋ',
                     'ﮓ', 'ﮔ', 'ﺋ', 'ﺁ', 'ﺍ', 'لا']   # ـلا ?

    def __init__(self, json_path: str = "letters.json"):
        self._letter_map: Dict[str, PersianLetter] = self.load_persian_letters(json_path)
        self._letter_forms = None
        self._form_letter_map = None

    def get_persian_letters(self, as_dict=False):
        return {letter.character: copy(letter) for letter in self._letter_map.values()} if as_dict \
            else list(self._letter_map.keys())

    def get_persian_letter_forms(self):
        if self._letter_forms is None:
            forms = set()
            forms.update(*((v.initial_form, v.medial_form, v.final_form, v.isolated_form)
                           for v in self._letter_map.values()))
            if None in forms:
                forms.remove(None)
            self._letter_forms = list(forms)
        return copy(self._letter_forms)

    def get_form_of_letter(self, c, throw_unknown=False):
        if self._form_letter_map is None:
            self.get_form_letter_map()
        assert len(c) == 1, f"'{c}' is not a character"
        form = next(iter(form for form, letters in self._form_letter_map.items() if c in letters), -1)
        if form == -1 and throw_unknown:
            raise Exception(f"Form of '{c}' is not found.")
        return form

    def get_form_letter_map(self):
        form = PersianLetterForm
        if self._form_letter_map is None:
            flp = {form.ISOLATED: set(), form.INITIAL: set(), form.FINAL: set(), form.MEDIAL: set()}
            for c in self._letter_map.values():
                isolated, initial, final, medial = c.isolated_form, c.initial_form, c.final_form, c.medial_form
                if isolated: flp[form.ISOLATED].add(isolated)
                if initial: flp[form.INITIAL].add(initial)
                if final: flp[form.FINAL].add(final)
                if medial: flp[form.MEDIAL].add(medial)
            self._form_letter_map = flp
        return deepcopy(self._form_letter_map)

    @staticmethod
    def load_persian_letters(json_path='letters.json'):
        with open(json_path, 'r', encoding="utf-8") as file:
            letters_dict_list = json.load(file)["letters"]
        letters = {}
        for letter_dict in letters_dict_list:
            letter = PersianLetter('\0')
            letter.__dict__ = letter_dict
            letters[letter.character] = letter
        return letters

    def freeze_letters(self, string: str, throw_unknown=False):
        frozen_letters = []
        for i, c in enumerate(string):
            if c in self._letter_map:
                c = self.get_letter_form(string, i)
            elif throw_unknown:
                raise Exception(f"Unknown letter '{c}' in \"{string}\".")
            frozen_letters.append(c)
        return "".join(frozen_letters)

    def get_letter_form(self, string: str, index: int) -> str:
        flag = 0
        c = string[index]
        if index < len(string) - 1:
            cf = string[index + 1]
            if cf in self._letter_map and \
                    self._letter_map[c].can_connect(PersianLetterSide.FRONT) and \
                    self._letter_map[cf].can_connect(PersianLetterSide.BACK):
                flag |= PersianLetterSide.FRONT
        if index > 0:
            cb = string[index - 1]
            if cb in self._letter_map and \
                    self._letter_map[c].can_connect(PersianLetterSide.BACK) and \
                    self._letter_map[cb].can_connect(PersianLetterSide.FRONT):
                flag |= PersianLetterSide.BACK
        return self._letter_map[c].get_connected_form(flag)

    def get_equal_words(self, length: int, batch: int, occurrence=1, seed=None, ugly=False):
        """Generate random words with equal weight (probability) for letters"""
        choices = random.Random(seed).choices if seed else random.choices
        letters = CharacterManager.sadiq_letters if ugly else self.get_persian_letters()
        if 1 < occurrence <= length:
            letters *= occurrence
        words = list({''.join(choices(letters, k=length)) for _ in range(batch)})
        return words


if __name__ == '__main__':
    cm = CharacterManager()
    flm = cm.get_form_letter_map()
    print(flm)
    print(cm.get_form_of_letter('n', throw_unknown=True))
