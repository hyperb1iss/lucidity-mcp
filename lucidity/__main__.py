"""Lucidity main module.

This module allows the package to be run directly with `python -m lucidity`.
"""

import sys

from .server import main

if __name__ == "__main__":
    sys.exit(main())
