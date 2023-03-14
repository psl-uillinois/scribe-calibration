import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim

import calibration_settings as cs
from calibration_utility import get_calibration_data
[lp_sums, sums] = get_calibration_data()

fig = plt.figure()
im = plt.imshow(sums[0], interpolation='none')
ax = plt.gca()

fps = 30
mspf = 1000/fps
seconds = len(lp_sums)
frames = seconds * fps

def animate(i):
    ax.set_title(f'{lp_sums[i // fps]}% LP Calibration')
    sums_data = sums[i // fps, 2:117, 2:117]
    im.set_array(sums_data)
    im.set_clim(vmin=np.min(sums_data), vmax=np.max(sums_data))
    return [im]

anim.FuncAnimation(fig, animate, frames=frames, interval=mspf, blit=False)

plt.show()
