from ..processing.fftshift import *  # noqa: F403
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.misc.fftshift has been moved to nabu.processing.fftshift", do_print=True, func_name="fftshift"
)
