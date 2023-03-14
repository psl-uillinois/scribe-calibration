import numpy as np
from scipy.interpolate import pchip
import matplotlib.pyplot as plt
import math
from numpy.polynomial import Polynomial
from functools import cache

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

total_radius = 50  # 100 um diameter


def get_index(x):
    background_index = 1.15

    delta_n = 0
    if x % 10 < 5:
        delta_n = 0.32
        # delta_n = 0.004 * (x/10 + 50)
    return delta_n + background_index


def get_intensity(x, y, max_intensity, min_intensity, periods, duty_cycles):
    period_section = min(math.floor(x / 100 + 5), 9)
    duty_cycle_section = min(math.floor(-y / 10 + 5), 9)

    zero_mark = ((math.floor(x / 10) + 50) % 10 == 0 and (y + 50 < 10)) ^ ((y + 50) % 10 == 0 and (x/10 + 50 < 10))

    period = periods[period_section]
    duty_cycle = duty_cycles[duty_cycle_section]

    intensity = min_intensity
    if not zero_mark and x % period < int(period * duty_cycle):
        intensity = max_intensity
    return intensity
    # return 70 # math.floor((x + 500) / 100) * 10 + 30


def get_phase_mask(max_intensity, min_intensity=0, periods=[6, 7, 8, 9, 10, 12, 14, 16, 18, 20], duty_cycles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]):
    phase_mask = np.zeros([1201, 121])
    for x in range(-600, 601):
        for y in range(-60, 61):
            if abs(x) <= 500 and abs(y) <= 50: # and not ((abs(y) > 45 and (x % 100) < 10 and abs(x) < 490) or (abs(y) > 40 and 0 <= x < 10)):
                phase_mask[x + 600, y + 60] = get_intensity(x, y, max_intensity, min_intensity, periods, duty_cycles)
    return phase_mask

phase_mask = 0

if __name__ == '__main__':
    for intensity in [50, 70, 100, 120]:
        grating_phase_mask = get_phase_mask(intensity)
        grating = Device(custom_name=f"VARIABLE_GRATING", custom_text=f"_{intensity}", custom_text_inner=f", INT={intensity}, PERIOD=[6..10, 12..20], DUTY=[0.1..1.0]", custom_file=True,
                         target_intensity=grating_phase_mask, enable_calibration=True, enable_piezo_correction=True,
                         enable_time_correction=True, thickness=4.8, xsize=150, ysize=150)
        make_device(grating, join("..", cs.device_input_dir, f"VARIABLE_GRATING_{intensity}.pickle"))
        phase_mask = grating_phase_mask

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

font = {'size'   : 15}

plt.rc('font', **font)
plt.figure(1, figsize=(8, 6))
plt.imshow(np.transpose(phase_mask), aspect=10)
plt.xlabel('X ($\mu$m)')
plt.ylabel('Y ($\mu$m)')
plt.colorbar(label="Fluorescence Intensity (arb.)")
# #plt.savefig('axicon_int.png', dpi=1200)
# plt.figure(2, figsize=(8, 6))
# plt.imshow(np.transpose(index_map), aspect=10)
# plt.xlabel('X ($\mu$m)')
# plt.ylabel('Y ($\mu$m)')
# plt.colorbar(label="Refractive Index")
# #plt.savefig('axicon_idx.png', dpi=1200)
plt.show()