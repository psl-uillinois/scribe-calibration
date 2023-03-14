import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

import calibration_settings as cs
from calibration_utility import get_calibration_data

# Plot SI Fig. 2

[lp_sums, sums] = get_calibration_data()

num_lp = np.shape(lp_sums)[0]

font = {'size'   : 15}
plt.rc('font', **font)

cropped_sums = np.zeros((num_lp, 80, 80))
cropped_sums_range = np.zeros(num_lp)
cropped_sums_range_integral = np.zeros(num_lp)
for i in range(0, num_lp):
   cropped_sums[i] = sums[i,20:100,20:100]
   cropped_sums_range[i] = np.std(cropped_sums[i]) / np.mean(cropped_sums[i]) * 100
   cropped_sums_range_integral[i] = cropped_sums_range[i] - 5.2
   if i > 0:
       cropped_sums_range_integral[i] += cropped_sums_range_integral[i - 1]
sums_stats = cropped_sums.reshape(cropped_sums.shape[0], -1)
plt.figure(1, figsize=(10, 6))
plt.boxplot(sums_stats.transpose(), positions=np.array(lp_sums) / 2, whis=100)
plt.xlabel('Laser Power (mW)')
plt.ylabel('Fluorescence Intensity (arb. units)')


def f(x, a, b, c, d):
   return a / (1. + np.exp(-c * (x - d))) + b


popt, pcov = curve_fit(f, np.log(lp_sums), cropped_sums_range_integral, p0=np.array([120, 0, 1, 2.5]), method="trf", maxfev=1000)
lp_all = np.linspace(lp_sums[0], lp_sums[-1], 101)

plt.savefig('boxplot.png', dpi=1200)
plt.figure(2, figsize=(8, 6))
plt.plot(np.array(lp_sums) / 2, cropped_sums_range)
plt.xlabel('Laser Power (mW)')
plt.ylabel('Coefficient of Variation (%)')
plt.savefig('cov.png', dpi=1200)
plt.figure(3, figsize=(8, 6))
plt.plot(lp_all / 2, f(np.log(lp_all), *popt))
plt.scatter(np.array(lp_sums) / 2, cropped_sums_range_integral)
plt.xscale('log')
plt.xticks(ticks=[10, 11, 12, 13, 14, 15, 16], labels=[str(x) for x in [10, 11, 12, 13, 14, 15, 16]])
plt.xlabel('Laser Power (mW)')
plt.ylabel('Integrated Coefficient of Variation (arb. units)')
plt.savefig('logistic.png', dpi=1200)

plt.figure(4)
print(lp_sums[6])
data = sums[6,20:100,20:100].flatten()
plt.hist(data, bins=np.arange(data.min(), data.max()+1))

plt.show()