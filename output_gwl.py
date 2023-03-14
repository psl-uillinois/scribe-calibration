import calibration_settings as cs

from output_file import OutputFile


class GWL(OutputFile):
    def __init__(self, filename):
        self.f = open(filename, "w")
        self.last_point = None
        self.last_point_written = True
        self.last_lp_written = 0
        self.skip_duplicates = False

    def write_metadata(self, xsize, ysize, xarray, yarray, text, skip_duplicates):
        self.f.write(f"% {xsize}, {ysize}\n")
        self.f.write(f"% {xarray}, {yarray}\n")
        self.f.write(f"% {text}\n")
        self.skip_duplicates = skip_duplicates

    def write_beginning(self):
        self.f.write(cs.gwl_settings)
        self.f.write(f"MoveStageX -{cs.piezo_offset}\nMoveStageY -{cs.piezo_offset}\n")

    def write_end(self):
        self.f.write(f"MoveStageX {cs.piezo_offset}\nMoveStageY {cs.piezo_offset}\n")
        self.f.write(cs.gwl_settings)

    def close(self):
        self.f.close()

    def add_point_raw(self, x_out, y_out, z_out, lp):
            self.f.write(f"{x_out} {y_out} {z_out} {round(lp, 2)}\n")

    def add_point(self, x_out, y_out, z_out, lp):
        if x_out == int(x_out):
            x_out = int(x_out)
        else:
            x_out = round(x_out, 2)
        if y_out == int(y_out):
            y_out = int(y_out)
        else:
            y_out = round(y_out, 2)

        write_point = True
        if self.last_point is not None and self.skip_duplicates:
            step_change = abs(lp - self.last_lp_written) > 2
            if not step_change:
                write_point = False
            elif not self.last_point_written:
                self.add_point_raw(*self.last_point)
            if y_out == int(y_out):
                write_point = True

        if write_point:
            self.add_point_raw(x_out, y_out, z_out, lp)
            self.last_lp_written = lp
        self.last_point = [x_out, y_out, z_out, lp]
        self.last_point_written = write_point

    def write(self):
        if not self.last_point_written:
            self.add_point_raw(*self.last_point)
        self.last_point_written = True
        self.last_point = None
        self.last_lp_written = 0

        self.f.write("Write\n")

    def move_sample(self, x, y):
        self.f.write(f"PiezoGotoX {round(x + cs.piezo_offset, 3)}\n")
        self.f.write(f"PiezoGotoY {round(y + cs.piezo_offset, 3)}\n")

    def recalibrate(self):
        self.f.write("Recalibrate\n")