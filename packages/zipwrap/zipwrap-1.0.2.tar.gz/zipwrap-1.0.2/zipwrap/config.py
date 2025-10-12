from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
from typing import Iterable, Sequence

from zipwrap import DEFAULTS


@dataclass(frozen=True)
class Config:
    """Runtime configuration for zipwrap."""

    root: Path
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    outfile: Path
    recurse: bool
    compression: int

    @staticmethod
    def from_sources(args: argparse.Namespace, config_path: Path | None) -> "Config":
        """
        Build final config by layering JSON (if present) under CLI flags.
        CLI always wins. Missing values fall back to DEFAULTS.
        """
        data = dict(DEFAULTS)
        if config_path:
            with config_path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if not isinstance(loaded, dict):
                raise ValueError("Config JSON must be an object at the top level.")
            data.update({k: v for k, v in loaded.items() if v is not None})

        def normalize_list(maybe_list, default: Sequence[str]) -> tuple[str, ...]:
            if maybe_list is None:
                return tuple(default)
            if isinstance(maybe_list, str):
                return (maybe_list,)
            if isinstance(maybe_list, Iterable):
                return tuple(str(x) for x in maybe_list)
            raise TypeError("List-like expected for include/exclude")

        # CLI overrides
        root = Path(args.root if args.root is not None else data.get("root", DEFAULTS["root"])).resolve()
        include = normalize_list(args.include if args.include else data.get("include", DEFAULTS["include"]), DEFAULTS["include"])
        exclude = normalize_list(args.exclude if args.exclude else data.get("exclude", DEFAULTS["exclude"]), DEFAULTS["exclude"])
        outfile = Path(args.outfile if args.outfile is not None else data.get("outfile", DEFAULTS["outfile"]))

        if getattr(args, "recurse", None) is True:
            recurse = True
        elif getattr(args, "no_recurse", None) is True:
            recurse = False
        else:
            recurse = bool(data.get("recurse", DEFAULTS["recurse"]))

        compression = int(args.compression if args.compression is not None else data.get("compression", DEFAULTS["compression"]))
        compression = max(0, min(9, compression))

        if not outfile.is_absolute():
            outfile = (root / outfile).resolve()

        if not outfile.parent.exists():
            outfile.parent.mkdir(parents=True, exist_ok=True)

        return Config(root=root, include=include, exclude=exclude, outfile=outfile, recurse=recurse, compression=compression)
