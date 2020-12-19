import json

LABEL_MAP = {'ﺎ': 0, 'ﺐ': 1, 'ﺑ': 2, 'ﺖ': 3, 'ﺗ': 4, 'ﺚ': 5,
             'ﺛ': 6, 'ﺞ': 7, 'ﺟ': 8, 'ﺢ': 9, 'ﺣ': 10, 'ﺦ': 11,
             'ﺧ': 12, 'ﺪ': 13, 'ﺬ': 14, 'ﺮ': 15, 'ﺰ': 16, 'ﺲ': 17,
             'ﺳ': 18, 'ﺶ': 19, 'ﺷ': 20, 'ﺺ': 21, 'ﺻ': 22, 'ﺾ': 23,
             'ﺿ': 24, 'ﻂ': 25, 'ﻆ': 26, 'ﻉ': 27, 'ﻊ': 28, 'ﻋ': 29,
             'ﻌ': 30, 'ﻍ': 31, 'ﻎ': 32, 'ﻏ': 33, 'ﻐ': 34, 'ﻒ': 35,
             'ﻓ': 36, 'ﻖ': 37, 'ﻗ': 38, 'ﻘ': 39, 'ﻚ': 40, 'ﻛ': 41,
             'ﻞ': 42, 'ﻟ': 43, 'ﻠ': 44, 'ﻢ': 45, 'ﻣ': 46, 'ﻦ': 47,
             'ﻧ': 48, 'ﻩ': 49, 'ﻪ': 50, 'ﻫ': 51, 'ﻬ': 52, 'ﻮ': 53,
             'ﯼ': 54, 'ﯾ': 55, 'ﭗ': 56, 'ﭘ': 57, 'ﭻ': 58, 'ﭼ': 59,
             'ﮋ': 60, 'ﮓ': 61, 'ﮔ': 62, 'ﺋ': 63, 'ﺁ': 64, 'لا': 65}


def sort_word(word: json):
    """Use Bubble sort to sort characters based on their bbox position"""
    for i in range(len(word)):
        already_sorted = True
        for j in range(len(word) - i - 1):
            x = word[j]['bbox'][0]
            x_next = word[j + 1]['bbox'][0]
            if x > x_next:
                word[j], word[j + 1] = word[j + 1], word[j]
                already_sorted = False
        if already_sorted:
            break
    return word[::-1]


def show_word(word: json) -> list:
    """Get characters of the word from label map"""
    def search_keys_by_val(dict, byVal):
        """LABEL_MAP is reversed, so we need to search by value"""
        items_list = dict.items()
        for item in items_list:
            if item[1] == byVal:
                key = item[0]
        return key
    sensitivity = 0.7   # Show characters you're at least 70% sure about
    print_string = []
    for char in word:
        if char['score'] > sensitivity:
            cat_id = char['category_id']
            harf = search_keys_by_val(LABEL_MAP, cat_id)
            print_string.append(harf)
    return print_string


def read_output(jfile):
    """Read the output.json file"""
    with open(jfile, 'r') as f:
        file = f.read()
        jdump = json.loads(file)
    return jdump


def get_words(dump: json, n_words: int) -> list:
    """Gets output.json and returns a clean list of words."""
    words = [[]]
    for n in range(n_words):
        for char in dump:
            if char['image_id'] == n:
                words[n].append(char)
    return words


def predict(file_path, n_words: int):
    output = read_output(file_path)
    words = get_words(output, n_words)
    for word in words:
        word = sort_word(word)
        print(show_word(word))


if __name__ == "__main__":
    output_path = '/home/sadegh/Downloads/coco_instances_results.json'
    predict(output_path, 1)

