from license_plate import PlatePredicter as pp
from plate_locator import PlateLocator as pl
from zoo import Vehicle
from google import SheetsController
import cv2
import datetime as dt
import numpy as np
from typing import List, Union

ALL_CAR = []

LOCATOR = None
PREDICTOR = None
TEST_MODE = None
WEBCAM = None
SHEET_CONTROLLER = None

FACTORY_TIME = 10
BLOCK_TIME = 1
THINKS = 3
COLOR = [255, 128, 50]


def put_text_on_img(img, word, xyxy):
    img[xyxy[1]: xyxy[1] + THINKS, xyxy[0]:xyxy[2]] = COLOR
    img[xyxy[3]: xyxy[3] + THINKS, xyxy[0]:xyxy[2]] = COLOR
    img[xyxy[1]: xyxy[3], xyxy[0]: xyxy[0] + THINKS] = COLOR
    img[xyxy[1]: xyxy[3], xyxy[2]: xyxy[2] + THINKS] = COLOR
    img = cv2.putText(img, word, (xyxy[0], xyxy[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR, THINKS, cv2.LINE_AA)
    return img



def into_park_action(vehicle: Vehicle.Vehicle):
    SHEET_CONTROLLER.add_vehicle_record(vehicle)


def leave_park_action(vehicle: Vehicle.Vehicle):
    SHEET_CONTROLLER.update_vehicle(vehicle)


def check_parking(been_check: Vehicle.Vehicle):
    if been_check is None:
        return None


    if len(ALL_CAR) > 0:
        for index, car in enumerate(ALL_CAR):
            if been_check == car:
                ALL_CAR[index].parking = False
                ALL_CAR[index].leave_time = been_check.in_park_time
                print(f'car: {ALL_CAR[index].__str__()} was leaved')
                leave_park_action(ALL_CAR[index])
                return None
    ALL_CAR.append(been_check)
    into_park_action(been_check)


def predict_plate_word(img: str, bbx) -> Union[List[Union[List[str], np.ndarray]], None]:
    """
        This method predicted plate serial in crops that yolov5 predicted, then return a list of plate serial, as well as
         an image that writes plate serial on when TEST_MODE is turned on.
    :param img: str
    :param bbx: torch.Tensor
    :return:
    """
    if len(bbx):
        # initial some variable
        all_pred_word = []
        max_area = 0
        bbx = bbx[0]
        tmp_img = img.copy() # prepare for TEST_MODE

        for *xyxy, conf, cls in reversed(bbx):
            xyxy = [int(coor.item()) for coor in xyxy]
            crops = img[xyxy[1]:xyxy[3], xyxy[0]:xyxy[2]]

            plate_str = PREDICTOR.predict(crops)

            if TEST_MODE:
                tmp_img = put_text_on_img(tmp_img, plate_str, xyxy)

            all_pred_word.append(plate_str)

        # Whatever TEST_MODE is on or off, return pred_word and tmp_img
        return all_pred_word, tmp_img

    return None


def found_plate(start_time, init_results, init_new_img=None):
    all_prob = {}

    while (dt.datetime.now() - start_time).seconds <= 10:
        ret, image = WEBCAM.read()
        all_bbx = LOCATOR.predict(image)
        results, new_img = predict_plate_word(image, all_bbx)

        # To avoid word predictor not very accuracy enough
        for word in results:
            all_prob[word] = all_prob.get(word, 0) + 1

        if TEST_MODE:
            cv2.imshow('Webcam 0', new_img)
            keyboard_input = cv2.waitKey(1)

            if keyboard_input & 0xff == ord('q'):
                break
    check_parking(Vehicle.make_vehicle(all_prob, start_time, new_img))


def main_loop():
    just_record = False
    block_from = None

    while True:
        ret, image = WEBCAM.read()
        all_bbx = LOCATOR.predict(image)
        results, new_img = predict_plate_word(image, all_bbx)
        # print(results)
        has_results = results is not None and len(results) > 0


        if has_results and not just_record:
            found_plate(dt.datetime.now(), results, new_img)
            just_record = True
            block_from = dt.datetime.now()
        # else:
            # if TEST_MODE:
            #     if not has_results:
            #         print(f'No results', end=' ')
            #     if just_record:
            #         print(f'Still Blocking!', end=' ')
            #     print()

        if just_record and (dt.datetime.now() - block_from).seconds > BLOCK_TIME:
            just_record = False
            print(f'Current car: {[car.__str__() for car in ALL_CAR]}')

        if TEST_MODE:
        # cv2.imshow('Webcam 0', image)
            cv2.imshow('Webcam 0', new_img)
            keyboard_input = cv2.waitKey(1)

            if keyboard_input & 0xff == ord('q'):
                break


def init():
    global PREDICTOR, LOCATOR, TEST_MODE, WEBCAM, SHEET_CONTROLLER
    print(f'Start Initial')
    PREDICTOR = pp.PlatePredictor(weights_path='./static/weights/char_predictor/best.pth')
    LOCATOR = pl.PlateLocator(weights_path='./static/weights/locator/best.pt')
    SHEET_CONTROLLER = SheetsController.SheetsController(credit_path='./static/credit/sheet_keys.json')
    activate_test_mode = input('Test Mode?(y/N)')
    TEST_MODE = (activate_test_mode == 'y') or (activate_test_mode == 'Y')
    WEBCAM = cv2.VideoCapture(0)
    print('init is done')


if __name__ == '__main__':
    init()
    main_loop()