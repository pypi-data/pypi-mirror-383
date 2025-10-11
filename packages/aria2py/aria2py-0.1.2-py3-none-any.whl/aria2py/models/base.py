"""
Base model for all aria2c options.
"""

from abc import ABC
from dataclasses import dataclass, fields
from typing import Any, Dict, List

from aria2py.exceptions import InvalidOptionError


@dataclass
class OptionModel(ABC):
    """Base model for aria2c options."""
    
    def to_command_options(self) -> List[str]:
        """Convert options to command-line arguments."""
        options: List[str] = []

        for option_field in fields(self):
            key = option_field.name
            value = getattr(self, key)
            metadata = option_field.metadata or {}

            if metadata.get("skip_cli"):
                continue

            if value is None:
                continue

            if isinstance(value, (list, dict)) and not value:
                continue

            cli_name = metadata.get("cli_name", key.replace("_", "-"))
            option_name = f"--{cli_name}"

            if isinstance(value, bool):
                if metadata.get("flag_style") == "flag":
                    if value:
                        options.append(option_name)
                else:
                    options.append(f"{option_name}={'true' if value else 'false'}")
                continue

            if isinstance(value, list):
                if metadata.get("repeat"):
                    for item in value:
                        options.append(f"{option_name}={item}")
                else:
                    joined = ",".join(str(item) for item in value)
                    options.append(f"{option_name}={joined}")
                continue

            options.append(f"{option_name}={value}")

        return options

    def to_rpc_options(self) -> Dict[str, Any]:
        """Convert options to an aria2 RPC-compatible dictionary."""
        rpc_options: Dict[str, Any] = {}

        for option_field in fields(self):
            key = option_field.name
            value = getattr(self, key)
            metadata = option_field.metadata or {}

            if metadata.get("skip_cli"):
                continue

            if value is None:
                continue

            if isinstance(value, (list, dict)) and not value:
                continue

            rpc_name = metadata.get("cli_name", key.replace("_", "-"))

            if isinstance(value, bool):
                rpc_options[rpc_name] = "true" if value else "false"
                continue

            if isinstance(value, list):
                if metadata.get("repeat"):
                    rpc_options[rpc_name] = list(value)
                else:
                    rpc_options[rpc_name] = ",".join(str(item) for item in value)
                continue

            rpc_options[rpc_name] = str(value)

        return rpc_options

    def validate(self) -> None:
        """Hook for subclasses to provide additional validation."""
        return

    def _ensure_positive(self, name: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (int, float)) and value <= 0:
            raise InvalidOptionError(name, value, "must be greater than 0")

    def _ensure_non_negative(self, name: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (int, float)) and value < 0:
            raise InvalidOptionError(name, value, "must be zero or greater")

    def _ensure_choices(self, name: str, value: Any, choices: List[Any]) -> None:
        if value is None:
            return
        if value not in choices:
            raise InvalidOptionError(name, value, f"must be one of {choices!r}")
