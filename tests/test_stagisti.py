#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test `stagisti.py`."""
import os
from pathlib import Path
from subprocess import check_output
import sys

def test_stagisti():
    """Test `stagisti.py`."""
    assert check_output(
        [
            sys.executable,
            str(Path(__file__).parent.parent/"src"/"stagisti.py"),
            "-q"
        ],
        env=os.environ.copy()
    ).decode("utf-8").strip() == "['Rosalinda', 'Riccardo', 'Giacomo', 'Jacopo']"
