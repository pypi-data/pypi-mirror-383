"""
aria2py - A Python wrapper for aria2c with improved UX and type safety.
"""

from aria2py.client import Aria2Client
from aria2py.models import (
    BasicOptions,
    HttpOptions,
    BitTorrentOptions,
    MetalinkOptions,
    RpcOptions,
    AdvancedOptions
)

__version__ = "0.1.2"
