import numpy as np

from output_gwl import GWL

output_class = GWL

gwl_settings = ("GalvoScanMode\nPiezoSettlingTime 20\nGalvoAcceleration 1\nStageVelocity 200\nXOffset 0\nYOffset 0\n" +
               "PowerScaling 1.0\nScanSpeed 10000\nTextLaserPower 20\nFindInterfaceAt 0\n")

# Location of data directories (relative to this directory)
raw_data_dir = "raw_calibration_data"
data_dir = "calibration_data"
device_dir = "device"
device_input_dir = "device_input"

# File extension on all raw data files
raw_data_filetype = "png"
alignment_data_filetype = "txt"
calibration_data_filetype = "npy"
device_filetype = "gwl"
device_input_filetype = "pickle"

# Location of alignment marks in calibration device (units: um)
alignment_physical_loc = np.array([[65, -65], [-65, -65], [65, 65]])

# Size of each bin in the correction (units: um)
box_size = 1

# Total size of correction (units: um)
correction_size = 120
correction_offset = correction_size // 2

writing_slice = 0.1

writable_area = 100
writable_offset = writable_area // 2

piezo_offset = 10
piezo_max = 7

array_size = int(correction_size / box_size) + 1

piezo_step = 1

measured_power = 1

enhance_contrast = False
multithread = True
multi_recalibrate = False

lp_threshold = 10

max_calibration_intensity = [150, 170]

# Size of raw calibration images (units: pixels)
img_x = 1024
img_y = 1024

auto_align_inset = 50

flipped_images = [3, 4]
