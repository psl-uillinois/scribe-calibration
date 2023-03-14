import sys

import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
from scipy.interpolate import pchip
from scipy.optimize import curve_fit

from calibration_utility import get_calibration_data

[lp_sums, sums] = get_calibration_data()
sums_means = np.mean(sums[:, 10:110, 10:110], axis=(1, 2))

peak_intensity_const = 0.1272

if __name__ == '__main__':
    plt.plot(lp_sums, sums_means)
    plt.show()

def exp_fit(x, a, b, c):
    return a * np.exp(b * x) + c


def lin_fit(x, a, b):
    return a * x + b


def get_lp(intensity, data):
    pass
    # x_range = np.arange(min(lp_sums), max(lp_sums), 0.01)
    # int_interp = get_fit_function_cached(HashWrapper(data))
    #
    # comparison = (int_interp >= intensity)
    # idx_out = 0
    # if True in comparison:
    #     idx_out = np.argmax(comparison)
    # else:
    #     idx_out = np.shape(x_range)[0] - 1
    #
    # return round(x_range[idx_out], 2)

    #popt, pcov = curve_fit(exp_fit, x_data, data, maxfev=10000)

    #if intensity < popt[2] or np.log((intensity - popt[2]) / popt[0]) / popt[1] < min_lp + 1:
        #popt, pcov = curve_fit(lin_fit, x_data[0:2], data[0:2], maxfev=10000)
        #predicted_lp = (intensity - popt[1]) / popt[0]
        #return predicted_lp
    #elif random.randint(0, 1000) == 0:
    #    plt.figure(1)
    #    plt.scatter(x_data, data)
    #    plt.plot(x_data, data)
    #    popt_exp, pcov = curve_fit(exp_fit, x_data, data, maxfev=10000)
    #    popt_lin, pcov = curve_fit(lin_fit, x_data[0:2], data[0:2], maxfev=10000)
    #    x_int_1 = np.linspace(min_lp - 3, min_lp + 1, 100)
    #    x_int_2 = np.linspace(min_lp + 1 + 0.0001, min_lp + num_lp, 100)
    #    x_data = np.append(x_int_1, x_int_2)
    #    data = np.append(lin_fit(x_int_1, *popt_lin), exp_fit(x_int_2, *popt_exp))
        #plt.scatter(x_data, data)
        #plt.show()
        #plt.plot(x_data, data)
    #    plt.xlabel("Laser power (%)")
    #    plt.ylabel("Intensity (arb.)")
        #plt.plot(x_int, exp_fit(x_int, *popt))
    #    plt.show()

    #predicted_lp = np.log((intensity - popt[2]) / popt[0]) / popt[1]
    #return predicted_lp


def gen_log(x, A, K, C, Q, B, nu):
    nu = abs(nu)
    Y = A + ((K - A) / np.power((C + Q * np.exp(-B * x)), 1/nu))
    return Y


def plot_lp(x, y, sym1, sym2, col, ax1, ax2, convert=False):
    #x_data = np.arange(min_lp, min_lp + num_lp)
    x_data = np.array(lp_sums)
    sums_data = None
    if x is None and y is None:
        sums_data = np.mean(sums[:,10:110,10:110], axis=(1, 2))
    else:
        sums_data = sums[:, x, y]
    #sums_data = np.sort(sums_data)
    interp = pchip(x_data, sums_data)
    #popt, pcov = curve_fit(gen_log, x_data, sums_data, maxfev=10000)

    #x_range = np.arange(min_lp, min_lp + num_lp - 1 + 0.01, 0.01)
    x_range = np.arange(min(lp_sums), max(lp_sums) + 0.01, 0.01)
    int_interp = interp(x_range)

    intensities = [30, 40, 50, 60, 70, 90, 110]
    indices = [1.21663, 1.23858, 1.27420, 1.30057, 1.32248, 1.40676, 1.50357]

    fit = Polynomial.fit(intensities, indices, deg=3)

    #x_lps = np.arange(min_lp, min_lp + num_lp)
    x_markers = [np.ndarray.tolist(np.where(abs(x_range - k) < 0.005)[0])[0] for k in x_data]

    y_out = interp(x_range)
    #y_out = gen_log(x_range, *popt)
    if convert:
        y_out = fit(y_out)

    if x is None:
        np.set_printoptions(threshold=sys.maxsize)
        print(x_range)
        print(y_out)

    ax1.plot((x_range / 2), y_out, markevery=x_markers, marker=sym1, linestyle=sym2, color=col)  #, label='Cubic Spline'
    ax2.plot((x_range / 2) * peak_intensity_const, y_out, markevery=x_markers, marker=sym1, linestyle=sym2, color=col)  #, label='Cubic Spline'
    #plt.plot(x_range / 2, y_out)  #, label='Cubic Spline'
    #plt.scatter(x_data / 2, sums_data, color='r')
    #plt.scatter(np.arange(min_lp, min_lp + num_lp) / 2, sums[:, x, y], marker=sym1, color=col)