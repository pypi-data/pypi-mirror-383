"""
Advanced options for aria2c.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union

from aria2py.models.base import OptionModel


@dataclass
class AdvancedOptions(OptionModel):
    """Advanced options for aria2c."""
    
    # Behavior control
    allow_overwrite: Optional[bool] = None
    allow_piece_length_change: Optional[bool] = None
    always_resume: Optional[bool] = None
    auto_file_renaming: Optional[bool] = None
    conditional_get: Optional[bool] = None
    daemon: Optional[bool] = None
    deferred_input: Optional[bool] = None
    file_allocation: Optional[str] = None
    force_save: Optional[bool] = None
    save_not_found: Optional[bool] = None
    hash_check_only: Optional[bool] = None
    human_readable: Optional[bool] = None
    
    # Network settings
    async_dns: Optional[bool] = None
    async_dns_server: Optional[str] = None
    disable_ipv6: Optional[bool] = None
    enable_color: Optional[bool] = None
    enable_mmap: Optional[bool] = None
    event_poll: Optional[str] = None
    interface: Optional[str] = None
    multiple_interface: Optional[str] = None
    min_tls_version: Optional[str] = None
    
    # Performance options
    disk_cache: Optional[str] = None
    max_download_limit: Optional[str] = None
    max_overall_download_limit: Optional[str] = None
    optimize_concurrent_downloads: Optional[Union[bool, str]] = None
    piece_length: Optional[str] = None
    socket_recv_buffer_size: Optional[str] = None
    max_resume_failure_tries: Optional[int] = None
    
    # Resource control
    max_mmap_limit: Optional[str] = None
    rlimit_nofile: Optional[int] = None
    stop: Optional[int] = None
    stop_with_process: Optional[int] = None
    
    # Logging & display
    console_log_level: Optional[str] = None
    log_level: Optional[str] = None
    stderr: Optional[bool] = None
    summary_interval: Optional[int] = None
    truncate_console_readout: Optional[bool] = None
    show_console_readout: Optional[bool] = None
    quiet: Optional[bool] = None
    
    # Session management
    auto_save_interval: Optional[int] = None
    gid: Optional[str] = None
    save_session: Optional[str] = None
    save_session_interval: Optional[int] = None
    keep_unfinished_download_result: Optional[bool] = None
    max_download_result: Optional[int] = None
    
    # QoS
    dscp: Optional[str] = None
    
    # Event hooks
    on_bt_download_complete: Optional[str] = None
    on_download_complete: Optional[str] = None
    on_download_error: Optional[str] = None
    on_download_pause: Optional[str] = None
    on_download_start: Optional[str] = None
    on_download_stop: Optional[str] = None
    
    # URI processing
    parameterized_uri: Optional[bool] = None
    force_sequential: Optional[bool] = None
    
    # Checksums
    checksum: Optional[str] = None
    realtime_chunk_checksum: Optional[bool] = None
    
    # Miscellaneous
    conf_path: Optional[str] = None
    content_disposition_default_utf8: Optional[bool] = None
    download_result: Optional[str] = None
    no_conf: Optional[bool] = None
    no_file_allocation_limit: Optional[str] = None
    remove_control_file: Optional[bool] = None
    version: Optional[bool] = field(default=None, metadata={"flag_style": "flag"})

    def validate(self) -> None:
        self._ensure_non_negative("max-resume-failure-tries", self.max_resume_failure_tries)
        self._ensure_choices(
            "min-tls-version",
            self.min_tls_version,
            ["TLSv1.1", "TLSv1.2", "TLSv1.3"],
        )
