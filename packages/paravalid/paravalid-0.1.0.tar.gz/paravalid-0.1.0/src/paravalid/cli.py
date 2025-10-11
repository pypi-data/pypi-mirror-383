"""Command-line interface for paravalid."""

from __future__ import annotations

import argparse
import sys

from paravalid import __version__, is_nogil_available, is_nogil_active


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="paravalid",
        description="Parallel validation and serialization for Python 3.13+",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--check-nogil",
        action="store_true",
        help="Check if no-GIL Python is available and active",
    )

    args = parser.parse_args()

    if args.check_nogil:
        available = is_nogil_available()
        active = is_nogil_active()

        print(f"No-GIL available: {available}")
        print(f"No-GIL active: {active}")

        if available and active:
            print("\n✓ paravalid can use parallel execution with no-GIL")
            return 0
        elif available and not active:
            print(
                "\n⚠ No-GIL is available but not active. Run Python with PYTHON_GIL=0"
            )
            return 1
        else:
            print("\n✗ No-GIL is not available. paravalid will use sequential fallback")
            return 1

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
