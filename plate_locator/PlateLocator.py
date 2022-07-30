import numpy as np
import torch

from models.experimental import attempt_load
from utils.general import non_max_suppression, \
    scale_coords
from utils.augmentations import letterbox


def preprocess(image, stride) -> torch.Tensor:
    img = letterbox(image, 640, stride=stride)[0]

    # Convert
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).float() / 255.0
    if len(img.shape) == 3:
        img = img[None]
    return img



class PlateLocator:
    def __init__(self, weights_path, device='cuda:0', iou_thres=0.25, conf_thres=0.25, max_det=1000):
        self.models = attempt_load(weights_path, device)
        self.stride = int(self.models.stride.max())
        print(self.stride)
        self.device = device
        self.iou_thres = iou_thres
        self.conf_thres = conf_thres
        self.max_det = max_det

    def predict(self, image):
        img_for_input = preprocess(image, self.stride).to(self.device)
        pred = self.models(img_for_input, augment=False, visualize=False)[0]
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, None, False, max_det=self.max_det)
        return self._pred_fix(pred, img_for_input.size(), image.shape)

    def _pred_fix(self, predictions, resize_img, org_shape):
        for index in range(len(predictions)):
            det = predictions[index]
            det[:, :4] = scale_coords(resize_img[2:], det[:, :4], org_shape).round()
            predictions[index] = det
        return predictions