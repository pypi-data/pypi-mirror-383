"""
BitTorrent options for aria2c.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from aria2py.exceptions import InvalidOptionError
from aria2py.models.base import OptionModel


@dataclass
class BitTorrentOptions(OptionModel):
    """BitTorrent options for aria2c."""
    
    # Torrent file
    torrent_file: Optional[str] = None
    
    # File selection
    select_file: Optional[str] = None
    show_files: Optional[bool] = None
    index_out: List[str] = field(default_factory=list, metadata={"repeat": True, "cli_name": "index-out"})
    
    # Basic settings
    bt_max_open_files: Optional[int] = None
    listen_port: Optional[str] = None  # Can be a range "6881-6999"
    follow_torrent: Optional[str] = None  # true, false, or mem
    
    # BT peers and connections
    bt_max_peers: Optional[int] = None
    bt_request_peer_speed_limit: Optional[str] = None
    bt_exclude_tracker: Optional[str] = None
    bt_tracker: Optional[str] = None
    bt_tracker_connect_timeout: Optional[int] = None
    bt_tracker_interval: Optional[int] = None
    bt_tracker_timeout: Optional[int] = None
    bt_external_ip: Optional[str] = None
    
    # BT advanced features
    bt_prioritize_piece: Optional[str] = None
    bt_seed_unverified: Optional[bool] = None
    bt_save_metadata: Optional[bool] = None
    bt_metadata_only: Optional[bool] = None
    bt_hash_check_seed: Optional[bool] = None
    bt_load_saved_metadata: Optional[bool] = None
    bt_remove_unselected_file: Optional[bool] = None
    
    # DHT options
    enable_dht: Optional[bool] = None
    enable_dht6: Optional[bool] = None
    dht_listen_port: Optional[str] = None
    dht_listen_addr6: Optional[str] = None
    dht_entry_point: Optional[str] = None
    dht_entry_point6: Optional[str] = None
    dht_file_path: Optional[str] = None
    dht_file_path6: Optional[str] = None
    dht_message_timeout: Optional[int] = None
    
    # Encryption
    bt_force_encryption: Optional[bool] = None
    bt_require_crypto: Optional[bool] = None
    bt_min_crypto_level: Optional[str] = None
    
    # LPD settings
    bt_enable_lpd: Optional[bool] = None
    bt_lpd_interface: Optional[str] = None
    
    # Seeding
    seed_ratio: Optional[float] = None
    seed_time: Optional[int] = None
    
    # Other BT features
    enable_peer_exchange: Optional[bool] = None
    bt_stop_timeout: Optional[int] = None
    bt_detach_seed_only: Optional[bool] = None
    bt_enable_hook_after_hash_check: Optional[bool] = None
    
    # Upload limits
    max_overall_upload_limit: Optional[str] = None
    max_upload_limit: Optional[str] = None
    
    # Customization
    peer_id_prefix: Optional[str] = None
    peer_agent: Optional[str] = None

    def validate(self) -> None:
        self._ensure_positive("bt-max-open-files", self.bt_max_open_files)
        self._ensure_positive("bt-max-peers", self.bt_max_peers)
        self._ensure_positive("bt-tracker-connect-timeout", self.bt_tracker_connect_timeout)
        self._ensure_positive("bt-tracker-interval", self.bt_tracker_interval)
        self._ensure_positive("bt-tracker-timeout", self.bt_tracker_timeout)
        self._ensure_positive("bt-stop-timeout", self.bt_stop_timeout)
        self._ensure_positive("seed-time", self.seed_time)
        if self.seed_ratio is not None and self.seed_ratio < 0:
            raise InvalidOptionError("seed-ratio", self.seed_ratio, "must be >= 0")
