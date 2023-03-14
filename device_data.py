from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Device:
    custom_name: str = ""
    custom_text: str = ""
    custom_text_inner: str = ""
    custom_file: bool = False
    single_target_intensity: int = 0
    target_intensity: np.array = None
    prism: bool = False
    enable_calibration: bool = False
    enable_piezo_correction: bool = False
    enable_time_correction: bool = False
    thickness: float = 0.0
    xsize: int = 0
    ysize: int = 0
    xarray: int = 1
    yarray: int = 1
    high_res_y: bool = False
