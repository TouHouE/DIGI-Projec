import base64

class Vehicle:
    def __init__(self, plate_serial, parking_time, plate_image):
        self.plate_serial = plate_serial
        self.in_park_time = parking_time
        self.plate_image = plate_image
        self.parking = True
        self.leave_time = None

    def to_list(self):
        return [
            ','.join(self.plate_serial),
            str(self.in_park_time),
            str(self.leave_time),
            #self.plate_image.tostring()
        ]

    def __str__(self):
        if self.parking:
            return f'{"=" * 15}All Plate Serials: {self.plate_serial}\nParking from: {self.in_park_time}, Parking: {self.parking}'
        else:
            return f'{"=" * 15}All Plate Serials: {self.plate_serial}\nDuration: {self.leave_time - self.in_park_time}, Parking: {self.parking}'


    def __eq__(self, other):
        if isinstance(other, set):
            intersection_set = set(self.plate_serial) & other
        else:
            intersection_set = set(self.plate_serial) & set(other.plate_serial)
        return len(intersection_set) > 0


def make_vehicle(plate_serials: dict, parking_time, plate_image, top_n_accuracy=3, create_threshold=100) -> Vehicle:
    if sum(plate_serials.values()) < create_threshold:
        return None
    # print(plate_serials)
    sorted_plate = [plate for _, plate in sorted(zip(plate_serials.values(), plate_serials.keys()))]
    # print(sorted_plate)
    return Vehicle(sorted_plate[-1 * top_n_accuracy:], parking_time, plate_image)
