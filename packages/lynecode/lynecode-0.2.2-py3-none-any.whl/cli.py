"""
Thin CLI wrapper to support `lyne code [path]` in addition to `lynecode [path]`.

This module forwards to `main.main` while ensuring the path argument is
resolved to an absolute path when omitted.
"""

import sys
from pathlib import Path
import argparse


def entry() -> None:
    """CLI entry point for the `lyne` command.

    Supports:
    - lyne code [path]
    - lyne [path]               (treated the same as `lyne code [path]`)
    """
    import main as lyne_main

    parser = argparse.ArgumentParser(
        prog="lyne",
        description="Lyne: Intelligent File & Text Manipulation System"
    )

    subparsers = parser.add_subparsers(dest="command")

    code_parser = subparsers.add_parser(
        "code", help="Run Lyne on a path (default subcommand)"
    )
    code_parser.add_argument(
        "path",
        nargs="?",
        help="Path to operate on; if omitted, uses the absolute current working directory"
    )

    parser.add_argument(
        "fallback_path",
        nargs="?",
        help=argparse.SUPPRESS
    )

    args, unknown = parser.parse_known_args()

    if args.command in (None, "code"):
        provided_path = getattr(args, "path", None) or getattr(args, "fallback_path", None)
        if provided_path:
            target_path = str(Path(provided_path).resolve())
        else:
            target_path = str(Path.cwd().resolve())

        original_argv = list(sys.argv)
        try:
            sys.argv = [original_argv[0], target_path] + list(unknown)
            lyne_main.main()
        finally:
            sys.argv = original_argv
        return

    parser.print_help()


if __name__ == "__main__":
    entry()