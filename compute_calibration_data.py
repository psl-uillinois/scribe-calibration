from os import listdir
from os.path import isfile, join, exists
from PIL import Image
import numpy as np
import os
from multiprocessing import Pool, freeze_support, cpu_count
import matplotlib.pyplot as plt
import calibration_settings as cs

# Converts between 2D datapoints and 3D datapoints (padded with a third column of ones)
pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
unpad = lambda x: x[:, :-1]

alignment_physical_loc = pad(cs.alignment_physical_loc)


def load_aligment_loc(text_file):
    alignment_file = open(text_file, mode="r")
    alignment_pixel_loc = alignment_file.read()
    alignment_file.close()
    alignment_pixel_loc = [int(x) for x in
                           "".join(filter(lambda x: x.isdigit() or x == "\n" or x == ",", alignment_pixel_loc))
                             .replace("\n", ",").split(",")]

    alignment_pixel_loc = np.array([[alignment_pixel_loc[0], alignment_pixel_loc[1]],
                                    [alignment_pixel_loc[2], alignment_pixel_loc[3]],
                                    [alignment_pixel_loc[4], alignment_pixel_loc[5]]])

    alignment_pixel_loc = pad(alignment_pixel_loc)

    return alignment_pixel_loc


def get_binned_data(img, array_size, transform):
    sums = np.zeros((array_size, array_size))
    count = np.zeros((array_size, array_size))
    avg = np.zeros((array_size, array_size))
    for x in range(0, cs.img_x):
        for y in range(0, cs.img_y):
            original_loc = [x, y]
            loc = transform(np.array([original_loc]))

            # Check that physical location is within bounds
            if not ((loc[0][0] > -cs.correction_size / 2 - cs.box_size / 2) and
                    (loc[0][0] < cs.correction_size / 2 + cs.box_size / 2) and
                    (loc[0][1] > -cs.correction_size / 2 - cs.box_size / 2) and
                    (loc[0][1] < cs.correction_size / 2 + cs.box_size / 2)):
                continue

            # Fetch indices of final array location
            idx = [int(x) for x in
                   np.ndarray.tolist(((loc + cs.correction_size / 2 + cs.box_size / 2)
                                      // cs.box_size))[0]]

            # Add
            sums[idx[0], idx[1]] += img[original_loc[0], original_loc[1]]
            count[idx[0], idx[1]] += 1
    avg = sums / count

    return avg


def gen_calibration_file(filename):
    file_type = filename.split(".")[-1]
    if file_type != cs.raw_data_filetype:
        return

    text_file = join(cs.raw_data_dir, filename.split(".")[0] + "." + cs.alignment_data_filetype)
    save_file = join(cs.data_dir, filename.split(".")[0] + "." + cs.calibration_data_filetype)
    if not exists(text_file):
        return

    # Extract metadata in filename as integers
    metadata = [int(x) for x in "".join(filter(lambda x: x.isdigit() or x == "_", filename.split(".")[0])).split("_")]

    # Extract pixel data from filename
    # Transposed to allow indexing with [x, y] rather than [y, x]
    img = np.transpose(np.array(Image.open(join(cs.raw_data_dir, filename))))

    # Transform images into physical coordinate system
    alignment_pixel_loc = load_aligment_loc(text_file)

    A = np.linalg.solve(alignment_pixel_loc, alignment_physical_loc)
    transform = lambda x: unpad(np.dot(pad(x), A))

    array_size = int(cs.correction_size / cs.box_size) + 1

    # Bin data into locations
    avg = get_binned_data(img, array_size, transform)
    np.save(save_file, avg, allow_pickle=False)


if os.name == "nt":
    freeze_support()

if __name__ == '__main__':
    raw_calibration_filenames = [f for f in listdir(cs.raw_data_dir)
                                 if isfile(join(cs.raw_data_dir, f))]

    pool = Pool(cpu_count())
    pool.map(gen_calibration_file, raw_calibration_filenames)
    exit(0)