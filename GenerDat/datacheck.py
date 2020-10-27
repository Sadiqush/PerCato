import json
import pprint
import textutil
import sys
sys.path.insert(0, '/home/sadegh/PycharmProjects/ocrdg/CleanDat')
import conv2dete
import re


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
    res = (re.sub('.', lambda x: r'\u % 04X' % ord(x.group()), checkstr))
    print(res)


def map_check(alph, checkdic):
    """See all the chars in a dictionary as unicode."""
    for c in alph:
        mainc = (re.sub('.', lambda x: r'\u % 04X' % ord(x.group()), c))
        ans = checkdic[c]
        res = (re.sub('.', lambda x: r'\u % 04X' % ord(x.group()), ans))
        print(c, ' --> ', mainc, " --> ", res)
    return None


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    json_file = '/home/sadegh/Projects/OCR/datasets/data8.1/final.json'
    new_alph = textutil.TextGen.get_join_alphabet(view=True)
    org_alph = textutil.ALPHABET
    map_dic = conv2dete.map_unis()
    # sum_class(json_file)
    # sum_list(json_file)
    # compat_check(new_alph)
    # fe_check(str(new_alph))
    map_check(org_alph, map_dic)
