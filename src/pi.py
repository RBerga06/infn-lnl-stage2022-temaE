#!/usr/bin/env python3
from rand import TrueRandomGenerator
import matplotlib.pyplot as plt
from math import pi as PI
import random
import sys
import os

# Costanti
K = 255**2
BUG = True


# Calcolo di π con metodo Monte Carlo e numeri casuali generati con TrueRandomGenerator
def main():
    # Determina l'algoritmo da utlizzare
    width = os.get_terminal_size().columns          # Larghezza del terminale
    title = " Monte Carlo Method π Approximator "   # Titolo
    around = "=" * (max(0, width - len(title))//2)  # Testo da inserire attorno al titolo
    print(around, title, around, sep="")
    print(f"""
>>> Choose an algorithm:
 [0] Interpret data as sequential (x, y) points.
 [1] Interpret data as adjacent/linked (x, y) points.
 [2] Generate every possible (x, y) combination.
 [3] Use pseudo-random (x, y) points.\
""")
    # Richiede all'utente l'algoritmo da utilizzare (il valore di "_mode")
    while True:
        try:
            _mode = int(input("> "))
        # Gestione errori: per terminare il programma
        except (KeyboardInterrupt, EOFError, OSError):
            sys.exit(0)
        # Gestione errori: input non intero (chiede nuovamente)
        except:
            print("[!] Please type in an integer (0|1|2|3)!")
            continue
        # Numero intero: ok
        else:
            # Troppo grande o troppo piccolo (chiede nuovamente)
            if _mode > 3 or _mode < 0:
                print("[!] Invalid integer (has to be in [0, 3])!")
                continue
            # Tutto ok: "_mode" è impostato e si continua col programma
            break

    # Inizializzazione
    TRG = TrueRandomGenerator(bug=BUG)  # Generatore
    LEN = TRG.nRandomNumbers            # Numero di valori casuali disponibili
    N_in:     int         = 0   # Numero di coordinate casuali all'interno del cerchio
    x_in:     list[int]   = []  # Lista delle coordinate x all'interno del cerchio
    y_in:     list[int]   = []  # Lista delle coordinate y all'interno del cerchio
    x_out:    list[int]   = []  # Lista delle coordinate x all'esterno del cerchio
    y_out:    list[int]   = []  # Lista delle coordinate y all'esterno del cerchio
    pi_array: list[float] = []  # Lista delle stime di π nel tempo
    pi:       float       = 0   # Stima di π, ricalcolata ad ogni iterazione

    # ------------------------- Metodo 1: base, O(n) --------------------------
    if _mode == 0:
        for i in range (LEN // 2):
            # Generazione di coordinate con due numeri casuali sequenziali
            x = TRG.random_number()
            y = TRG.random_number()

            # Se il punto di coordinate (x, y) appartiene al 1/4 di cerchio di raggio 255...
            if x**2 + y**2 <= K:
                N_in = N_in + 1  # ... incrementa il numero di coordinate all'interno ...
                x_in.append(x)   # ... salva la coordinata x nella lista dedicata ...
                y_in.append(y)   # ... salva la coordinata y nella lista dedicata ...
            else: # ... altrimenti le coordinate (x, y) non appartengono al cerchio ...
                x_out.append(x)  # ... salva la coordinata x nella lista dedicata ...
                y_out.append(y)  # ... salva la coordinata y nella lista dedicata.

            pi = N_in * 4 / (i + 1)  # Calcolo di π ad ogni ciclo
            pi_array.append(pi)  # Salva "pi" nella lista dedicata

        # Disegna i punti nel piano cartesiano
        plt.scatter(x_in,  y_in,  marker = ".")
        plt.scatter(x_out, y_out, marker = ".")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

        # Disegno andamento della stima di π in funzione del numero di coordinate
        plt.plot(pi_array)
        plt.plot([PI] * (LEN // 2), linestyle = "dashed")
        plt.show()

    # -------------- Metodo 2: coppie di valori adiacenti, O(n) ---------------
    elif _mode == 1:
        y = TRG.random_number()       # Assegnazione valore di default (pre-ciclo)
        for i in range (LEN-1):
            x = y                     # Assegnazione a "x" del numero casuale "y" precedentemente utilizzato
            y = TRG.random_number()   # Creazione nuovo numero casuale
            if x**2 + y**2 <= K:      # Analogo al metodo 1
                N_in = N_in + 1
                x_in.append(x)
                y_in.append(y)
            else:
                x_out.append(x)
                y_out.append(y)

            pi = N_in * 4 / (i + 1)
            pi_array.append(pi)

        plt.scatter(x_out, y_out, marker = ".")
        plt.scatter(x_in,  y_in,  marker = ".")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

        plt.plot(pi_array)
        plt.plot([PI] * (LEN - 1), linestyle = "dashed")
        plt.show()

    # ------------ Metodo 3: tutte le coordinate possibili, O(n^2) ------------
    elif _mode == 2:
        bytes = [b**2 for b in TRG.randomNumbers]   # Pre-calcolo dei quadrati, per ottimizzazione

        for i, x in enumerate(bytes):       # "x" scorre vettore "bytes", "i" l'indice
            for y in bytes:                 # "y" scorre vettore "bytes"
                if x + y <= K:              # Analogo al metodo 1
                    N_in += 1
            pi_array.append(N_in * 4 / (LEN * (i + 1)))

        pi = N_in * 4 / LEN**2            # Calcolo stima finale di π

        # Andamento di pi in funzione del numero di coordinate
        plt.plot(pi_array, marker = ".", linestyle = "")
        plt.plot([PI] * LEN, linestyle = "dashed")
        plt.show()

    # ---------------------- Metodo pseudocasuali, O(n) -----------------------
    else:
        # Procedimento analogo al metodo 1, eccetto che i numeri "casuali" utilizzati sono
        #   generati in maniera pseudocasuale dal computer.

        for i in range (LEN*100):           # I valori sono 100 volte di più di quelli del metodo 1
            x = random.randint(0, 255)
            y = random.randint(0, 255)
            if x**2 + y**2 <= K:
                N_in = N_in +1
                x_in.append(x)
                y_in.append(y)
            else:
                x_out.append(x)
                y_out.append(y)

            pi = N_in * 4 / (i + 1)
            pi_array.append(pi)

        plt.scatter(x_out, y_out, marker = ".")
        plt.scatter(x_in,  y_in,  marker = ".")
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

        plt.plot(pi_array)
        plt.plot([PI] * LEN * 100, linestyle = "dashed")
        plt.show()

    # Stampa la stima finale di π
    print(pi)



# Chiama "main()" quando il programma viene eseguito direttamente
if __name__ == '__main__':
    main()
