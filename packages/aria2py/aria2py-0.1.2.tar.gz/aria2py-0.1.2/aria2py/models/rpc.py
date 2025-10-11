"""
RPC options for aria2c.
"""

from dataclasses import dataclass
from typing import List, Optional

from aria2py.models.base import OptionModel


@dataclass
class RpcOptions(OptionModel):
    """RPC options for aria2c."""
    
    # Basic options
    enable_rpc: Optional[bool] = None
    pause: Optional[bool] = None
    pause_metadata: Optional[bool] = None
    
    # Server settings
    rpc_listen_port: Optional[int] = None
    rpc_listen_all: Optional[bool] = None
    rpc_max_request_size: Optional[str] = None
    
    # Security
    rpc_secret: Optional[str] = None
    rpc_user: Optional[str] = None  # Deprecated
    rpc_passwd: Optional[str] = None  # Deprecated
    
    # SSL/TLS
    rpc_secure: Optional[bool] = None
    rpc_certificate: Optional[str] = None
    rpc_private_key: Optional[str] = None
    
    # Behavior
    rpc_save_upload_metadata: Optional[bool] = None
    rpc_allow_origin_all: Optional[bool] = None
