"""Main client for aria2py."""

import os
import shlex
import subprocess
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from aria2py.exceptions import Aria2CommandError, Aria2NotInstalledError
from aria2py.models.advanced import AdvancedOptions
from aria2py.models.basic import BasicOptions
from aria2py.models.bt import BitTorrentOptions
from aria2py.models.http import HttpOptions
from aria2py.models.metalink import MetalinkOptions
from aria2py.models.rpc import RpcOptions
from aria2py.rpc_client import Aria2RpcClient
from aria2py.utils import is_aria2c_installed, run_aria2c, run_aria2c_passthrough


class Aria2Client:
    """High-level client for the aria2c command-line utility."""

    def __init__(
        self,
        basic_options: Optional[BasicOptions] = None,
        http_options: Optional[HttpOptions] = None,
        bt_options: Optional[BitTorrentOptions] = None,
        metalink_options: Optional[MetalinkOptions] = None,
        rpc_options: Optional[RpcOptions] = None,
        advanced_options: Optional[AdvancedOptions] = None,
        *,
        require_local_binary: bool = True,
    ) -> None:
        """
        Initialize the aria2c client.

        Args:
            basic_options: Basic options for aria2c.
            http_options: HTTP/FTP/SFTP options for aria2c.
            bt_options: BitTorrent options for aria2c.
            metalink_options: Metalink options for aria2c.
            rpc_options: RPC options for aria2c.
            advanced_options: Advanced options for aria2c.
            require_local_binary: When ``True`` (default) ensure ``aria2c`` is available
                before spawning local processes.
        """

        self.require_local_binary = require_local_binary

        if self.require_local_binary and not is_aria2c_installed():
            raise Aria2NotInstalledError()

        self.basic_options = basic_options or BasicOptions()
        self.http_options = http_options or HttpOptions()
        self.bt_options = bt_options or BitTorrentOptions()
        self.metalink_options = metalink_options or MetalinkOptions()
        self.rpc_options = rpc_options or RpcOptions()
        self.advanced_options = advanced_options or AdvancedOptions()
        self._proc: Optional[subprocess.Popen] = None
        self._rpc_client: Optional[Aria2RpcClient] = None

    def _assert_binary_available(self) -> None:
        if self.require_local_binary and not is_aria2c_installed():
            raise Aria2NotInstalledError()

    def _validate_all(self) -> None:
        for model in (
            self.basic_options,
            self.http_options,
            self.bt_options,
            self.metalink_options,
            self.rpc_options,
            self.advanced_options,
        ):
            model.validate()

    def _run_command(self, command_args: List[str], stream: bool = False) -> subprocess.CompletedProcess:
        """
        Execute aria2c with the provided arguments, optionally streaming output.
        """

        self._assert_binary_available()

        argv = ["aria2c"] + command_args
        command_repr = " ".join(shlex.quote(arg) for arg in argv)

        if stream:
            return_code = run_aria2c_passthrough(command_args)
            if return_code != 0:
                raise Aria2CommandError(
                    command=command_repr,
                    return_code=return_code,
                    stdout="",
                    stderr="",
                )
            return subprocess.CompletedProcess(argv, return_code, stdout=None, stderr=None)

        result = run_aria2c(command_args, capture_output=True)
        if result.returncode != 0:
            raise Aria2CommandError(
                command=command_repr,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        return result

    def _create_rpc_client(self) -> Aria2RpcClient:
        """Instantiate an RPC client using the current RPC options."""

        port = self.rpc_options.rpc_listen_port or 6800
        scheme = "https" if self.rpc_options.rpc_secure else "http"
        url = f"{scheme}://127.0.0.1:{port}/jsonrpc"
        return Aria2RpcClient(url=url, secret=self.rpc_options.rpc_secret)

    def download(self, uris: Union[str, List[str]], stream: bool = False) -> subprocess.CompletedProcess:
        """Download the provided URI(s)."""

        if isinstance(uris, str):
            uris = [uris]

        # Store URIs in basic options (not emitted on the CLI)
        self.basic_options.uris = list(uris)

        command_args = self._build_command()
        command_args.extend(uris)

        return self._run_command(command_args, stream=stream)

    def download_torrent(self, torrent_path: str, stream: bool = False) -> subprocess.CompletedProcess:
        """Download a torrent file."""

        command_args = self._build_command()
        command_args.append(torrent_path)
        return self._run_command(command_args, stream=stream)

    def download_metalink(self, metalink_path: str, stream: bool = False) -> subprocess.CompletedProcess:
        """Download a metalink file."""

        command_args = self._build_command()
        command_args.append(metalink_path)
        return self._run_command(command_args, stream=stream)

    def download_magnet(self, magnet_uri: str, stream: bool = False) -> subprocess.CompletedProcess:
        """Download a magnet URI."""

        command_args = self._build_command()
        command_args.append(magnet_uri)
        return self._run_command(command_args, stream=stream)

    def fetch(self, target: Union[str, List[str]], stream: bool = False) -> subprocess.CompletedProcess:
        """Auto-detect the download type and dispatch to the appropriate handler."""

        if isinstance(target, list):
            return self.download(target, stream=stream)

        target_str = str(target)

        if target_str.startswith("magnet:"):
            return self.download_magnet(target_str, stream=stream)

        parsed = urlparse(target_str)
        scheme = parsed.scheme.lower()
        is_remote = scheme in {"http", "https", "ftp", "ftps", "sftp"}
        path_hint = (parsed.path or "").lower() if is_remote else target_str.lower()

        if path_hint.endswith(".torrent"):
            return self.download_torrent(target_str, stream=stream)

        if path_hint.endswith(".metalink") or path_hint.endswith(".meta4"):
            return self.download_metalink(target_str, stream=stream)

        if is_remote:
            return self.download(target_str, stream=stream)

        if os.path.isfile(target_str):
            previous_input_file = self.basic_options.input_file
            try:
                self.basic_options.input_file = target_str
                return self.download([], stream=stream)
            finally:
                self.basic_options.input_file = previous_input_file

        raise ValueError(f"Unrecognized download target: {target_str}")

    @property
    def rpc(self) -> Aria2RpcClient:
        """Return a lazily-instantiated RPC client."""

        if not self.rpc_options.enable_rpc:
            raise RuntimeError(
                "RPC is not enabled. Set rpc_options.enable_rpc=True before accessing the RPC client."
            )
        if self._rpc_client is None:
            self._rpc_client = self._create_rpc_client()
        return self._rpc_client

    def start_rpc_server(self, inherit_stdio: bool = True) -> subprocess.Popen:
        """Start the aria2c RPC server."""

        if self._proc and self._proc.poll() is None:
            return self._proc

        self._assert_binary_available()

        # Ensure RPC is enabled
        self.rpc_options.enable_rpc = True

        command_args = self._build_command()

        stdout = None if inherit_stdio else subprocess.PIPE
        stderr = None if inherit_stdio else subprocess.PIPE
        process = subprocess.Popen(
            ["aria2c"] + command_args,
            stdout=stdout,
            stderr=stderr,
            text=not inherit_stdio,
        )
        self._proc = process
        self._rpc_client = None

        return process

    def __enter__(self) -> "Aria2Client":
        if self.rpc_options.enable_rpc:
            self.start_rpc_server(inherit_stdio=True)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None
        self._rpc_client = None

    def _build_command(self) -> List[str]:
        """Build the aria2c command from all option groups."""

        self._validate_all()

        command_args: List[str] = []
        command_args.extend(self.basic_options.to_command_options())
        command_args.extend(self.http_options.to_command_options())
        command_args.extend(self.bt_options.to_command_options())
        command_args.extend(self.metalink_options.to_command_options())
        command_args.extend(self.rpc_options.to_command_options())
        command_args.extend(self.advanced_options.to_command_options())
        return command_args

    def _rpc_download_options(self) -> Dict[str, Union[str, List[str]]]:
        """Build a dictionary of options suitable for RPC per-download calls."""

        self._validate_all()

        merged: Dict[str, Union[str, List[str]]] = {}
        for model in (
            self.basic_options,
            self.http_options,
            self.bt_options,
            self.metalink_options,
            self.advanced_options,
        ):
            merged.update(model.to_rpc_options())

        excluded_keys = {
            "help",
            "uris",
            "torrent-file",
            "metalink-file",
            "input-file",
        }

        return {
            key: value
            for key, value in merged.items()
            if not key.startswith("rpc-") and key not in excluded_keys
        }

    def add(self, uris: Union[str, List[str]], position: Optional[int] = None) -> Any:
        """Queue download(s) through the aria2 RPC interface."""

        if isinstance(uris, str):
            uris = [uris]

        options = self._rpc_download_options()
        return self.rpc.add_uri(list(uris), options=options, position=position)

    # --- Convenience wrappers over RPC ---
    def pause(self, gid: str) -> Any:
        return self.rpc.pause(gid)

    def resume(self, gid: str) -> Any:
        return self.rpc.unpause(gid)

    def remove(self, gid: str) -> Any:
        return self.rpc.remove(gid)

    def status(self, gid: str, keys: Optional[List[str]] = None) -> Any:
        return self.rpc.tell_status(gid, keys)

    def active(self, keys: Optional[List[str]] = None) -> Any:
        return self.rpc.tell_active(keys)

    def waiting(self, offset: int = 0, num: int = 50, keys: Optional[List[str]] = None) -> Any:
        return self.rpc.tell_waiting(offset, num, keys)

    def stopped(self, offset: int = 0, num: int = 50, keys: Optional[List[str]] = None) -> Any:
        return self.rpc.tell_stopped(offset, num, keys)

    def set_global(self, **options: Union[str, int, bool]) -> Any:
        serialized = {
            key.replace("_", "-"): (
                "true" if value is True else "false" if value is False else str(value)
            )
            for key, value in options.items()
        }
        return self.rpc.change_global_option(serialized)

    def set_options(self, gid: str, **options: Union[str, int, bool]) -> Any:
        serialized = {
            key.replace("_", "-"): (
                "true" if value is True else "false" if value is False else str(value)
            )
            for key, value in options.items()
        }
        return self.rpc.change_option(gid, serialized)

    def add_torrent_rpc(
        self,
        torrent_path: str,
        uris: Optional[List[str]] = None,
        position: Optional[int] = None,
    ) -> Any:
        with open(torrent_path, "rb") as fh:
            payload = fh.read()
        return self.rpc.add_torrent(
            payload,
            uris=uris,
            options=self._rpc_download_options(),
            position=position,
        )

    def add_metalink_rpc(
        self,
        metalink_path: str,
        position: Optional[int] = None,
    ) -> Any:
        with open(metalink_path, "rb") as fh:
            payload = fh.read()
        return self.rpc.add_metalink(
            payload,
            options=self._rpc_download_options(),
            position=position,
        )
