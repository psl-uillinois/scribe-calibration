import os
from os import listdir
from os.path import isfile, join, exists
from multiprocessing import Pool, freeze_support, cpu_count

from calibrate_device import calibrate_from_file
import calibration_settings as cs

if os.name == "nt":
    freeze_support()

if __name__ == '__main__':
    device_input_filenames = [join(cs.device_input_dir, f) for f in listdir(cs.device_input_dir)
                              if isfile(join(cs.device_input_dir, f))]

    if cs.multithread:
        pool = Pool(cpu_count())
        pool.map(calibrate_from_file, device_input_filenames)
    else:
        list(map(calibrate_from_file, device_input_filenames))
    exit(0)
