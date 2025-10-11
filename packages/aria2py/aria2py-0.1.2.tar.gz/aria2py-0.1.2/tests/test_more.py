import base64
import json
import subprocess
import unittest
from typing import Any, Dict, List, Optional
from unittest import mock

from aria2py.client import Aria2Client
from aria2py.exceptions import Aria2RpcError
from aria2py.models.metalink import MetalinkOptions
from aria2py.models.rpc import RpcOptions
from aria2py.rpc_client import Aria2RpcClient
from aria2py.utils import parse_aria2c_version


class UtilsParseVersionTests(unittest.TestCase):
    @mock.patch("aria2py.utils.subprocess.run")
    def test_returns_first_line_only(self, m_run: mock.MagicMock) -> None:
        completed = subprocess.CompletedProcess(
            ["aria2c", "--version"],
            0,
            stdout="aria2 version 1.36.0\nFeatures: SSL, libxml2, etc\n",
            stderr="",
        )
        m_run.return_value = completed
        self.assertEqual(parse_aria2c_version(), "aria2 version 1.36.0")

    @mock.patch("aria2py.utils.subprocess.run")
    def test_raises_on_nonzero_exit(self, m_run: mock.MagicMock) -> None:
        completed = subprocess.CompletedProcess(
            ["aria2c", "--version"],
            1,
            stdout="",
            stderr="oops",
        )
        m_run.return_value = completed
        with self.assertRaises(RuntimeError):
            parse_aria2c_version()


class MetalinkShimTests(unittest.TestCase):
    def test_metalink_select_and_show_files_in_cli_and_rpc(self) -> None:
        opts = MetalinkOptions(select_file="1-3,8", show_files=True)
        cli = opts.to_command_options()
        self.assertIn("--select-file=1-3,8", cli)
        self.assertIn("--show-files", cli)
        rpc = opts.to_rpc_options()
        self.assertEqual("1-3,8", rpc.get("select-file"))
        self.assertEqual("true", rpc.get("show-files"))


class FetchDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Aria2Client(require_local_binary=False)
        self._captured: Dict[str, List[str]] = {}

        def _fake_run(args: List[str], stream: bool = False) -> subprocess.CompletedProcess:
            self._captured["args"] = list(args)
            return subprocess.CompletedProcess(["aria2c"] + args, 0, stdout="", stderr="")

        self._run_patch = mock.patch.object(
            self.client,
            "_run_command",
            side_effect=lambda args, stream=False: _fake_run(args, stream),
        )
        self._run_patch.start()

    def tearDown(self) -> None:
        self._run_patch.stop()

    @mock.patch("aria2py.client.os.path.isfile", return_value=False)
    def test_http_url(self, m_isfile: mock.MagicMock) -> None:
        self.client.fetch("https://example.com/a.zip")
        args = self._captured["args"]
        self.assertIn("https://example.com/a.zip", args)

    @mock.patch("aria2py.client.os.path.isfile", return_value=False)
    def test_remote_torrent_by_extension(self, m_isfile: mock.MagicMock) -> None:
        self.client.fetch("https://host/test.torrent")
        args = self._captured["args"]
        self.assertIn("https://host/test.torrent", args)

    @mock.patch("aria2py.client.os.path.isfile", return_value=False)
    def test_remote_metalink_by_extension(self, m_isfile: mock.MagicMock) -> None:
        self.client.fetch("https://host/file.meta4")
        args = self._captured["args"]
        self.assertIn("https://host/file.meta4", args)

    @mock.patch("aria2py.client.os.path.isfile", return_value=False)
    def test_magnet_uri(self, m_isfile: mock.MagicMock) -> None:
        magnet = "magnet:?xt=urn:btih:DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"
        self.client.fetch(magnet)
        args = self._captured["args"]
        self.assertIn(magnet, args)

    @mock.patch("aria2py.client.os.path.isfile", side_effect=lambda p: p == "files.txt")
    def test_local_input_file(self, m_isfile: mock.MagicMock) -> None:
        self.client.fetch("files.txt")
        args = self._captured["args"]
        self.assertIn("--input-file=files.txt", args)
        self.assertFalse(any(arg == "files.txt" for arg in args))
        self.assertIsNone(self.client.basic_options.input_file)

    @mock.patch("aria2py.client.os.path.isfile", return_value=False)
    def test_list_of_uris(self, m_isfile: mock.MagicMock) -> None:
        uris = ["https://a/x", "https://b/y"]
        self.client.fetch(uris)
        args = self._captured["args"]
        for uri in uris:
            self.assertIn(uri, args)


class _FakeResponseOK:
    def __init__(self, payload: Optional[Dict[str, Any]] = None) -> None:
        self._payload = payload or {"jsonrpc": "2.0", "id": 1, "result": "ok"}

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "_FakeResponseOK":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class _FakeResponseError(_FakeResponseOK):
    def __init__(self) -> None:
        super().__init__({"jsonrpc": "2.0", "id": 1, "error": {"code": 1, "message": "bad"}})


