from os import listdir
from os.path import isfile, join, exists
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

import calibration_settings as cs

pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
unpad = lambda x: x[:, :-1]

alignment_physical_loc = pad(cs.alignment_physical_loc)

raw_calibration_filenames = [f for f in listdir(cs.raw_data_dir) if isfile(join(cs.raw_data_dir, f))]

for filename in raw_calibration_filenames:
    file_type = filename.split(".")[-1]
    if file_type != cs.raw_data_filetype:
        continue

    text_file = join(cs.raw_data_dir, filename.split(".")[0] + f".{cs.alignment_data_filetype}")
    if exists(text_file):
        continue

    # Extract metadata in filename as integers
    metadata = [int(x) for x in ''.join(filter(lambda x: x.isdigit() or x == '_', filename.split(".")[0])).split("_")]

    img = np.transpose(np.array(Image.open(join(cs.raw_data_dir, filename))))

    # Start with bottom left corner
    sums = np.zeros((2, cs.auto_align_inset))
    test = np.zeros((cs.auto_align_inset, cs.auto_align_inset))
    for x in range(0, cs.auto_align_inset):
        for y in range(0, cs.auto_align_inset):
            value = img[x, y + (cs.img_y - cs.auto_align_inset)]
            sums[0, x] += value
            sums[1, y] += value
            test[x, y] = value
    bottom_left = str(np.argmax(sums[0])) + ", " + str((cs.img_y - cs.auto_align_inset) + np.argmax(sums[1]))
    print(filename + " BL: " + str(sums[0, np.argmax(sums[0])]) + ", " + str(sums[1, np.argmax(sums[1])]))

    # Find bottom right corner
    sums = np.zeros((2, cs.auto_align_inset))
    test = np.zeros((cs.auto_align_inset, cs.auto_align_inset))
    for x in range(0, cs.auto_align_inset):
        for y in range(0, cs.auto_align_inset):
            value = img[x + (cs.img_x - cs.auto_align_inset), y + (cs.img_y - cs.auto_align_inset)]
            sums[0, x] += value
            sums[1, y] += value
            test[x, y] = value
    bottom_right = str((cs.img_x - cs.auto_align_inset) + np.argmax(sums[0])) + ", " + str((cs.img_y - cs.auto_align_inset) + np.argmax(sums[1]))
    print(filename + " BR: " + str(sums[0, np.argmax(sums[0])]) + ", " + str(sums[1, np.argmax(sums[1])]))

    # Find top left corner
    sums = np.zeros((2, cs.auto_align_inset))
    test = np.zeros((cs.auto_align_inset, cs.auto_align_inset))
    for x in range(0, cs.auto_align_inset):
        for y in range(0, cs.auto_align_inset):
            value = img[x, y]
            sums[0, x] += value
            sums[1, y] += value
            test[x, y] = value
    top_left = str(np.argmax(sums[0])) + ", " + str(np.argmax(sums[1]))
    print(filename + " TL: " + str(sums[0, np.argmax(sums[0])]) + ", " + str(sums[1, np.argmax(sums[1])]))

    # Find top right corner
    sums = np.zeros((2, cs.auto_align_inset))
    test = np.zeros((cs.auto_align_inset, cs.auto_align_inset))
    for x in range(0, cs.auto_align_inset):
        for y in range(0, cs.auto_align_inset):
            value = img[x + (cs.img_x - cs.auto_align_inset), y]
            sums[0, x] += value
            sums[1, y] += value
            test[x, y] = value
    top_right = str((cs.img_x - cs.auto_align_inset) + np.argmax(sums[0])) + ", " + str(np.argmax(sums[1]))
    print(filename + " TR: " + str(sums[0, np.argmax(sums[0])]) + ", " + str(sums[1, np.argmax(sums[1])]))

    f = open(text_file, "w")
    if metadata[2] not in cs.flipped_images:
        f.write("\n".join([bottom_left, bottom_right, top_left]))
    else:
        f.write("\n".join([top_right, top_left, bottom_right]))
    f.close()
