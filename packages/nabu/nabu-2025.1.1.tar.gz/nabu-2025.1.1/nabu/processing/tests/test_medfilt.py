import pytest
import numpy as np
from silx.math.medianfilter import medfilt2d
from nabu.testutils import generate_tests_scenarios, get_data
from nabu.cuda.utils import get_cuda_context, __has_pycuda__

if __has_pycuda__:
    from nabu.processing.medfilt_cuda import MedianFilter
    import pycuda.gpuarray as garray


scenarios = generate_tests_scenarios(
    {
        "input_on_gpu": [False, True],
        "output_on_gpu": [False, True],
        "footprint": [(3, 3), (5, 5)],
        "mode": ["reflect", "nearest"],
        "batched_2d": [False, True],
    }
)


@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls
    cls.data = np.ascontiguousarray(get_data("brain_phantom.npz")["data"][::2, ::2][:-1, :])
    cls.tol = 1e-7
    cls.ctx = get_cuda_context(cleanup_at_exit=False)
    cls.allocate_numpy_arrays()
    cls.allocate_cuda_arrays()
    yield
    cls.ctx.pop()


@pytest.mark.skipif(not (__has_pycuda__), reason="Need Cuda/pycuda for this test")
@pytest.mark.usefixtures("bootstrap")
class TestMedianFilter:
    @classmethod
    def allocate_numpy_arrays(cls):
        cls.input = cls.data
        cls.input3d = np.tile(cls.input, (2, 1, 1))

    @classmethod
    def allocate_cuda_arrays(cls):
        cls.d_input = garray.to_gpu(cls.input)
        cls.d_output = garray.zeros_like(cls.d_input)
        cls.d_input3d = garray.to_gpu(cls.input3d)
        cls.d_output3d = garray.zeros_like(cls.d_input3d)

    # parametrize on a class method will use the same class, and launch this
    # method with different scenarios.
    @pytest.mark.parametrize("config", scenarios)
    def testMedfilt(self, config):
        if config["input_on_gpu"]:
            input_data = self.d_input if not (config["batched_2d"]) else self.d_input3d
        else:
            input_data = self.input if not (config["batched_2d"]) else self.input3d
        if config["output_on_gpu"]:
            output_data = self.d_output if not (config["batched_2d"]) else self.d_output3d
        else:
            output_data = None
        # Cuda median filter
        medfilt = MedianFilter(
            input_data.shape,
            footprint=config["footprint"],
            mode=config["mode"],
            cuda_options={"ctx": self.ctx},
        )
        res = medfilt.medfilt2(input_data, output=output_data)
        if config["output_on_gpu"]:
            res = res.get()
        # Reference (scipy)
        ref = medfilt2d(self.input, config["footprint"][0], mode=config["mode"])
        max_absolute_error = np.max(np.abs(res - ref))
        assert max_absolute_error < self.tol, "Something wrong with configuration %s" % str(config)
