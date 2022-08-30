import json

TIME_UNIT = 1
PARKING_PAY_RATE = 10  # the parking pay rate is 5 NTD per minute
FACTORY_TIME = 10
BLOCK_TIME = 1
BBX_THICKNESS = 3
MAX_OF_VEHICLE_SPACE = 3
COLOR = [255, 128, 50]

# CURRENT_IP = '192.168.0.10'
CURRENT_IP = '10.100.101.12'


def init_user2plate() -> dict:
    with open('./static/user.json', 'r') as fin:
        json_obj = json.load(fin)
    return json_obj


def init_user2token() -> dict:
    with open('./static/credit/token.json', 'r') as fin:
        json_obj = json.load(fin)
    return json_obj


def get_parking_cost(duration) -> int:
    return int((duration / TIME_UNIT) * PARKING_PAY_RATE)




