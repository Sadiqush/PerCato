import json
import random
from copy import copy, deepcopy
from enum import IntFlag
from functools import reduce
from pathlib import Path
from re import finditer
from typing import List, Tuple, Iterable, Union, Dict

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor


class ImageMeta:
    """
    This class is used to export images along with generated metadata, aka making the json file.

    Args:
        text (str): input text for json.
        image (np.array): the output image.
        parts (list): text chars for json.
        boxes (): my anus hungers.
        id (int): wtf
    """
    id = 0

    def __init__(self, text, image: np.array, parts, boxes, id=-1):
        self.text = text
        self.image = image
        self.parts = parts
        # self.visible_parts = visible_parts
        self.boxes = boxes
        self.length = len(parts)
        if id > 0:
            self.id = id
        else:
            self.id = ImageMeta.id
            ImageMeta.id += 1

    def save_image(self, path, transpose=False):
        """
        Save image to the path.

        Args:
            path (str): absolute path for the image.
            transpose (bool): transpose image array before saving (default: False).
        """
        image = Image.fromarray(self.image.transpose() if transpose else self.image)
        image.save(path)
        return None

    def save_image_with_boxes(self, path, color="yellow", transpose=True):
        """
        Draw bbox on image and save to the path.

        Args:
            path (str): absolute path for the image.
            color (str): the color of bbox.
            transpose (bool): transpose image array before saving (default: True).
        """
        image = self.image.transpose()
        image = np.concatenate([image[..., np.newaxis]] * 3, axis=2)
        value = list(ImageColor.getrgb(color))
        for x0, y0, x1, y1 in self.boxes:
            image[x0:x1 + 1, y0] = value
            image[x0:x1 + 1, y1] = value
            image[x0, y0:y1 + 1] = value
            image[x1, y0:y1 + 1] = value
        Image.fromarray(image.transpose((1, 0, 2))).save(path)
        return None

    def to_dict(self, path):
        """
        Generate a json block for the image. It's not in COCO format.

        Args:
            path (str): non-absolute path (name) of the image.

        Returns:
            json_dic (dic): json block of the image.
        """
        h, w = self.image.shape
        # TODO: Use COCO standard format
        json_dic = {"id": self.id, "text": self.text, "image_name": path, "parts": self.parts.reverse(),
                    "width": w, "height": h, "boxes": self.boxes, "n": self.length}
        return json_dic


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
        sadiq_letters = ['ﺎ', 'ﺐ', 'ﺑ', 'ﺖ', 'ﺗ', 'ﺚ', 'ﺛ', 'ﺞ', 'ﺟ',
                         'ﺢ', 'ﺣ', 'ﺦ', 'ﺧ', 'ﺪ', 'ﺬ', 'ﺮ', 'ﺰ', 'ﺲ',
                         'ﺳ', 'ﺶ', 'ﺷ', 'ﺺ', 'ﺻ', 'ﺾ', 'ﺿ', 'ﻂ',
                         'ﻆ', 'ﻉ', 'ﻊ', 'ﻋ', 'ﻌ', 'ﻍ', 'ﻎ', 'ﻏ', 'ﻐ',
                         'ﻒ', 'ﻓ', 'ﻖ', 'ﻗ', 'ﻘ', 'ﻚ', 'ﻛ', 'ﻞ',
                         'ﻟ', 'ﻠ', 'ﻢ', 'ﻣ', 'ﻦ', 'ﻧ', 'ﻩ', 'ﻪ', 'ﻫ',
                         'ﻬ', 'ﻮ', 'ﯼ', 'ﯾ', 'ﭗ', 'ﭘ', 'ﭻ', 'ﭼ', 'ﮋ',
                         'ﮓ', 'ﮔ', 'ﺋ', 'ﺁ', 'لا']
        letters = sadiq_letters if ugly else self.get_persian_letters()
        if 1 < occurrence <= length:
            letters *= occurrence
        words = list({''.join(choices(letters, k=length)) for _ in range(batch)})
        return words


