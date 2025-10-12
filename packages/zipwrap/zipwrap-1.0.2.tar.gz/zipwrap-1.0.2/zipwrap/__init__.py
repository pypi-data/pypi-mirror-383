"""
zipwrap
-------

A config-driven wrapper around the Linux `zip` CLI

Usage:
    zipwrap --config config.json
    zipwrap --root . --include "*.py" --exclude "venv/**" --outfile dist/code.zip --recurse --compression 9
"""
DEFAULTS = {
    "root": ".",
    "include": ["*"],
    "exclude": [".venv/**", "venv/**", "*.zip"],
    "outfile": "archive.zip",
    "recurse": True,
    "compression": 9,
}

__all__ = [DEFAULTS]
