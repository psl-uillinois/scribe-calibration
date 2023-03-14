import os
import sys
import inspect
import pickle
from os.path import isfile, join, exists

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import calibration_settings as cs
from device_data import Device


def make_device(device, filename):
    f = open(filename, "wb")
    pickle.dump(device, f)
    f.close()


if __name__ == "__main__":
    #for (intensity, thickness) in [(15, 13.4), (20, 13.4), (50, 13.4), (90, 13.4), (90, 8.8), (120, 8.8), (150, 8.8), (180, 8.8), (210, 8.8), (230, 8.8)]:
    #for (intensity, thickness) in [(90, 13.4), (90, 8.8)]:
    #for (intensity, thickness) in [(180, 4.4), (210, 4.4), (230, 4.4)]:
    for (intensity, thickness) in [(30, 4.8), (70, 4.8)]:
        #if intensity == 15:
        rectangle = Device(custom_name="", custom_text="", custom_text_inner="", custom_file=False,
                       single_target_intensity=intensity, target_intensity=None, prism=False, enable_calibration=True,
                       enable_piezo_correction=True, enable_time_correction=True, thickness=thickness,
                       xsize=300, ysize=300, xarray=1, yarray=1)
        make_device(rectangle, join("..", cs.device_input_dir, f"rectangle_{intensity}_{str(thickness).replace('.','p')}.{cs.device_input_filetype}"))
        rectangle = Device(custom_name="", custom_text="_PIEZO_CONSTTIME", custom_text_inner=", PIEZO, CONSTTIME", custom_file=False,
                       single_target_intensity=intensity, target_intensity=None, prism=False, enable_calibration=False,
                       enable_piezo_correction=True, enable_time_correction=True, thickness=thickness,
                       xsize=300, ysize=300, xarray=1, yarray=1)
        make_device(rectangle, join("..", cs.device_input_dir, f"rectangle_{intensity}_{str(thickness).replace('.','p')}_PIEZO_CT.{cs.device_input_filetype}"))
        rectangle = Device(custom_name="", custom_text="_CALIBRATED_CONSTTIME", custom_text_inner=", CALIBRATED, CONSTTIME", custom_file=False,
                       single_target_intensity=intensity, target_intensity=None, prism=False, enable_calibration=True,
                       enable_piezo_correction=False, enable_time_correction=True, thickness=thickness,
                       xsize=300, ysize=300, xarray=1, yarray=1)
        make_device(rectangle, join("..", cs.device_input_dir, f"rectangle_{intensity}_{str(thickness).replace('.','p')}_CAL_CT.{cs.device_input_filetype}"))
        rectangle = Device(custom_name="", custom_text="_CONSTTIME", custom_text_inner=", CONSTTIME", custom_file=False,
                       single_target_intensity=intensity, target_intensity=None, prism=False, enable_calibration=False,
                       enable_piezo_correction=False, enable_time_correction=True, thickness=thickness,
                       xsize=300, ysize=300, xarray=1, yarray=1)
        make_device(rectangle, join("..", cs.device_input_dir, f"rectangle_{intensity}_{str(thickness).replace('.','p')}_CO.{cs.device_input_filetype}"))