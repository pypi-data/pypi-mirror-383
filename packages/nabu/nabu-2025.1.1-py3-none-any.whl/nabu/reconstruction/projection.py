import numpy as np
import pycuda.driver as cuda
import pycuda.gpuarray as garray
from ..utils import updiv, get_cuda_srcfile
from ..cuda.utils import copy_array
from ..cuda.kernel import CudaKernel
from ..cuda.processing import CudaProcessing

_sizeof_float32 = np.dtype(np.float32).itemsize


class Projector:
    """
    A class for performing a tomographic projection (Radon Transform) using Cuda.
    """

    _projector_name = "joseph_projector"
    _projector_signature = "PiiPfPPPPiiifii"

    def __init__(
        self,
        slice_shape,
        angles,
        rot_center=None,
        detector_width=None,
        normalize=False,
        extra_options=None,
        cuda_options=None,
    ):
        """
        Initialize a Cuda tomography forward projector.

        Parameters
        -----------
        slice_shape: tuple
            Shape of the slice: (num_rows, num_columns).
        angles: int or sequence
            Either an integer number of angles, or a list of custom angles values in radian.
        param rot_center: float, optional
            Rotation axis position. Default is `(shape[1]-1)/2.0`.
        detector_width: int, optional
            Detector width in pixels.
            If `detector_width > slice_shape[1]`, the  projection data will be surrounded with zeros.
            Using `detector_width < slice_shape[1]` might result in a local tomography setup.
        normalize: bool, optional
            Whether to normalize projection.
            If set to True, sinograms are multiplied by the factor pi/(2*nprojs).
        extra_options: dict, optional
            Current allowed options:
                offset_x, axis_corrections
        cuda_options: dict, optional
            Cuda options passed to the CudaProcessing class.
        """
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        self._configure_extra_options(extra_options)
        self._init_geometry(slice_shape, rot_center, angles, detector_width)
        self.normalize = normalize
        self._allocate_memory()
        self._compute_angles()
        self._proj_precomputations()
        self._compile_kernels()

    def _configure_extra_options(self, extra_options):
        self.extra_options = {
            "offset_x": None,
            "axis_corrections": None,  # TODO
        }
        extra_opts = extra_options or {}
        self.extra_options.update(extra_opts)

    def _init_geometry(self, slice_shape, rot_center, angles, detector_width):
        if np.isscalar(slice_shape):
            slice_shape = (slice_shape, slice_shape)
        self.shape = slice_shape
        if np.isscalar(angles):
            angles = np.linspace(0, np.pi, angles, endpoint=False, dtype="f")
        self.angles = angles
        self.nprojs = len(angles)
        self.dwidth = detector_width or self.shape[1]
        self.sino_shape = (self.nprojs, self.dwidth)

        # In PYHST (c_hst_project_1over.cu), axis_pos is overwritten to (dimslice-1)/2.
        # So tuning axis position is done in another way. In CCspace.c:
        # offset_x = start_x - move_x
        # start_x = start_voxel_1 (zero-based, so 0 by default)
        # MOVE_X = start_x + (num_x - 1)/2 -  ROTATION_AXIS_POSITION;
        self.axis_pos = self.rot_center = rot_center or (self.shape[1] - 1) / 2.0
        self.offset_x = self.extra_options["offset_x"] or np.float32(self.axis_pos - (self.shape[1] - 1) / 2.0)
        self.axis_pos0 = np.float32((self.shape[1] - 1) / 2.0)

    def _allocate_memory(self):
        self.dimgrid_x = updiv(self.dwidth, 16)
        self.dimgrid_y = updiv(self.nprojs, 16)
        self._dimrecx = self.dimgrid_x * 16
        self._dimrecy = self.dimgrid_y * 16
        self.d_sino = garray.zeros((self._dimrecy, self._dimrecx), np.float32)
        self.d_angles = garray.zeros((self._dimrecy,), np.float32)
        self._d_beginPos = garray.zeros((2, self._dimrecy), np.int32)
        self._d_strideJoseph = garray.zeros((2, self._dimrecy), np.int32)
        self._d_strideLine = garray.zeros((2, self._dimrecy), np.int32)
        self.d_axis_corrections = garray.zeros((self.nprojs,), np.float32)
        if self.extra_options.get("axis_corrections", None) is not None:
            self.d_axis_corrections.set(self.extra_options["axis_corrections"])

        # Textures
        self.d_image_cua = cuda.np_to_array(np.zeros((self.shape[0] + 2, self.shape[1] + 2), "f"), "C")

    def _compile_kernels(self):
        self.gpu_projector = CudaKernel(
            self._projector_name,
            filename=get_cuda_srcfile("proj.cu"),
        )
        self.texref_slice = self.gpu_projector.module.get_texref("texSlice")
        self.texref_slice.set_array(self.d_image_cua)
        self.texref_slice.set_filter_mode(cuda.filter_mode.LINEAR)
        self.gpu_projector.prepare(self._projector_signature, [self.texref_slice])

        self.kernel_args = (
            self.d_sino.gpudata,
            np.int32(self.shape[1]),
            np.int32(self.dwidth),
            self.d_angles.gpudata,
            np.float32(self.axis_pos0),
            self.d_axis_corrections.gpudata,
            self._d_beginPos.gpudata,
            self._d_strideJoseph.gpudata,
            self._d_strideLine.gpudata,
            np.int32(self.nprojs),
            np.int32(self._dimrecx),
            np.int32(self._dimrecy),
            self.offset_x,
            np.int32(1),  # josephnoclip, 1 by default
            np.int32(self.normalize),
        )
        self._proj_kernel_blk = (16, 16, 1)
        self._proj_kernel_grd = (self.dimgrid_x, self.dimgrid_y, 1)

    def _compute_angles(self):
        angles2 = np.zeros(self._dimrecy, dtype=np.float32)  # dimrecy != num_projs
        angles2[: self.nprojs] = np.copy(self.angles)
        angles2[self.nprojs :] = angles2[self.nprojs - 1]
        self.angles2 = angles2
        self.d_angles[:] = angles2[:]

    def _proj_precomputations(self):
        beginPos = np.zeros((2, self._dimrecy), dtype=np.int32)
        strideJoseph = np.zeros((2, self._dimrecy), dtype=np.int32)
        strideLine = np.zeros((2, self._dimrecy), dtype=np.int32)
        cos_angles = np.cos(self.angles2)
        sin_angles = np.sin(self.angles2)
        dimslice = self.shape[1]

        M1 = np.abs(cos_angles) > 0.70710678
        M1b = np.logical_not(M1)
        M2 = cos_angles > 0
        M2b = np.logical_not(M2)
        M3 = sin_angles > 0
        M3b = np.logical_not(M3)
        case1 = M1 * M2
        case2 = M1 * M2b
        case3 = M1b * M3
        case4 = M1b * M3b

        beginPos[:, case1] = 0
        strideJoseph[0][case1] = 1
        strideJoseph[1][case1] = 0
        strideLine[0][case1] = 0
        strideLine[1][case1] = 1

        beginPos[:, case2] = dimslice - 1
        strideJoseph[0][case2] = -1
        strideJoseph[1][case2] = 0
        strideLine[0][case2] = 0
        strideLine[1][case2] = -1

        beginPos[0][case3] = dimslice - 1
        beginPos[1][case3] = 0
        strideJoseph[0][case3] = 0
        strideJoseph[1][case3] = 1
        strideLine[0][case3] = -1
        strideLine[1][case3] = 0

        beginPos[0][case4] = 0
        beginPos[1][case4] = dimslice - 1
        strideJoseph[0][case4] = 0
        strideJoseph[1][case4] = -1
        strideLine[0][case4] = 1
        strideLine[1][case4] = 0

        self._d_beginPos.set(beginPos)
        self._d_strideJoseph.set(strideJoseph)
        self._d_strideLine.set(strideLine)

    def _check_input_array(self, image):
        if image.shape != self.shape:
            raise ValueError("Expected slice shape = %s, got %s" % (str(self.shape), str(image.shape)))
        if image.dtype != np.dtype("f"):
            raise ValueError("Expected float32 data type, got %s" % str(image.dtype))
        if not isinstance(image, (np.ndarray, garray.GPUArray)):
            raise TypeError("Expected either numpy.ndarray or pyopencl.array.Array")
        if isinstance(image, np.ndarray) and not image.flags["C_CONTIGUOUS"]:
            raise ValueError("Please use C-contiguous arrays")

    def set_image(self, image, check=True):
        if check:
            self._check_input_array(image)
        copy_array(
            self.d_image_cua,
            image,
            dst_x_in_bytes=_sizeof_float32,
            dst_y=1,
            check=False,  # cannot check when using offsets
        )

    def projection(self, image, output=None, do_checks=True):
        """
        Perform the projection of an image.

        Parameters
        -----------
        image: array
            Image to forward project
        output: array, optional
            Output image
        """

        self.set_image(image, check=do_checks)
        self.gpu_projector(*self.kernel_args, grid=self._proj_kernel_grd, block=self._proj_kernel_blk)

        if output is None:
            res = self.d_sino.get()
            res = res[: self.nprojs, : self.dwidth]  # copy ?
        else:
            output[:, :] = self.d_sino[: self.nprojs, : self.dwidth]
            res = output
        return res

    __call__ = projection
