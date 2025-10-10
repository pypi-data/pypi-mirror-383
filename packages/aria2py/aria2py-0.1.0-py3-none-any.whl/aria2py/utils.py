"""
Utilities for aria2py.
"""

import os
import subprocess
from typing import List

from aria2py.exceptions import Aria2NotInstalledError


def run_aria2c(command_args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """
    Run aria2c with the given arguments.
    
    Args:
        command_args: List of command arguments to pass to aria2c
        capture_output: Whether to capture stdout/stderr output
        
    Returns:
        CompletedProcess instance containing the results of the command
    """
    try:
        return subprocess.run(
            ["aria2c"] + command_args,
            check=False,
            capture_output=capture_output,
            text=True
        )
    except FileNotFoundError:
        raise Aria2NotInstalledError()


def run_aria2c_passthrough(command_args: List[str]) -> int:
    """
    Run aria2c inheriting stdout/stderr so the user sees aria2c's console output.
    
    Args:
        command_args: List of command arguments to pass to aria2c
        
    Returns:
        The process return code.
    """
    try:
        result = subprocess.run(["aria2c"] + command_args, check=False)
        return result.returncode
    except FileNotFoundError:
        raise Aria2NotInstalledError()


def is_aria2c_installed() -> bool:
    """Check if aria2c is installed and available in PATH."""
    try:
        subprocess.run(
            ["aria2c", "--version"],
            check=False,
            capture_output=True,
            text=True
        )
        return True
    except FileNotFoundError:
        return False


def check_path_exists(path: str, path_type: str = "file") -> bool:
    """
    Check if a path exists and is of the expected type.
    
    Args:
        path: Path to check
        path_type: Type of path ('file' or 'directory')
        
    Returns:
        True if path exists and is of the expected type, False otherwise
    """
    if path_type == "file":
        return os.path.isfile(path)
    elif path_type == "directory":
        return os.path.isdir(path)
    else:
        raise ValueError(f"Invalid path_type: {path_type}. Must be 'file' or 'directory'.")


def parse_aria2c_version() -> str:
    """
    Get the version of aria2c.
    
    Returns:
        Version string
    """
    result = subprocess.run(
        ["aria2c", "--version"],
        check=False,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get aria2c version: {result.stderr}")
    
    # Extract version from the output (usually the first line)
    return result.stdout.splitlines()[0].strip()
