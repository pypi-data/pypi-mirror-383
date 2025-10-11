# aria2py

A modern, type-safe Python wrapper around the aria2c download utility with a clean local CLI experience and batteries-included JSON-RPC client.

## Requirements

- Python **3.9+**
- `aria2c` available on your `PATH`

Install aria2c first (examples show macOS and Debian/Ubuntu, adapt as needed):

```bash
# macOS
brew install aria2

# Debian/Ubuntu
sudo apt install aria2
```

## Installation

Install the latest release from PyPI:

```bash
pip install aria2py
```

To try the bleeding-edge version straight from GitHub:

```bash
pip install git+https://github.com/omar-hanafy/aria2py.git
```

## Quick Start

### One-liner download

```python
from aria2py import Aria2Client

client = Aria2Client()
result = client.download("https://example.com/file.zip")
print(result.stdout)
```

`download()` returns `subprocess.CompletedProcess`, so stdout/stderr and the exit code are readily available. Set `stream=True` to mirror aria2c’s live console output:

```python
client.download("https://example.com/file.zip", stream=True)
```

### Smart fetch helper

`fetch()` inspects the target and dispatches automatically:

```python
client.fetch("https://example.com/file.zip")    # HTTP/S
client.fetch("magnet:?xt=urn:btih:...")         # Magnet links
client.fetch("https://example.com/file.torrent")
client.fetch("downloads.meta4")
client.fetch(["https://mirror/a", "https://mirror/b"])  # Multiple URIs
```

If a local text file is passed, the path is emitted as `--input-file=...`.

### Configure options with dataclasses

Every aria2c switch maps to a typed field. Combine option groups to tailor the command:

```python
from aria2py import Aria2Client, BasicOptions, HttpOptions

client = Aria2Client(
    basic_options=BasicOptions(
        dir="/tmp/downloads",
        continue_download=True,
    ),
    http_options=HttpOptions(
        header=["User-Agent: aria2py"],
        retry_wait=5,
        max_tries=3,
    ),
)

client.fetch("https://example.com/bundle.zip")
```

Validation runs before any process is spawned, surfacing typos (bad enums, negative values, etc.) immediately.

### BitTorrent and Metalink helpers

```python
from aria2py import Aria2Client, BitTorrentOptions, MetalinkOptions

client = Aria2Client(
    bt_options=BitTorrentOptions(enable_dht=True, seed_ratio=1.0),
    metalink_options=MetalinkOptions(select_file="1-5", show_files=True),
)

client.download_magnet("magnet:?xt=urn:btih:...")
client.download_torrent("/path/to/file.torrent")
client.download_metalink("/path/to/file.meta4")
```

`MetalinkOptions` exposes dedicated `select_file` / `show_files` shims so you no longer need to reach into the BitTorrent option set for file selection.

## Working with the JSON-RPC API

### Starting and managing an RPC server

```python
from aria2py import Aria2Client, RpcOptions

client = Aria2Client(
    rpc_options=RpcOptions(
        enable_rpc=True,
        rpc_listen_port=6800,
        rpc_secret="my-secret-token",
    )
)

with client:  # starts aria2c with RPC enabled
    print(client.rpc.get_version())
    # ... perform RPC calls ...
```

The context manager ensures the aria2c process terminates cleanly when you exit the block. You can also call `start_rpc_server()` yourself; repeated calls are idempotent while the process is running.

To connect to an already running aria2c instance, disable the local binary requirement:

```python
remote = Aria2Client(
    rpc_options=RpcOptions(enable_rpc=True, rpc_listen_port=6800, rpc_secret="token"),
    require_local_binary=False,
)
print(remote.rpc.get_version())
```

### Queueing and controlling downloads

High-level helpers translate Python keyword arguments into aria2-compatible option dictionaries:

