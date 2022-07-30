import oauth2client.service_account as sa
import gspread

from zoo import Vehicle

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





