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

# intensities = [50, 90, 120, 150, 180, 210, 230]
# indices = [1.2145, 1.3000, 1.3974, 1.4635, 1.5170, 1.5413, 1.5542]

intensities = [20.0, 30.0, 50.0, 70.0, 90.0, 110.0, 130.0, 150.0, 155.0, 160.0, 165.0, 170.0, 180.0, 190.0, 210.0]
indices = [1.21794, 1.21868, 1.22734, 1.24510, 1.28114, 1.29168, 1.31855, 1.33427, 1.37435, 1.39784, 1.42430, 1.42883, 1.48128, 1.52624, 1.57516]
# fit1 = Polynomial.fit(indices[:8], intensities[:8], deg=3)
# fit2 = Polynomial.fit(indices[7:12], intensities[7:12], deg=3)
# fit3 = Polynomial.fit(indices[11:], intensities[11:], deg=3)
#
# def fit(x):
#     single_value = False
#     if isinstance(x, float) or isinstance(x, int):
#         single_value = True
#         x = np.array([x])
#     y = np.where(x < 1.33427, fit1(x), np.where(x > 1.42883, fit3(x), fit2(x)))
#     if single_value:
#         return y[0]
#     return y

# interp = pchip(indices, intensities)
fit = Polynomial.fit(indices, intensities, deg=3)

total_radius = 50  # 100 um diameter


def get_index(radius, min_n = 1.22, max_n=1.55):
    thickness = 5

    delta_n = (max_n - min_n) * ((total_radius - radius) ** 2 / total_radius ** 2)
    return delta_n + min_n


def get_intensity(radius, focal_length = 600, focal_depth = 100):
    index = get_index(radius, focal_length, focal_depth)
    intensity = fit(index)
    return intensity

def get_phase_mask(focal_length, focal_depth):
    phase_mask = np.zeros([1201, 1201])
    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                phase_mask[x + 600, y + 600] = get_intensity(radius, focal_length, focal_depth)
    return phase_mask


def get_index_mask():
    index_map = np.zeros([1201, 1201])
    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                index_map[x + 600, y + 600] = get_index(radius)
            else:
                index_map[x + 600, y + 600] = 1.15
    return index_map

phase_mask = None
if __name__ == '__main__':
    for (fl, fd) in [(1.22, 1.30), (1.22, 1.55)]:
        grin_lens_phase_mask = get_phase_mask(focal_length=fl, focal_depth=fd)
        phase_mask = grin_lens_phase_mask
        grin_lens = Device(custom_name=f"GRIN_LENS", custom_text=f"_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}", custom_text_inner=f", MIN_N={fl}, MAX_N={fd}", custom_file=True,
                         target_intensity=grin_lens_phase_mask, enable_calibration=True, enable_piezo_correction=True,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(grin_lens, join("..", cs.device_input_dir, f"GRIN_LENS_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}.pickle"))
        grin_lens = Device(custom_name=f"GRIN_LENS", custom_text=f"_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_CALIBRATED_CONSTTIME", custom_text_inner=f", MIN_N={fl}, MAX_N={fd}, CALONLY", custom_file=True,
                         target_intensity=grin_lens_phase_mask, enable_calibration=True, enable_piezo_correction=False,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(grin_lens, join("..", cs.device_input_dir, f"GRIN_LENS_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_CALONLY.pickle"))
        grin_lens = Device(custom_name=f"GRIN_LENS", custom_text=f"_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_PIEZO_CONSTTIME", custom_text_inner=f", MIN_N={fl}, MAX_N={fd}, PIEZO", custom_file=True,
                         target_intensity=grin_lens_phase_mask, enable_calibration=False, enable_piezo_correction=True,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(grin_lens, join("..", cs.device_input_dir, f"GRIN_LENS_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_PIEZO.pickle"))
        grin_lens = Device(custom_name=f"GRIN_LENS", custom_text=f"_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_CONTROL", custom_text_inner=f", MIN_N={fl}, MAX_N={fd}, CONTROL", custom_file=True,
                         target_intensity=grin_lens_phase_mask, enable_calibration=False, enable_piezo_correction=False,
                         enable_time_correction=False, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(grin_lens, join("..", cs.device_input_dir, f"GRIN_LENS_{str(fl).replace('.', 'p')}_{str(fd).replace('.', 'p')}_CONTROL.pickle"))

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
plt.imshow(phase_mask)
plt.xlabel('X ($\mu$m)')
plt.ylabel('Y ($\mu$m)')
plt.colorbar(label="Fluorescence Intensity (arb.)")
# plt.savefig('grin_lens_int.png', dpi=1200)
# plt.figure(2, figsize=(8, 6))
# plt.imshow(index_map)
# plt.xlabel('X ($\mu$m)')
# plt.ylabel('Y ($\mu$m)')
# plt.colorbar(label="Refractive Index")
# plt.savefig('grin_lens_idx.png', dpi=1200)
plt.show()