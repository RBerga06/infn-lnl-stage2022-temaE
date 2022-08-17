#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests configuration."""
from __future__ import annotations
from pathlib import Path
import sys


def fix_sys_path():
    """Fix `sys.path`."""
    path = str(Path(__file__).parent.parent/"src")
    if path not in sys.path:
        sys.path.append(path)


def pytest_sessionstart():
    """Initialize tests."""
    fix_sys_path()
