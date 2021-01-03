import json
import random
from pathlib import Path

import numpy as np

from textutils import TextGen


def generate_word(gen, file, word):
    print(word)
    meta = gen.create_meta_image(word)
    meta.save_image(f"{image_path}/image{meta.id}.png")
    # TODO: argument no meta
    # meta.save_image_with_boxes(f"{image_path}/image_box{meta.id}.jpg")
    print(f"{meta.id}) {word}")
    js = json.dumps(meta.to_dict(f"image{meta.id}.png"))
    if meta.id == 0:
        js = "[{}".format(js)
    elif meta.id == batch - 1:
        js = ",\n{}]".format(js)
    else:
        if meta.id % 100 == 0:
            file.flush()
        js = ",\n{}".format(js)
    file.write(js)


def get_mean_words(gen):
    with open('words.csv', 'r', encoding='utf-8') as file:
        text = file.read()
        words = list(text.split('\n'))
    alphabet = gen.char_manager.get_persian_letters()
    words = [word for word in words if all(c in alphabet for c in word)]
    words = np.random.choice(words, batch).tolist()
    return words


def get_words(gen):
    leng = random.randint(length[0], length[1])
    words = gen.char_manager.get_equal_words(leng, 10, ugly=ugly_mode)
    return words


def main():
    gen = TextGen(font_path, 64, ['لا', 'لله', 'ریال'])
    Path(image_path).mkdir(parents=True, exist_ok=True)
    gen.reject_unknown = True
    if is_meaningful:
        words = get_mean_words(gen)
    else:
        words = get_words(gen)
    print("start...")
    with open(json_path, 'w') as file:
        print(f"generating in: {image_path}")
        for i in range(int(batch/10)):
            gen.reject_unknown = not ugly_mode
            for word in words:
                generate_word(gen, file, word)
        return None


im_sadiqu = 1
if im_sadiqu:
    image_path = Path.home() / "Projects/OCR/datasets/data16-test/train_images"
    json_path = str((image_path.parent / "train_ocr.json").absolute())
    image_path = str(image_path.absolute())
    ocr_path = Path.home() / 'PycharmProjects/ocrdg/'
    font_path = str((ocr_path / "b_nazanin.ttf").absolute())
else:
    image_path = "images/"
    json_path = "final.json"
    font_path = "b_nazanin.ttf"

batch = 10
length = (3, 6)
is_meaningful = True
ugly_mode = False
using_mask = False
save_with_detectron_format = False
loosebox = False

if __name__ == '__main__':
    assert not (is_meaningful and ugly_mode), "You can't have ugly and meaningful at the same time retard."
    assert not (using_mask and loosebox), "You can't have masks and boxes at the same time retard."
    main()
