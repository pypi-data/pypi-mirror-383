# ---------------------------------------------------------------------
# Gufo Err
# ---------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# ---------------------------------------------------------------------
"""Human-readable error reporting.

Attributes:
    __version__: Current version.
    HAS_CODE_POSITION: True, if Python interpreter supports
        exact code positions  (Python 3.11+)
"""

# Gufo Labs modules
from .abc.failfast import BaseFailFast
from .abc.middleware import BaseMiddleware
from .err import Err, err
from .frame import HAS_CODE_POSITION, exc_traceback, iter_frames
from .logger import logger
from .types import (
    Anchor,
    CodePosition,
    ErrorInfo,
    FrameInfo,
    SourceInfo,
)

__version__: str = "0.6.0"
__all__ = [
    "HAS_CODE_POSITION",
    "Anchor",
    "BaseFailFast",
    "BaseMiddleware",
    "CodePosition",
    "Err",
    "ErrorInfo",
    "FrameInfo",
    "SourceInfo",
    "err",
    "exc_traceback",
    "iter_frames",
    "logger",
]
