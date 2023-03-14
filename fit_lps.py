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

[lp_sums, sums] = get_calibration_data()
sums_means = np.mean(sums[:, 10:110, 10:110], axis=(1, 2))


@lru_cache(maxsize=None, typed=False)
def get_fit_function_cached(data):
    return get_fit_function(data.unwrap())


def get_fit_function(data):
    x_data = np.array(lp_sums)
    interp = pchip(x_data, data)

    x_range = np.arange(min(lp_sums), max(lp_sums), 0.01)
    int_interp = interp(x_range)
    return int_interp


@lru_cache(maxsize=128, typed=False)
def get_lp_cached(intensity, data):
    return get_lp(intensity, data.unwrap())


def get_lp(intensity, data):
    x_range = np.arange(min(lp_sums), max(lp_sums), 0.01)
    int_interp = get_fit_function_cached(HashWrapper(data))

    comparison = (int_interp >= intensity)
    idx_out = 0
    if True in comparison:
        idx_out = np.argmax(comparison)
    else:
        idx_out = np.shape(x_range)[0] - 1

    return round(x_range[idx_out], 2)


@lru_cache(maxsize=128, typed=False)
def get_lps_cached(intensities, enable_calibration):
    return get_lps(intensities.unwrap(), enable_calibration)


def get_lps(intensities, enable_calibration):
    x_size = intensities.shape[0]
    y_size = intensities.shape[1]
    lps = np.zeros((x_size, y_size))
    for x in range(0, x_size):
        for y in range(0, y_size):
            lp_x = round(x * ((cs.array_size - 1) / (x_size - 1)))
            lp_y = round(y * ((cs.array_size - 1) / (y_size - 1)))
            if intensities[x, y] == 0:
                lps[x, y] = 0.01
            else:
                if enable_calibration:
                    if cs.max_calibration_intensity is not None and len(cs.max_calibration_intensity) == 2:
                        if intensities[x, y] <= cs.max_calibration_intensity[0]:
                            lps[x, y] = get_lp_cached(intensities[x, y], HashWrapper(sums[:, lp_x, lp_y]))
                        elif intensities[x, y] >= cs.max_calibration_intensity[1]:
                            lps[x, y] = get_lp_cached(intensities[x, y], HashWrapper(sums_means))
                        else:
                            lp_avg = get_lp_cached(intensities[x, y], HashWrapper(sums_means))
                            lp = get_lp_cached(intensities[x, y], HashWrapper(sums[:, lp_x, lp_y]))

                            weight = ((intensities[x, y] - cs.max_calibration_intensity[0]) /
                                     (cs.max_calibration_intensity[1] - cs.max_calibration_intensity[0]))

                            lps[x, y] = lp * (1 - weight) + lp_avg * (weight)
                    else:
                        lps[x, y] = get_lp_cached(intensities[x, y], HashWrapper(sums[:, lp_x, lp_y]))
                else:
                    lps[x, y] = get_lp_cached(intensities[x, y], HashWrapper(sums_means))
    return lps
