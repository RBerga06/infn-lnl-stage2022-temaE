#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-error
"""Test `spettro.py`."""
from __future__ import annotations
import sys
from pathlib import Path
from conftest import sys_argv, MPLTest
from spettro import main as _test


mpl = MPLTest()


@mpl.tests(0, "spettro.png")
@mpl.collects(reset=True)
def test_ui():
    """Test `main(...)`"""
    with sys_argv([sys.argv[0], str((Path(__file__).parent.parent/"src"/"fondo.root").resolve()), *sys.argv[1:]]):
        _test()
