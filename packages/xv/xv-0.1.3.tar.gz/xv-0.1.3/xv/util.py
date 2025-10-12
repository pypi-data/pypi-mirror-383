"""Utils"""

import os
from functools import partial, cached_property
from typing import Mapping, Callable, Optional, TypeVar, KT, Iterable, Any
from config2py import get_app_config_folder
from graze import (
    graze as _graze,
    Graze as _Graze,
    GrazeReturningFilepaths as _GrazeReturningFilepaths,
)

package_name = "xv"


MappingFactory = Callable[..., Mapping]


DFLT_DATA_DIR = get_app_config_folder(package_name, ensure_exists=True)
GRAZE_DATA_DIR = get_app_config_folder(
    os.path.join(package_name, "graze"), ensure_exists=True
)
graze_kwargs = dict(
    rootdir=GRAZE_DATA_DIR,
    key_ingress=_graze.key_ingress_print_downloading_message_with_size,
)
graze = partial(_graze, **graze_kwargs)
grazed_path = partial(graze, return_filepaths=True)
Graze = partial(_Graze, **graze_kwargs)
GrazeReturningFilepaths = partial(_GrazeReturningFilepaths, **graze_kwargs)


def get_xv_app_folder(name, *, ensure_exists=True):
    return get_app_config_folder(f"{package_name}/{name}", ensure_exists=ensure_exists)
