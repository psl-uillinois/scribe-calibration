from os import listdir
from os.path import isfile, join, exists
from PIL import Image
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
from scipy.optimize import curve_fit
from scipy.interpolate import pchip
from numpy.polynomial import Polynomial
import math
import sys
from functools import lru_cache
import pickle

from device_data import Device
import calibration_settings as cs
from calibration_utility import get_calibration_data, HashWrapper

from fit_lps import get_lps_cached

def calibrate_from_file(input_filename):
    f = open(input_filename, "rb")
    device = pickle.load(f)
    f.close()
    calibrate(device, input_filename)


def calibrate(device: Device, input_filename=""):
    custom_file = device.custom_file

    custom_text = device.custom_text
    custom_text_inner = device.custom_text_inner

    high_res_y = device.high_res_y

    prism = device.prism

    enable_calibration = device.enable_calibration  # "calibrated" = fluorescence intensity correction
    enable_piezo_correction = device.enable_piezo_correction  # "corrected" = piezo movement correction
    enable_time_correction = device.enable_time_correction  # "consttime" = constant-time between z layers correction

    target_intensity = device.target_intensity
    single_target_intensity = device.single_target_intensity
    if not custom_file:
        target_intensity = np.zeros((cs.correction_size + 1, cs.correction_size + 1))
        for x in range(-cs.writable_offset, cs.writable_offset + 1):
            for y in range(-cs.writable_offset, cs.writable_offset + 1):
                target_intensity[x + cs.correction_offset, y + cs.correction_offset] = single_target_intensity

    # 5 um for box / 12.8 um for 15 deg prism
    # 4.4 um for 5 deg prism
    thickness = device.thickness
    if len(target_intensity.shape) > 2:
        thickness = (target_intensity.shape[2] - 1) / 10

    custom_name = device.custom_name

    if custom_file:
        if custom_text != '':
            custom_name = custom_name + '_'
        output_file = join(cs.device_dir, f"{custom_name}{custom_text}.{cs.device_filetype}")
    elif prism:
        output_file = join(cs.device_dir, f"prism__{single_target_intensity:03d}int_{str(thickness).replace('.', 'p')}thick{custom_text}.{cs.device_filetype}")
    else:
        output_file = join(cs.device_dir, f"block__{single_target_intensity:03d}int_{str(thickness).replace('.', 'p')}thick{custom_text}.{cs.device_filetype}")

    writing_size = int(cs.writable_area / cs.writing_slice) + 1
    writing_correction_size = int(cs.correction_size / cs.writing_slice) + 1
    actual_array_size = int(cs.writable_area / cs.box_size) + 1

    if high_res_y:
        actual_array_size = int(cs.writable_area / cs.writing_slice) + 1

    lps = get_lps_cached(HashWrapper(target_intensity), enable_calibration)
    mean_lp_overall = np.mean(lps[lps>cs.lp_threshold])

    print(input_filename, mean_lp_overall)

    xsize = device.xsize
    ysize = device.ysize
    if not custom_file:
        if prism:
            xsize = 300
            ysize = 300
        else:
            xsize = 130
            ysize = 130

    output = cs.output_class(output_file)

    if not custom_file:
        output.write_metadata(xsize, ysize, device.xarray, device.yarray,
                              f"INT={single_target_intensity}, MIC_POW={cs.measured_power}, \
SLICE=1um, THICK={thickness}um, AVG_LP={round(mean_lp_overall, 2)}, \
STEP={round(cs.piezo_step, 2)}{custom_text_inner}\n\n", high_res_y)
    else:
        output.write_metadata(xsize, ysize, device.xarray, device.yarray,
                              f"MIC_POW={cs.measured_power}, \
SLICE=1um, THICK={thickness}um, AVG_LP={round(mean_lp_overall, 2)}, \
STEP={round(cs.piezo_step, 2)}{custom_text_inner}\n\n", high_res_y)

    output.write_beginning()

    piezo_step = cs.piezo_step
    piezo_offset_x = -(cs.piezo_max + piezo_step)
    piezo_offset_y = -(cs.piezo_max + piezo_step)
    if not enable_piezo_correction:
        piezo_offset_x = 0
        piezo_offset_y = 0
        piezo_step = 0

    for z in range(int(thickness / cs.writing_slice), -1, -1):
        x_size = target_intensity.shape[0]
        y_size = target_intensity.shape[1]

        z_out = -z * 0.1
        if z_out == int(z_out):
            z_out = int(z_out)
        else:
            z_out = round(z_out, 1)
        print(z_out)
        z_index = int(thickness / cs.writing_slice) - z

        piezo_offset_x += piezo_step
        if piezo_offset_x > cs.piezo_max:
            piezo_offset_x = -cs.piezo_max

        piezo_offset_y += piezo_step
        if piezo_offset_y > cs.piezo_max:
            piezo_offset_y = -cs.piezo_max

        output.move_sample(piezo_offset_x, piezo_offset_y)

        actual_writing_offset_x = int((cs.piezo_offset - piezo_offset_x) / cs.writing_slice)
        actual_writing_offset_y = int((cs.piezo_offset - piezo_offset_y) / cs.box_size)
        if high_res_y:
            actual_writing_offset_y = int((cs.piezo_offset - piezo_offset_y) / cs.writing_slice)

        if not high_res_y:
            if len(target_intensity.shape) > 2:
                lps = get_lps_cached(HashWrapper(np.roll(np.roll(target_intensity[:,:,z_index], round(-piezo_offset_x * ((x_size - 1) / (cs.array_size - 1))), 0), -piezo_offset_y, 1)), enable_calibration)
            else:
                lps = get_lps_cached(HashWrapper(np.roll(np.roll(target_intensity, round(-piezo_offset_x * ((x_size - 1) / (cs.array_size - 1))), 0), -piezo_offset_y, 1)), enable_calibration)
        else:
            if len(target_intensity.shape) > 2:
                y_size = np.shape(target_intensity)[1]
                lps = get_lps_cached(HashWrapper(np.roll(np.roll(target_intensity[:,:,z_index], round(-piezo_offset_x * ((x_size - 1) / (cs.array_size - 1))), 0), round(-piezo_offset_y * ((y_size - 1) / ((int(cs.correction_size / cs.box_size) + 1) - 1))), 1)), enable_calibration)
            else:
                lps = get_lps_cached(HashWrapper(np.roll(np.roll(target_intensity, round(-piezo_offset_x * ((x_size - 1) / (cs.array_size - 1))), 0), round(-piezo_offset_y * ((y_size - 1) / ((int(cs.correction_size / cs.box_size) + 1) - 1))), 1)), enable_calibration)

        for x in range(0 + actual_writing_offset_x, writing_size + actual_writing_offset_x):
            x_out = x * cs.writing_slice - cs.correction_size / 2

            if prism:
                x_max = (cs.writable_area / 2) * (thickness + 0.01 - z * 0.1) / (thickness + 0.01)
                current_x = x * cs.writing_slice - cs.correction_size / 2 + piezo_offset_x
                if abs(current_x) > x_max:
                    if enable_time_correction:
                        output.add_point(x_out, -cs.writable_area / 2 - piezo_offset_y, z_out, 0.01)
                        output.add_point(x_out, cs.writable_area / 2 - piezo_offset_y, z_out, 0.01)
                        output.write()
                    continue

            points_written = False
            for y in range(0 + actual_writing_offset_y, actual_array_size + actual_writing_offset_y):
                calibration_x = round(x / (writing_correction_size - 1) * (x_size - 1))
                calibration_y = y
                lp = lps[calibration_x, calibration_y]

                # Enhance contrast for visual purposes
                if cs.enhance_contrast:
                    lp = (lp - 20) * 40

                # Uncomment for LOW_LP
                #lp = max(0.01, lp - 2)

                y_out = y * cs.box_size - cs.correction_size / 2
                if high_res_y:
                    y_out = y * cs.writing_slice - cs.correction_size / 2

                if enable_time_correction or lp > 1:
                    points_written = True
                    output.add_point(x_out, y_out, z_out, lp)

            if points_written:
                output.write()

        if abs(z) % 20 == 0 and cs.multi_recalibrate:
            output.recalibrate()

    output.write_end()
    output.close()
