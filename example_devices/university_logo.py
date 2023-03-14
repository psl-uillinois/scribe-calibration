import math
from os import listdir
from os.path import isfile, join, exists
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import random

from numpy.polynomial import Polynomial
from scipy.interpolate import pchip

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


img = np.array(Image.open("blocki.png"))
#print(img[50, 60, 2])
#exit(0)


intensities = [50, 90, 120, 150, 180, 210, 230]
indices = [1.2145, 1.3000, 1.3974, 1.4635, 1.5170, 1.5413, 1.5542]

blue_low = 0
blue_high = 70
blue_period = 20
blue_duty_cycle = 0.5
orange_low = 0
orange_high = 70
orange_period = 18
orange_duty_cycle = 0.4

interp = pchip(indices, intensities)
fit = Polynomial.fit(indices, intensities, deg=3)

total_radius = 50  # 100 um diameter


def get_intensity(x, y):
    intensity_out = 0
    pixel = img[min(y + 50, 99), min(round(x/10 + 50), 99)]
    # pixel = [1, 0, 0, 0]
    if pixel[2] == pixel[0]:  # B = R
        intensity_out = 0
    elif pixel[2] > pixel[0]:  # B > R
        intensity_out = blue_low
        if x % blue_period < int(blue_period * blue_duty_cycle):
            pixel_test_1 = img[min(y + 50, 99), min(round((x-x%blue_period)/10 + 50), 99)]
            pixel_test_2 = img[min(y + 50, 99), min(round((x-x%blue_period+int(blue_period * blue_duty_cycle))/10 + 50), 99)]
            if pixel_test_1[2] > pixel_test_1[0] and pixel_test_2[2] > pixel_test_2[0]:
                intensity_out = blue_high
    else:
        intensity_out = orange_low
        if x % orange_period < int(orange_period * orange_duty_cycle):
            pixel_test_1 = img[min(y + 50, 99), min(round((x-x%orange_period)/10 + 50), 99)]
            pixel_test_2 = img[min(y + 50, 99), min(round((x-x%orange_period+int(orange_period * orange_duty_cycle))/10 + 50), 99)]
            if pixel_test_1[2] < pixel_test_1[0] and pixel_test_2[2] < pixel_test_2[0]:
                intensity_out = orange_high

    return intensity_out


def get_phase_mask():
    phase_mask = np.zeros([1201, 121])
    for x in range(-600, 601):
        for y in range(-60, 61):
            if abs(x) <= 500 and abs(y) <= 50:
                phase_mask[x + 600, y + 60] = get_intensity(x, -y)
    return phase_mask


def get_index_map():
    index_map = np.zeros([1201, 121])
    for x in range(-600, 601):
        for y in range(-60, 61):
            if abs(x) <= 500 and abs(y) <= 50:
                index_map[x + 600, y + 60] = get_index(x, y)
            else:
                index_map[x + 600, y + 60] = 1.15
    return index_map



if __name__ == '__main__':
    grating_phase_mask = get_phase_mask()
    grating = Device(custom_name=f"BLOCKI", custom_text=f"", custom_text_inner=f", BLOCKI", custom_file=True,
                     target_intensity=grating_phase_mask, enable_calibration=True, enable_piezo_correction=True,
                     enable_time_correction=True, thickness=4.8, xsize=300, ysize=150, xarray=2)
    make_device(grating, join("..", cs.device_input_dir, f"BLOCKI"))
    grating_phase_mask = get_phase_mask()
    grating = Device(custom_name=f"BLOCKI", custom_text=f"_CONTROL", custom_text_inner=f", BLOCKI_CONTROL", custom_file=True,
                     target_intensity=grating_phase_mask, enable_calibration=False, enable_piezo_correction=False,
                     enable_time_correction=False, thickness=4.8, xsize=300, ysize=150, xarray=2)
    make_device(grating, join("..", cs.device_input_dir, f"BLOCKI_CONTROL"))

# Plot fluorescence intensity vs refractive index
#font = {'size'   : 15}
#plt.rc('font', **font)
#plt.figure(1, figsize=(8, 6))
#x = np.linspace(1.2, 1.55, 101)
#plt.plot(x, fit(x), color='k')
#plt.scatter(indices, intensities, color='k')
#plt.xlim([1.2, 1.55])
#plt.xlabel('Refractive Index')
#plt.ylabel('Fluorescence Intensity (arb.)')
#plt.savefig('index_vs_intensity.png', dpi=1200)
#plt.show()
#exit(0)


#x = np.linspace(0, 50, 101)
#focal_depth = 0
#plt.plot(x, get_index(x))
#focal_depth = 1000
#plt.plot(x, get_index(x))
#plt.figure(2)
#focal_depth = 0
#plt.plot(x, get_intensity(x))
#focal_depth = 1000
#plt.plot(x, get_intensity(x))
#plt.show()

# font = {'size'   : 15}
#
# plt.rc('font', **font)
# plt.figure(1, figsize=(8, 6))
# plt.imshow(np.transpose(phase_mask), aspect=10)
# plt.xlabel('X ($\mu$m)')
# plt.ylabel('Y ($\mu$m)')
# plt.colorbar(label="Fluorescence Intensity (arb.)")
# #plt.savefig('axicon_int.png', dpi=1200)
# plt.figure(2, figsize=(8, 6))
# plt.imshow(np.transpose(index_map), aspect=10)
# plt.xlabel('X ($\mu$m)')
# plt.ylabel('Y ($\mu$m)')
# plt.colorbar(label="Refractive Index")
# #plt.savefig('axicon_idx.png', dpi=1200)
# plt.show()