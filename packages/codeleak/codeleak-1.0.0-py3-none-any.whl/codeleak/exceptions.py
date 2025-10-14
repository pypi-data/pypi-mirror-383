# -*- coding: utf-8 -*-
"""Custom exceptions for codeleak"""

import sys


class CodeleakError(Exception):
    """Base exception for all codeleak errors"""
    pass


def die(msg, code=1):
    """Print error and exit"""
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)
