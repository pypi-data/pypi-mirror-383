import warnings

from smml.dataset import *

warnings.warn(
    f"{__file__} is deprecated and will be removed in future versions. Use `smml.dataset` instead.",
    DeprecationWarning,
    stacklevel=2,
)
