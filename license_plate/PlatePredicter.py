from license_plate.models import alpr
import cv2
from PIL import Image
import numpy as np
CTC_DECODER_TYPE = ['bestPath', 'beamSearch']


class PlatePredictor:
    def __init__(self, weights_path: str, ctc_decoder_type: str=CTC_DECODER_TYPE[0]):
        self.lpr = alpr.AutoLPR(decoder=ctc_decoder_type, normalise=False)
        self.lpr.load(crnn_path=weights_path)

    def predict(self, image: np.ndarray) -> str:
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        return self.lpr.predict(image)


if __name__ == '__main__':
    weights_abs_path = r'C:\Users\user\Desktop\Program\Python\DIGIProject\res\crnn-license-plate-OCR\model\weights\best-fyp-improved.pth'
    p = PlatePredictor(weights_abs_path)
    img = cv2.imread(f'./tmp.png')
    img = Image.fromarray(img)
    ans = p.predict(img)

    print(ans)
