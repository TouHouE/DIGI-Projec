from license_plate import PlatePredicter as pp
from plate_locator import PlateLocator as pl
from zoo import Vehicle
import json
import cv2
import datetime as dt
import numpy as np
from typing import List, Union
from utils import global_const as C
from utils import SheetsController
from utils import MessageProducer as MP
from line import LineNotifyPoster


USER2PLATE = None
USER2TOKEN = None

LOCATOR = None
PREDICTOR = None
TEST_MODE = None
WEBCAM = None
SHEET_CONTROLLER = None
WEBSITE_UPDATER = None

# C.PARKING_PAY_RATE = 5  # the parking pay rate is 5 NTD per minute
# C.FACTORY_TIME = 10
# C.BLOCK_TIME = 1
# C.BBX_THICKNESS = 3
# C.MAX_OF_VEHICLE_SEATS = 3
# C.COLOR = [255, 128, 50]

global_vehicle_record = []
global_current_space = 0


def update_website(alert: bool = False):
    try:
        import websocket
        ws = websocket.create_connection(f'ws://{C.CURRENT_IP}:9001')
        # print('already create connection')
        ws.send(json.dumps({
            'data': global_current_space,
            'color': 'red' if global_current_space == 3 else 'lime',
            'is_alert': alert
        }))
    except Exception as e:
        pass


