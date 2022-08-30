from flask import Flask, json
from utils import SheetsController
from utils import global_const as initializer

GOOGLE_SHEET_MANAGER = SheetsController.SheetsController(credit_path='./static/credit/sheet_keys.json')
server = Flask(__name__, static_folder='./static/web')
server.config['DEBUG'] = True
# CURRENT_IP = '192.168.0.10'


@server.route('/')
def index():
    with open('./static/web/index.html', 'r') as fin:
        html_text = ''.join(fin.readlines())
    return html_text


@server.route('/static/web/js/<string:js_name>', methods=["GET"])
def take_js_file(js_name):
    with open(f'./static/web/js/{js_name}', 'r') as fin:
        js_text = ''.join(fin.readlines())


    js_text = js_text.replace('?IP', f'\"{initializer.CURRENT_IP}\"')
    return js_text


@server.route('/init', methods=["GET"])
def init_viewer():
    num_vehicle = GOOGLE_SHEET_MANAGER.get_still_in_park()
    response = server.response_class(
        response=json.dumps({
            'data': num_vehicle,
            'color': 'red' if num_vehicle == 3 else 'lime',
            'is_aleart': False
        }),
        status=200,
        mimetype='application/json'
    )
    return response

# According to lecturer's request, this humble server be made
if __name__ == '__main__':
    server.run(host=initializer.CURRENT_IP, port=8001, debug=True)