#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests configuration."""
from __future__ import annotations
from pathlib import Path
import sys


def pytest_sessionstart():
    """Initialize tests."""
    print("test_init()")
    path = str(Path(__file__).parent.parent/"src")
    print(path)
    if path not in sys.path:
        sys.path.append(path)
