# async_server_ops (robust 0.3.0)

Async, robust file operations:
- **Local** (tokio fs)
- **Remote** via **OpenSSH** (`scp`) with optional **rsync** (auto-fallback if missing)
- Non-interactive defaults (BatchMode, ConnectTimeout, ServerAlive*)
- Correct `scp` port flag (`-P`), separate from `ssh -p`
- Optional password mode via `sshpass -e` (set `password`), otherwise **key-based**

## Build (Rust)
```bash
cargo build
```

## Build (Python)
```bash
pip install maturin
maturin develop -F python        # dev install into venv
# or build wheels:
maturin build -F python --release --manylinux 2014
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
        prefer_rsync=False,             # rsync optional; scp is default path
        # password=None,                # set if you really must use passwords (requires sshpass on client)
        # robust non-interactive defaults already applied; you can add more:
        ssh_extra_args=[
            "-o","IdentitiesOnly=yes",
            "-o","BatchMode=yes",
            "-o","ConnectTimeout=8",
            "-o","ServerAliveInterval=5","-o","ServerAliveCountMax=2",
        ],
    )
    m = ServerManager.remote(cfg)

    # Remote file to local
    rem = "/home/administrator/FoodIpadStorage/temp/dksl_c4db8429.pdf"
    await m.download_file(rem, "file.pdf")
    print("downloaded")

    # Upload back
    await m.create_dir_all("/tmp/ops_demo")
    await m.upload_file("file.pdf", "/tmp/ops_demo/file.pdf")
    print("uploaded")

asyncio.run(main())
```

## Preflight check
```python
ok = await m.preflight()  # checks ssh/scp locally, connectivity, and remote rsync presence
print("preflight:", ok)
```

## Notes
- Install `rsync` on both sides if you set `prefer_rsync=True`. Otherwise scp is used.
- If you use password auth, install `sshpass` on the client (the lib passes it via env `SSHPASS` safely).
- For production, load your key into **ssh-agent** to avoid prompts.
