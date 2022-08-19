#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa `root.py`"""
from __future__ import annotations
import os
from subprocess import check_output
import sys
from typing import Any

from conftest import fix_sys_path

fix_sys_path()  # Necessary for call from subprocess
from root import ROOT, test as _test


def _print_backend():
    print("PyROOT" if ROOT else "uproot")


def _backend(**vars: Any) -> str:
    return check_output(
        [sys.executable, __file__, "-q"],
        env={**os.environ, **{key: str(val) for key, val in vars.items()}},
    ).decode("utf-8").strip()


class TestEnvVars:
    """Test environment variables support."""

    def test_FORCE_UPROOT_0(self):
        """FORCE_UPROOT=0"""
        assert _backend(FORCE_UPROOT=0) in {"uproot", "PyROOT"}

    def test_FORCE_UPROOT_1(self):
        """FORCE_UPROOT=1"""
        assert _backend(FORCE_UPROOT=1) == "uproot"


def test_root_read():
    """`root.test()`"""
    _test()


if __name__ == "__main__":
    _print_backend()
