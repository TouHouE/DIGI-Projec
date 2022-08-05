import json


def init_user2plate() -> dict:
    with open('./static/user.json', 'r') as fin:
        json_obj = json.load(fin)
    return json_obj


def init_user2token() -> dict:
    with open('./static/credit/token.json', 'r') as fin:
        json_obj = json.load(fin)
    return json_obj