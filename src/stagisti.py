#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Distribuisci le parti della presentazione casualmente fra gli stagisti."""
from rand import TrueRandomGenerator

g = TrueRandomGenerator()
for i in range(0x16):
    g.random_number()
stagisti = ["Rosalinda", "Jacopo", "Giacomo", "Riccardo"]
risultati = []
while len(risultati) < 4:
    stagista = stagisti[g.random_number() % 4]
    if stagista not in risultati:
        risultati.append(stagista)
print(risultati)
