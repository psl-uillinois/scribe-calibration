import numpy as np
from scipy.interpolate import pchip
import matplotlib.pyplot as plt
import math
from numpy.polynomial import Polynomial
from functools import cache
from matplotlib.colors import LinearSegmentedColormap

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

intensities = [110.0, 140.0, 170.0, 180.0, 190.0, 20.0, 210.0, 50.0, 80.0]
indices = [1.2889975, 1.3441183333333333, 1.4401933333333334, 1.5082991666666665, 1.5534683333333337, 1.1970875, 1.577805, 1.2401255555555555, 1.2600069999999997]
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
fit = Polynomial.fit(indices, intensities, deg=4)

total_radius = 50  # 100 um diameter


def get_phase(radius, wavelength = 0.643, focal_length = 600, focal_depth = 100):
    # wavelength = 0.643  # Microns -- red laser
    # focal_length = 600  # 0.6 mm
    # focal_depth = 100  # 0.1 mm

    phase = (math.pi * (radius ** 2) /
            (wavelength * (focal_length + (focal_depth * (radius ** 2) / (total_radius ** 2)))))
    return phase  #% (math.pi * 2)


def get_index(radius, wavelength = 0.643, focal_length = 600, focal_depth = 100):
    background_index = 1.22  #1.20 for LOW_N
    thickness = 5

    phase = get_phase(radius, wavelength, focal_length, focal_depth)
    delta_n = phase * wavelength / (thickness * 2 * math.pi)
    return delta_n + background_index


def get_intensity(radius, wavelength = 0.643, focal_length = 600, focal_depth = 100):
    index = get_index(radius, wavelength, focal_length, focal_depth)
    intensity = fit(index)
    return intensity

def get_phase_mask(wavelength, focal_length, focal_depth):
    phase_mask = np.zeros([1201, 1201])
    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                phase_mask[x + 600, y + 600] = get_intensity(radius, wavelength, focal_length, focal_depth)
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
    i = 1
    ctext = ", STANDARD"
    for (fl, fd) in [(2000, 100)]:
        axicon_phase_mask = get_phase_mask(wavelength=0.643, focal_length=fl, focal_depth=fd)
        phase_mask = axicon_phase_mask
        axicon = Device(custom_name=f"AXICON", custom_text=f"_{i}_{fl}_{fd}", custom_text_inner=f", FOCAL_LENGTH={fl}, FOCAL_DEPTH={fd}{ctext}", custom_file=True,
                         target_intensity=axicon_phase_mask, enable_calibration=True, enable_piezo_correction=True,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(axicon, join("..", cs.device_input_dir, f"AXICON_{i}_{fl}_{fd}.pickle"))
        axicon = Device(custom_name=f"AXICON", custom_text=f"_{i}_{fl}_{fd}_CALIBRATED_CONSTTIME", custom_text_inner=f", FOCAL_LENGTH={fl}, FOCAL_DEPTH={fd}, CALONLY{ctext}", custom_file=True,
                         target_intensity=axicon_phase_mask, enable_calibration=True, enable_piezo_correction=False,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(axicon, join("..", cs.device_input_dir, f"AXICON_{i}_{fl}_{fd}_CALONLY.pickle"))
        axicon = Device(custom_name=f"AXICON", custom_text=f"_{i}_{fl}_{fd}_PIEZO_CONSTTIME", custom_text_inner=f", FOCAL_LENGTH={fl}, FOCAL_DEPTH={fd}, PIEZO{ctext}", custom_file=True,
                         target_intensity=axicon_phase_mask, enable_calibration=False, enable_piezo_correction=True,
                         enable_time_correction=True, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(axicon, join("..", cs.device_input_dir, f"AXICON_{i}_{fl}_{fd}_PIEZO.pickle"))
        axicon = Device(custom_name=f"AXICON", custom_text=f"_{i}_{fl}_{fd}_CONTROL", custom_text_inner=f", FOCAL_LENGTH={fl}, FOCAL_DEPTH={fd}, CONTROL{ctext}", custom_file=True,
                         target_intensity=axicon_phase_mask, enable_calibration=False, enable_piezo_correction=False,
                         enable_time_correction=False, thickness=4.8, xsize=300, ysize=300, high_res_y=True)
        make_device(axicon, join("..", cs.device_input_dir, f"AXICON_{i}_{fl}_{fd}_CONTROL.pickle"))

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
#plt.figure(1, figsize=(6, 5))
#plt.subplot(2, 1, 1)
fig = plt.figure(1, figsize=(6, 6), frameon=False)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
plt.imshow(phase_mask, cmap='cividis', extent=[0, 120, 0, 120], vmin=20)  #gist_rainbow alt
#plt.xlabel('X ($\mu$m)')
#plt.ylabel('Y ($\mu$m)')
#plt.colorbar(label="Fluorescence Intensity (arb.)")
# plt.savefig('axicon_int.png', dpi=1200)
# plt.figure(2, figsize=(8, 6))
# plt.imshow(index_map)
# plt.xlabel('X ($\mu$m)')
# plt.ylabel('Y ($\mu$m)')
# plt.colorbar(label="Refractive Index")
#plt.subplot(2, 1, 2)
#plt.plot(np.linspace(0, 120, np.shape(phase_mask)[0]), phase_mask[int(np.shape(phase_mask)[0]/2)])
#plt.xlabel('X ($\mu$m)')
#plt.ylabel('Intensity at y=60')
#plt.tight_layout()
plt.savefig('axicon_cividis.png', dpi=1200)
plt.show()