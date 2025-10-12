#!/usr/bin/env python3
"""
zipwrap.cli
===========

A config-driven wrapper around the Linux `zip` command for Linux environments.

Config schema (dict[str, list[str] | str | bool | int]):
{
  "root": ".",
  "include": ["*"],
  "exclude": [".venv/**", "venv/**", "*.zip"],
  "outfile": "archive.zip",
  "recurse": true,
  "compression": 9
}
"""
from __future__ import annotations

import argparse
import fnmatch
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from tqdm import tqdm

from zipwrap.config import Config
from zipwrap import DEFAULTS  # noqa: F401


def _zip_available() -> bool:
    """Check whether the `zip` executable exists in PATH."""
    return shutil.which("zip") is not None


def _glob_many(root: Path, patterns: Sequence[str], recurse: bool) -> List[Path]:
    """
    Resolve many glob patterns (files only). If `recurse` is True, patterns are used with rglob; otherwise glob.
    Patterns are evaluated relative to `root`.
    """
    results: list[Path] = []
    for pat in patterns:
        try:
            iterator = root.rglob(pat) if recurse else root.glob(pat)
            for p in iterator:
                if p.is_file():
                    results.append(p.resolve())
        except Exception:
            continue
    return results


def _filter_excludes(root: Path, files: Sequence[Path], exclude_patterns: Sequence[str], recurse: bool) -> List[Path]:
    """
    Remove files matching any exclude pattern. We match against POSIX-style paths relative to root.
    Using fnmatch for flexible wildcards, applied to relative strings.
    """
    rel_map = {f: f.relative_to(root).as_posix() for f in files}
    excluded_rel: set[str] = set()

    # Precompute excluded sets via glob for correctness with ** semantics.
    excluded_files = set(_glob_many(root, exclude_patterns, recurse))
    for f in excluded_files:
        if f in rel_map:
            excluded_rel.add(rel_map[f])

    # Also honor fnmatch for patterns that didn't arise from glob
    out: list[Path] = []
    for f, rel in rel_map.items():
        if any(fnmatch.fnmatch(rel, pat) for pat in exclude_patterns):
            continue
        if rel in excluded_rel:
            continue
        out.append(f)
    return out


def collect_files(root: Path, include: Sequence[str], exclude: Sequence[str], recurse: bool, outfile: Path | None = None) -> List[Path]:
    """
    Compute the final list of files to zip.
    """
    included = _glob_many(root, include, recurse)
    filtered = _filter_excludes(root, included, exclude, recurse)

    if outfile:
        try:
            if outfile.is_relative_to(root):
                filtered = [p for p in filtered if p.resolve() != outfile.resolve()]
        except AttributeError:
            # py3.10 fallback
            try:
                outfile.relative_to(root)
                filtered = [p for p in filtered if p.resolve() != outfile.resolve()]
            except ValueError:
                pass

    # Deduplicate while retaining stable order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in filtered:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def run_zip(root: Path, outfile: Path, files: Sequence[Path], compression: int, logger: logging.Logger) -> int:
    """
    Invoke the system `zip` command to create/update the archive.
    """
    if not _zip_available():
        logger.error("zip executable not found in PATH.")
        return 127

    flags = [f"-{compression}", "-q", "-X", "-y"]
    cmd = ["zip", *flags, str(outfile)]
    rel_files = [str(p.relative_to(root)) for p in files]

    logger.debug("Executing: %s", " ".join(cmd + rel_files))
    proc = subprocess.run(cmd + rel_files, cwd=str(root), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if proc.returncode == 12:
        logger.warning("zip reported: nothing to do (no files matched).")
        return 12
    if proc.returncode != 0:
        logger.error("zip failed with exit code %d. Stderr:\n%s", proc.returncode, proc.stderr)
    return proc.returncode


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build the CLI parser. CLI overrides config. Progress bar stays on stdout.
    """
    p = argparse.ArgumentParser(prog="zipwrap", description="Config-driven wrapper around Linux `zip` with tqdm.")
    p.add_argument("-c", "--config", type=str, help="Path to config JSON.")
    p.add_argument("--root", type=str, help="Root directory to zip from (default: config or .).")
    p.add_argument("--include", action="append", help="Glob pattern(s) to include. Repeatable. If absent, uses config or '*'.")
    p.add_argument("--exclude", action="append", help="Glob pattern(s) to exclude. Repeatable.")
    p.add_argument("--outfile", type=str, help="Output archive path. Relative paths resolve under --root.")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--recurse", action="store_true", default=None, help="Recurse into subdirectories while matching.")
    group.add_argument("--no-recurse", action="store_true", default=None, help="Do not recurse into subdirectories while matching.")
    p.add_argument("--compression", type=int, choices=range(0, 10), metavar="{0..9}", help="Compression level (0..9).")
    p.add_argument("--verbose", action="store_true", help="Enable debug logging to stderr.")
    p.add_argument("--log-file", type=str, help="Optional path to a logfile (stderr otherwise).")
    return p


def configure_logging(verbose: bool, log_file: str | None) -> logging.Logger:
    """
    Set up logging on stderr or a file. Progress bar owns stdout exclusively.
    """
    logger = logging.getLogger("zipwrap")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    handler: logging.Handler
    if log_file:
        handler = logging.FileHandler(log_file, encoding="utf-8")
    else:
        handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def main(argv: Sequence[str] | None = None) -> int:
    """
    Entrypoint. Parse args, build config, collect files with a progress bar,
    and shell out to `zip`.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    logger = configure_logging(verbose=args.verbose, log_file=args.log_file)

    config_path = Path(args.config).resolve() if args.config else None
    config = Config.from_sources(args, config_path)

    logger.info("Root: %s", config.root)
    logger.info("Outfile: %s", config.outfile)
    logger.debug("Include: %s", ", ".join(config.include))
    logger.debug("Exclude: %s", ", ".join(config.exclude))
    logger.info("Recurse: %s | Compression: %d", config.recurse, config.compression)

    # Stage 1: Include pass
    stage1 = _glob_many(config.root, config.include, config.recurse)
    with tqdm(total=len(stage1), desc="Scanning includes", unit="file", leave=False) as bar:
        for _ in stage1:
            bar.update(1)

    # Stage 2: Exclusion filter
    final_files = collect_files(config.root, config.include, config.exclude, config.recurse, outfile=config.outfile)
    with tqdm(total=len(final_files), desc="Finalizing list", unit="file", leave=False) as bar:
        for _ in final_files:
            bar.update(1)

    if not final_files:
        logger.warning("No files matched after filters; nothing to zip.")
        return 12

    rc = run_zip(config.root, config.outfile, final_files, config.compression, logger)
    if rc == 0:
        logger.info("Wrote archive: %s (%d files)", config.outfile, len(final_files))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
