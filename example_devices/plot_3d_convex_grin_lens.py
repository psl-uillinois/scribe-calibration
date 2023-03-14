import numpy as np
from scipy.interpolate import pchip
import matplotlib.pyplot as plt
import math
from numpy.polynomial import Polynomial
from functools import cache
from random import randint

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
fit = Polynomial.fit(indices, intensities, deg=3)

total_radius = 50  # 100 um diameter
wavelength = 0.642

def get_index(radius, focal_length = 2000, min_n = 1.22):
    thickness = 5

    phase = -math.pi * radius ** 2 / (wavelength * focal_length)  # FLIP has phase negated
    delta_n = wavelength * phase / (2 * math.pi * thickness)
    return delta_n + min_n


def get_intensity(radius, focal_length = 2000, min_n = 1.22):
    index = get_index(radius, focal_length, min_n)
    intensity = fit(index)
    return intensity

def get_phase_mask(focal_length, min_n):
    phase_mask = np.zeros([1201, 1201])
    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                phase_mask[x + 600, y + 600] = get_intensity(radius, focal_length, min_n)
    return phase_mask


def get_index_mask(focal_length, min_n):
    index_map = np.zeros([1201, 1201])
    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                index_map[x + 600, y + 600] = get_index(radius, focal_length, min_n)
            else:
                index_map[x + 600, y + 600] = 1.15
    return index_map


def edge_of_radius(x, y):
    radius = ((x / 10) ** 2 + (y / 10) ** 2) ** (1 / 2)
    for i in range(-1, 2):
        for j in range(-1, 2):
            radius2 = (((x+i) / 10) ** 2 + ((y+j) / 10) ** 2) ** (1 / 2)
            if (radius <= total_radius) != (radius2 <= total_radius):
                return True
    return False

from mpl_toolkits.mplot3d import Axes3D

reduce_for_debug = False

def single_3d_plot(fig, k, elev, azim, data, hide_axis_string=None, marker_size=0.005, label_offset=''):
    xa, ya, za, ca = data

    ax = fig.add_subplot(k, projection='3d')

    p = ax.scatter(xa, ya, za, c=ca, cmap='cividis', s=marker_size, vmin=np.min(ca), vmax=np.max(ca))
    ax.set_xlabel(f'{label_offset}X ($\mu$m)', labelpad=5)
    ax.set_ylabel('Y ($\mu$m)', labelpad=5)
    ax.set_zlabel('Z ($\mu$m)', labelpad=3)

    xrange = np.ptp(xa)
    yrange = np.ptp(ya)
    zrange = np.ptp(za)
    ax.set_box_aspect([xrange, yrange, zrange * 5])  # equal aspect ratio

    ax.axes.set_xlim3d(left=-60, right=60)
    ax.axes.set_ylim3d(bottom=-60, top=60)
    ax.axes.set_zlim3d(bottom=-5, top=5)
    ax.zaxis.set_ticks([-4, 0, 4])
    ax.view_init(elev, azim)

    if hide_axis_string is not None:
        hidden_axis = getattr(ax, f'{hide_axis_string}axis')
        hidden_axis.label.set_visible(False)
        hidden_axis.set_ticks([])

    return p


phase_mask = None
if __name__ == '__main__':
    fl = 2000
    mn = 1.35

    xa = []
    ya = []
    za = []
    ca = []

    for x in range(-600, 601):
        for y in range(-600, 601):
            radius = ((x/10) ** 2 + (y/10) ** 2) ** (1/2)
            if radius <= total_radius:
                if reduce_for_debug:
                    if randint(0, 10) != 0:
                        continue
                # radius = (round(x/10) ** 2 + round(y/10) ** 2) ** (1/2)
                index = get_index(radius, fl, mn)
                xa.append(x/10)
                ya.append(y/10)
                za.append(2.5)
                ca.append(index)
                xa.append(x/10)
                ya.append(y/10)
                za.append(-2.5)
                ca.append(index)
                if edge_of_radius(x, y):
                    for i in range(1, 50):
                        xa.append(x / 10)
                        ya.append(y / 10)
                        za.append(i/10 - 2.5)
                        ca.append(index)

    xa = np.array(xa)
    ya = np.array(ya)
    za = np.array(za)
    ca = np.array(ca)
    #ca = (ca - np.min(ca)) / (np.max(ca) - np.min(ca))

    fig = plt.figure(figsize=(7, 7))

    data = [xa, ya, za, ca]
    p = single_3d_plot(fig, 221, 30, -60, data)
    single_3d_plot(fig, 222, 90, 90, data, 'z', marker_size=0.0005)  # XY plot
    plt.gca().set_proj_type('ortho')

    #single_3d_plot(fig, 4, 0, 0, data)

    #fig.subplots_adjust(right=0.8)
    #cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    #fig.colorbar(p, cax=cbar_ax)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.4)

    plt.savefig('3dconvexgrinlens_top.png', dpi=600)

    fig = plt.figure(figsize=(7, 7))
    single_3d_plot(fig, 111, 0, -90, data, 'y', marker_size=0.05, label_offset='\n\n')  # XZ plot
    plt.gca().set_proj_type('ortho')

    plt.tight_layout()
    plt.savefig('3dconvexgrinlens_bottom.png', dpi=600)

    fig = plt.figure(figsize=(7, 7))
    cbar_ax = fig.add_axes([0.88, 0.05, 0.03, 0.90])
    cbar = fig.colorbar(p, cax=cbar_ax)
    cbar.ax.set_ylabel('Refractive index', rotation=90)
    plt.savefig('3dconvexgrinlens_colorbar.png', dpi=600)

    plt.show()
