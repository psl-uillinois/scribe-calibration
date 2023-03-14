import math
import os

# Folder must match that of gen_fab.m
source_folder = 'source_gwl'

# These folders will become subfolders of the source folder
array_source_subfolder = 'array'
device_source_subfolder = 'device'

# Set film parameters
# Units: micron
film_thickness = 20
film_thickness_adj = -0.5
oxidized = True

# Set default array parameters
# Units: micron
x_array_default = 1
y_array_default = 1

# Set cell size for master file
x_cell_size = 150
y_cell_size = 150

# Set parameters for local alignment marks
cross_size = 50
if not oxidized:
    cross_lp = 20
else:
    cross_lp = 40
cross_width = 1
cross_res = 0.1

# Set fabrication text parameters
text_size_unit = 12

# Allows program to automatically determine optimal position for arrays
compact_grid = False
# This option only matters if compact_grid is disabled. It sets a fixed width of the master file, or -1 for automatic
fixed_grid_width = 12
maximum_height = -1

# Separate filenames by semicolon (;), or use "all" for all devices in directory
device_filenames = 'all'

# Output filenames
master_filename = 'MasterFile.gwl'
backup_filename = 'BackupMasterFile.gwl'
csv_filename = 'MasterCoords.csv'
backup_csv_filename = 'BackupCoords.csv'

# Begin of actual program


# Default beginning content for GWL master file
# This sets some necessary parameters for writing using our system.
def make_beginning(f, ox, height, actual_height, size_x, size_y):
    if ox:
        f.write('''% Size: ''' + str(size_x) + ', ' + str(size_y) + '''\n\
InvertZAxis 1\nGalvoScanMode\nContinuousMode\nPiezoSettlingTime 5\nGalvoAcceleration 1\n\
StageVelocity 200\nXOffset 0\nYOffset 0\nZOffset 0\nPowerScaling 1.0\nScanSpeed 10000\n
TextLaserPower 20\nvar $height = ''' + str(height) +
                '''\n\
FindInterfaceAt 0\nRecalibrate\n\n\
''')
    else:
        f.write('''% Size: ''' + str(size_x) + ', ' + str(size_y) + '''\n\
InvertZAxis 1\nGalvoScanMode\nContinuousMode\nPiezoSettlingTime 5\nGalvoAcceleration 1\n\
StageVelocity 200\nXOffset 0\nYOffset 0\nZOffset 0\nPowerScaling 1.0\nScanSpeed 10000\n
TextLaserPower 20\nvar $height = ''' + str(height) +
                '''\n\
FindInterfaceAt ''' + str(actual_height) + '''\nRecalibrate\n\n\
''')


# Initializes variables needed to use stage movement API
def init_move_to(f):
    f.curr_x = 0
    f.curr_y = 0


# Moves the stage to a specific x,y location using MoveStage commands
def move_to(f, x, y):
    if x != f.curr_x:
        f.write('MoveStageX ' + str(x - f.curr_x) + '\n')
    if y != f.curr_y:
        f.write('MoveStageY ' + str(y - f.curr_y) + '\n')
    f.curr_x = x
    f.curr_y = y


# Moves the stage by a certain x,y shift using MoveStage commands
def move_by(f, x, y):
    if x != 0:
        f.write('MoveStageX ' + str(x) + '\n')
    if y != 0:
        f.write('MoveStageY ' + str(y) + '\n')
    f.curr_x = f.curr_x + x
    f.curr_y = f.curr_y + y


