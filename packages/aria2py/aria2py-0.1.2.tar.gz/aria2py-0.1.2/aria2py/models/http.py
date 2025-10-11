"""
HTTP/FTP/SFTP options for aria2c.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from aria2py.models.base import OptionModel


@dataclass
class HttpOptions(OptionModel):
    """HTTP/FTP/SFTP options for aria2c."""
    
    # Proxy settings
    all_proxy: Optional[str] = None
    all_proxy_passwd: Optional[str] = None
    all_proxy_user: Optional[str] = None
    
    # No proxy for specific domains
    no_proxy: Optional[str] = None
    
    # HTTP-specific proxies
    http_proxy: Optional[str] = None
    http_proxy_passwd: Optional[str] = None
    http_proxy_user: Optional[str] = None
    
    # HTTPS-specific proxies
    https_proxy: Optional[str] = None
    https_proxy_passwd: Optional[str] = None
    https_proxy_user: Optional[str] = None
    
    # FTP-specific proxies
    ftp_proxy: Optional[str] = None
    ftp_proxy_passwd: Optional[str] = None
    ftp_proxy_user: Optional[str] = None
    
    # Authentication
    http_user: Optional[str] = None
    http_passwd: Optional[str] = None
    netrc_path: Optional[str] = None
    no_netrc: Optional[bool] = None
    
    # FTP settings
    ftp_user: Optional[str] = None
    ftp_passwd: Optional[str] = None
    ftp_pasv: Optional[bool] = None
    ftp_type: Optional[str] = None  # binary or ascii
    ftp_reuse_connection: Optional[bool] = None
    ssh_host_key_md: Optional[str] = None
    
    # SSL/TLS options
    ca_certificate: Optional[str] = None
    certificate: Optional[str] = None
    private_key: Optional[str] = None
    check_certificate: Optional[bool] = None
    
    # HTTP specific options
    referer: Optional[str] = None
    user_agent: Optional[str] = None
    header: List[str] = field(default_factory=list, metadata={"repeat": True})
    no_want_digest_header: Optional[bool] = None
    
    # Cookie options
    load_cookies: Optional[str] = None
    save_cookies: Optional[str] = None
    
    # HTTP features
    http_accept_gzip: Optional[bool] = None
    http_auth_challenge: Optional[bool] = None
    http_no_cache: Optional[bool] = None
    use_head: Optional[bool] = None
    dry_run: Optional[bool] = None
    enable_http_keep_alive: Optional[bool] = None
    enable_http_pipelining: Optional[bool] = None
    
    # Connection options
    proxy_method: Optional[str] = None
    connect_timeout: Optional[int] = None
    timeout: Optional[int] = None  # Set timeout in seconds
    lowest_speed_limit: Optional[str] = None
    max_tries: Optional[int] = None
    retry_wait: Optional[int] = None
    max_file_not_found: Optional[int] = None
    reuse_uri: Optional[bool] = None

    # Server selection
    uri_selector: Optional[str] = None
    server_stat_of: Optional[str] = None
    server_stat_if: Optional[str] = None
    server_stat_timeout: Optional[int] = None
    stream_piece_selector: Optional[str] = None

    def validate(self) -> None:
        self._ensure_positive("connect-timeout", self.connect_timeout)
        self._ensure_positive("timeout", self.timeout)
        self._ensure_positive("max-tries", self.max_tries)
        self._ensure_positive("retry-wait", self.retry_wait)
        self._ensure_non_negative("max-file-not-found", self.max_file_not_found)
        self._ensure_positive("server-stat-timeout", self.server_stat_timeout)
        self._ensure_choices("ftp-type", self.ftp_type, ["binary", "ascii"])
        if self.uri_selector:
            self._ensure_choices("uri-selector", self.uri_selector, ["inorder", "feedback", "adaptive"])
        self._ensure_choices("proxy-method", self.proxy_method, ["get", "tunnel"])
        self._ensure_choices(
            "stream-piece-selector",
            self.stream_piece_selector,
            ["default", "inorder", "random", "geom"],
        )
    
