from pathlib import Path

batch = 10
length = (3, 6)
is_meaningful = True   # Buggy
ugly_mode = False
using_mask = False
loosebox = False
save_with_detectron_format = False

im_sadiqu = 1
if im_sadiqu:
    image_path = Path.home() / "percat_images"
    json_path = str((image_path.parent / "train_ocr.json").absolute())
    letters_path = str((image_path.parent / "used_letters").absolute())
    image_path = str(image_path.absolute())
    ocr_path = Path.home() / 'PycharmProjects/PerCato/'
    font_path = str((ocr_path / "b_nazanin.ttf").absolute())
else:
    image_path = "images/"
    json_path = "final.json"
    font_path = "b_nazanin.ttf"