# Generates an alignment marker at either the top left or bottom right of a cell
def make_cross(f, top_left):
    # Write vertical lines
    for x in range(0, int(cross_width / cross_res)):
        if top_left:
            f_array.write(str(x * cross_res + cross_res / 2) + ' 0 0 ' + str(cross_lp) + '\n')
            f_array.write(str(x * cross_res + cross_res / 2) + ' ' + str(-cross_size) + ' 0 ' + str(cross_lp) + '\n')
        else:
            f_array.write(str(-x * cross_res - cross_res / 2) + ' 0 0 ' + str(cross_lp) + '\n')
            f_array.write(str(-x * cross_res - cross_res / 2) + ' ' + str(cross_size) + ' 0 ' + str(cross_lp) + '\n')
        f_array.write('Write\n')

    # Write horizontal lines
    for y in range(0, int(cross_width / cross_res)):
        if top_left:
            f_array.write(str(cross_width + cross_res / 2) + ' ' + str(-y * cross_res - cross_res / 2) + ' 0 ' + str(cross_lp) + '\n')
            f_array.write(str(cross_size) + ' ' + str(-y * cross_res - cross_res / 2) + ' 0 ' + str(cross_lp) + '\n')
        else:
            f_array.write(str(-cross_width - cross_res / 2) + ' ' + str(y * cross_res + cross_res / 2) + ' 0 ' + str(cross_lp) + '\n')
            f_array.write(str(-cross_size) + ' ' + str(y * cross_res + cross_res / 2) + ' 0 ' + str(cross_lp) + '\n')
        f_array.write('Write\n')


# Make sure sub-folders exist
array_source_folder = os.path.join(source_folder, array_source_subfolder)
device_folder = os.path.join(source_folder, device_source_subfolder)
try:
    os.mkdir(array_source_folder)
except FileExistsError:
    pass
try:
    os.mkdir(device_folder)
except FileExistsError:
    pass

# Extract actual device filenames
if device_filenames == 'all':
    device_filenames = [f for f in os.listdir(device_folder) if os.path.isfile(os.path.join(device_folder, f))]
    device_filenames.sort()
else:
    device_filenames = device_filenames.split(';')

# Initialize device metadata storage
device_locations = []
array_cell_sizes = []

# Generate array files from device files
for device_filename in device_filenames:
    f_device = open(os.path.join(device_folder, device_filename), 'r')

    # Extract metadata from device files
    line = f_device.readline()
    if line.startswith('%'):
        # Retrieve individual device size
        device_sizes = [float(x.strip()) for x in line.replace('%', '').split(',')]
    else:
        print('Error: ' + os.path.join(device_folder, device_filename) + ' missing metadata at beginning of file')
        exit(1)

    # Retrieve array size
    line = f_device.readline()
    array_quantities = [1, 1]
    array_metadata_present = False
    if line.startswith('%'):
        array_quantities = [int(x.strip()) for x in line[1:].split(',')]

        # Setup line for comment reading
        line = f_device.readline()
    else:
        array_quantities = [x_array_default, y_array_default]

    # Check for comments
    filename_comment = (device_filename.split('.')[0]  # Remove extension
                        .split('__')[0]  # Remove parameters
                        .replace('_', ' '))  # Use spaces instead of underscores
    comments = [[filename_comment]]
    while line.startswith('%'):
        comment = line[1:].strip()
        if comment != '':
            comments.append(comment.split(', '))
        line = f_device.readline()
    comments = sum(comments, [])  # Flatten list

    f_device.close()

    # Determine text bounds
    x_text_size = text_size_unit * max([len(x) for x in comments])
    y_text_size = text_size_unit * len(comments)

    # Retrieve individual device size
    x_device_size = device_sizes[0]
    y_device_size = device_sizes[1]

    # Retrieve array amount
    x_array_quantity = array_quantities[0]
    y_array_quantity = array_quantities[1]

    # Calculate array spatial dimensions
    x_array_size = x_device_size * x_array_quantity + cross_width * 2
    y_array_size = y_device_size * y_array_quantity + cross_width * 2 + y_text_size

    if math.ceil(x_array_size / x_cell_size) < math.ceil(x_text_size / x_cell_size):
        print('Warning: ' + os.path.join(device_folder, device_filename) + ' has text extending beyond cell bounds')
    if x_array_size < x_text_size:
        x_array_size = x_text_size

    # Calculate cell sizes
    x_cells = math.ceil(x_array_size / x_cell_size)
    y_cells = math.ceil(y_array_size / y_cell_size)
    array_cells = [x_cells, y_cells]

    # Begin generating array file
    f_array = open(os.path.join(array_source_folder, device_filename), 'w')
    f_array.write('MessageOut "Beginning ' + device_filename + '"\n')
    init_move_to(f_array)

    # Move to top left edge and generate alignment marker
    x_edge = -x_cell_size * x_cells / 2
    y_edge = y_cell_size * y_cells / 2
    move_to(f_array, x_edge, y_edge)
    make_cross(f_array, top_left=True)

    f_array.write('\n')

    # Move to each device and fabricate it
    device_location = []
    x_start = x_device_size / 2 - x_cell_size * x_cells / 2 + cross_width
    y_start = -y_device_size / 2 + y_cell_size * y_cells / 2 - cross_width
    for y in range(0, y_array_quantity):
        for x in range(0, x_array_quantity):
            move_to(f_array, x * x_device_size + x_start, -y * y_device_size + y_start)
            f_array.write('include ' + os.path.join('..', device_source_subfolder, device_filename) + '\n')
            device_location.append([x * x_device_size + x_start, -y * y_device_size + y_start])

    f_array.write('\n')

    # Move to text location and write it
    x_text_start = x_edge + cross_width + text_size_unit
    y_text_start = y_edge - (y + 1) * y_device_size - cross_width - text_size_unit
    move_to(f_array, x_text_start, y_text_start)
    f_array.write('\nTextFontSize 8\nTextLaserPower 20\nTextPositionX 0\nTextPositionY 0\n')
    # Write subsequent lines if available
    for i in range(0, len(comments)):
        f_array.write('WriteText "' + comments[i] + '"\n')
        if i < len(comments) - 1:
            move_by(f_array, 0, -text_size_unit)
        else:
            f_array.write('\n')

    # Write bottom right alignment mark
    move_to(f_array, -x_edge, -y_edge)
    make_cross(f_array, top_left=False)

    # Return to center of the array for purposes of the master file
    move_to(f_array, 0, 0)

    f_array.write('MessageOut "Finished ' + device_filename + '"\n')

    f_array.close()

    # Add metadata to array
    device_locations.append(device_location)
    array_cell_sizes.append(array_cells)

