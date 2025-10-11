"""
Basic options for aria2c.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from aria2py.models.base import OptionModel


@dataclass
class BasicOptions(OptionModel):
    """Basic options for aria2c."""
    
    # Directory to store downloaded files
    dir: Optional[str] = None
    
    # Input file containing URIs to download
    input_file: Optional[str] = None
    
    # Log file
    log: Optional[str] = None
    
    # Maximum number of parallel downloads
    max_concurrent_downloads: Optional[int] = None
    
    # Check integrity of the file
    check_integrity: Optional[bool] = None
    
    # Continue downloading a partially downloaded file
    continue_download: Optional[bool] = field(default=None, metadata={"cli_name": "continue"})
    
    # Show help with tags
    help: Optional[str] = None
    
    # Out file name
    out: Optional[str] = None
    
    # Remote time
    remote_time: Optional[bool] = None
    
    # Split file to download in parallel
    split: Optional[int] = None
    
    # Minimum size to split (e.g., '20M')
    min_split_size: Optional[str] = None
    
    # Maximum connections per server
    max_connection_per_server: Optional[int] = None

    # URIs to download
    uris: List[str] = field(default_factory=list, metadata={"skip_cli": True})

    def validate(self) -> None:
        self._ensure_positive("max-concurrent-downloads", self.max_concurrent_downloads)
        self._ensure_positive("split", self.split)
        self._ensure_positive("max-connection-per-server", self.max_connection_per_server)
