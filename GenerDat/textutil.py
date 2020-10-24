import json
import pathlib
import os
import random
from itertools import product
from typing import List, Tuple, Iterable, Set

import numpy as np
from skimage.measure import label
from PIL import Image, ImageDraw, ImageFont, ImageColor

JOINER = u'\u200d'
NON_JOINER = u'\u200c'
JOINABLE_LETTERS = "ضصثقفغعهخحجچشسیبلتنمکگظطپئ"
NON_JOINABLE_LETTERS = "رزدذواآأ"
ALPHABET = JOINABLE_LETTERS + NON_JOINABLE_LETTERS
SYMBOLS = "|{}[]؛:«»؟<>ء\/.=-+()*،×٪٫٬!"
NUMBERS = "۰۱۲۳۴۵۶۷۸۹"
VOWEL_SYMBOLS = [chr(i) for i in (1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1648)]


class ImageMeta:
    """
    This class is used to export images along with generated metadata, aka making the json file.

    Args:
        text (str): input text for json.
        image (np.array): the output image.
        parts (): text chars for json.
        boxes ():
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
        json_dic = {"id": self.id, "text": self.text, "image_name": path, "parts": self.parts,
                    "width": w, "height": h, "boxes": self.boxes, "n": self.length}
        return json_dic


class TextGen:
    """
    This class generates images and their metadata using given text and font.

    Args:
        font_path (str): absolute path for the .ttf font file.
        font_size (int): font size for the text.
        exceptions: exception words, e.g. لا.
    """

    def __init__(self, font_path, font_size, exceptions: Iterable[str] = None):
        self.font = ImageFont.truetype(font_path, size=font_size, encoding='utf-8')
        self._dummy = ImageDraw.Draw(Image.new('L', (0, 0)))
        self.exceptions = set(exceptions) if exceptions else set()

    def create_meta_image(self, text):
        """Generates metadata for ImageMeta class to use"""
        image = self.create_image(text)
        boxes = self.get_rectangles(image, text)
        parts = self.get_characters(text)
        # visible_parts = self.get_visible_parts(text)
        meta = ImageMeta(text, image, parts, boxes)
        return meta

    def create_image(self, text):
        """Generates image by given font and text"""
        size = self.get_size(text)
        image = Image.new('L', size, color='black')
        d = ImageDraw.Draw(image)
        d.text((0, 0), text, "white", spacing=0, font=self.font, direction='rtl', language='fa-IR')
        return np.array(image)

    def get_rectangles(self, image: np.ndarray, text):
        """Generates bboxes using generated image and the containing text"""
        x1i = 0
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
                    raise Exception("Only one of the this shids must be passed.")
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
                    # print("herex:",x,j)
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
        rectangles = self.get_rectangles(image, text)
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
        # from skimage.filters import threshold_otsu
        # from skimage.segmentation import clear_border
        # from skimage.measure import label
        # from skimage.morphology import closing, square
        # thresh = threshold_otsu(image)
        # bw = closing(image > thresh, square(3))
        # cleared = clear_border(bw)
        # labels: np.ndarray = label(cleared)
        labels: np.ndarray = label(image > 0)
        coords = np.where(labels == labels[i, j])
        return list(zip(*coords))

    def get_size(self, text) -> Tuple[int, int]:
        """Returns image size of the given text. Font itself is effective on the size."""
        return self._dummy.textsize(text, spacing=0, font=self.font, language='fa_IR', direction="rtl")

    def get_characters(self, text):
        """Gets characters of a text as a list with respect to exceptions."""
        n = len(text)
        chars = []
        while n > 0:
            ex = self._search_exception_backward(n, text)
            count = len(ex) if ex else 1
            chars.append(text[n - count:n])
            n -= count
        return chars

    def get_character_widths(self, text) -> List[int]:
        """Returns a list containing widths (and only width) of characters in a text."""
        if len(text) - text.count(JOINER) < 2:
            w, _ = self.get_size(text)
            return [w - 1]
        reduced = self.reduce(text)
        # print(reduced)
        widths = []
        width, _ = self.get_size(text)
        for item in reduced[1:]:
            w, _ = self.get_size(item)
            widths.append(width + 1 - w)
        widths.append(width - 1)
        return widths

    def reduce(self, text):
        """why tf I exist?"""
        n = len(text)
        items = []
        while n > 0:
            lastc = text[n - 1]
            if lastc == " ":
                n -= 1
                continue
            s = text[:n]
            ex = self._search_exception_backward(n, text)
            count = len(ex) if ex else 1
            if self.is_joined(s, text[n:]):
                s += JOINER
            items.append(s)
            n -= count
        return items

    def _search_exception_backward(self, leng, text):
        """Finds exceptions (e.g. لا) in a text and returns it as a string."""
        if self.exceptions:
            for item in self.exceptions:
                n = len(item)
                if n <= leng and item == text[leng - n:leng]:    # [leng - n:leng]?
                    return item
        return None

    def get_visible_parts(self, text):
        chars = self.get_characters(text)
        chars.reverse()
        visible_parts = []
        i, n = 0, len(chars)
        while i < n - 1:
            c = chars[i]
            if self.is_joined(c, chars[i + 1]):
                c += JOINER
            visible_parts.append(c)
            i += 1
        visible_parts.append(chars[i])
        print(visible_parts)
        return visible_parts

    @staticmethod
    def get_join_alphabet(view=False):
        """Create an alphabet that consists of all kinds of models of arabic letters"""
        letters = []
        for c in range(65165, 65264):  # TODO: Its arabic unicode. Use persian alphabet
            letters.append(chr(c))
        if view:
            print("the alphabet is a total of %s:" % len(letters))
            for i in letters:
                print(f"{i}\t", end="")
        return letters

    @staticmethod
    def is_joined(str0, str1):
        """Checks if two string are joinable. returns bool."""
        if str0:
            c0 = str0[-1]
        else:
            return False
        if str1:
            c1 = str1[0]
        else:
            return False
        if c0 in JOINABLE_LETTERS and c1 not in SYMBOLS + NUMBERS:
            return True
        else:
            return False

    @staticmethod
    def get_glyph(string, index):
        c = string[index]
        if TextGen.is_joined(string[:index + 1], string[index + 1:]):
            c += JOINER
        return c


def get_mask(image: np.ndarray, x0, y0, x1, y1):
    temp_mask = np.zeros(image.shape, '?')
    temp_mask[x0:x1 + 1, y0:y1 + 1] = 1
    mask: np.ndarray = (image > 0) & temp_mask
    return mask.astype('b')


def get_words_of_length(length: int, repetition=False, letters: str = ALPHABET) -> Set:
    tuples = product(letters, repeat=length)
    if repetition:
        return {''.join(tup) for tup in tuples if len(set(tup)) == length}
    else:
        return {''.join(tup) for tup in tuples}


def get_equal_words(length: int, batch: int, all_join=True) -> List:
    """Generate random words with equal weight (probability) for letters"""
    if all_join:
        letters = TextGen.get_join_alphabet(view=True)
    else:
        letters = ALPHABET
    # print(letters)

    words = []
    random.seed(42)
    for i in range(batch):
        word = ''.join(random.choices(letters, k=length, weights=[1] * len(letters)))
        words.append(word)
    # print(words)

    return words


def main():
    gen = TextGen(font_path, 64, ['لا', 'لله', 'ریال'])
    pathlib.Path(image_path).mkdir(parents=True, exist_ok=True)
    if is_meaningful:
        with open('words.csv', 'r', encoding='utf-8') as file:
            text = file.read()
            words = list(text.split('\n'))
        words = [word for word in words if all(c in ALPHABET for c in word)]
        words = np.random.choice(words, batch).tolist()
    else:
        words = get_equal_words(length, batch, True)
    words = ['لالایی'] + words
    print(words)
    print("start...")
    n = len(words)
    flush_period = 100
    with open(json_path, 'w') as file:
        print(f"generating in: {image_path}")
        for i in range(n):
            word = words[i]
            meta = gen.create_meta_image(word)
            meta.save_image(f"{image_path}/image{meta.id}.png")
            meta.save_image_with_boxes(f"{image_path}/image_box{meta.id}.jpg")
            print(f"{meta.id}) {word}")
            js = json.dumps(meta.to_dict(f"image{meta.id}.png"))
            if i == 0:
                js = "[{}".format(js)
            elif i == n - 1:
                js = ",\n{}]".format(js)
            else:
                if i % flush_period == 0:
                    file.flush()
                js = ",\n{}".format(js)
            file.write(js)
    return None


if __name__ == '__main__':
    image_path = os.path.join(pathlib.Path.home(), 'Projects/OCR/datasets/data4/images')
    json_path = os.path.join(image_path, "../final.json")
    ocr_path = os.path.join(pathlib.Path.home(), 'PycharmProjects/ocrdg/GenerDat/')
    font_path = os.path.join(ocr_path, "b_nazanin.ttf")
    batch = 10
    length = 3
    is_meaningful = False
    main()
