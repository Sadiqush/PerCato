import json
import os
# import GenerDat.textutil


def convert2detectron(img_dir):
    json_file = os.path.join(img_dir, "final-pretty.json")
    img_dir = os.path.join(img_dir, "images")

    with open(json_file) as f:
        imgs_anns = json.load(f)

    dataset_dicts = []
    for idx in range(len(imgs_anns)):
        block = imgs_anns[idx]
        record = {}

        filename = os.path.join(img_dir, block["image_name"])

        record["file_name"] = filename
        record["image_id"] = idx
        record["height"] = block["height"]
        record["width"] = block["width"]

        annos = []
        for id_harf in range(block["n"]):
            harf = block["parts"][id_harf]
            # mask = block["encoded_masks"][id_harf].split()
            bbox = block["box"][id_harf]
            obj = {
                # "bbox": [np.min(px), np.min(py), np.max(px), np.max(py)],
                # "bbox_mode": BoxMode.XYXY_ABS,
                # "segmentation": [list(mask)],
                # "category_id": 0
                "category_id": harf,
                "bbox": bbox,
                "bbox_mode": 0
            }
            annos.append(obj)
        record["annotations"] = annos
        dataset_dicts.append(record)
    return dataset_dicts


def write_json(json_file, json_dir, output_name):
    # Serializing json
    json_obj = json.dumps(json_file, indent=4)

    # Writing to sample.json
    output_path = os.path.join(json_dir, output_name)
    with open(output_path, "w") as outfile:
        outfile.write(json_obj)


def slice_json(json_dir, input_name):
    json_path = os.path.join(json_dir, input_name)
    with open(json_path, 'r+') as file_obj:
        data = json.load(file_obj)
        amount = int(len(data) * 20 / 100)
        json_val = data[0:amount]
        json_train = data[amount:]

    write_json(json_val, json_dir, "val_ocr.json")
    write_json(json_train, json_dir, "train_ocr.json")


def slice_images(img_dir, json_file, output_name):
    json_path = os.path.join(img_dir, "", json_file)
    with open(json_path) as f:
        json_file = json.load(f)

    output_path = os.path.join(img_dir, "", output_name)
    output = open(output_path, "w")
    for block in json_file:
        file_name = os.path.join(img_dir, block["image_name"])
        output.write(str(file_name) + "\n")
    output.close()


def map_unis(parts: list) -> list:
    """
    This is used to change normal letter forms to isolated forms.
    input normal, output isolated (06xx to FExx).
    """
    alph_map = {'ض': 'ﺽ', 'ص': 'ﺹ', 'ث': 'ﺙ', 'ق': 'ﻕ', 'ف': 'ﻑ', 'غ': 'ﻍ', 'ع': 'ﻉ',
              'ه': 'ﻩ', 'خ': 'ﺥ', 'ح': 'ﺡ', 'ج': 'ﺝ', 'چ': 'ﭺ', 'ش': 'ﺵ', 'س': 'ﺱ',
              'ی': 'ﯼ', 'ب': 'ﺏ', 'ل': 'ﻝ', 'ت': 'ﺕ', 'ن': 'ﻥ', 'م': 'ﻡ', 'ک': 'ﮎ',
              'گ': 'ﮒ', 'ظ': 'ﻅ', 'ط': 'ﻁ', 'پ': 'ﭖ', 'ئ': 'ﺉ', 'ر': 'ﺭ', 'ز': 'ﺯ',
              'د': 'ﺩ', 'ذ': 'ﺫ', 'و': 'ﻭ', 'ا': 'ﺍ', 'آ': 'ﺁ', 'أ': 'ﺃ', 'لا': 'لا'}
    outpart = []
    for c in parts:
        outpart.append(alph_map[c])
    return outpart


if __name__ == "__main__":
    project_path = "/home/sadegh/Projects/OCR/datasets/data4"

    # dataset_dicts = convert2detectron(project_path)
    # write_json(dataset_dicts, project_path, "final-formatted.json")
    # slice_json(project_path, "final-pretty.json")
    # slice_images(project_path + "/images", "val_ocr.json", "val_images.txt")
    # slice_images(project_path + "/images", "train_ocr.json", "train_images.txt")
    # map_unis(["ص", "ا", "د"])
