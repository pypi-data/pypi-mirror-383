from .imports import *
# -------- Public API drop-ins that mirror your originals --------
from .filter_params import *
from .file_filters import *
# -------------------------------------------------------------
# Wrapper: respects your original API and naming conventions
# -------------------------------------------------------------

def get_allowed_predicate(allowed=None):
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate()
    else:
        def allowed(*args):
            return True
    return allowed


# -------------------------------------------------------------
# Remote-aware globbing
# -------------------------------------------------------------
def get_globs(items, recursive: bool = True, allowed=None, **kwargs):
    """
    Behaves like your original get_globs(), but can traverse both
    local and remote paths transparently via normalize_items().
    """
    glob_paths = []
    roots = [p for p in make_list(items) if p]

    kwargs.setdefault("mindepth", 0)
    if not recursive:
        kwargs.setdefault("maxdepth", 1)
    
    for fs, root, _ in normalize_items(roots, **kwargs):
        # use the backend's recursive walker
        nu_items = fs.glob_recursive(root, **kwargs)
        if allowed:
           
            nu_items = [n for n in nu_items if n and allowed(n)]
            
        glob_paths += nu_items
    return glob_paths


# -------------------------------------------------------------
# Allowed filters
# -------------------------------------------------------------
def get_allowed_files(items, allowed=True, **kwargs):
    allowed = get_allowed_predicate(allowed=allowed)
    out = []
    for fs, item, _ in normalize_items(items, **kwargs):
        if fs.isfile(item) and allowed(item):
            out.append(item)
    return out


def get_allowed_dirs(items, allowed=False, **kwargs):
    allowed = get_allowed_predicate(allowed=allowed)
    out = []
    for fs, item, _ in normalize_items(items, **kwargs):
        if fs.isdir(item) and allowed(item):
            out.append(item)
    return out


# -------------------------------------------------------------
# Filtered sets
# -------------------------------------------------------------
def get_filtered_files(items, allowed=None, files=None, **kwargs):
    allowed = get_allowed_predicate(allowed=allowed)
    files = set(files or [])
    out = []
    for fs, root, _ in normalize_items(items, **kwargs):
        for p in fs.glob_recursive(root, **kwargs):
            if p in files:
                continue
            if allowed(p) and fs.isfile(p):
                out.append(p)
    return out


def get_filtered_dirs(items, allowed=None, dirs=None, **kwargs):
    allowed = get_allowed_predicate(allowed=allowed)
    dirs = set(dirs or [])
    out = []
    for fs, root, _ in normalize_items(items, **kwargs):
        for p in fs.glob_recursive(root, **kwargs):
            if p in dirs:
                continue
            if allowed(p) and fs.isdir(p):
                out.append(p)
    return out


# -------------------------------------------------------------
# Recursive expansion
# -------------------------------------------------------------
def get_all_allowed_files(items, allowed=None, **kwargs):
    dirs = get_all_allowed_dirs(items, allowed=allowed, **kwargs)
    files = get_allowed_files(items, allowed=allowed, **kwargs)
    seen = set(files)
    for fs, directory, _ in normalize_items(dirs, **kwargs):
        for p in fs.glob_recursive(directory, **kwargs):
            if p in seen:
                continue
            if allowed and not allowed(p):
                continue
            if fs.isfile(p):
                files.append(p)
                seen.add(p)
    return files


def get_all_allowed_dirs(items, allowed=None, **kwargs):
    allowed = get_allowed_predicate(allowed=allowed)
    out = []
    seen = set()
    for fs, root, _ in normalize_items(items, **kwargs):
        if fs.isdir(root) and allowed(root):
            out.append(root)
            seen.add(root)
        for p in fs.glob_recursive(root, **kwargs):
            if p in seen:
                continue
            if allowed(p) and fs.isdir(p):
                out.append(p)
                seen.add(p)
    return out


# -------------------------------------------------------------
# Unified directory scan
# -------------------------------------------------------------
def get_files_and_dirs(
    directory: str,
    cfg: Optional["ScanConfig"] = None,
    allowed_exts: Optional[Set[str]] = False,
    unallowed_exts: Optional[Set[str]] = False,
    exclude_types: Optional[Set[str]] = False,
    exclude_dirs: Optional[List[str]] = False,
    exclude_patterns: Optional[List[str]] = False,
    add=False,
    recursive: bool = True,
    include_files: bool = True,
    **kwargs
):
    """
    Same public signature as your original get_files_and_dirs(),
    but powered by backend objects (LocalFS or SSHFS).
    """
    cfg = cfg or define_defaults(
        allowed_exts=allowed_exts,
        unallowed_exts=unallowed_exts,
        exclude_types=exclude_types,
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        add=add
    )
    allowed = make_allowed_predicate(cfg)
    items = []
    files = []
    if recursive:
        items = get_globs(directory, recursive=recursive, allowed=allowed, **kwargs)
    else:
        for fs, base, _ in normalize_items(make_list(directory), **kwargs):
            try:
                items += [fs.join(base, name) for name in fs.listdir(base)]
            except Exception:
                pass

    dirs = get_allowed_dirs(items, allowed=allowed, **kwargs)
    if include_files:
        files = get_allowed_files(items, allowed=allowed, **kwargs)
    return dirs, files


# -------------------------------------------------------------
# Unchanged predicate builder
# -------------------------------------------------------------
def make_allowed_predicate(cfg: ScanConfig) -> Callable[[str], bool]:
    def allowed(path: str) -> bool:
        p = Path(path)
        name = p.name.lower()
        path_str = str(p).lower()

        # A) directory exclusions
        if cfg.exclude_dirs:
            for dpat in cfg.exclude_dirs:
                if dpat in path_str or fnmatch.fnmatch(name, dpat.lower()):
                    if p.is_dir() or dpat in path_str:
                        return False

        # B) filename pattern exclusions
        if cfg.exclude_patterns:
            for pat in cfg.exclude_patterns:
                if fnmatch.fnmatch(name, pat.lower()):
                    return False

        # C) extension gates
        if p.is_file():
            ext = p.suffix.lower()
            if (cfg.allowed_exts and ext not in cfg.allowed_exts) or \
               (cfg.unallowed_exts and ext in cfg.unallowed_exts):
                return False
        return True
    return allowed