class TextGen:
    """
    This class generates images and their metadata using given text and font.

    Args:
        font_path (str): absolute path for the .ttf font file.
        font_size (int): font size for the text.
        exceptions: exception words, e.g. لا.
    """

    def __init__(self, font_path, font_size, exceptions: Iterable[str] = None, anti_alias=False, reject_unknown=True):
        self.char_manager = CharacterManager()
        self.font = ImageFont.truetype(font_path, size=font_size, encoding='utf-8')
        self._dummy = ImageDraw.Draw(Image.new('L', (0, 0)))
        self.exceptions = set(exceptions) if exceptions else set()
        self.anti_alias = anti_alias
        self.reject_unknown = reject_unknown

    def create_meta_image(self, text):
        """Generates metadata for ImageMeta class to use"""
        image = self.create_image(text)
        boxes = self.get_boxes(image, text)
        # for i, box in enumerate(boxes):
        #     mask = get_mask(image.transpose(), *box)
        #     cv2.imwrite(image_path + f'{text}ez_{i}.png', mask.transpose() * 255)
        parts = self.get_characters(text, self.reject_unknown)
        # visible_parts = self.get_visible_parts(text)
        meta = ImageMeta(text, image, parts, boxes)
        return meta

    def create_image(self, text):
        """Generates image by given font and text"""
        size = tuple(np.add(self.get_size(text), (4, 20)))
        image = Image.new('L', size, color='black')
        if self.anti_alias:
            image = image.resize(image.size, resample=Image.ANTIALIAS)
        d = ImageDraw.Draw(image)
        d.text((0, 10), text, "white", font=self.font, direction='rtl', language='fa-IR')
        return np.array(image)

    def get_boxes(self, image: np.ndarray, text):
        """Generates bounding boxes using generated image and the containing text"""
        widths = self.get_character_widths(text)
        image = image.transpose()
        width, height = image.shape
        widths = [0] + widths
        # ux0, ux1 = x0, x1
        rectangles = []
        n = len(widths)
        good_pixels = set()
        bad_pixels = set()
        x0, x1 = 0, 0
        y0, y1 = 0, 0
        label_n, labels = cv2.connectedComponents(image)
        comps_pixels = [list(zip(*np.where(labels == i))) for i in range(label_n)]
        box_pixels_cache = {}

        def check_pixel(image, x0, x1, y0, y1, i, j):
            good = False
            img_pixels = next(pixels for pixels in comps_pixels if (i, j) in pixels)
            # seg_pixels = list(zip(*np.where(labels[x0:x1 + 1, y0:y1 + 1] == labels[i, j])))
            seg_pixels = [tup for tup in img_pixels if x0 <= tup[0] <= x1 and y0 <= tup[1] <= y1]
            box = (x0, y0, x1, y1)
            if box not in box_pixels_cache:
                comp_n, seg_labels = cv2.connectedComponents(get_mask(image, x0, y0, x1, y1))
                box_pixels_cache[box] = [list(zip(*np.where(seg_labels == i))) for i in range(comp_n)]
            seg_parts_pixels = box_pixels_cache[box]
            smol_pixels = next(pixels for pixels in seg_parts_pixels if (i, j) in pixels)
            ns, ni = len(seg_pixels), len(img_pixels)
            xs, ys = zip(*seg_pixels)
            shape = (max(xs) + 1 - min(xs), max(ys) + 1 - min(ys))
            xs, ys = zip(*smol_pixels)
            smol_shape = (max(xs) + 1 - min(xs), max(ys) + 1 - min(ys))
            if ni - ns < 3:
                good = True
            elif len(smol_pixels) < 4 or smol_shape < (4, 4) or shape < (4, 4):
                good = False
            elif ns / (ns + ni) > 0.1 or ns > 15:
                good = True
            return good, smol_pixels

        def complex_condition(x=-1, y=-1):
            pixels = set()
            if x >= 0:
                if y >= 0:
                    raise Exception("Only one of the this shits must be passed.")
                iterable = [(x, j) for j in range(y0, y1 + 1)]
            elif y >= 0:
                iterable = [(i, y) for i in range(x0, x1 + 1)]
            else:
                raise Exception("No parameters.")
            for i, j in iterable:
                if image[i, j] > 0 and (i, j) not in pixels:
                    if (i, j) in bad_pixels:
                        continue
                    if (i, j) in good_pixels:
                        return False
                    good, p = check_pixel(image, x0, x1, y0, y1, i, j)
                    if good:
                        good_pixels.update(p)
                        return False
                    pixels.update(p)
                    bad_pixels.update(p)
            return True

        for i in range(n - 1):
            x0, x1 = widths[i], widths[i + 1]
            y0, y1 = 0, height - 1
            # x1i += 1
            # if x1i == 3:
            #     print("here")
            if np.sum(image[x0:x1] > 0) < 4:
                raise Exception("Given space is empty: {}:{}.".format(x0, x1))
            while complex_condition(x=x0):
                x0 += 1
            while complex_condition(x=x1):
                x1 -= 1
            while complex_condition(y=y0):
                y0 += 1
            while complex_condition(y=y1):
                y1 -= 1
            rectangles.append((x0, y0, x1, y1))
        return rectangles

    def get_pixels(self, image: np.ndarray, text) -> List[Tuple[str, List[Tuple[int, int]]]]:
        pos = len(text)
        label_pixels = []
        image = image.transpose()
        rectangles = self.get_boxes(image, text)
        for x0, y0, x1, y1 in rectangles:
            pixels = []
            for i in range(x0, x1 + 1):
                for j in range(y0, y1 + 1):
                    if image[i, j] > 0:
                        pixels.append((i, j))
            pos -= 1
            label_pixels.append((text[pos], []))
        return label_pixels

    def get_size(self, text) -> Tuple[int, int]:
        """Returns image size of the given text. Font itself is effective on the size."""
        return self._dummy.textsize(text, spacing=0, font=self.font, language='fa_IR', direction="rtl")

    def get_characters(self, text, freeze_letters=True, reject=True):
        """Gets characters of a text as a list with respect to exceptions."""
        chars = list(self.char_manager.freeze_letters(text, reject)) if freeze_letters else list(text)
        exception_spans = self.find_exceptions(text)
        # print(exception_spans)
        for s, e in exception_spans[::-1]:
            chars[s] = reduce(str.__add__, chars[s:e])
            del chars[s + 1:e]
        # print(chars)
        return chars

    def get_character_widths(self, text) -> List[int]:
        """Returns a list containing widths (and only width) of characters in a text."""
        if len(text) < 2:
            w, _ = self.get_size(text)
            return [w - 1]
        chars = self.get_characters(text, self.reject_unknown, self.reject_unknown)
        reduced = []
        n = len(chars)
        for i in range(1, n + 1):
            reduced.append("".join(chars[:i]))
        reduced.reverse()
        # print(reduced)
        width, _ = self.get_size(text)
        widths = []
        for item in reduced[1:]:
            w, _ = self.get_size(item)
            widths.append(width + 1 - w)
        widths.append(width - 1)
        return widths

    def find_exceptions(self, text) -> List[Tuple[int, int]]:
        if not self.exceptions:
            return []
        exceptions = [(match.start(), match.end()) for match in finditer("|".join(self.exceptions), text)]
        return exceptions


