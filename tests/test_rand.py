#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-error
"""Test `rand.py`"""
from __future__ import annotations
from rand import cyclic_local_means


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