def put_text_on_img(img, word, xyxy):
    # draw vertical line
    img[xyxy[1]: xyxy[1] + C.BBX_THICKNESS, xyxy[0]:xyxy[2]] = C.COLOR
    img[xyxy[3]: xyxy[3] + C.BBX_THICKNESS, xyxy[0]:xyxy[2]] = C.COLOR

    # draw horizontal line
    img[xyxy[1]: xyxy[3], xyxy[0]: xyxy[0] + C.BBX_THICKNESS] = C.COLOR
    img[xyxy[1]: xyxy[3], xyxy[2]: xyxy[2] + C.BBX_THICKNESS] = C.COLOR

    # put plate serial on
    img = cv2.putText(img, word, (xyxy[0], xyxy[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, C.COLOR, C.BBX_THICKNESS, cv2.LINE_AA)
    return img


# TODO add more action when vehicle into park
def into_park_action(vehicle: Vehicle.Vehicle, method: str = 'append'):
    # update data to Google sheets
    if method == 'append':
        SHEET_CONTROLLER.add_vehicle_record(vehicle)
    elif method == 'update':
        SHEET_CONTROLLER.update_vehicle(vehicle)

    update_website()


# TODO add more action when vehicle leave park
def leave_park_action(vehicle: Vehicle.Vehicle):
    """
        This method is used to implement all the actions of the system when the vehicle leaves the parking lot
    :param vehicle:
    :return: None
    """
    SHEET_CONTROLLER.update_vehicle(vehicle)    # update new info on Google sheets
    parking_time = (vehicle.leave_time - vehicle.in_park_time)
    total_cost = C.get_parking_cost(parking_time.total_seconds())

    if vehicle.owner != '':
        # If we know the vehicle's owner into this statement.
        # calculate parking fee
        try:
            message = MP.line_leave_park_message(vehicle.owner, vehicle.in_park_time, vehicle.leave_time, total_cost)
            LineNotifyPoster.post_message(
                line_token=USER2TOKEN[vehicle.owner],
                message=message
            )
            print(f'Message:{message}')
        except KeyError as ke:
            print(f'Oops your line token has\'t been recorded!')
    else:
        print(MP.line_leave_park_message('Stranger', vehicle.in_park_time, vehicle.leave_time, total_cost, isStranger=True))
    update_website()


def no_more_space_action(vehicle: Vehicle.Vehicle):
    """
        This method is used to implement all the actions of the system when there are no more seats in the parking lot
    :param vehicle:
    :return:
    """
    update_website(True)
    # pass


def check_parking(vehicle_to_be_confirmed: Vehicle.Vehicle):
    """This method is used to check if the vehicle is left or in park.
    :param vehicle_to_be_confirmed:
    :return:
    """
    global global_current_space
    is_leave = False
    is_update = False

    # if `make_vehicle fails`, this statement will escape this method
    if vehicle_to_be_confirmed is None:
        return None

    # this statement for check current vehicle is leave or into parking lot.
    for index, car in enumerate(global_vehicle_record):
        is_leave = vehicle_to_be_confirmed == car and global_vehicle_record[index].parking
        is_update = vehicle_to_be_confirmed == car and not global_vehicle_record[index].parking

        if is_leave:
            # Adding `leave_time` and change `parking`
            # Updating locally data
            global_vehicle_record[index].parking = False
            global_vehicle_record[index].leave_time = vehicle_to_be_confirmed.in_park_time

            # show info
            print(f'car: {global_vehicle_record[index]}\n was leaved')
            update_number_of_space()

            # into method of leave parking lot
            leave_park_action(global_vehicle_record[index])
            return None

    # check the parking lot is full or not
    if global_current_space < C.MAX_OF_VEHICLE_SPACE:

        # check is first time into parking lot or not
        if is_update:
            global_vehicle_record[index].parking = True
            global_vehicle_record[index].leave_time = None
            update_number_of_space()
            print(f'wellcome: \n{vehicle_to_be_confirmed}')
            into_park_action(vehicle_to_be_confirmed, method='update')
        else:
            print(f'First time: \n{vehicle_to_be_confirmed}')
            global_vehicle_record.append(vehicle_to_be_confirmed)
            update_number_of_space()
            into_park_action(vehicle_to_be_confirmed)
    else:
        print(f'There are no more space in the parking lot')
        no_more_space_action(vehicle_to_be_confirmed)

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
            xyxy = [int(coor.item()) if coor >= 0 else 0 for coor in xyxy]
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
    check_parking(Vehicle.make_vehicle(all_prob, start_time, new_img, owner_map=USER2PLATE))


def main_loop():
    just_record = False
    block_from = None

    while True:
        ret, image = WEBCAM.read()
        all_bbx = LOCATOR.predict(image)
        results, new_img = predict_plate_word(image, all_bbx)
        # print(results)
        has_results = results is not None and len(results) > 0

        # Because of the accuracy, we need more sample to do statistics.
        # We also need to separate the detection times for each vehicle to avoid confusing which plate belongs
        # to which vehicle.
        if has_results and not just_record:
            found_plate(dt.datetime.now(), results, new_img)
            just_record = True  # setting detection was stopped
            block_from = dt.datetime.now()

        if just_record and (dt.datetime.now() - block_from).seconds > C.BLOCK_TIME:
            just_record = False
            # print(f'Current car: {[str(car) for car in ALL_CAR]}')
            in_park = list(filter(lambda x: x.parking, global_vehicle_record))
            was_leaved = list(filter(lambda x: not x.parking, global_vehicle_record))

            #
            # print(f'Vehicles in park: ')
            # for v in in_park:
            #     print(v)
            #
            # print(f'Vehicles was leaved: ')
            # for v in was_leaved:
            #     print(v)

        if TEST_MODE:
            cv2.imshow('Webcam 0', new_img)
            keyboard_input = cv2.waitKey(1)

            if keyboard_input & 0xff == ord('q'):
                break


def update_number_of_space():
    global global_current_space
    global_current_space = 0

    for v in global_vehicle_record:
        global_current_space += v.parking  # int + bool


def init():
    """
        Initial all global variable in this method.
    :return: None
    """
    global PREDICTOR, LOCATOR, TEST_MODE, WEBCAM, SHEET_CONTROLLER, USER2PLATE, USER2TOKEN, WEBSITE_UPDATER
    print(f'Start Initial\n{"=" * 15}')
    USER2PLATE = C.init_user2plate()
    USER2TOKEN = C.init_user2token()
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
    show_parkinglot_record()
    activate_test_mode = input('Test Mode?(y/N)')
    TEST_MODE = (activate_test_mode == 'y') or (activate_test_mode == 'Y')
    WEBCAM = cv2.VideoCapture(0)
    print(f'All init are done\n{"=" * 15}\n')


def reload_ALL_CAR():
    """
        loading all vehicle record from Google sheets
    :return:
    """
    global global_vehicle_record
    global_vehicle_record = SHEET_CONTROLLER.get_whole_sheet()
    print(f'All number of vehicle in record is {len(global_vehicle_record)}')
    update_number_of_space()
    print(f'Number of vehicle in parking right now is: {global_current_space}')
    update_website()


def show_parkinglot_record():
    in_park = list(filter(lambda x: x.parking, global_vehicle_record))
    leave_part = list(filter(lambda x: not x.parking, global_vehicle_record))

    print(f'{"=" * 20}In the parking lot{"=" * 20}')
    for vehicle_in_park in in_park:
        print(vehicle_in_park)
    print(f'{"=" * 20}Has left the parking lot{"=" * 20}')
    for v in leave_part:
        print(v)



if __name__ == '__main__':
    init()
    main_loop()