from __future__ import annotations

import importlib
from typing import get_args, get_origin


def has_dict_with_nonstr_keys(ann):
    origin = get_origin(ann)
    args = get_args(ann)

    if origin is None or len(args) == 0:
        return False
    if origin is dict and args[0] is not str:
        return True
    return any(has_dict_with_nonstr_keys(arg) for arg in args)
