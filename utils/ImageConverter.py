import base64
import numpy as np
import cv2


def img2base64(image: np.ndarray):
    image = np.ascontiguousarray(image[..., ::-1])
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text


def base642img(b64_image):
    jpg_org = base64.b64decode(b64_image)
    jpg_as_np = np.frombuffer(jpg_org, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img