```python
from aria2py import Aria2Client, BasicOptions, RpcOptions

client = Aria2Client(
    basic_options=BasicOptions(dir="/data"),
    rpc_options=RpcOptions(enable_rpc=True, rpc_secret="token"),
    require_local_binary=False,
)

gid = client.add("https://example.com/archive.zip")
client.pause(gid)
client.resume(gid)
status = client.status(gid, keys=["status", "completedLength", "downloadSpeed"])
queue = client.waiting(offset=0, num=50)
stopped = client.stopped(offset=0, num=50)
stats = client.rpc.get_global_stat()

client.set_options(gid, max_download_limit="500K")
client.set_global(max_overall_download_limit="5M", enable_color=False)
```

Torrent and metalink payloads can be uploaded without manual base64 encoding:

```python
client.add_torrent_rpc("ubuntu.torrent", uris=["https://mirror.example/ubuntu.iso"])
client.add_metalink_rpc("downloads.meta4")
```

Errors coming back from aria2 are raised as `Aria2RpcError` so you can handle them cleanly:

```python
from aria2py.exceptions import Aria2RpcError

try:
    client.pause("0000000000000000")
except Aria2RpcError as exc:
    print(exc.code, exc)
```

If you need lower-level control, the underlying `Aria2RpcClient` is available via `client.rpc` and supports every helper directly (`add_uri`, `tell_active`, `remove_download_result`, `purge_download_result`, and more).

### Authenticating with cookies

aria2c understands the classic Netscape cookie jar format (the one Firefox/Chrome export). Point `HttpOptions.load_cookies` at your `cookies.txt` to replay authenticated sessions:

```python
from aria2py import Aria2Client, BasicOptions, HttpOptions

client = Aria2Client(
    basic_options=BasicOptions(dir="/tmp/downloads"),
    http_options=HttpOptions(
        load_cookies="/tmp/cookies.txt",          # use exported browser cookies
        save_cookies="/tmp/cookies-refreshed.txt" # optional: persist updates from aria2c
    ),
)

client.fetch("https://example.com/private/file.zip")
```

The same configuration flows through JSON-RPC calls (`add`, `add_torrent_rpc`, `set_options`, etc.), so downloads launched remotely pick up identical cookie headers. Paths must be accessible to the aria2c process, so prefer absolute locations.

## Streaming the aria2c console

When you pass `stream=True` to any download method (`download`, `download_magnet`, `fetch`, etc.) aria2py invokes aria2c with stdout/stderr wired to your terminal, mirroring the native CLI experience—handy when you want to monitor progress without parsing output.

## Error Handling

Custom exceptions provide actionable feedback:

- `Aria2NotInstalledError` – aria2c is missing on the host.
- `Aria2CommandError` – local process exited non-zero; includes stdout/stderr for debugging.
- `Aria2RpcError` – JSON-RPC error response with structured code/message/data attributes.

Example:

```python
from aria2py import Aria2Client, RpcOptions
from aria2py.exceptions import Aria2CommandError, Aria2NotInstalledError, Aria2RpcError

client = Aria2Client(require_local_binary=False, rpc_options=RpcOptions(enable_rpc=True))

try:
    client.fetch("https://example.com/file.zip")
except Aria2NotInstalledError:
    print("Install aria2c before running local downloads.")
except Aria2CommandError as exc:
    print(f"aria2c failed: {exc.stderr}")
except Aria2RpcError as exc:
    print(f"RPC error {exc.code}: {exc}")
```

## Testing

The repository ships with a growing unit test suite that exercises option conversion, dispatch logic, RPC payloads, and process lifecycle. Run everything with:

```bash
pytest
# or
python -m unittest discover
```

## Option Coverage

Option classes mirror the aria2 manual and are tracked in [docs/option_coverage.md](https://github.com/omar-hanafy/aria2py/blob/main/docs/option_coverage.md). Each dataclass groups related switches:

- `BasicOptions`
- `HttpOptions`
- `BitTorrentOptions`
- `MetalinkOptions`
- `RpcOptions`
- `AdvancedOptions`

Because the models are plain dataclasses, IDE auto-complete and static typing tools (mypy/pyright) work out of the box.

## License

aria2py is released under the MIT License. See [LICENSE](./LICENSE) for details.
