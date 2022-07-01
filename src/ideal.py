import matplotlib.pyplot as plt
from math import pi as PI

def grid(N):
    TOT = N**2
    K = (N-1)**2
    N_in = 0
    N_out = 0
    for x in range(N):
        for y in range(N):
            v = x**2 + y**2 - K
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
    print(N, pim, piM, pi, sep=" \t")
    return pi


def theoretical(N, case):
    TOT = N**2
    N_in = int(PI * TOT / 4)
    if case == 0:
        print(N_in)
    elif case == 1:
        print(N_in * 4 / TOT)
        print(abs(PI - N_in * 4 / TOT))
    return N_in


if __name__ == "__main__":
    for N in range(1, 1024):
        grid(N)
    #theoretical(N, case)

    #diff = []
    #for i in range(500):
    #    diff.append(-ideal(i, case) + theoretical(i, case))
    #print()
    #print(diff)
#
    #plt.plot(diff)
    #plt.show()