def get_mask(image: np.ndarray, x0, y0, x1, y1):
    temp_mask = np.zeros(image.shape, '?')
    temp_mask[x0:x1 + 1, y0:y1 + 1] = 1
    mask: np.ndarray = (image > 0) & temp_mask
    return mask.astype('b')


def main():
    gen = TextGen(font_path, 64, ['لا', 'لله', 'ریال'], reject_unknown=not ugly_mode)
    Path(image_path).mkdir(parents=True, exist_ok=True)
    words = gen.char_manager.get_equal_words(length, batch, ugly=ugly_mode)
    print("start...")
    flush_period = 100
    images = []
    with open(json_path, 'w') as file:
        print(f"generating in: {image_path}")
        for i in range(batch):
            word = words[i]
            # print(word)
            meta = gen.create_meta_image(word)
            images.append(meta.image)
            meta.save_image(f"{image_path}/image{meta.id}.png")
            # TODO: argument no meta
            meta.save_image_with_boxes(f"{image_path}/image_box{meta.id}.jpg")
            print(f"{meta.id}) {word}")
            js = json.dumps(meta.to_dict(f"image{meta.id}.png"))
            if i == 0:
                js = "[{}".format(js)
            elif i == batch - 1:
                js = ",\n{}]".format(js)
            else:
                if i % flush_period == 0:
                    file.flush()
                js = ",\n{}".format(js)
            file.write(js)
        np.savez_compressed('images', *images)


im_sadiqu = 0
if im_sadiqu:
    image_path = Path.home() / "Projects/OCR/datasets/data13/images"
    json_path = str((image_path.parent / "final.json").absolute())
    image_path = str(image_path.absolute())
    ocr_path = Path.home() / 'PycharmProjects/ocrdg/GenerDat/'
    font_path = str((ocr_path / "b_nazanin.ttf").absolute())
else:
    image_path = "images/"
    json_path = "final.json"
    font_path = "b_nazanin.ttf"

if __name__ == '__main__':
    print(font_path)
    assert Path(font_path).exists()
    batch = 10
    length = 5
    ugly_mode = False
    main()
