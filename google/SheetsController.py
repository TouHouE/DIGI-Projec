import oauth2client.service_account as sa
import gspread
import datetime as dt

from zoo import Vehicle

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class SheetsController:
    def __init__(self, credit_path, sheet_key='1FiIP9hLHhvFYydsj4w645dMgTkzwgHL_zmOpxO5SFhk'):
        self.credit_account = None
        self.update_credit(credit_path)
        self.root_sheet = self.get_root_sheet(sheet_key)

    def update_credit(self, credit_path):
        sac = sa.ServiceAccountCredentials.from_json_keyfile_name(credit_path)
        self.credit_account = gspread.authorize(sac)

    def get_root_sheet(self, root_sheet_key) -> gspread.spreadsheet.Spreadsheet:
        return self.credit_account.open_by_key(root_sheet_key)

    def add_vehicle_record(self, vehicle: Vehicle.Vehicle):
        info_list = vehicle.to_list()
        print(f'append info: {info_list}')
        self.root_sheet.sheet1.append_row(info_list)

    def update_vehicle(self, vehicle: Vehicle.Vehicle):
        info_list = vehicle.to_list()
        plate_record = self.root_sheet.sheet1.col_values(1)
        plate_record = [set(record.split(',')) for record in plate_record]

        for row_minus_1, plate_set in enumerate(plate_record):
            if vehicle == plate_set:
                break

        for col_minus_1, data in enumerate(info_list):
            print(f'R{row_minus_1 + 1}C{col_minus_1 + 1} -> {data}')
            self.root_sheet.sheet1.update_cell(row_minus_1 + 1, col_minus_1 + 1, data)

    def get_whole_sheet(self):
        def str2datetime(str_dt):
            cut = str_dt.split('.')
            return dt.datetime.strptime(cut[0], TIME_FORMAT)

        raw_data = self.root_sheet.sheet1.get_all_values()
        data = raw_data[1:]
        vehicle_list = []

        for vehicle_info in data:
            plate_serials = vehicle_info[0].split(',')
            park_in_time = str2datetime(vehicle_info[1])
            leave_park_time = None if vehicle_info[2] == 'None' else str2datetime(vehicle_info[2])
            base64_image = vehicle_info[3]
            owner = vehicle_info[4]
            tmp = Vehicle.Vehicle(plate_serials, park_in_time, base64_image, leave_park_time is None, leave_park_time, owner)
            vehicle_list.append(tmp)
        return vehicle_list






