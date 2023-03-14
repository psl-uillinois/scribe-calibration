import sys

import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import Polynomial
import matplotlib.ticker as ticker

from plot_lp import plot_lp
import calibration_settings as cs

# Figure 3b/c in final paper
# Plot (x, y)

plt.figure(1, figsize=(3.5, 3.75))
convert_to_idx = False


font = {'size'   : 13}
plt.rc('font', **font)
ax1 = plt.gca()
ax2 = ax1.twiny()
#plot_lp(60, 60, 's', '--', 'tab:red', convert_to_idx)
#plot_lp(30, 30, '^', '-.', 'tab:purple', convert_to_idx)
#plot_lp(30, 80, 'o', '-', 'tab:orange', convert_to_idx)
#plot_lp(100, 100, 'v', '-', 'tab:blue', convert_to_idx)
plot_lp(50, 50, 's', '--', 'tab:red', ax1, ax2, convert_to_idx)
plot_lp(5, 115, 'o', '-', 'tab:orange', ax1, ax2, convert_to_idx)
plot_lp(115, 115, 'v', '-', 'tab:blue', ax1, ax2, convert_to_idx)
#plot_lp(None, None, '*', '-', 'tab:blue', convert_to_idx)
ax1.set_xlabel('Average Power (mW)')
ax2.set_xlabel('Peak Intensity (TW/cm$^2$)')
ax1.set_ylabel('Fluorescence Intensity\n(arb. units)')
plt.ylim([0, 250])

enable_index = False
if enable_index:
    ax2 = ax1.twinx()
    plt.sca(ax2)
    ax2.set_ylabel('Refractive Index')

    intensities = [110.0, 140.0, 170.0, 180.0, 190.0, 20.0, 210.0, 50.0, 80.0]
    indices = [1.2889975, 1.3441183333333333, 1.4401933333333334, 1.5082991666666665, 1.5534683333333337, 1.1970875, 1.577805, 1.2401255555555555, 1.2600069999999997]
    fit = Polynomial.fit(indices, intensities, deg=3)

    mark_ind = np.array([1.2, 1.3, 1.4, 1.5])
    mark_int = fit(mark_ind) / 250

    ax2.yaxis.set_major_locator(ticker.FixedLocator((mark_int)))
    ax2.yaxis.set_major_formatter(ticker.FixedFormatter((mark_ind)))

ax1.tick_params(which='both', direction="in")
ax2.tick_params(which='both', direction="in")
plt.gcf().subplots_adjust(bottom=0.15)
plt.tight_layout()
plt.savefig('calibration_points.png', dpi=1200)
# plt.figure(2)
# plt.imshow(np.transpose(sums[3]))
plt.show()

# print(np.mean(get_lps(target_intensity)[11:109, 11:109]))
# exit(0)

# for x in range(0, array_size):
#    for y in range(0, array_size):
#        #lp = round(get_lp(target_intensity, sums[:, x, y]), 2)
#        if random.randint(0, 1000) == 0:
#            cs = CubicSpline(np.arange(min_lp, min_lp + num_lp), sums[:, x, y])
#            interp = pchip(np.arange(min_lp, min_lp + num_lp), sums[:, x, y])
#
#            x_range = np.arange(min_lp, min_lp + num_lp - 1, 0.01)
#            plt.plot(x_range, interp(x_range), label='Cubic Spline')
#            plt.scatter(np.arange(min_lp, min_lp + num_lp), sums[:, x, y])
#            plt.show()
#         lps[x, y] = lp
#    print(x)
#
# plt.imshow(lps)
# plt.show()
# exit(0)
#
# np.save("orange_low.npy", lps)
# exit(0)
#
# averaged_lps = np.zeros((array_size, array_size))
# for x in range(0, array_size):
#    for y in range(0, array_size):
#        averaged_lps[x, y] = np.mean(lps[max(0, x-2):min(array_size-1, x+3), max(0, y-2):min(array_size-1, y+3)])
#
# plt.imshow(np.transpose(averaged_lps))
# plt.show()
#
# exit(0)