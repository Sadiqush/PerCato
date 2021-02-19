import numpy as np
from PIL import ImageColor, Image

from params import using_mask


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

    def __init__(self, text, image: np.array, parts, boxes, masks=[], id=-1):
        self.text = text
        self.image = image
        self.parts = parts
        self.boxes = boxes
        self.masks = masks
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
        for x0, y0, x1, y1 in self.masks:
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
        self.parts.reverse()
        if using_mask:
            json_dic = {"id": self.id, "text": self.text, "image_name": path, "parts": self.parts,
                        "width": w, "height": h, "boxes": self.boxes, "masks": self.masks, "n": self.length}
        else:
            json_dic = {"id": self.id, "text": self.text, "image_name": path, "parts": self.parts,
                        "width": w, "height": h, "boxes": self.boxes, "n": self.length}
        return json_dic


class DetectronMeta(ImageMeta):

    def __init__(self, text, image: np.array, parts, boxes, image_dir, save_image=True, save_labeled_image=True, id=-1):
        super().__init__(text, image, parts, boxes, id)
        if save_image:
            self.file_name = f"{image_dir}/image{self.id}.png"
            self.save_image(self.file_name)
        if save_labeled_image:
            self.labeled_file_name = f"{image_dir}/image{self.id}_labeled.tif"
            self.save_image_with_boxes(self.labeled_file_name)

    @staticmethod
    def from_imagemeta(meta: ImageMeta, image_dir, save_image=True, save_labeled_image=True):
        return DetectronMeta(
            meta.text, meta.image, meta.parts, meta.boxes, image_dir, save_image, save_labeled_image, meta.id)

    _letters = []

    def to_dict(self, letter_id_map=None):
        if letter_id_map is None:
            import warnings
            warnings.warn("Consider not using auto ID.")
            DetectronMeta._letters.extend(p for p in self.parts if p not in DetectronMeta._letters)
            letter_id_map = {item: i for i, item in enumerate(DetectronMeta._letters)}
        h, w = self.image.shape
        annotations = [
            {'bbox': box, 'bbox_mode': 0, 'category_id': letter_id_map[part]} for box, part in
            zip(self.boxes, self.parts)
        ]
        json_dict = {'file_name': self.file_name, 'height': h, 'width': w, 'image_id': self.id,
                     'annotations': annotations}
        return json_dict
