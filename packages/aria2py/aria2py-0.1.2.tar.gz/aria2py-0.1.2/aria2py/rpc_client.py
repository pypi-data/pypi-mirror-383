"""
Lightweight JSON-RPC client for interacting with the aria2c RPC interface.
"""

import base64
import itertools
import json
from typing import Any, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aria2py.exceptions import Aria2RpcError


class Aria2RpcClient:
    """Minimal helper for invoking aria2c JSON-RPC methods."""

    def __init__(self, url: str = "http://127.0.0.1:6800/jsonrpc", secret: Optional[str] = None, timeout: float = 15.0):
        self.url = url
        self.secret = secret
        self.timeout = timeout
        self._ids = itertools.count(1)

    def _payload(self, method: str, params: Optional[List[Any]] = None) -> bytes:
        call_params: List[Any] = params[:] if params else []
        if self.secret:
            call_params = [f"token:{self.secret}"] + call_params

        body = {
            "jsonrpc": "2.0",
            "id": next(self._ids),
            "method": method,
            "params": call_params,
        }
        return json.dumps(body).encode("utf-8")

    def call(self, method: str, params: Optional[List[Any]] = None) -> Any:
        """Invoke an aria2 JSON-RPC method."""
        request = Request(
            self.url,
            data=self._payload(method, params),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"RPC call failed: {exc}") from exc

        data = json.loads(payload)
        if "error" in data and data["error"]:
            err = data["error"]
            raise Aria2RpcError(err.get("code"), err.get("message"), err.get("data"))
        return data.get("result")

    def add_uri(
        self,
        uris: List[str],
        options: Optional[dict] = None,
        position: Optional[int] = None,
    ) -> Any:
        params: List[Any] = [uris]
        if options is not None:
            params.append(options)
        elif position is not None:
            params.append({})
        if position is not None:
            params.append(position)
        return self.call("aria2.addUri", params)

    def tell_status(self, gid: str, keys: Optional[List[str]] = None) -> Any:
        params: List[Any] = [gid]
        if keys:
            params.append(keys)
        return self.call("aria2.tellStatus", params)

    def tell_active(self, keys: Optional[List[str]] = None) -> Any:
        params: List[Any] = []
        if keys:
            params.append(keys)
        return self.call("aria2.tellActive", params)

    def pause(self, gid: str) -> Any:
        return self.call("aria2.pause", [gid])

    def unpause(self, gid: str) -> Any:
        return self.call("aria2.unpause", [gid])

    def remove(self, gid: str) -> Any:
        return self.call("aria2.remove", [gid])

    def get_version(self) -> Any:
        return self.call("aria2.getVersion")

    def add_torrent(
        self,
        torrent_bytes: bytes,
        uris: Optional[List[str]] = None,
        options: Optional[dict] = None,
        position: Optional[int] = None,
    ) -> Any:
        b64 = base64.b64encode(torrent_bytes).decode("ascii")
        params: List[Any] = [b64]
        if uris is not None:
            params.append(uris)
        if options is not None or position is not None:
            params.append(options or {})
        if position is not None:
            params.append(position)
        return self.call("aria2.addTorrent", params)

    def add_metalink(
        self,
        metalink_bytes: bytes,
        options: Optional[dict] = None,
        position: Optional[int] = None,
    ) -> Any:
        b64 = base64.b64encode(metalink_bytes).decode("ascii")
        params: List[Any] = [b64]
        if options is not None or position is not None:
            params.append(options or {})
        if position is not None:
            params.append(position)
        return self.call("aria2.addMetalink", params)

    def tell_waiting(self, offset: int, num: int, keys: Optional[List[str]] = None) -> Any:
        params: List[Any] = [offset, num]
        if keys:
            params.append(keys)
        return self.call("aria2.tellWaiting", params)

    def tell_stopped(self, offset: int, num: int, keys: Optional[List[str]] = None) -> Any:
        params: List[Any] = [offset, num]
        if keys:
            params.append(keys)
        return self.call("aria2.tellStopped", params)

    def get_global_stat(self) -> Any:
        return self.call("aria2.getGlobalStat")

    def change_option(self, gid: str, options: dict) -> Any:
        return self.call("aria2.changeOption", [gid, options])

    def change_global_option(self, options: dict) -> Any:
        return self.call("aria2.changeGlobalOption", [options])

    def remove_download_result(self, gid: str) -> Any:
        return self.call("aria2.removeDownloadResult", [gid])

    def purge_download_result(self) -> Any:
        return self.call("aria2.purgeDownloadResult")
