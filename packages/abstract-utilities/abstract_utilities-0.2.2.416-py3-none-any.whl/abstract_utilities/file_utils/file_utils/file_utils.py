from .imports import *
# -------- Public API drop-ins that mirror your originals --------
from .filter_params import *
from .file_filters import *
def make_allowed_predicate(cfg: ScanConfig, *, isdir=None, isfile=None) -> Callable[[str], bool]:
    def _isdir(p: str) -> bool: return isdir(p) if isdir else Path(p).is_dir()
    def _isfile(p: str) -> bool: return isfile(p) if isfile else Path(p).is_file()
    def allowed(path: str) -> bool:
        name = os.path.basename(path).lower()
        path_str = path.lower()

        if cfg.exclude_dirs:
            for dpat in cfg.exclude_dirs:
                d = dpat.lower()
                if d in path_str or fnmatch.fnmatch(name, d):
                    if _isdir(path) or d in path_str:
                        return False

        if cfg.exclude_patterns:
            for pat in cfg.exclude_patterns:
                if fnmatch.fnmatch(name, pat.lower()):
                    return False

        if _isfile(path):
            ext = os.path.splitext(name)[1].lower()
            if (cfg.allowed_exts and ext not in cfg.allowed_exts) or (cfg.unallowed_exts and ext in cfg.unallowed_exts):
                return False
        return True
    return allowed

def get_globs(paths, recursive: bool = True, allowed=None, **kwargs) -> List[str]:
    roots = [p for p in make_list(paths) if p]
    res: List[str] = []
    if recursive:
        kwargs.setdefault("mindepth", 1)
    else:
        kwargs.setdefault("mindepth", 1)
        kwargs.setdefault("maxdepth", 1)
    for fs, root in normalize_items(roots, **kwargs):
        gl = fs.glob_recursive(root, **kwargs)
        if allowed:
            gl = [p for p in gl if allowed(p)]
        res.extend(gl)
    return res

def get_allowed_files(paths, allowed=True, **kwargs) -> List[str]:
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate(ScanConfig())
    elif allowed is False:
        allowed = (lambda *_: True)

    roots = [p for p in make_list(paths) if p]
    out: List[str] = []
    kwargs = {**kwargs, "include_files": True, "include_dirs": False}
    for fs, root in normalize_items(roots):
        if fs.isdir(root):
            for p in fs.glob_recursive(root, **kwargs):
                if allowed and not allowed(p): continue
                if fs.isfile(p): out.append(p)
        else:
            if allowed and not allowed(root): continue
            if fs.isfile(root): out.append(root)
    return out

def get_allowed_dirs(paths, allowed=False, **kwargs) -> List[str]:
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate(ScanConfig())
    else:
        allowed = (lambda *_: True)

    roots = [p for p in make_list(paths) if p]
    out: List[str] = []
    kwargs = {**kwargs, "include_files": False, "include_dirs": True}
    for fs, root in normalize_items(roots):
        if fs.isdir(root):
            if (not allowed) or allowed(root):
                out.append(root)
            for p in fs.glob_recursive(root, **kwargs):
                if (not allowed) or allowed(p):
                    if fs.isdir(p): out.append(p)
    return out

def get_filtered_files(paths, allowed=None, files: List[str] | None = None, **kwargs) -> List[str]:
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate(ScanConfig())
    else:
        allowed = (lambda *_: True)

    files = files or []
    roots = [p for p in make_list(paths) if p]
    out: List[str] = []
    kwargs = {**kwargs, "include_files": True, "include_dirs": False}
    for fs, root in normalize_items(roots):
        for p in fs.glob_recursive(root, **kwargs):
            if p in files: continue
            if allowed and not allowed(p): continue
            if fs.isfile(p): out.append(p)
    return out

def get_filtered_dirs(paths, allowed=None, dirs: List[str] | None = None, **kwargs) -> List[str]:
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate(ScanConfig())
    else:
        allowed = (lambda *_: True)

    dirs = dirs or []
    roots = [p for p in make_list(paths) if p]
    out: List[str] = []
    kwargs = {**kwargs, "include_files": False, "include_dirs": True}
    for fs, root in normalize_items(roots):
        for p in fs.glob_recursive(root, **kwargs):
            if p in dirs: continue
            if allowed and not allowed(p): continue
            if fs.isdir(p): out.append(p)
    return out

def get_all_allowed_files(paths, allowed=None, **kwargs) -> List[str]:
    dirs = get_all_allowed_dirs(paths, allowed=allowed, **kwargs)
    files = get_allowed_files(paths, allowed=allowed, **kwargs)
    seen = set(files)
    for fs, directory in normalize_items(dirs):
        for p in fs.glob_recursive(directory, **kwargs):
            if p in seen: continue
            if allowed and not allowed(p): continue
            if fs.isfile(p):
                files.append(p); seen.add(p)
    return files

def get_all_allowed_dirs(paths, allowed=None, **kwargs) -> List[str]:
    if allowed is not False:
        if allowed is True:
            allowed = None
        allowed = allowed or make_allowed_predicate(ScanConfig())
    else:
        allowed = (lambda *_: True)

    roots = [p for p in make_list(paths) if p]
    out: List[str] = []
    seen = set()
    kwargs = {**kwargs, "include_dirs": True}
    for fs, root in normalize_items(roots):
        if fs.isdir(root) and ((not allowed) or allowed(root)):
            out.append(root); seen.add(root)
        for p in fs.glob_recursive(root, **kwargs):
            if p in seen: continue
            if allowed and not allowed(p): continue
            if fs.isdir(p):
                out.append(p); seen.add(p)
    return out
def get_files_and_dirs(
    directory: str | list[str]=None,
    cfg: Optional["ScanConfig"] = None,
    allowed_exts: Optional[Set[str]] = False,
    unallowed_exts: Optional[Set[str]] = False,
    exclude_types: Optional[Set[str]] = False,
    exclude_dirs: Optional[List[str]] = False,
    exclude_patterns: Optional[List[str]] = False,
    add: bool = False,
    recursive: bool = True,
    include_files: bool = True,
    paths: str | list[str]=None,
    **kwargs
):
    cfg = cfg or define_defaults(
        allowed_exts=allowed_exts,
        unallowed_exts=unallowed_exts,
        exclude_types=exclude_types,
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        add=add,
    )
    # make predicate backend-agnostic here; the per-backend calls below pass strings only
    allowed = make_allowed_predicate(cfg)

    if recursive:
        kwargs.setdefault("mindepth", 1)
    else:
        kwargs.setdefault("mindepth", 1)
        kwargs.setdefault("maxdepth", 1)

    roots = make_list(directory or paths)
    items = get_globs(roots, recursive=recursive, allowed=allowed, **kwargs)

    dirs = get_allowed_dirs(items, allowed=allowed, **kwargs)
    files = get_allowed_files(items, allowed=allowed, **kwargs) if include_files else []
    return dirs, files
