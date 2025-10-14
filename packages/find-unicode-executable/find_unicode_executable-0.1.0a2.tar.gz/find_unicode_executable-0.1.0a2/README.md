# `find-unicode-executable`

A Python package that provides cross-platform Unicode executable path resolution. Like Unix `which` command but better.

## Features

- **Compatibility** - Python 2+, Windows and Unix-like systems supported
- **Generator-based** - finds all matching executables, not just the first one
- **Thread-safe** - no global state
- **Supports multi-call binaries** - DOES NOT follow symlinks to canonical paths (that would mess up `argv[0]` passed to multi-call binaries)

## Installation

```bash
pip install find-unicode-executable
```

## Usage Example

```python
# coding=utf-8
from __future__ import print_function
from find_unicode_executable import find_unicode_executable

# Find all Python executables in resolution order
# Sample output on Linux:
# /home/user/miniconda3/bin/python3.12
# /usr/bin/python3.10
# /usr/bin/python3.10
# Sample output on Windows:
# C:\Python38\python.exe
# C:\Python27\python.exe
for executable_path in find_unicode_executable(u'python'):
    print(executable_path)
```

### Windows-Specific Features

On Windows, the package automatically handles:

- `PATHEXT` environment variable (`.exe`, `.bat`, etc.)
- Current directory checking (Windows behavior)
- Case-insensitive matching

## Comparison to Alternatives

| Feature               | find-unicode-executable | `shutil.which` | Unix `which` |
|-----------------------|-------------------------|----------------|--------------|
| Multiple results      | ✅ Yes                   | ❌ No           | ❌ No         |
| Windows PATHEXT       | ✅ Yes                   | ✅ Yes          | ❌ No         |
| Thread-safe           | ✅ Yes                   | ✅ Yes          | ❌ No         |
| Follows symlinks      | ✅ Yes                   | ❌ No           | ❌ No         |
| Current dir (Windows) | ✅ Yes                   | ❌ No           | ❌ No         |

## Why Use This Package?

1. When you need **all** matches, not just the first one
2. For consistent behavior across platforms
3. When you need proper Windows executable resolution
4. For thread-safe executable finding
5. When you want to follow symlinks to real paths

## Contributing

Contributions welcome! Please open issues or pull requests on GitHub.

## License

This project is licensed under the [MIT License](LICENSE).