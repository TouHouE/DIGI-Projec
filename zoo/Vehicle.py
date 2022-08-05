import base64


class Vehicle:
    def __init__(self, plate_serial, parking_time, plate_image, parking=True, leave_time=None, owner=''):
        self.plate_serial = plate_serial
        self.in_park_time = parking_time
        self.plate_image = plate_image
        self.parking = parking
        self.leave_time = leave_time
        self.owner = owner

    def to_list(self):
        #   TODO: find a method that convert np.ndarray to string
        return [
            ','.join(self.plate_serial),
            str(self.in_park_time),
            str(self.leave_time),
            #self.plate_image.tostring()
        ]

    def __str__(self):
        if self.parking:
            return f'{"=" * 15}\nOwner: {self.owner}\nAll Plate Serials: {self.plate_serial}\nParking from: {self.in_park_time}, Parking: {self.parking}'
        else:
            return f'{"=" * 15}\nOwner: {self.owner}\nAll Plate Serials: {self.plate_serial}\nDuration: {self.leave_time - self.in_park_time}, Parking: {self.parking}'


    def __eq__(self, other):
        if isinstance(other, set):
            intersection_set = set(self.plate_serial) & other
        else:
            intersection_set = set(self.plate_serial) & set(other.plate_serial)
        return len(intersection_set) > 0


def make_vehicle(plate_serials: dict, parking_time, plate_image, owner_map, top_n_accuracy=3, create_threshold=100) -> Vehicle:
    """
    This method is used to create a Vehicle object and do some preprocessing.
    :param plate_serials:
    :param parking_time:
    :param plate_image:
    :param top_n_accuracy:
    :param create_threshold:
    :return:
    """
    if sum(plate_serials.values()) < create_threshold:
        return None
    sorted_plate = [plate for _, plate in sorted(zip(plate_serials.values(), plate_serials.keys()))]
    top_n_plate = sorted_plate[-1 * top_n_accuracy:]
    # set = set(top_n_plate)
    for user_name, plate_serial in owner_map.items():
        if plate_serial in top_n_plate:
            return Vehicle(top_n_plate, parking_time, plate_image, owner=user_name)

    return None