# Perform calculations to aid organizing arrays in master file
array_cell_areas = [dimensions[0] * dimensions[1] for dimensions in array_cell_sizes]

# Initialize variables to store the results of array organization
cells = [x[:] for x in [[False] * sum([dimensions[1] for dimensions in array_cell_sizes])]
         * sum([dimensions[0] for dimensions in array_cell_sizes])]

array_locations = [x[:] for x in ([[0, 0]] * len(device_filenames))]
writing_order = []

x_master = 0
y_master = 0

if compact_grid:  # Arrange cells in most space-efficient arrangement
    while True:
        # Pick arrays in order of largest area first
        i = array_cell_areas.index(max(array_cell_areas))
        if array_cell_areas[i] == 0:  # All arrays have been placed
            break
        # Remove the current array from future placing consideration
        array_cell_areas[i] = 0

        # Collect variables on how to place the array
        x_size = array_cell_sizes[i][0]
        y_size = array_cell_sizes[i][1]
        x = 0
        y = 0
        placed = False
        ideal_location = []
        ideal_increase = 0
        while True:
            # Iterate through possible locations to place array
            # Note: This searches on a series of lines, each getting further away from the center
            placeable = True
            for xi in range(0, x_size):
                for yi in range(0, y_size):
                    if cells[xi + x][yi + y] or (maximum_height != -1 and (y + yi) > maximum_height):
                        placeable = False
            increase = max((x + x_size) - x_master, 0) + max((y + y_size) - y_master, 0)
            if placeable and (not placed or increase < ideal_increase):
                ideal_location = [x, y]
                ideal_increase = increase
                placed = True
            if x == y:  # Need to search further out
                x = y + 1
                y = 0
                if placed:
                    break
            elif y == x - 1:  # Begin searching horizontally
                y = y + 1
                x = 0
            elif x >= y:  # Continue searching vertically
                y = y + 1
            else:  # Continue searching horizontally
                x = x + 1

        # Place the array in the best location found
        x = ideal_location[0]
        y = ideal_location[1]
        array_locations[i][0] = x
        array_locations[i][1] = y
        x_master = max(x + x_size, x_master)
        y_master = max(y + y_size, y_master)
        for xi in range(0, x_size):
            for yi in range(0, y_size):
                cells[xi + x][yi + y] = True

    # Raster left to right, top to bottom
    while len(writing_order) < len(device_filenames):
        next_write = -1
        x = 0
        y = 0
        for i in range(0, len(device_filenames)):
            if i in writing_order:
                continue
            if (next_write == -1 or
                    array_locations[i][0] < x or
                    (array_locations[i][0] == x and (array_locations[i][1] < y))):
                next_write = i
                x = array_locations[i][0]
                y = array_locations[i][1]
        writing_order.append(next_write)

