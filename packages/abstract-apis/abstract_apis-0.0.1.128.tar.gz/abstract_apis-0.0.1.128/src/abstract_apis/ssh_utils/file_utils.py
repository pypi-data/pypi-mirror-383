from .imports import *
from .ssh_utils import *
from .ssh_classes import *
# -------- Public API drop-ins that mirror your originals --------

def get_globs(items: Iterable[str], recursive: bool = True, allowed: AllowedPredicate = None) -> List[str]:
    """
    Accepts a mixture of local paths and remote specs ("user@host:/abs/path").
    Returns a single list of paths (local or remote strings).
    """
    res: List[str] = []
    for fs, root in normalize_items(items):
        # Note: SSHFS ignores `recursive` flag because `find` inherently recurses.
        gl = fs.glob_recursive(root)
        if allowed:
            gl = [p for p in gl if allowed(p)]
        res.extend(gl)
    return res

def get_allowed_files(items: Iterable[str], allowed: AllowedPredicate = None) -> List[str]:
    out = []
    for fs, root in normalize_items(items):
        if fs.isdir(root):
            for p in fs.glob_recursive(root):
                if allowed and not allowed(p): 
                    continue
                if fs.isfile(p):
                    out.append(p)
        else:
            if allowed and not allowed(root):
                continue
            if fs.isfile(root):
                out.append(root)
    return out

def get_allowed_dirs(items: Iterable[str], allowed: AllowedPredicate = None) -> List[str]:
    out = []
    for fs, root in normalize_items(items):
        if fs.isdir(root):
            if (not allowed) or allowed(root):
                out.append(root)
            for p in fs.glob_recursive(root):
                if (not allowed) or allowed(p):
                    if fs.isdir(p):
                        out.append(p)
    return out

def get_filtered_files(items: Iterable[str], allowed: AllowedPredicate = None, files: List[str] | None = None) -> List[str]:
    files = files or []
    out = []
    for fs, root in normalize_items(items):
        for p in fs.glob_recursive(root):
            if p in files:
                continue
            if allowed and not allowed(p):
                continue
            if fs.isfile(p):
                out.append(p)
    return out

def get_filtered_dirs(items: Iterable[str], allowed: AllowedPredicate = None, dirs: List[str] | None = None) -> List[str]:
    dirs = dirs or []
    out = []
    for fs, root in normalize_items(items):
        for p in fs.glob_recursive(root):
            if p in dirs:
                continue
            if allowed and not allowed(p):
                continue
            if fs.isdir(p):
                out.append(p)
    return out

def get_all_allowed_files(items: Iterable[str], allowed: AllowedPredicate = None) -> List[str]:
    # Start with the “roots” first, then walk
    dirs = get_all_allowed_dirs(items, allowed=allowed)
    files = get_allowed_files(items, allowed=allowed)
    seen = set(files)
    # Reuse normalize so we know which backend applies to each dir
    for fs, directory in normalize_items(dirs):
        for p in fs.glob_recursive(directory):
            if p in seen:
                continue
            if allowed and not allowed(p):
                continue
            if fs.isfile(p):
                files.append(p)
                seen.add(p)
    return files

def get_all_allowed_dirs(items: Iterable[str], allowed: AllowedPredicate = None) -> List[str]:
    out = []
    seen = set()
    for fs, root in normalize_items(items):
        if fs.isdir(root) and ((not allowed) or allowed(root)):
            out.append(root); seen.add(root)
        for p in fs.glob_recursive(root):
            if p in seen:
                continue
            if allowed and not allowed(p):
                continue
            if fs.isdir(p):
                out.append(p)
                seen.add(p)
    return out
