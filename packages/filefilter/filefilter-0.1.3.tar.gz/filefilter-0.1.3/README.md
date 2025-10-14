
# File Filter Library

**Version:** 0.1.3

A lightweight, cross-platform Python utility for collecting files from a directory tree based on
configurable include/exclude patterns. Supports case-insensitive matching, multi-dot extensions, and
a verbose diagnostic mode for debugging filter behavior.

---

##  Features

- **Recursive file collection** using `os.walk`
- **Configurable JSON input** — specify `root_dir`, `filters`, and `verbose`
- **Include / Exclude rules** for:
  - Directories (root-anchored or anywhere)
  - Filenames (glob-style with `*` wildcards)
  - File extensions (`.ext` or `ext`, multi-dot supported)
- **Cross-platform** normalization of paths and extensions
- **Case-insensitive** matching (`casefold()`)
- **Verbose mode** for tracing inclusion/exclusion decisions

---

##  Installation

No external dependencies required beyond the Python standard library.

```bash
pip install filefilter
```

---

##  Basic Usage

### Minimal Example

```python
import json
from file_filter import filter_paths

config = {
    "root_dir": ".",
    "filters": {
        "include": {
            "dirs": [],
            "files": ["*.py"],
            "extensions": ["py"]
        },
        "exclude": {
            "dirs": ["__pycache__"],
            "files": [],
            "extensions": []
        }
    }
}

paths = filter_paths(json.dumps(config))
print(paths)
```

✅ **Output Example**
```
['/abs/path/project/main.py', '/abs/path/project/utils/helper.py']
```

---

## Configuration Schema

The library expects a JSON string with this shape:

```json
{
  "root_dir": "./project",
  "verbose": false,
  "filters": {
    "include": {
      "dirs": ["src", "/tests"],
      "files": ["*.py", "README.*"],
      "extensions": ["py", "tar.gz"]
    },
    "exclude": {
      "dirs": ["__pycache__", "build"],
      "files": ["temp_*"],
      "extensions": ["log"]
    }
  }
}
```

| Field | Type | Description |
|:------|:-----|:-------------|
| `root_dir` | `str` | Root directory for walking. Can be relative or absolute. |
| `verbose` | `bool` | Print diagnostic messages about filter decisions. |
| `filters.include` | `dict` | Inclusion patterns for dirs, files, and extensions. |
| `filters.exclude` | `dict` | Exclusion patterns for dirs, files, and extensions. |
| `/dir` prefix | — | Root-anchored pattern, matches only first-level directory. |
| `**/dir/**` | — | Recursive pattern; middle `**` is simplified as “any level”. |

---

## Verbose Mode Example

```python
config = {
    "root_dir": ".",
    "verbose": True,
    "filters": {
        "include": {
            "dirs": [],
            "files": ["*.md", "*.txt"],
            "extensions": []
        },
        "exclude": {
            "dirs": ["build"],
            "files": [],
            "extensions": []
        }
    }
}

filter_paths(json.dumps(config))
```

🗒️ Example Console Output:

```
[config] root_dir: /project
[walk] scanning /project
[check] readme.md
  -> include by filename pattern '*.md'
[check] build/tmp/log.txt
  -> excluded by dir 'build'
[result] total matches: 1
```

---

##  Typical Use Cases

### 1️⃣ Collect Python Source Files
```json
{
  "filters": {
    "include": { "dirs": [], "files": ["*.py"], "extensions": ["py"] },
    "exclude": { "dirs": ["__pycache__"], "files": [], "extensions": [] }
  }
}
```

### 2️⃣ Gather Documentation Only
```json
{
  "filters": {
    "include": { "dirs": [], "files": ["*.md", "*.rst"], "extensions": [] },
    "exclude": { "dirs": ["build"], "files": [], "extensions": [] }
  }
}
```

### 3️⃣ Extract Assets by Multi-Dot Extension
```json
{
  "filters": {
    "include": { "dirs": [], "files": [], "extensions": ["tar.gz"] },
    "exclude": { "dirs": [], "files": [], "extensions": [] }
  }
}
```

### 4️⃣ Verbose Debug Filtering
Set `"verbose": true` in config to trace decisions.

---

##  Notes & Implementation Details

- Files are returned as **absolute, OS-native normalized paths**.
- Directory matching is case-insensitive using `.casefold()`.
- Symlinked files are ignored (`islink()` skipped).
- Root-level files are always included when include-dir filters exist, unless explicitly excluded.

---

##  License

MIT License © 2025 devcoons

---

