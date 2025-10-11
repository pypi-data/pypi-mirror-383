# SPDX-License-Identifier: MIT
"""pixhawkcontroller public API (main entrypoint)."""

from .main import FlightControllerInterface, FlightControllerInfo, TonesQb, find_usb_vid_pid
from .__version__ import __version__

__all__ = [
    "FlightControllerInterface",
    "FlightControllerInfo",
    "TonesQb",
    "find_usb_vid_pid",
    "__version__",
]

__author__ = "Md Shahriar Forhad"
__email__ = "shahriar.forhad.eee@gmail.com"
__license__ = "MIT"
