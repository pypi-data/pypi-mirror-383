import subprocess
import unittest
from unittest import mock

from aria2py.utils import parse_aria2c_version


class UtilsTests(unittest.TestCase):
    def test_parse_version_returns_first_line(self) -> None:
        completed = subprocess.CompletedProcess(
            ["aria2c", "--version"],
            0,
            stdout="aria2 version 1.37.0\nCopyright (C) 2023\n",
            stderr="",
        )
        with mock.patch("aria2py.utils.subprocess.run", return_value=completed):
            version = parse_aria2c_version()
        self.assertEqual("aria2 version 1.37.0", version)

    def test_parse_version_failure_raises(self) -> None:
        completed = subprocess.CompletedProcess(
            ["aria2c", "--version"],
            1,
            stdout="",
            stderr="boom",
        )
        with mock.patch("aria2py.utils.subprocess.run", return_value=completed):
            with self.assertRaises(RuntimeError):
                parse_aria2c_version()


if __name__ == "__main__":
    unittest.main()
