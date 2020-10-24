import json
import pprint


def sum_list(json_path):
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


def num_class(json_path):
    """Show total number of classes in the data."""
    with open(json_path) as f:
        x = json.load(f)
        chars = []
        for block in x:
            chars.extend(block['parts'])
    # print(set(chars))
    return len(set(chars))


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    # json_file = '/home/sadegh/Projects/OCR/datasets/medaya/final-pretty.json'
    json_file = '/home/sadegh/Projects/OCR/datasets/data4/final.json'
    sum_list(json_file)
    print('Total number of classes is:', num_class(json_file))
