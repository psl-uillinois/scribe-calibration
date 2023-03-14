from os.path import isfile, join, exists
from os import listdir
import numpy as np
from hashlib import sha1

import calibration_settings as cs

class HashWrapper(object):
    def __init__(self, val):
        self.__val = val

    def __eq__(self, other):
        if not isinstance(other, HashWrapper):
            return False
        return np.array_equal(self.__val, other.__val)

    def __hash__(self):
        return int.from_bytes(sha1(self.__val).digest(), byteorder='big')

    def unwrap(self):
        return self.__val

def get_calibration_data_preaverage(data_dir):
    calibration_filenames = [f for f in listdir(data_dir) if isfile(join(data_dir, f))]

    lp_sums = []

    for filename in calibration_filenames:
        file_type = filename.split(".")[-1]
        if file_type != "npy":
            continue

        # Extract metadata in filename as integers
        metadata = [int(x) for x in
                    ''.join(filter(lambda x: x.isdigit() or x == '_', filename.split(".")[0])).split("_")]
        if metadata[1] != cs.measured_power:
            continue
        if not metadata[0] in lp_sums:
            lp_sums.append(metadata[0])

    lp_sums.sort()
    num_lp = len(lp_sums)
    sums_list = [[] for i in range(0, num_lp)]

    for filename in calibration_filenames:
        file_type = filename.split(".")[-1]
        if file_type != cs.calibration_data_filetype:
            continue

        # Extract metadata in filename as integers
        metadata = [int(x) for x in
                    ''.join(filter(lambda x: x.isdigit() or x == '_', filename.split(".")[0])).split("_")]

        if metadata[1] != cs.measured_power:
            continue

        img = np.load(join(data_dir, filename), allow_pickle=False)
        sums_list[lp_sums.index(metadata[0])].append(img)

    return [lp_sums, sums_list]


def get_calibration_data(data_dir=cs.data_dir):
    [lp_sums, sums_list] = get_calibration_data_preaverage(data_dir)
    num_lp = len(lp_sums)
    sums = np.zeros((num_lp, cs.array_size, cs.array_size))

    for i in range(0, num_lp):
        sums[i] = np.mean(np.stack(sums_list[i], axis=2), axis=2)

    return [lp_sums, sums]
