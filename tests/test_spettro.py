#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-error
"""Test `spettro.py`."""
from __future__ import annotations
from pathlib import Path
import sys

from spettro import main as _test


def test_ui():
    """Test `main(...)`"""
    argv = sys.argv.copy()
    sys.argv.insert(1, str((Path(__file__).parent.parent/"src"/"fondo.root").resolve()))
    _test()
    sys.argv = argv.copy()
