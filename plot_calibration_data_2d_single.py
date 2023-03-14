import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

import calibration_settings as cs
from calibration_utility import get_calibration_data_preaverage
[lp_sums, sums_list] = get_calibration_data_preaverage(data_dir=cs.data_dir)

lp_selected = 35

sums_selected = sums_list[lp_sums.index(lp_selected)]

subplots = len(sums_selected) + 1

fig = plt.figure()
for i in range(0, subplots-1):
    plt.subplot(1, subplots, i+1)
    plt.title(f'{lp_selected}% LP: {i+1}')
    im = plt.imshow(sums_selected[i][4:114, 4:114], interpolation='none')

plt.subplot(1, subplots, subplots)
plt.title(f'{lp_selected}% LP: MEAN')
im = plt.imshow(np.mean(np.stack(sums_selected, axis=2), axis=2)[4:114, 4:114], interpolation='none')

plt.show()