class RpcHappyPathsTests(unittest.TestCase):
    def _patch_and_assert(
        self,
        method_name: str,
        assert_params_fn,
        return_error: bool = False,
    ) -> mock.MagicMock:
        def _fake_urlopen(request, timeout: Optional[float] = None):
            body = json.loads(request.data.decode("utf-8"))
            self.assertEqual(method_name, body["method"])
            assert_params_fn(body["params"])
            return _FakeResponseError() if return_error else _FakeResponseOK()

        return mock.patch("aria2py.rpc_client.urlopen", side_effect=_fake_urlopen)

    def test_add_torrent_payload(self) -> None:
        rpc = Aria2RpcClient(secret="s3cr3t")
        blob = b"abc"
        expected_b64 = base64.b64encode(blob).decode("ascii")

        def _assert_params(params: List[Any]) -> None:
            self.assertEqual("token:s3cr3t", params[0])
            self.assertEqual(expected_b64, params[1])
            self.assertEqual(["u1", "u2"], params[2])
            self.assertEqual({"dir": "/tmp"}, params[3])
            self.assertEqual(1, params[4])

        with self._patch_and_assert("aria2.addTorrent", _assert_params):
            rpc.add_torrent(blob, uris=["u1", "u2"], options={"dir": "/tmp"}, position=1)

    def test_add_metalink_payload(self) -> None:
        rpc = Aria2RpcClient(secret="tok")
        blob = b"<metalink/>"
        expected_b64 = base64.b64encode(blob).decode("ascii")

        def _assert_params(params: List[Any]) -> None:
            self.assertEqual("token:tok", params[0])
            self.assertEqual(expected_b64, params[1])
            self.assertEqual({"dir": "/data"}, params[2])
            self.assertEqual(0, params[3])

        with self._patch_and_assert("aria2.addMetalink", _assert_params):
            rpc.add_metalink(blob, options={"dir": "/data"}, position=0)

    def test_change_option_and_global(self) -> None:
        rpc = Aria2RpcClient(secret="tok")

        def _assert_change_option(params: List[Any]) -> None:
            self.assertEqual("token:tok", params[0])
            self.assertEqual("gid123", params[1])
            self.assertEqual({"max-download-limit": "100K"}, params[2])

        with self._patch_and_assert("aria2.changeOption", _assert_change_option):
            rpc.change_option("gid123", {"max-download-limit": "100K"})

        def _assert_change_global(params: List[Any]) -> None:
            self.assertEqual("token:tok", params[0])
            self.assertEqual({"max-overall-download-limit": "1M"}, params[1])

        with self._patch_and_assert("aria2.changeGlobalOption", _assert_change_global):
            rpc.change_global_option({"max-overall-download-limit": "1M"})

    def test_tell_waiting_and_stopped(self) -> None:
        rpc = Aria2RpcClient(secret="tok")

        def _assert_waiting(params: List[Any]) -> None:
            self.assertEqual(["token:tok", 0, 10, ["gid", "status"]], params)

        with self._patch_and_assert("aria2.tellWaiting", _assert_waiting):
            rpc.tell_waiting(0, 10, keys=["gid", "status"])

        def _assert_stopped(params: List[Any]) -> None:
            self.assertEqual(["token:tok", 5, 20], params)

        with self._patch_and_assert("aria2.tellStopped", _assert_stopped):
            rpc.tell_stopped(5, 20)

    def test_rpc_error_raises_typed_exception(self) -> None:
        rpc = Aria2RpcClient()
        with mock.patch("aria2py.rpc_client.urlopen", return_value=_FakeResponseError()):
            with self.assertRaises(Aria2RpcError):
                rpc.tell_active()


class _FakePopen:
    def __init__(self, *args, **kwargs) -> None:
        self._terminated = False
        self._killed = False
        self._returncode: Optional[int] = None

    def poll(self) -> Optional[int]:
        return self._returncode

    def terminate(self) -> None:
        self._terminated = True

    def wait(self, timeout: Optional[float] = None) -> int:
        self._returncode = 0
        return 0

    def kill(self) -> None:
        self._killed = True


class ProcessLifecycleTests(unittest.TestCase):
    @mock.patch("aria2py.client.subprocess.Popen", return_value=_FakePopen())
    def test_context_manager_starts_and_terminates(self, m_popen: mock.MagicMock) -> None:
        client = Aria2Client(rpc_options=RpcOptions(enable_rpc=True), require_local_binary=False)
        with client:
            _ = client.rpc
            self.assertIsNotNone(client._proc)
            self.assertIsNotNone(client._rpc_client)
        self.assertIsNone(client._proc)
        self.assertIsNone(client._rpc_client)
        fake = m_popen.return_value
        self.assertTrue(fake._terminated)
        self.assertEqual(fake.poll(), 0)

    @mock.patch("aria2py.client.subprocess.Popen", return_value=_FakePopen())
    def test_start_rpc_server_idempotent(self, m_popen: mock.MagicMock) -> None:
        client = Aria2Client(rpc_options=RpcOptions(enable_rpc=True), require_local_binary=False)
        first = client.start_rpc_server()
        second = client.start_rpc_server()
        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
