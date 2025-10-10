"""
Exceptions for aria2py.
"""


class Aria2PyError(Exception):
    """Base exception for aria2py."""
    pass


class Aria2CommandError(Aria2PyError):
    """Exception raised when an aria2c command fails."""
    
    def __init__(self, command: str, return_code: int, stdout: str, stderr: str):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        
        message = (
            f"aria2c command failed with return code {return_code}\\n"
            f"Command: {command}\\n"
            f"Stdout: {stdout}\\n"
            f"Stderr: {stderr}"
        )
        
        super().__init__(message)


class Aria2NotInstalledError(Aria2PyError):
    """Exception raised when aria2c is not installed."""
    
    def __init__(self):
        super().__init__(
            "aria2c is not installed or not available in PATH. "
            "Please install aria2c and ensure it's available in your PATH."
        )


class InvalidOptionError(Aria2PyError):
    """Exception raised when an invalid option is provided."""
    
    def __init__(self, option_name: str, option_value=None, reason: str = None):
        message = f"Invalid option: {option_name}"
        
        if option_value is not None:
            message += f" with value {option_value!r}"
            
        if reason:
            message += f". {reason}"
            
        super().__init__(message)


class Aria2RpcError(Aria2PyError):
    """Raised when aria2 JSON-RPC returns an error."""

    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.data = data
        detail = f"RPC error {code}: {message}"
        if data is not None:
            detail = f"{detail} | data={data!r}"
        super().__init__(detail)
