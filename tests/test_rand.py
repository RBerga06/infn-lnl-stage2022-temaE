#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-error
"""Test `rand.py`"""
from __future__ import annotations
from rand import SRC, TrueRandomGenerator as TRNG, cyclic_local_means, test as _test
from conftest import MPLTest


def test_clm():
    """Test the cyclic local means."""
    expected_results = [
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
        [0.5, 1.5, 2.5, 3.5, 4.5, 2.5],
        [2.0, 1.0, 2.0, 3.0, 4.0, 3.0],
        [2.0, 1.5, 2.5, 3.5, 3.0, 2.5],
        [2.4, 2.2, 2.0, 3.0, 2.8, 2.6],
        [2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
    ]
    for i, result in enumerate(expected_results):
        assert cyclic_local_means(list(range(6)), spread=i+1) == result


class TestTRNG:
    """Test the `TrueRandomGenerator` class."""

    def test_datafile_fondo(self):
        """Make sure the data from `fondo.root` is loaded correctly."""
        trng = TRNG(file=SRC/"fondo.root")
        first10 = [246, 108, 238, 243, 190, 5, 219, 82, 98, 57]
        assert trng.n_random_numbers == 177
        assert trng.random_numbers[:10] == first10
        for n in first10:
            assert trng.random_number() == n

    def test_datafile_data(self):
        """Make sure the data from `data.root` is loaded correctly."""
        trng = TRNG(file=SRC/"data.root")
        first10 = [87, 223, 176, 76, 234, 41, 75, 124, 232, 251]
        assert trng.n_random_numbers == 15513
        assert trng.random_numbers[:10] == first10
        for n in first10:
            assert trng.random_number() == n

    def test_bug(self):
        """Make sure the `bug=` flag works correctly."""
        trng = TRNG(file=SRC/"fondo.root", bug=True)
        first10 = [246, 108, 238, 243, 190, 5, 219, 82, 98,  57]
        last10  = [191, 241,  96, 193, 229, 8,  31, 110, 5, 193]
        assert trng.n_random_numbers == 354
        assert trng.random_numbers[:10] == first10
        assert trng.random_numbers[-10:] == last10


class TestPlots:
    """Test plots."""
    MPL = MPLTest()

    @MPL.collects()
    def test_plots(self):
        """Create plots."""
        _test()
        assert print(self.MPL.figures)

    for i, name in enumerate(["deltas", "bits", "bytes"]):
        MPL.test(i, f"rand_{name}.png", auto_def=True)
