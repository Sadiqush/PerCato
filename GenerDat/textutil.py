import pathlib
from typing import List, Tuple, Iterable
from re import finditer
import os

import numpy as np
from skimage.measure import label
from PIL import Image, ImageDraw, ImageFont

from GenerDat.characterutil import *
from functools import reduce
from GenerDat.container import ImageMeta

# JOINER = u'\u200d'
# NON_JOINER = u'\u200c'
# JOINABLE_LETTERS = "ضصثقفغعهخحجچشسیبلتنمکگظطپئ"
# NON_JOINABLE_LETTERS = "رزدذواآأ"
# ALPHABET = JOINABLE_LETTERS + NON_JOINABLE_LETTERS
# SYMBOLS = r"|{}[]؛:«»؟<>ء\/.=-+()*،×٪٫٬!"
# NUMBERS = "۰۱۲۳۴۵۶۷۸۹"
# VOWEL_SYMBOLS = [chr(i) for i in (1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1648)]


class TextGen:
    """
    This class generates images and their metadata using given text and font.

    Args:
        font_path (str): absolute path for the .ttf font file.
        font_size (int): font size for the text.
        exceptions: exception words, e.g. لا.
    """

    def __init__(self, font_path, font_size, exceptions: Iterable[str] = None, anti_alias=False):
        self.char_manager = CharacterManager()
        self.font = ImageFont.truetype(font_path, size=font_size, encoding='utf-8')
        self._dummy = ImageDraw.Draw(Image.new('L', (0, 0)))
        self.exceptions = set(exceptions) if exceptions else set()
        self.anti_alias = anti_alias

    def create_meta_image(self, text):
        """Generates metadata for ImageMeta class to use"""
        image = self.create_image(text)
        boxes = self.get_boxes(image, text)
        parts = self.get_characters(text)
        # visible_parts = self.get_visible_parts(text)
        meta = ImageMeta(text, image, parts, boxes)
        return meta

    def create_image(self, text):
        """Generates image by given font and text"""
        size = self.get_size(text)
        image = Image.new('L', size, color='black')
        if self.anti_alias:
            image = image.resize(image.size, resample=Image.ANTIALIAS)
        d = ImageDraw.Draw(image)
        d.text((0, 0), text, "white", spacing=0, font=self.font, direction='rtl', language='fa-IR')
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

        def check_pixel(image, x0, x1, y0, y1, i, j):
            good = False
            img_pixels = self.get_connected_pixels(image, i, j)
            # img_pixels = image
            seg_pixels = [pixel for pixel in img_pixels if x0 <= pixel[0] <= x1 and y0 <= pixel[1] <= y1]
            # if (np.sum(seg_pixels) > 0) < 4:
            #     good = False
            #     return good, seg_pixels
            ns, ni = len(seg_pixels), len(img_pixels)
            xs = []
            ys = []
            for pixel in seg_pixels:
                xs.append(pixel[0])
                ys.append(pixel[1])
            shape = (max(xs) + 1 - min(xs), max(ys) + 1 - min(ys))
            if ns + 2 >= ni:
                good = True
            elif shape[0] < 2 or shape[1] < 2:
                good = False
            elif ns / (ns + ni) > 0.1 or ns > 15:
                good = True
            return good, seg_pixels

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

    def get_connected_pixels(self, image: np.ndarray, i, j):
        labels: np.ndarray = label(image > 0)
        coords = np.where(labels == labels[i, j])
        return list(zip(*coords))

    def get_size(self, text) -> Tuple[int, int]:
        """Returns image size of the given text. Font itself is effective on the size."""
        return self._dummy.textsize(text, spacing=0, font=self.font, language='fa_IR', direction="rtl")

    def get_characters(self, text, freeze_letters=True):
        """Gets characters of a text as a list with respect to exceptions."""
        chars = list(self.char_manager.fix_letters(text, reject_unknown=True)) if freeze_letters else list(text)
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
        chars = self.get_characters(text)
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
    gen = TextGen(font_path, 64, ['لا', 'لله', 'ریال'])
    pathlib.Path(image_path).mkdir(parents=True, exist_ok=True)
    if is_meaningful:
        with open('words.csv', 'r', encoding='utf-8') as file:
            text = file.read()
            words = list(text.split('\n'))
        alphabet = list(gen.char_manager._letters_map)
        words = [word for word in words if all(c in alphabet for c in word)]
        words = np.random.choice(words, batch).tolist()
    else:
        words = gen.char_manager.get_equal_words(length, batch)
    print("start...")
    flush_period = 100
    with open(json_path, 'w') as file:
        print(f"generating in: {image_path}")
        for i in range(batch):
            word = words[i]
            # print(word)
            meta = gen.create_meta_image(word)
            meta.save_image(f"{image_path}/image{meta.id}.png")
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
    return None


if __name__ == '__main__':
    image_path = os.path.join(pathlib.Path.home(), 'Projects/OCR/datasets/data10/images')
    json_path = os.path.join(image_path, "../final.json")
    ocr_path = os.path.join(pathlib.Path.home(), 'PycharmProjects/ocrdg/GenerDat/')
    font_path = os.path.join(ocr_path, "b_nazanin.ttf")
    batch = 10
    length = 5
    is_meaningful = False
    main()
