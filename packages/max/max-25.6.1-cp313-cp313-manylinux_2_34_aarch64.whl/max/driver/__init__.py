# ===----------------------------------------------------------------------=== #
#
# This file is Modular Inc proprietary.
#
# ===----------------------------------------------------------------------=== #

from max._core import __version__
from max._core_types.driver import DLPackArray

from .driver import (
    CPU,
    Accelerator,
    Device,
    DeviceSpec,
    DeviceStream,
    accelerator_api,
    accelerator_architecture_name,
    accelerator_count,
    devices_exist,
    load_devices,
    scan_available_devices,
)
from .tensor import Tensor

del driver  # type: ignore
del tensor  # type: ignore

__all__ = [
    "CPU",
    "Accelerator",
    "DLPackArray",
    "Device",
    "DeviceSpec",
    "DeviceStream",
    "Tensor",
    "accelerator_api",
    "accelerator_architecture_name",
    "devices_exist",
    "load_devices",
    "scan_available_devices",
]
