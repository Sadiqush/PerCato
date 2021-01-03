import json
import pprint
import re

from main import json_path


def sum_class(json_path):
    """Show how much of each letter we have."""
    char_list = {}
    with open(json_path) as f:
        x = json.load(f)
        for block in x:
            chars = block['parts']
            for i in chars:
                if i in char_list:
                    char_list[i] += 1
                else:
                    char_list[i] = 1
    char_list['sum'] = sum(char_list.values())
    pp.pprint(char_list)
    return None


def sum_list(json_path):
    """Show total number of classes in the data."""
    with open(json_path) as f:
        x = json.load(f)
        chars = []
        for block in x:
            chars.extend(block['parts'])
    # print(set(chars))
    print(len(set(chars)))
    return None


def compat_check(newalph):
    """Check the compatibility of unicodes with the old ALPHABET used."""
    count = 0
    for c in textutil.ALPHABET:
        if c in newalph:
            count += 1
    if count == 33:
        print("It's compatible.")
    else:
        print("Only %d are compatible." % count)


def fe_check(checkstr):
    """See all the chars in a list as unicode."""
    for c in checkstr:
        res = (re.sub('GenerDat', lambda x: r'\u%04X' % ord(x.group()), c))
        print("%s is %s" % (c, res))


def map_check(alph, checkdic):
    """See all the chars in a dictionary as unicode."""
    for c in alph:
        mainc = (re.sub('GenerDat', lambda x: r'\u%04X' % ord(x.group()), c))
        ans = checkdic[c]
        res = (re.sub('GenerDat', lambda x: r'\u%04X' % ord(x.group()), ans))
        print(c, ' --> ', mainc, " --> ", res)
    return None


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    # json_path = '/home/sadegh/Projects/OCR/datasets/data10/final.json'
    # new_alph = textutil.TextGen.get_join_alphabet(view=False)
    # org_alph = textutil.ALPHABET
    # compat_check(new_alph)
    # fe_check(str(new_alph))
    # map_check(org_alph, map_dic)
    # niga = map_unis(["ص", "ا", "د"])
    # print(niga)
    # red = ['ﺽ', 'ﺹ', 'ﺙ', 'ﻕ', 'ﻑ', 'ﻍ', 'ﻉ', 'ﻩ', 'ﺥ', 'ﺡ', 'ﺝ',
    #        'ﭺ', 'ﺵ', 'ﺱ', 'ﯼ', 'ﺏ', 'ﻝ', 'ﺕ', 'ﻥ', 'ﻡ', 'ﮎ', 'ﮒ',
    #        'ﻅ', 'ﻁ', 'ﭖ', 'ﺉ', 'ﺭ', 'ﺯ', 'ﺩ', 'ﺫ', 'ﻭ', 'ﺍ', 'ﺁ',
    #        'ﺃ', 'لا']
    # fe_check(red)

    sum_class(json_path)
    sum_list(json_path)

