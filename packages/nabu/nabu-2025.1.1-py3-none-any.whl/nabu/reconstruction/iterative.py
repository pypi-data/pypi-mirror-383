import numpy as np


class IterativeBase:

    backend = None  # placeholder
    implementation = None  # placeholder

    default_extra_options = {
        "axis_correction": None,
        "centered_axis": False,
        "clip_outer_circle": False,
        "scale_factor": None,
        "outer_circle_value": 0.0,
    }

    backend_processing_class = ProcessingBase

    def __init__(
        self,
        sino_shape,
        angles=None,
        rot_center=None,
        halftomo=False,
        filter_name=None,
        slice_roi=None,
        scale_factor=None,
        extra_options=None,
        backend_options=None,
    ): ...
