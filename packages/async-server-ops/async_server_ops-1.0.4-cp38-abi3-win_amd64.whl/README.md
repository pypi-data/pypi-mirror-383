# async_server_ops 1.0.0 (scp-only, robust)

- Remote operations via **OpenSSH scp** (no rsync dependency)
- **Non-interactive defaults** (BatchMode, ConnectTimeout, keepalives) to prevent hangs
- **Correct flags**: `ssh -p`, `scp -P`
- Optional **password** via `sshpass -e` (set `password`), but keys are recommended
- Builds **abi3** wheel for Python 3.8+

## Build for Python (wheel/dev)
```bash
pip install -U maturin
maturin develop -F python --release
# or build wheel: maturin build -F python --release
```

## Python usage
```python
import asyncio
from async_server_ops import ServerManagerPy as ServerManager, PyRemoteConfig as RemoteConfig

async def main():
    cfg = RemoteConfig(
        host="192.168.222.61",
        user="administrator",
        key_path="~/.ssh/id_ed25519",
        port=22,
        prefer_rsync=False,             # scp-only build; flag kept for API compatibility
        ssh_extra_args=[
            "-o","IdentitiesOnly=yes",
            "-o","BatchMode=yes",
            "-o","ConnectTimeout=8",
            "-o","ServerAliveInterval=5","-o","ServerAliveCountMax=2",
        ],
        # password=None,                # optional: requires sshpass installed on client
    )
    m = ServerManager.remote(cfg)

    print("preflight:", await m.preflight())

    rem = "/home/administrator/FoodIpadStorage/temp/dksl_c4db8429.pdf"
    await m.download_file(rem, "file.pdf")
    await m.create_dir_all("/tmp/ops_demo")
    await m.upload_file("file.pdf", "/tmp/ops_demo/file.pdf")
    print("done")

asyncio.run(main())
```
