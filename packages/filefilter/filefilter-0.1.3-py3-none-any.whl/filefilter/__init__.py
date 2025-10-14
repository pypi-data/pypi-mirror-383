__version__ = '0.1.3'

import json
import os
import re
from fnmatch import fnmatch


def filter_paths(config_json: str, resolve_base: str = "cwd") -> list[str]:
    """
    Given a JSON string defining 'root_dir' and 'filters',
    returns a list of file paths matching the rules.
    """
    data = json.loads(config_json)
    cfg = Config(data, resolve_base=resolve_base)
    return collect_files(cfg)


def normalize_path(p: str) -> str:
    """Collapse backslashes and multiple slashes to '/', trim whitespace (comparison only)."""
    p = re.sub(r"[\\/]+", "/", p)
    return p.strip()


def parse_dir_patterns(patterns):
    """
    Parse directory glob patterns into:
      - root-only patterns (first segment match)
      - anywhere patterns (any ancestor segment)
    Strips '**/' prefix and '/**' suffix, handles leading '/' for root-only.
    Case-insensitive via casefold().
    """
    root_patts = []
    any_patts = []
    for raw in patterns:
        p = normalize_path(raw)
        anchored = p.startswith("/")
        low = p.casefold()
        low = re.sub(r"^\*\*/", "", low)
        low = re.sub(r"/\*\*$", "", low)
        low = low.rstrip("/")
        if not low:
            continue
        if anchored:
            low = low.lstrip("/")  # compare to bare segment
            root_patts.append(low)
        else:
            any_patts.append(low)
    return root_patts, any_patts


def parse_file_patterns(patterns):
    """Normalize and casefold filename patterns (fnmatch semantics)."""
    return [normalize_path(p).casefold() for p in patterns]


def parse_extensions(patterns):
    """
    Normalize extensions so both 'ext' and '.ext' are treated the same.
    Stored as casefolded, with a leading '.'. Supports multi-dot suffixes.
    """
    out: list[str] = []
    for e in patterns or []:
        if not isinstance(e, str):
            continue
        s = e.strip().lstrip(".")
        if not s:
            continue
        out.append("." + s.casefold())
    return out


class Config:
    def __init__(self, data: dict, resolve_base: str = "cwd"):
        self.verbose = bool(data.get("verbose", False))

        raw_root_original = str(data["root_dir"]).strip()
        if os.path.isabs(raw_root_original):
            root = raw_root_original
        else:
            if resolve_base in ("", "cwd"):
                base_dir = os.getcwd()
            elif resolve_base == "script":
                base_dir = os.path.dirname(os.path.abspath(__file__))
            else:
                base_dir = resolve_base
            root = os.path.join(base_dir, raw_root_original)

        # OS-native absolute normalized root
        self.root_dir = os.path.abspath(os.path.normpath(root))

        inc = data["filters"]["include"]
        exc = data["filters"]["exclude"]

        # Include/Exclude directory patterns
        self.inc_dirs_root, self.inc_dirs_any = parse_dir_patterns(inc.get("dirs", []))
        self.exc_dirs_root, self.exc_dirs_any = parse_dir_patterns(exc.get("dirs", []))

        # Presence flags (so empty list can still mean "gate is enabled")
        self.inc_dirs_enabled = "dirs" in inc
        self.inc_exts_enabled = "extensions" in inc

        # Include/Exclude filename patterns
        self.include_files = parse_file_patterns(inc.get("files", []))
        self.exclude_files = parse_file_patterns(exc.get("files", []))

        # Include/Exclude extensions
        self.inc_exts = parse_extensions(inc.get("extensions", []))
        self.exc_exts = parse_extensions(exc.get("extensions", []))

        if self.verbose:
            print(f"[config] root_dir: {self.root_dir}")
            print(f"[config] include dirs enabled={self.inc_dirs_enabled}, root={self.inc_dirs_root}, any={self.inc_dirs_any}")
            print(f"[config] exclude dirs root={self.exc_dirs_root}, any={self.exc_dirs_any}")
            print(f"[config] include files={self.include_files}")
            print(f"[config] exclude files={self.exclude_files}")
            print(f"[config] include ext enabled={self.inc_exts_enabled}, list={self.inc_exts}")
            print(f"[config] exclude ext={self.exc_exts}")


