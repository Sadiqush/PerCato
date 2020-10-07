import json
import os
import pathlib
import numpy as np
import pandas as pd
from itertools import product
from typing import List, Tuple, Iterable, Set
from PIL import Image, ImageDraw, ImageFont, ImageColor
JOINER = chr(8205)
JOINABLES = "ضصثقفغعهخحجچشسیبلتنمکگظطپئ"
NON_JOINABLES = " ؟ .،×٪٬!"


class ImageMeta:
    id = 0
    def __init__(self,text, image, parts, boxes):
        self.text = text
        self.image = image
        self.parts = parts
        self.boxes = boxes
        self.id = ImageMeta.id
        ImageMeta.id += 1
        self.length = len(parts)

    def save_image(self, path, transpose=False):
        image = Image.fromarray(self.image.transpose() if transpose else self.image)
        image.save(path)

    def save_image_with_boxes(self, path, color="yellow", transpose=False):
        image = self.image.transpose()
        image = np.concatenate([image[..., np.newaxis]] * 3, axis=2)
        value = list(ImageColor.getrgb(color))
        for x0, y0, x1, y1 in self.boxes:
            image[x0:x1 + 1, y0] = value
            image[x0:x1 + 1, y1] = value
            image[x0, y0:y1 + 1] = value
            image[x1, y0:y1 + 1] = value
        Image.fromarray(image.transpose((1,0,2))).save(path)

    def to_dict(self, path):
        w, h = self.image.shape
        dic = {"id":self.id, "text":self.text, "image_name":path, "parts":self.parts, "width":w, "height":h,
               "boxes":self.boxes, "n": self.length}
        return dic

class TextGen:
    def __init__(self, font_path, font_size, exceptions: Iterable[str] = None):
        self.font = ImageFont.truetype(font_path, size=font_size, encoding='utf-8')
        self._dummy = ImageDraw.Draw(Image.new('L', (0, 0)))
        self.exceptions = set(exceptions) if exceptions else set()

    def create_image(self, text):
        size = self.get_size(text)
        image = Image.new('L', size, color='black')
        d = ImageDraw.Draw(image)
        d.text((0, 0), text, "white", spacing=0, font=self.font, direction='rtl', language='fa-IR')
        return np.array(image)

    def create_meta_image(self, text):
        image = self.create_image(text)
        boxes = self.get_rectangles(image,text)
        parts = self.get_characters(text)
        meta = ImageMeta(text, image, parts, boxes)
        return meta

    def get_rectangles(self, image: np.ndarray, text):
        x1i = 0
        widths = self.get_character_widths(text)
        image = image.transpose()
        width, height = image.shape
        widths = [0] + widths
        # ux0, ux1 = x0, x1
        rectangles = []
        n = len(widths)
        for i in range(n - 1):
            x0, x1 = widths[i], widths[i + 1]
            y0, y1 = 0, height - 1
            good_pixels = set()
            bad_pixels = set()

            def check_pixel(image, x0, x1, y0, y1, i, j):
                good = False
                img_pixels = self.get_connected_pixels(image, i, j)
                seg_pixels = [pixel for pixel in img_pixels if x0 <= pixel[0] <= x1 and y0 <= pixel[1] <= y1]
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
        a = [(i, j)]
        w, h = image.shape
        idx, n = 0, 1
        while idx < n:
            i, j = a[idx]
            to_check = [(i + 1, j), (i, j + 1), (i - 1, j), (i, j - 1)]
            for x, y in to_check:
                if 0 <= x < w and 0 <= y < h and (x, y) not in a and image[x, y] > 0:
                    a.append((x, y))
                    n += 1
            idx += 1
        return a

    def get_size(self, text) -> Tuple[int, int]:
        return self._dummy.textsize(text, spacing=0, font=self.font, language='fa_IR', direction="rtl")

    def get_characters(self, text):
        n = len(text)
        chars = []
        while n > 0:
            ex = self._search_exception_backward(n, text)
            count = len(ex) if ex else 1
            chars.append(text[n - count:n])
            n -= count
        return chars

    def get_character_widths(self, text) -> List[int]:
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
        n = len(text)
        items = []
        while n > 0:
            c = text[n - 1]
            if c == " ":
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

    def _search_exception_backward(self, end, text):
        if self.exceptions:
            for item in self.exceptions:
                n = len(item)
                if n <= end and item == text[end - n:end]:
                    return item
        return ''

    @staticmethod
    def is_joined(str0, str1):
        if str0:
            c0 = str0[-1]
        else:
            return False
        if str1:
            c1 = str1[0]
        else:
            return False
        if c0 in JOINABLES and c1 not in NON_JOINABLES:
            return True
        else:
            return False


def get_mask(image: np.ndarray, x0, y0, x1, y1):
    temp_mask = np.zeros(image.shape, '?')
    temp_mask[x0:x1 + 1, y0:y1 + 1] = 1
    mask: np.ndarray = (image > 0) & temp_mask
    return mask.astype('b')


def binary_rle(arr):
    rle = []
    last = 0
    l = 0
    for num in arr:
        if num == last:
            l += 1
        else:
            rle.append(l)
            last = num
            l = 1
    rle.append(l)
    if last == 0:
        rle.append(0)
    return rle


def binary_rle_decode(rle, delimiter=' '):
    rle_arr = np.fromstring(rle, 'i', sep=delimiter)
    arr = []
    zeros = rle_arr[::2]
    ones = rle_arr[1::2]
    for i in range(0, len(zeros)):
        arr.extend([0] * zeros[i])
        arr.extend([0] * ones[i])
    return arr


def get_words_of_length(length:int, repetition=False, letters:str = 'ضصثقفغعهخحجچشییبلاتنمکگظطزرذدپوژ') -> Set:
    tuples = product(letters, repeat=length)
    if repetition:
        return {''.join(tup) for tup in tuples if len(set(tup)) == length}
    else:
        return {''.join(tup) for tup in tuples}


def main():
    gen = TextGen(r"b_nazanin.ttf", 64, ['لا', 'لله', 'ریال'])
    text = "صادق"
    pathlib.Path("/images").mkdir(parents=True, exist_ok=True)
    words = pd.read_excel(r"words.xlsx").to_numpy()[:, 0]
    non = u'\u200c'
    loqats = 'ضصثقفغعهخحجچشییبلاتنمکگظطزرذدپوژ'
    words = [word for word in words if all(c in loqats for c in word)]
    words = np.random.choice(words, 30).tolist()
    print("start...")
    image_dicks = []
    n = len(words)
    flush_period = 1
    with open("final.json", 'w') as file:
        for i in range(n):
            word = words[i]
            meta = gen.create_meta_image(word)
            meta.save_image(f"images/image{meta.id}.png")
            meta.save_image_with_boxes(f"images/image_box{meta.id}.jpg")
            print(f"{meta.id}) {word}")
            image_dicks.append(meta.to_dict(f"image{meta.id}.png"))
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


if __name__ == '__main__':
    main()