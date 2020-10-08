import json
import pprint


def sum_list(json_path):
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


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    # json_file = '/home/sadegh/Projects/OCR/datasets/medaya/final-pretty.json'
    json_file = '/home/sadegh/Projects/OCR/datasets/dgen2/v40/final-pretty.json'
    sum_list(json_file)