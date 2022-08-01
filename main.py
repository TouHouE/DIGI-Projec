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
NUM_OF_VEHICLE_SEATS = 3
COLOR = [255, 128, 50]
current_seats = 0


def put_text_on_img(img, word, xyxy):
    # draw vertical line
    img[xyxy[1]: xyxy[1] + THINKS, xyxy[0]:xyxy[2]] = COLOR
    img[xyxy[3]: xyxy[3] + THINKS, xyxy[0]:xyxy[2]] = COLOR

    # draw horizontal line
    img[xyxy[1]: xyxy[3], xyxy[0]: xyxy[0] + THINKS] = COLOR
    img[xyxy[1]: xyxy[3], xyxy[2]: xyxy[2] + THINKS] = COLOR

    # put plate serial on
    img = cv2.putText(img, word, (xyxy[0], xyxy[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR, THINKS, cv2.LINE_AA)
    return img


# TODO add more action when vehicle into park
def into_park_action(vehicle: Vehicle.Vehicle):
    SHEET_CONTROLLER.add_vehicle_record(vehicle)


# TODO add more action when vehicle leave park
def leave_park_action(vehicle: Vehicle.Vehicle):
    SHEET_CONTROLLER.update_vehicle(vehicle)


def check_parking(vehicle_to_be_confirmed: Vehicle.Vehicle):
    """This method is used to check if the vehicle is left or in park.
    :param vehicle_to_be_confirmed:
    :return:
    """
    global current_seats

    # if make_vehicle fails, this statement will escape this method
    if vehicle_to_be_confirmed is None:
        return None

    # this part for leave park
    for index, car in enumerate(ALL_CAR):

        if vehicle_to_be_confirmed == car:
            if ALL_CAR[index].parking:
                # Adding `leave_time` and change `parking`
                ALL_CAR[index].parking = False
                ALL_CAR[index].leave_time = vehicle_to_be_confirmed.in_park_time

                # show info
                print(f'car: {ALL_CAR[index]}\n| was leaved')
                update_seats_number()
                # into method of leave park
                leave_park_action(ALL_CAR[index])
                return None
            else:
                ALL_CAR[index].parking = True
                ALL_CAR[index].leave_time = None
                print(f'wellcome: {ALL_CAR[index]}')


    # check the park is full or not
    if current_seats < NUM_OF_VEHICLE_SEATS:
        ALL_CAR.append(vehicle_to_be_confirmed)
        update_seats_number()
        into_park_action(vehicle_to_be_confirmed)
    else:
        print(f'There are no seats in the park')


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

        # To avoid word predictors that are not sufficiently accurate
        for word in results:
            all_prob[word] = all_prob.get(word, 0) + 1

        if TEST_MODE:
            cv2.imshow(f'Webcam 0', new_img)
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

        if just_record and (dt.datetime.now() - block_from).seconds > BLOCK_TIME:
            just_record = False
            print(f'Current car: {[car.__str__() for car in ALL_CAR]}')
            in_park = list(filter(lambda x: x.parking, ALL_CAR))
            was_leaved = list(filter(lambda x: not x.parking, ALL_CAR))

            print(f'Vehicles in park: ')
            for v in in_park:
                print(v)

            print(f'Vehicles was leaved: ')
            for v in was_leaved:
                print(v)

        if TEST_MODE:
        # cv2.imshow('Webcam 0', image)
            cv2.imshow('Webcam 0', new_img)
            keyboard_input = cv2.waitKey(1)

            if keyboard_input & 0xff == ord('q'):
                break


def update_seats_number():
    global current_seats
    current_seats = 0

    for v in ALL_CAR:
        current_seats += v.parking


def init():
    global PREDICTOR, LOCATOR, TEST_MODE, WEBCAM, SHEET_CONTROLLER
    print(f'Start Initial\n{"=" * 15}')
    print('Now initial plate serials predictor...')
    PREDICTOR = pp.PlatePredictor(weights_path='./static/weights/char_predictor/best.pth')
    print(f'plate serials predictor initial done!')
    print('Now initial plate location predictor...')
    LOCATOR = pl.PlateLocator(weights_path='./static/weights/locator/best.pt')
    print('plate location predictor initial done!')
    print('Now connecting google sheets...')
    SHEET_CONTROLLER = SheetsController.SheetsController(credit_path='./static/credit/sheet_keys.json')
    print('Connect done!')
    print(f'Start reloading...')
    reload_ALL_CAR()
    print(f'Reload is done')
    show_all_park()
    activate_test_mode = input('Test Mode?(y/N)')
    TEST_MODE = (activate_test_mode == 'y') or (activate_test_mode == 'Y')
    WEBCAM = cv2.VideoCapture(0)
    print('All init are done')


def reload_ALL_CAR():
    global ALL_CAR
    ALL_CAR = SHEET_CONTROLLER.get_whole_sheet()
    print(len(ALL_CAR))
    update_seats_number()


def show_all_park():
    in_park = list(filter(lambda x: x.parking, ALL_CAR))
    print('=' * 20)
    for vehicle_in_park in in_park:
        print(vehicle_in_park)
    print('=' * 20)


if __name__ == '__main__':
    init()
    main_loop()