else:  # Perform packing in sequential arrangement, left-to-right, top-to-bottom
    x_max = math.ceil(math.sqrt(sum(array_cell_areas)))
    if fixed_grid_width != -1:  # Use the sqrt of the area to determine width, if not already provided by user
        x_max = fixed_grid_width
    x = 0
    y = 0
    # Place in the order provided by the user (or alphabetically, if none provided)
    for i in range(0, len(device_filenames)):
        if x + array_cell_sizes[i][0] > x_max:
            x = 0
            y = y_master
        x_master = max(x + array_cell_sizes[i][0], x_master)
        y_master = max(y + array_cell_sizes[i][1], y_master)
        array_locations[i][0] = x
        array_locations[i][1] = y
        x = x + array_cell_sizes[i][0]
    writing_order = [x for x in range(0, len(device_filenames))]


# Open file resources
f_master = open(os.path.join(source_folder, master_filename), 'w')
f_backup = open(os.path.join(source_folder, backup_filename), 'w')
f_csv = open(os.path.join(source_folder, csv_filename), 'w')
f_csv_bck = open(os.path.join(source_folder, backup_csv_filename), 'w')

# Setup files for writing
make_beginning(f_master, oxidized, film_thickness + film_thickness_adj, film_thickness, x_master * x_cell_size, y_master * y_cell_size)
make_beginning(f_backup, oxidized, film_thickness + film_thickness_adj, film_thickness, x_master * x_cell_size, y_master * y_cell_size)
init_move_to(f_master)
init_move_to(f_backup)
f_master.write('ZOffset ' + str(film_thickness + film_thickness_adj) + '\n'
               + 'TextPositionZ ' + str(film_thickness + film_thickness_adj) + '\n\n')
f_backup.write('ZOffset ' + str(film_thickness + film_thickness_adj) + '\n'
               + 'TextPositionZ ' + str(film_thickness + film_thickness_adj) + '\n\n')

# Calculate starting offsets
x_start = (-x_master * x_cell_size) / 2
y_start = (y_master * y_cell_size) / 2
for order in range(0, len(writing_order)):
    # Retrieve information about specific array
    i = writing_order[order]
    device_filename = device_filenames[i]
    x_cell_quantity = array_locations[i][0]
    y_cell_quantity = array_locations[i][1]

    # Move to the center of the array and write it
    x = (x_cell_quantity + array_cell_sizes[i][0] / 2) * x_cell_size + x_start
    y = -(y_cell_quantity + array_cell_sizes[i][1] / 2) * y_cell_size + y_start

    move_to(f_master, x, y)
    f_master.write('include ' + os.path.join(array_source_subfolder, device_filename) + '\n')

    # Write to the backup file exactly one master file below the original array
    f_backup.write('%StageGotoX ' + str(x) +
                   '\n%StageGotoY ' + str(y - y_master * y_cell_size) + '\n')
    f_backup.write('%include ' + os.path.join(array_source_subfolder, device_filename) + '\n\n')

    # Write coordinates to the csv file
    for j in range(0, len(device_locations[i])):
        loc = device_locations[i][j]
        f_csv.write(device_filename.split('.')[0] + '__' + str(j) + ',' + str(loc[0] + x) + ',' + str(loc[1] + y)
                    + '\n')
        f_csv_bck.write(device_filename.split('.')[0] + '__' + str(j) + ',' + str(loc[0] + x) + ',' + str(loc[1] + y - y_master * y_cell_size)
                    + '\n')

move_to(f_master, 0, 0)
# Free up all remaining resources
f_master.close()
f_backup.close()
f_csv.close()