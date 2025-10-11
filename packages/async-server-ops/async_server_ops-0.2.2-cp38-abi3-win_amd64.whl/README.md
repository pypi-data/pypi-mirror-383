# async_server_ops 0.2.0 (tuned)

Async, cross-implementation file operations with **throughput tuning**.
Local backend uses `tokio::fs`. Remote backend shells out to **ssh/scp/rsync** via `tokio::process::Command`.

## New in 0.2 (tuning)
- `RemoteConfig.ssh_extra_args: Vec<String>` — inject flags like `-o IPQoS=throughput -c aes128-gcm@openssh.com -o ControlMaster=auto -o ControlPersist=60s`
- `RemoteConfig.prefer_rsync: bool` — use `rsync -a` for uploads/downloads (better for big/recursive or repeated transfers)
- `RemoteConfig.compression: Option<String>` — `"zstd"` (rsync >= 3.2) or `"zlib"`; omit for already-compressed data
- `ServerManager::upload_files_concurrent(pairs, concurrency)` — accelerate many small files

## Build (Rust)
```bash
cargo build
```

## Build (Python via maturin)
```bash
pip install maturin
maturin develop -F python
# or
maturin build -F python --release
```

## Python example
```python
import asyncio
from async_server_ops import ServerManagerPy as ServerManager, PyRemoteConfig as RemoteConfig

async def main():
    cfg = RemoteConfig(
        host="example.com",
        user="ubuntu",
        key_path="~/.ssh/id_rsa",
        port=22,
        ssh_extra_args=["-o","IPQoS=throughput","-c","aes128-gcm@openssh.com","-o","ControlMaster=auto","-o","ControlPersist=60s"],
        prefer_rsync=True,
        compression="zstd",  # or "zlib" or None
    )
    remote = ServerManager.remote(cfg)
    await remote.create_dir_all("/tmp/bench")
    await remote.upload_file("big.bin", "/tmp/bench/big.bin")
    print("exists:", await remote.exists("/tmp/bench/big.bin"))
    # batch small files
    await remote.upload_files_concurrent([("a.txt","/tmp/bench/a.txt"),("b.txt","/tmp/bench/b.txt")], concurrency=8)

asyncio.run(main())
```
