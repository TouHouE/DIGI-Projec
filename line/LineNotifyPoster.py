import requests
import numpy as np


def post_message(line_token: str, message: str) -> int:

    headers = {
        'Authorization': f'Bearer {line_token}',
        # 'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'message': message,
    }

    rep = requests.post('https://notify-api.line.me/api/notify', headers=headers, params=payload)
    return rep.status_code
