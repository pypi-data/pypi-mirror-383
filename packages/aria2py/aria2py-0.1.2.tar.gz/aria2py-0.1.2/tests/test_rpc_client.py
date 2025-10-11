import base64
import json
import unittest
from unittest import mock

from aria2py.exceptions import Aria2RpcError
from aria2py.rpc_client import Aria2RpcClient


class _DummyResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_DummyResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class RpcClientTests(unittest.TestCase):
    def test_call_raises_typed_error(self) -> None:
        payload = json.dumps(
            {"jsonrpc": "2.0", "error": {"code": 1, "message": "oops", "data": {"info": "bad"}}}
        ).encode("utf-8")

        with mock.patch("aria2py.rpc_client.urlopen", return_value=_DummyResponse(payload)):
            client = Aria2RpcClient()
            with self.assertRaises(Aria2RpcError) as ctx:
                client.call("aria2.getVersion")

        self.assertEqual(ctx.exception.code, 1)
        self.assertEqual(ctx.exception.data, {"info": "bad"})
        self.assertIn("oops", str(ctx.exception))

    def test_add_torrent_encodes_bytes(self) -> None:
        client = Aria2RpcClient()
        with mock.patch.object(client, "call", return_value="OK") as call_mock:
            result = client.add_torrent(b"torrent-bytes", uris=["http://mirror"], options={"foo": "bar"}, position=2)

        self.assertEqual(result, "OK")
        call_mock.assert_called_once()
        method, params = call_mock.call_args[0]
        self.assertEqual(method, "aria2.addTorrent")
        expected_b64 = base64.b64encode(b"torrent-bytes").decode("ascii")
        self.assertEqual(params[0], expected_b64)
        self.assertEqual(params[1], ["http://mirror"])
        self.assertEqual(params[2], {"foo": "bar"})
        self.assertEqual(params[3], 2)

    def test_add_metalink_encodes_bytes(self) -> None:
        client = Aria2RpcClient()
        with mock.patch.object(client, "call", return_value="OK") as call_mock:
            client.add_metalink(b"<metalink />", options={"foo": "bar"}, position=None)

        method, params = call_mock.call_args[0]
        self.assertEqual(method, "aria2.addMetalink")
        expected_b64 = base64.b64encode(b"<metalink />").decode("ascii")
        self.assertEqual(params[0], expected_b64)
        self.assertEqual(params[1], {"foo": "bar"})
        self.assertEqual(len(params), 2)

    def test_waiting_and_stopped_methods(self) -> None:
        client = Aria2RpcClient()
        with mock.patch.object(client, "call", return_value=[]) as call_mock:
            client.tell_waiting(0, 5, keys=None)
            client.tell_stopped(1, 10, keys=["gid"])

        calls = call_mock.call_args_list
        self.assertEqual(calls[0].args[0], "aria2.tellWaiting")
        self.assertEqual(calls[0].args[1], [0, 5])
        self.assertEqual(calls[1].args[0], "aria2.tellStopped")
        self.assertEqual(calls[1].args[1], [1, 10, ["gid"]])

    def test_change_option_helpers(self) -> None:
        client = Aria2RpcClient()
        with mock.patch.object(client, "call", return_value="done") as call_mock:
            client.change_option("gid123", {"foo": "1"})
            client.change_global_option({"bar": "2"})
            client.remove_download_result("gid456")
            client.purge_download_result()

        expected_calls = [
            mock.call("aria2.changeOption", ["gid123", {"foo": "1"}]),
            mock.call("aria2.changeGlobalOption", [{"bar": "2"}]),
            mock.call("aria2.removeDownloadResult", ["gid456"]),
            mock.call("aria2.purgeDownloadResult"),
        ]
        self.assertEqual(call_mock.call_args_list, expected_calls)


if __name__ == "__main__":
    unittest.main()
