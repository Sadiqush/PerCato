import json
import random

import numpy as np

import characterutil
from textutils import TextGen
from params import *


def generate_word(gen, file, word):
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


def write_letters(json_form=False):
    """
    writes the used letters for dataset as a file
    along with other files in output directory
    """
    charman = characterutil.CharacterManager
    letters = charman.sadiq_letters
    if json_form:
        # Using JSON format writes letters as unicode
        with open(letters_path + '.json', 'w') as f:
            jletters = json.dumps(letters, indent=4)
            f.write(jletters)
    else:
        with open(letters_path + '.txt', 'w') as f:
            f.write(str(letters))

    return None


def main():
    gen = TextGen(font_path, 64, ['لا', 'لله', 'ریال'])
    Path(image_path).mkdir(parents=True, exist_ok=True)
    gen.reject_unknown = True
    print("starting...")
    with open(json_path, 'w') as file:
        print(f"generating in: {image_path}")
        if is_meaningful:
            words = get_mean_words(gen)
            print(len(words))
            for i in range(batch):
                generate_word(gen, file, words[i])
        else:
            gen.reject_unknown = not ugly_mode
            for i in range(int(batch / 10)):
                words = get_words(gen)
                for word in words:
                    generate_word(gen, file, word)
    write_letters(json_form=False)
    return None


if __name__ == '__main__':
    assert not (is_meaningful and ugly_mode), "You can't have ugly and meaningful at the same time retard."
    assert not (using_mask and loosebox), "You can't have masks and boxes at the same time retard."
    main()
