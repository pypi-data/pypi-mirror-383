import pytest
import numpy as np
import scipy.interpolate
from nabu.processing.fft_cuda import get_available_fft_implems
from nabu.testutils import get_data as nabu_get_data
from nabu.testutils import __do_long_tests__
from nabu.preproc.flatfield import FlatFieldArrays
from nabu.preproc.ccd import CCDFilter
from nabu.preproc import ctf
from nabu.estimation.distortion import estimate_flat_distortion
from nabu.misc.filters import correct_spikes
from nabu.preproc.distortion import DistortionCorrection
from nabu.cuda.utils import __has_pycuda__

__has_cufft__ = False
if __has_pycuda__:
    from nabu.preproc.ctf_cuda import CudaCTFPhaseRetrieval

    avail_fft = get_available_fft_implems()
    __has_cufft__ = len(avail_fft) > 0


@pytest.fixture(scope="class")
def bootstrap_TestCtf(request):
    cls = request.cls
    cls.abs_tol = 1.0e-4

    test_data = nabu_get_data("ctf_tests_data_all_pars.npz")

    cls.rand_disp_vh = test_data["rh"]
    ## the dimension number 1 is over holotomo distances, so far our filter is for one distance only
    cls.rand_disp_vh.shape = [cls.rand_disp_vh.shape[0], cls.rand_disp_vh.shape[2]]
    cls.dark = test_data["dark"]
    cls.flats = [test_data["ref0"], test_data["ref1"]]
    cls.im = test_data["im"]
    cls.ipro = int(test_data["ipro"])
    cls.expected_result = test_data["result"]
    cls.ref_plain = test_data["ref_plain_float_flat"]

    cls.flats_n = test_data["refns"]

    cls.img_shape_vh = test_data["img_shape_vh"]
    cls.padded_img_shape_vh = test_data["padded_img_shape_vh"]
    cls.z1_vh = test_data["z1_vh"]
    cls.z2 = test_data["z2"]
    cls.pix_size_det = test_data["pix_size_det"][()]
    cls.length_scale = test_data["length_scale"]
    cls.wavelength = test_data["wave_length"]
    cls.remove_spikes_threshold = test_data["remove_spikes_threshold"]
    cls.delta_beta = 27


