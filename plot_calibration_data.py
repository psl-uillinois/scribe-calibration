import matplotlib.pyplot as plt
import numpy as np

import calibration_settings as cs
from calibration_utility import get_calibration_data

[lp_sums, sums] = get_calibration_data()

print(np.mean(sums, axis=(1, 2)))
plt.plot(lp_sums, np.mean(sums, axis=(1, 2)))
plt.xlabel('Laser power (%)')
plt.ylabel('Fluorescence intensity (arb.)')
plt.show()
