from PIL import ImageColor, Image
import numpy as np


class ImageMeta:
    """
    This class is used to export images along with generated metadata, aka making the json file.

    Args:
        text (str): input text for json.
        image (np.array): the output image.
        parts (list): text chars for json.
        boxes (): my anus hungers.
        id (int): wtf
    """
    id = 0

    def __init__(self, text, image: np.array, parts, boxes, id=-1):
        self.text = text
        self.image = image
        self.parts = parts
        # self.visible_parts = visible_parts
        self.boxes = boxes
        self.length = len(parts)
        if id > 0:
            self.id = id
        else:
            self.id = ImageMeta.id
            ImageMeta.id += 1

    def save_image(self, path, transpose=False):
        """
        Save image to the path.

        Args:
            path (str): absolute path for the image.
            transpose (bool): transpose image array before saving (default: False).
        """
        image = Image.fromarray(self.image.transpose() if transpose else self.image)
        image.save(path)
        return None

    def save_image_with_boxes(self, path, color="yellow", transpose=True):
        """
        Draw bbox on image and save to the path.

        Args:
            path (str): absolute path for the image.
            color (str): the color of bbox.
            transpose (bool): transpose image array before saving (default: True).
        """
        image = self.image.transpose()
        image = np.concatenate([image[..., np.newaxis]] * 3, axis=2)
        value = list(ImageColor.getrgb(color))
        for x0, y0, x1, y1 in self.boxes:
            image[x0:x1 + 1, y0] = value
            image[x0:x1 + 1, y1] = value
            image[x0, y0:y1 + 1] = value
            image[x1, y0:y1 + 1] = value
        Image.fromarray(image.transpose((1, 0, 2))).save(path)
        return None

    def to_dict(self, path):
        """
        Generate a json block for the image. It's not in COCO format.

        Args:
            path (str): non-absolute path (name) of the image.

        Returns:
            json_dic (dic): json block of the image.
        """
        h, w = self.image.shape
        # TODO: Use COCO standard format
        json_dic = {"id": self.id, "text": self.text, "image_name": path, "parts": self.parts,
                    "width": w, "height": h, "boxes": self.boxes, "n": self.length}
        return json_dic
