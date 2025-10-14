from .imports import *
from .ssh_utils import run_local_cmd, run_ssh_cmd,run_any_cmd,run_cmd

class PathBackend(Protocol):
    def join(self, *parts: str) -> str: ...
    def isfile(self, path: str) -> bool: ...
    def isdir(self, path: str) -> bool: ...
    def glob_recursive(self, base: str) -> List[str]: ...

# -------- Local FS --------
class LocalFS:
    def join(self, *parts: str) -> str:
        return os.path.join(*parts)

    def isfile(self, path: str) -> bool:
        return os.path.isfile(path)

    def isdir(self, path: str) -> bool:
        return os.path.isdir(path)

    def glob_recursive(self, base: str) -> List[str]:
        pattern = os.path.join(base, "**", "*")
        return glob.glob(pattern, recursive=True)

# -------- SSH FS --------
class SSHFS:
    """
    Remote file ops using `ssh user@host` and POSIX paths.
    Paths are treated as absolute or relative to `base` you pass in.
    """
    def __init__(self, user_at_host: str):
        self.user_at_host = user_at_host

    def join(self, *parts: str) -> str:
        # remote uses POSIX joining
        return posixpath.join(*parts)

    def _test(self, flag: str, path: str) -> bool:
        # -f (file), -d (dir)
        cmd = f"test {flag} {shlex.quote(path)} && echo __OK__ || true"
        out = run_ssh_cmd(self.user_at_host, cmd, workdir=None)
        return "__OK__" in (out or "")

    def isfile(self, path: str) -> bool:
        return self._test("-f", path)

    def isdir(self, path: str) -> bool:
        return self._test("-d", path)

    def glob_recursive(self, base: str) -> List[str]:
        # Use `find` to emulate glob **/*
        # Only return files & dirs; skip sockets/pipes/etc.
        # -L optional if you want to follow symlinks.
        cmd = f"find {shlex.quote(base)} -mindepth 1 -printf '%p\\n' 2>/dev/null"
        out = run_ssh_cmd(self.user_at_host, cmd, workdir=None)
        if not out:
            return []
        items = [line.strip() for line in out.splitlines() if line.strip()]
        return items
# -------- Helpers to parse item strings --------



def normalize_items(items: Iterable[str]) -> List[Tuple[PathBackend, str]]:
    """
    Map each item to (backend, root_path).
    Local paths -> (LocalFS(), path)
    Remote specs "user@host:/abs/path" -> (SSHFS(user@host), /abs/path)
    """
    pairs: List[Tuple[PathBackend, str]] = []
    for item in items:
        if not item:
            continue
        m = REMOTE_RE.match(item)
        if m:
            host = m.group("host")
            path = m.group("path")
            pairs.append((SSHFS(host), path))
        else:
            pairs.append((LocalFS(), item))
    return pairs
