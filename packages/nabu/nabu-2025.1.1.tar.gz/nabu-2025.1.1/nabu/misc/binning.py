import numpy as np
from ..utils import deprecated


def binning(img, bin_factor, out_dtype=np.float32):
    """
    Bin an image by a factor of "bin_factor".

    Parameters
    ----------
    bin_factor: tuple of int
        Binning factor in each axis.
    out_dtype: dtype, optional
        Output data type. Default is float32.

    Notes
    -----
    If the image original size is not a multiple of the binning factor,
    the last items (in the considered axis) will be dropped.
    The resulting shape is (img.shape[0] // bin_factor[0], img.shape[1] // bin_factor[1])
    """
    s = img.shape
    n0, n1 = bin_factor
    shp = (s[0] - (s[0] % n0), s[1] - (s[1] % n1))
    sub_img = img[: shp[0], : shp[1]]
    out_shp = (shp[0] // n0, shp[1] // n1)
    res = np.zeros(out_shp, dtype=out_dtype)
    for i in range(n0):
        for j in range(n1):
            res[:] += sub_img[i::n0, j::n1]
    res /= n0 * n1
    return res


def binning_n_alt(img, bin_factor, out_dtype=np.float32):
    """
    Alternate, "clever" but slower implementation
    """
    n0, n1 = bin_factor
    new_shape = tuple(s - (s % n) for s, n in zip(img.shape, bin_factor))
    sub_img = img[: new_shape[0], : new_shape[1]]
    img_view_4d = sub_img.reshape((new_shape[0] // n0, n0, new_shape[1] // n1, n1))
    return img_view_4d.astype(out_dtype).mean(axis=1).mean(axis=-1)


#
# COMPAT.
#


@deprecated("Please use binning()", do_print=True)
def binning2(img, out_dtype=np.float32):
    return binning(img, (2, 2), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def binning2_horiz(img, out_dtype=np.float32):
    return binning(img, (1, 2), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def binning2_vertic(img, out_dtype=np.float32):
    return binning(img, (2, 1), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def binning3(img, out_dtype=np.float32):
    return binning(img, (3, 3), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def binning3_horiz(img, out_dtype=np.float32):
    return binning(img, (1, 3), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def binning3_vertic(img, out_dtype=np.float32):
    return binning(img, (3, 1), out_dtype=out_dtype)


@deprecated("Please use binning()", do_print=True)
def get_binning_function(binning_factor):
    """
    Determine the binning function to use.
    """
    binning_functions = {
        (2, 2): binning2,
        (2, 1): binning2_vertic,
        (1, 2): binning2_horiz,
        (3, 3): binning3,
        (3, 1): binning3_vertic,
        (1, 3): binning3_horiz,
        (2, 3): None,  # was a limitation
        (3, 2): None,  # was a limitation
    }
    if binning_factor not in binning_functions:
        raise ValueError("Could not get a function for binning factor %s" % binning_factor)
    return binning_functions[binning_factor]
