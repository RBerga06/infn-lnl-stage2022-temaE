#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa `root.py`"""
from __future__ import annotations
from subprocess import check_output
import sys
from typing import Any

from root import ROOT


def _print_backend():
    print("PyROOT" if ROOT else "uproot")


def _backend(**vars: Any) -> str:
    return check_output(
        [sys.executable, __file__, "-q"],
        env={key: str(val) for key, val in vars.items()},
    ).decode("utf-8")


class TestEnvVars:
    """Test environment variables support."""

    def test_FORCE_UPROOT_0(self):
        """FORCE_UPROOT=0"""
        assert _backend(FORCE_UPROOT=0) == "PyROOT"

    def test_FORCE_UPROOT_1(self):
        """FORCE_UPROOT=1"""
        assert _backend(FORCE_UPROOT=1) == "uproot"



if __name__ == "__main__":
    _print_backend()
