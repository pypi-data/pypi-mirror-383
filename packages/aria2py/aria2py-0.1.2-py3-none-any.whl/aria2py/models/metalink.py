"""
Metalink options for aria2c.
"""

from dataclasses import dataclass, field
from typing import Optional

from aria2py.models.base import OptionModel


@dataclass
class MetalinkOptions(OptionModel):
    """Metalink options for aria2c."""
    
    # Metalink file
    metalink_file: Optional[str] = None
    
    # Basic options
    follow_metalink: Optional[str] = None  # true, false, or mem
    metalink_base_uri: Optional[str] = None
    
    # Preferences
    metalink_language: Optional[str] = None
    metalink_location: Optional[str] = None
    metalink_os: Optional[str] = None
    metalink_version: Optional[str] = None
    
    # Protocol settings
    metalink_preferred_protocol: Optional[str] = None
    metalink_enable_unique_protocol: Optional[bool] = None

    # Ergonomic shims for file filtering/inspection
    select_file: Optional[str] = field(default=None, metadata={"cli_name": "select-file"})
    show_files: Optional[bool] = field(default=None, metadata={"cli_name": "show-files", "flag_style": "flag"})