def _name_endswith_any(name_cf: str, suffixes: list[str]) -> bool:
    """Case-insensitive suffix match for file name against extension list."""
    return any(name_cf.endswith(suf) for suf in suffixes)


def should_include(full_path: str, cfg: Config) -> bool:
    """Determine if a file should be included based on the config rules."""
    rel = os.path.relpath(full_path, cfg.root_dir)
    rel_cmp = normalize_path(rel).casefold()
    segments = rel_cmp.split("/")
    name_cf = segments[-1]
    ancestors = segments[:-1]

    if cfg.verbose:
        print(f"[check] {rel}")

    # 1) Include-files override (always wins)
    for patt in cfg.include_files:
        if fnmatch(name_cf, patt):
            if cfg.verbose:
                print(f"  -> include by filename pattern '{patt}'")
            return True

    # 2) Excludes: extension
    if cfg.exc_exts and _name_endswith_any(name_cf, cfg.exc_exts):
        if cfg.verbose:
            print(f"  -> excluded by extension in {cfg.exc_exts}")
        return False

    # 3) Excludes: filename
    for patt in cfg.exclude_files:
        if fnmatch(name_cf, patt):
            if cfg.verbose:
                print(f"  -> excluded by filename '{patt}'")
            return False

    # 4) Excludes: directories (root-only)
    if ancestors and cfg.exc_dirs_root:
        first = ancestors[0]
        for patt in cfg.exc_dirs_root:
            if fnmatch(first, patt):
                if cfg.verbose:
                    print(f"  -> excluded by root dir '{patt}'")
                return False

    # 5) Excludes: directories (anywhere)
    for seg in ancestors:
        for patt in cfg.exc_dirs_any:
            if fnmatch(seg, patt):
                if cfg.verbose:
                    print(f"  -> excluded by dir '{patt}'")
                return False

    # 6) Include by directories (allowlist behavior driven by presence)
    if cfg.inc_dirs_enabled:
        # If include.dirs is present but both lists are empty,
        # ONLY include-files are allowed. Since include-files check already failed, reject.
        if not cfg.inc_dirs_root and not cfg.inc_dirs_any:
            if cfg.verbose:
                print("  -> excluded: include.dirs present but empty (only include.files allowed)")
            return False

        # Otherwise enforce directory allowlist; root-level files pass the gate.
        if ancestors:
            ok = False
            if cfg.inc_dirs_root:
                first = ancestors[0]
                for patt in cfg.inc_dirs_root:
                    if fnmatch(first, patt):
                        ok = True
                        break
            if not ok and cfg.inc_dirs_any:
                for seg in ancestors:
                    for patt in cfg.inc_dirs_any:
                        if fnmatch(seg, patt):
                            ok = True
                            break
                    if ok:
                        break
            if not ok:
                if cfg.verbose:
                    print("  -> excluded: no matching include-dir pattern")
                return False

    # 7) Include by extension (allowlist) — enabled by presence
    if cfg.inc_exts_enabled:
        if not _name_endswith_any(name_cf, cfg.inc_exts):
            if cfg.verbose:
                print("  -> excluded: extension not in include list")
            return False

    if cfg.verbose:
        print("  -> included")
    return True


def collect_files(cfg: Config) -> list[str]:
    """Walk root_dir and collect files passing should_include."""
    matches: list[str] = []
    if cfg.verbose:
        print(f"[walk] scanning {cfg.root_dir}")

    for root, _, files in os.walk(cfg.root_dir, followlinks=False):
        for fn in files:
            full = os.path.join(root, fn)
            if os.path.islink(full):
                if cfg.verbose:
                    print(f"[skip] symlink: {full}")
                continue
            if should_include(full, cfg):
                matches.append(os.path.abspath(os.path.normpath(full)))

    if cfg.verbose:
        print(f"[result] total matches: {len(matches)}")
    return matches
