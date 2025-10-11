import os
import subprocess
import tempfile
import unittest
from unittest import mock

from aria2py.client import Aria2Client
from aria2py.exceptions import Aria2CommandError, InvalidOptionError
from aria2py.models.advanced import AdvancedOptions
from aria2py.models.basic import BasicOptions
from aria2py.models.bt import BitTorrentOptions
from aria2py.models.http import HttpOptions
from aria2py.models.metalink import MetalinkOptions
from aria2py.models.rpc import RpcOptions


class OptionModelTests(unittest.TestCase):
    def test_basic_options_cli_bool(self) -> None:
        options = BasicOptions(continue_download=True)
        self.assertIn("--continue=true", options.to_command_options())

    def test_http_options_cli_repeat(self) -> None:
        options = HttpOptions(header=["X-A: 1", "X-B: 2"])
        self.assertEqual(
            ["--header=X-A: 1", "--header=X-B: 2"],
            options.to_command_options(),
        )

    def test_http_options_new_fields(self) -> None:
        options = HttpOptions(
            dry_run=True,
            proxy_method="tunnel",
            max_file_not_found=0,
            reuse_uri=False,
            server_stat_of="/tmp/stats.json",
            stream_piece_selector="geom",
            no_want_digest_header=True,
        )
        cli = options.to_command_options()
        self.assertIn("--dry-run=true", cli)
        self.assertIn("--proxy-method=tunnel", cli)
        self.assertIn("--max-file-not-found=0", cli)
        self.assertIn("--reuse-uri=false", cli)
        self.assertIn("--server-stat-of=/tmp/stats.json", cli)
        self.assertIn("--stream-piece-selector=geom", cli)
        self.assertIn("--no-want-digest-header=true", cli)

    def test_http_options_netrc_and_flags(self) -> None:
        options = HttpOptions(netrc_path="/tmp/.netrc", no_netrc=False)
        cli = options.to_command_options()
        self.assertIn("--netrc-path=/tmp/.netrc", cli)
        self.assertIn("--no-netrc=false", cli)
        rpc = options.to_rpc_options()
        self.assertEqual("/tmp/.netrc", rpc.get("netrc-path"))
        self.assertEqual("false", rpc.get("no-netrc"))

    def test_http_options_server_stats_validation(self) -> None:
        options = HttpOptions(max_file_not_found=0, server_stat_timeout=60)
        # Should not raise
        options.validate()
        cli = options.to_command_options()
        self.assertIn("--max-file-not-found=0", cli)
        self.assertIn("--server-stat-timeout=60", cli)

    def test_bt_options_new_fields(self) -> None:
        options = BitTorrentOptions(bt_max_open_files=128, dht_listen_addr6="2001:db8::1")
        cli = options.to_command_options()
        self.assertIn("--bt-max-open-files=128", cli)
        self.assertIn("--dht-listen-addr6=2001:db8::1", cli)

    def test_advanced_options_new_fields(self) -> None:
        options = AdvancedOptions(min_tls_version="TLSv1.3", max_resume_failure_tries=5, version=True)
        cli = options.to_command_options()
        self.assertIn("--min-tls-version=TLSv1.3", cli)
        self.assertIn("--max-resume-failure-tries=5", cli)
        self.assertIn("--version", cli)
        # Should not raise
        options.validate()

    def test_http_options_rpc_conversion(self) -> None:
        options = HttpOptions(header=["X-A: 1"], check_certificate=True)
        rpc_options = options.to_rpc_options()
        self.assertEqual(["X-A: 1"], rpc_options.get("header"))
        self.assertEqual("true", rpc_options.get("check-certificate"))

    def test_validation_errors(self) -> None:
        options = BasicOptions(max_concurrent_downloads=0)
        with self.assertRaises(InvalidOptionError):
            options.validate()

        http_options = HttpOptions(ftp_type="invalid")
        with self.assertRaises(InvalidOptionError):
            http_options.validate()

        http_options = HttpOptions(proxy_method="invalid")
        with self.assertRaises(InvalidOptionError):
            http_options.validate()

        http_options = HttpOptions(stream_piece_selector="fastest")
        with self.assertRaises(InvalidOptionError):
            http_options.validate()

        http_options = HttpOptions(max_file_not_found=-1)
        with self.assertRaises(InvalidOptionError):
            http_options.validate()

        advanced = AdvancedOptions(min_tls_version="SSLv3")
        with self.assertRaises(InvalidOptionError):
            advanced.validate()

        advanced = AdvancedOptions(max_resume_failure_tries=-1)
        with self.assertRaises(InvalidOptionError):
            advanced.validate()

        bt_options = BitTorrentOptions(bt_max_open_files=0)
        with self.assertRaises(InvalidOptionError):
            bt_options.validate()

    def test_advanced_version_flag(self) -> None:
        options = AdvancedOptions(version=True)
        self.assertIn("--version", options.to_command_options())

    def test_metalink_shim_cli_and_rpc(self) -> None:
        options = MetalinkOptions(select_file="1-3", show_files=True)
        cli = options.to_command_options()
        self.assertIn("--select-file=1-3", cli)
        self.assertIn("--show-files", cli)
        rpc = options.to_rpc_options()
        self.assertEqual("1-3", rpc.get("select-file"))
        self.assertEqual("true", rpc.get("show-files"))


class ClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Aria2Client(
            basic_options=BasicOptions(dir="/tmp"),
            http_options=HttpOptions(header=["X-A: 1"]),
            rpc_options=RpcOptions(enable_rpc=True),
            require_local_binary=False,
        )

    def test_build_command_validates(self) -> None:
        self.client.basic_options.max_concurrent_downloads = 1
        command = self.client._build_command()
        self.assertIn("--dir=/tmp", command)

    def test_rpc_download_options_excludes_non_per_download_fields(self) -> None:
        rpc_options = self.client._rpc_download_options()
        self.assertIn("dir", rpc_options)
        self.assertIn("header", rpc_options)
        self.assertNotIn("rpc-secret", rpc_options)
        self.assertNotIn("input-file", rpc_options)

    def test_run_command_error_raises(self) -> None:
        completed = subprocess.CompletedProcess(["aria2c"], 1, stdout="out", stderr="err")
        with mock.patch("aria2py.client.run_aria2c", return_value=completed):
            with self.assertRaises(Aria2CommandError):
                self.client._run_command(["--version"], stream=False)

    def test_set_global_serialization(self) -> None:
        rpc_mock = mock.Mock()
        self.client._rpc_client = rpc_mock
        self.client.set_global(max_concurrent_downloads=2, enable_color=True, enable_feature=False)
        rpc_mock.change_global_option.assert_called_once_with(
            {
                "max-concurrent-downloads": "2",
                "enable-color": "true",
                "enable-feature": "false",
            }
        )

    def test_set_options_serialization(self) -> None:
        rpc_mock = mock.Mock()
        self.client._rpc_client = rpc_mock
        self.client.set_options("gid123", max_connection_per_server=8, dry_run=True)
        rpc_mock.change_option.assert_called_once_with(
            "gid123",
            {
                "max-connection-per-server": "8",
                "dry-run": "true",
            },
        )

    def test_waiting_and_stopped_passthrough(self) -> None:
        rpc_mock = mock.Mock()
        self.client._rpc_client = rpc_mock
        self.client.waiting(offset=5, num=10, keys=["gid"])
        self.client.stopped(offset=1, num=2, keys=None)
        rpc_mock.tell_waiting.assert_called_once_with(5, 10, ["gid"])
        rpc_mock.tell_stopped.assert_called_once_with(1, 2, None)

    def test_add_torrent_rpc_reads_file(self) -> None:
        rpc_mock = mock.Mock()
        self.client._rpc_client = rpc_mock
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"torrent-bytes")
            tmp_path = tmp.name
        try:
            self.client.add_torrent_rpc(tmp_path, uris=["http://mirror"], position=3)
        finally:
            os.remove(tmp_path)

        rpc_mock.add_torrent.assert_called_once()
        args, kwargs = rpc_mock.add_torrent.call_args
        self.assertEqual(args[0], b"torrent-bytes")
        self.assertEqual(kwargs["uris"], ["http://mirror"])
        self.assertEqual(kwargs["position"], 3)
        self.assertIsInstance(kwargs["options"], dict)

    def test_add_metalink_rpc_reads_file(self) -> None:
        rpc_mock = mock.Mock()
        self.client._rpc_client = rpc_mock
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"<metalink />")
            tmp_path = tmp.name
        try:
            self.client.add_metalink_rpc(tmp_path, position=None)
        finally:
            os.remove(tmp_path)

        rpc_mock.add_metalink.assert_called_once()
        args, kwargs = rpc_mock.add_metalink.call_args
        self.assertEqual(args[0], b"<metalink />")
        self.assertIsNone(kwargs.get("position"))
        self.assertIsInstance(kwargs["options"], dict)


if __name__ == "__main__":
    unittest.main()
