#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ciò che succederebbe con un dataset ideale."""
from __future__ import annotations
import sys
# from math import pi as PI
# import matplotlib.pyplot as plt


def grid(N):
    """Calcola π sia per eccesso e per difetto su una griglia di lato `N`."""
    TOT = N**2
    squares = [x**2 for x in range(N)]
    # K = (N - 1) ** 2
    K = squares[-1]  # l'ultimo valore di `squares` è in effetti K
    N_in = 0
    N_out = 0
    for X in squares:
        for Y in squares:
            v = X + Y - K
            if v == 0:
                N_in += 1
                N_out += 1
            elif v < 0:
                N_in += 1
            else:
                N_out += 1
    pim = N_in * 4 / TOT
    piM = (TOT - N_out) * 4 / TOT
    pi = (pim + piM) / 2
    print(f"{N}\t{pim:01.15f}\t{piM:01.15f}\t{pi:01.15f}")
    return pi


# def theoretical(N, case):
#     TOT = N**2
#     N_in = int(PI * TOT / 4)
#     if case == 0:
#         print(N_in)
#     elif case == 1:
#         print(N_in * 4 / TOT)
#         print(abs(PI - N_in * 4 / TOT))
#     return N_in


def main():
    """Main program."""
    N = 1
    while True:
        try:
            grid(N)
            N += 1
        except KeyboardInterrupt:
            sys.exit(0)
    # theoretical(N, case)
    # diff = []
    # for i in range(500):
    #    diff.append(-ideal(i, case) + theoretical(i, case))
    # print()
    # print(diff)
    # plt.plot(diff)
    # plt.show()


if __name__ == "__main__":
    main()