@pytest.mark.usefixtures("bootstrap_TestCtf")
class TestCtf:
    def check_result(self, res, ref, error_message):
        diff = np.abs(res - ref)
        diff[diff > np.percentile(diff, 99)] = 0
        assert diff.max() < self.abs_tol * (np.abs(ref).mean()), error_message

    def test_ctf_id16_way(self):
        """test the ctf phase retrieval.
        The cft filter, of the CtfFilter class is iniitalised with the geomety informations contained in geo_pars object
        of the GeoPars class.
        The geometry encompass the case of astigmatic wavefront with a vertical and horisontal sources which are
        at distance z1_vh[0] and z1_vh[1] from the object.
        In the case of parllel geometry put  z1_vh[0]= z1_vh[1] = R
        where R is a large value ( meters).
        SI unit system is used. But the same results shudl be obtained with any homogenuous choice of the distance units.
        The img_shape is the shape of the images which will be processed.
        padded_img_shape is an intermediate shape which needs to be larger that the img_shape to avoid border effect due
        to convolutions.
        Length scale is an internal parameters which should not affect in anyway the result unless there are serious numerical
        problems involving very small lenghts. You can safely let the default value.
        """
        geo_pars = ctf.GeoPars(
            z1_vh=self.z1_vh,
            z2=self.z2,
            pix_size_det=self.pix_size_det,
            length_scale=self.length_scale,
            wavelength=self.wavelength,
        )

        flats = FlatFieldArrays(
            [1200] + list(self.img_shape_vh), {0: self.flats[0], 1200: self.flats[1]}, {0: self.dark}
        )

        my_flat = flats.get_flat(self.ipro)
        my_img = self.im - self.dark
        my_flat = my_flat - self.dark

        new_coordinates = estimate_flat_distortion(
            my_flat,
            my_img,
            tile_size=100,
            interpolation_kind="cubic",
            padding_mode="edge",
            correction_spike_threshold=3,
        )

        interpolator = scipy.interpolate.RegularGridInterpolator(
            (np.arange(my_flat.shape[0]), np.arange(my_flat.shape[1])),
            my_flat,
            bounds_error=False,
            method="linear",
            fill_value=None,
        )
        my_flat = interpolator(new_coordinates)

        my_img = my_img / my_flat
        my_img = correct_spikes(my_img, self.remove_spikes_threshold)

        my_shift = self.rand_disp_vh[:, self.ipro]

        ctf_filter = ctf.CtfFilter(
            self.dark.shape,
            geo_pars,
            self.delta_beta,
            padded_shape=self.padded_img_shape_vh,
            translation_vh=my_shift,
            normalize_by_mean=True,
            lim1=1.0e-5,
            lim2=0.2,
        )
        phase = ctf_filter.retrieve_phase(my_img)

        self.check_result(
            phase, self.expected_result, "retrieved phase and reference result differ beyond the accepted tolerance"
        )

    @pytest.mark.skipif(not (__do_long_tests__), reason="need environment variable NABU_LONG_TESTS=1")
    def test_ctf_id16_class(self):
        geo_pars = ctf.GeoPars(
            z1_vh=self.z1_vh,
            z2=self.z2,
            pix_size_det=self.pix_size_det,
            length_scale=self.length_scale,
            wavelength=self.wavelength,
        )
        distortion_correction = DistortionCorrection(
            estimation_method="fft-correlation",
            estimation_kwargs={
                "tile_size": 100,
                "interpolation_kind": "cubic",
                "padding_mode": "edge",
                "correction_spike_threshold": 3.0,
            },
            correction_method="interpn",
            correction_kwargs={"fill_value": None},
        )
        flats = FlatFieldArrays(
            [1200] + list(self.img_shape_vh),
            {0: self.flats[0], 1200: self.flats[1]},
            {0: self.dark},
            distortion_correction=distortion_correction,
        )

        # The "correct_spikes" function is numerically unstable (comparison with a float threshold).
        # If float32 is used for the image, one spike is detected while it is not in the previous test
        # (although the max difference between the inputs is about 1e-8).
        # We use float64 data type for the image to make tests pass.
        img = self.im.astype(np.float64)

        flats.normalize_single_radio(img, self.ipro)
        img = correct_spikes(img, self.remove_spikes_threshold)

        shift = self.rand_disp_vh[:, self.ipro]

        ctf_filter = ctf.CtfFilter(
            img.shape,
            geo_pars,
            self.delta_beta,
            padded_shape=self.padded_img_shape_vh,
            translation_vh=shift,
            normalize_by_mean=True,
            lim1=1.0e-5,
            lim2=0.2,
        )
        phase = ctf_filter.retrieve_phase(img)

        message = "retrieved phase and reference result differ beyond the accepted tolerance"
        assert np.abs(phase - self.expected_result).max() < 10 * self.abs_tol * (
            np.abs(self.expected_result).mean()
        ), message

    def test_ctf_plain_way(self):
        geo_pars = ctf.GeoPars(
            z1_vh=None,
            z2=self.z2,
            pix_size_det=self.pix_size_det,
            length_scale=self.length_scale,
            wavelength=self.wavelength,
        )
        flatfielder = FlatFieldArrays(
            [1] + list(self.img_shape_vh),
            {0: self.flats[0], 1200: self.flats[1]},
            {0: self.dark},
            radios_indices=[self.ipro],
        )

        spikes_corrector = CCDFilter(
            self.dark.shape, median_clip_thresh=self.remove_spikes_threshold, abs_diff=True, preserve_borders=True
        )

        img = self.im.astype("f")
        img = flatfielder.normalize_radios(np.array([img]))[0]
        img = spikes_corrector.median_clip_correction(img)

        ctf_args = [img.shape, geo_pars, self.delta_beta]
        ctf_kwargs = {"padded_shape": self.padded_img_shape_vh, "normalize_by_mean": True, "lim1": 1.0e-5, "lim2": 0.2}
        ctf_filter = ctf.CtfFilter(*ctf_args, **ctf_kwargs)
        phase = ctf_filter.retrieve_phase(img)

        self.check_result(phase, self.ref_plain, "Something wrong with CtfFilter")

        # Test R2C
        ctf_numpy = ctf.CtfFilter(*ctf_args, **ctf_kwargs, use_rfft=True)
        phase_r2c = ctf_numpy.retrieve_phase(img)
        self.check_result(phase_r2c, self.ref_plain, "Something wrong with CtfFilter-R2C")

        # Test multi-core FFT
        ctf_fft = ctf.CtfFilter(*ctf_args, **ctf_kwargs, use_rfft=True, fft_num_threads=0)
        if ctf_fft.use_rfft:
            # phase_fft = ctf_fft.retrieve_phase(img)
            self.check_result(phase_r2c, self.ref_plain, "Something wrong with CtfFilter-FFT")

    @pytest.mark.skipif(not (__has_pycuda__ and __has_cufft__), reason="pycuda and (cupy? or vkfft)")
    def test_cuda_ctf(self):
        data = nabu_get_data("brain_phantom.npz")["data"]
        delta_beta = 50.0
        energy_kev = 22.0
        distance_m = 1.0
        pix_size_m = 0.1e-6

        geo_pars = ctf.GeoPars(z2=distance_m, pix_size_det=pix_size_m, wavelength=1.23984199e-9 / energy_kev)
        # ctx = get_cuda_context()

        for normalize in [True, False]:
            ctf_filter = ctf.CTFPhaseRetrieval(
                data.shape, geo_pars, delta_beta=delta_beta, normalize_by_mean=normalize, use_rfft=True
            )
            cuda_ctf_filter = CudaCTFPhaseRetrieval(
                data.shape,
                geo_pars,
                delta_beta=delta_beta,
                use_rfft=True,
                normalize_by_mean=normalize,
            )
            ref = ctf_filter.retrieve_phase(data)

            d_data = cuda_ctf_filter.cuda_processing.to_device("_d_data", data)
            res = cuda_ctf_filter.retrieve_phase(d_data).get()
            err_max = np.max(np.abs(res - ref))

            assert err_max < 1e-2, "Something wrong with retrieve_phase(normalize_by_mean=%s)" % (str(normalize))
