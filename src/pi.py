#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilizza il TRNG per stimare π tramite il metodo Monte Carlo."""
from rand import TrueRandomGenerator
import matplotlib.pyplot as plt
from math import pi as PI
from pathlib import Path
import random
import sys
import os


# Costanti
K = 255**2
SRC = Path(__file__).parent  # Cartella di questo file


def bug(default: bool, /) -> bool:
    """Determina se è stato attivato il “bug” da riga di comando."""
    # $ python pi.py                 # --> di default
    # $ python pi.py --bug           # --> attivo
    # $ python pi.py --no-bug        # --> disattivato
    # $ python pi.py --no-bug --bug  # --> attivo      (--bug sovrascrive --no-bug)
    # $ python pi.py --bug --no-bug  # --> disattivato (--no-bug sovrascrive --bug)
    if "--bug" in sys.argv:
        if "--no-bug" in sys.argv:
            BUG = sys.argv[::-1].index("--bug") < sys.argv[::-1].index("--no-bug")
            sys.argv = [x for x in sys.argv if x not in ("--no-bug", "--bug")]
            return BUG
        else:
            sys.argv = [x for x in sys.argv if x != "--bug"]
            return True
    elif "--no-bug" in sys.argv:
        sys.argv = [x for x in sys.argv if x != "--no-bug"]
        return False
    return default


def mode() -> int:
    """Determina l'algoritmo da utilizzare"""
    # Controlla se l'algoritmo è stato selezionato da riga di comando.
    #   Struttura del vettore "sys.argv":
    #     $ python /path/to/script.py a1 a2 a3
    #     sys.argv = ["/path/to/script.py", "a1", "a2", "a3"]
    if len(sys.argv) > 1:
        # Ci sono almeno 2 valori in sys.argv, quindi è stato inserito almeno un argomento
        try:
            _mode = int(sys.argv[1])
        except BaseException:
            # Gestione errori: se il modo selezionato dalla riga di comando
            #   non è valido, continua con la selezione interattiva
            pass
        else:
            # Controlla se il numero inserito è valido
            if 0 <= _mode <= 3:
                # Valido
                return _mode
            else:
                # Invalido: continua con la selezione interattiva
                pass
    # Selezione interattiva dell'algoritmo
    print(f"""
>>> Choose an algorithm:
 [0] Interpret data as sequential (x, y) points.
 [1] Interpret data as adjacent/linked (x, y) points.
 [2] Generate every possible (x, y) combination.
 [3] Use pseudo-random (x, y) points.\
""")
    # Richiede all'utente l'algoritmo da utilizzare (il valore di "_mode")
    _mode: int
    while True:
        try:
            _mode = int(input("> "))
        # Gestione errori: per terminare il programma
        except (KeyboardInterrupt, EOFError, OSError):
            sys.exit(0)
        # Gestione errori: input non intero (chiede nuovamente)
        except BaseException:
            print("[!] Please type in an integer (0|1|2|3)!")
            continue
        # Numero intero: ok
        else:
            # Troppo grande o troppo piccolo (chiede nuovamente)
            if _mode > 3 or _mode < 0:
                print("[!] Invalid integer (has to be in [0, 3])!")
                continue
            # Tutto ok: "_mode" è impostato e si continua col programma
            return _mode  # questo 'return' interrompe il ciclo 'while' e ritorna il valore di '_mode'


# Calcolo di π con metodo Monte Carlo e numeri casuali generati con TrueRandomGenerator
def main():
    # Stampa il titolo
    width = os.get_terminal_size().columns
    title = " Monte Carlo Method π Approximator "
    around = "=" * (max(0, width - len(title)) // 2)
    print(around, title, around, sep="")

    # Determina il valore di "BUG", tenendo conto della riga di comando
    BUG = bug(True)  # Di default è attivo

    if __debug__:
        # Comunica che BUG è attivo (per sicurezza)
        print(f"[i] BUG is {'en' if BUG else 'dis'}abled.")

    # Determina l'algoritmo da utilizzare
    _mode: int = mode()  # Usa la funzione sopra definita
    print(f"[i] Using algorithm [{_mode}].")  # Stampa l'algoritmo, per sicurezza

    # Inizializzazione
    TRG = TrueRandomGenerator(bug=BUG)  # Il nostro generatore
    LEN = TRG.nRandomNumbers    # Numero di valori casuali disponibili
    N_in:     int         = 0   # Numero di coordinate casuali all'interno del cerchio  # noqa
    x_in:     list[int]   = []  # Lista delle coordinate x all'interno del cerchio      # noqa
    y_in:     list[int]   = []  # Lista delle coordinate y all'interno del cerchio      # noqa
    x_out:    list[int]   = []  # Lista delle coordinate x all'esterno del cerchio      # noqa
    y_out:    list[int]   = []  # Lista delle coordinate y all'esterno del cerchio      # noqa
    pi_array: list[float] = []  # Lista delle stime di π nel tempo
    pi: float = 0  # Stima di π, ricalcolata ad ogni iterazione

    # ------------------------- Metodo 1: base, O(n) --------------------------
    if _mode == 0:
        for i in range(LEN // 2):
            # Generazione di coordinate con due numeri casuali sequenziali
            x = TRG.random_number()
            y = TRG.random_number()

            # Se il punto di coordinate (x, y) appartiene al 1/4 di cerchio di raggio 255:
            if x**2 + y**2 <= K:
                N_in = N_in + 1  # incrementa il numero di coordinate all'interno,
                x_in.append(x)  # salva la coordinata x nella lista dedicata,
                y_in.append(y)  # salva la coordinata y nella lista dedicata.
            else:  # Altrimenti, le coordinate (x, y) non appartengono al cerchio:
                x_out.append(x)  # salva la coordinata x nella lista dedicata,
                y_out.append(y)  # salva la coordinata y nella lista dedicata.

            pi = N_in * 4 / (i + 1)  # Approssima π con i valori ottenuti finora
            pi_array.append(pi)  # Salva questa stima nella lista dedicata

        # Disegna i punti nel piano cartesiano
        plt.scatter(x_in, y_in, marker=".")  # type: ignore
        plt.scatter(x_out, y_out, marker=".")  # type: ignore
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

        # Disegna l'andamento della stima di π in funzione del numero di coordinate
        plt.plot(pi_array)
        plt.plot([PI] * (LEN // 2), linestyle="dashed")
        plt.show()

    # -------------- Metodo 2: coppie di valori adiacenti, O(n) ---------------
    elif _mode == 1:
        y = TRG.random_number()  # Assegnazione valore di default (pre-ciclo)
        for i in range(LEN - 1):
            x = y  # Assegnazione a "x" del numero casuale "y" precedentemente utilizzato
            y = TRG.random_number()  # Creazione nuovo numero casuale
            if x**2 + y**2 <= K:  # Analogo al metodo 1
                N_in = N_in + 1
                x_in.append(x)
                y_in.append(y)
            else:
                x_out.append(x)
                y_out.append(y)

            pi = N_in * 4 / (i + 1)  # Approssima π con i valori ottenuti finora
            pi_array.append(pi)  # Salva questa stima nella lista dedicata

        # Disegna i punti nel piano cartesiano
        plt.scatter(x_out, y_out, marker=".")  # type: ignore
        plt.scatter(x_in, y_in, marker=".")  # type: ignore
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

        # Disegna l'andamento della stima di π in funzione del numero di coordinate
        plt.plot(pi_array)
        plt.plot([PI] * (LEN - 1), linestyle="dashed")
        plt.show()

    # ------------ Metodo 3: tutte le coordinate possibili, O(n^2) ------------
    elif _mode == 2:
        # Pre-calcolo dei quadrati, per ottimizzazione
        nums = [b**2 for b in TRG.randomNumbers]

        # `enumerate([a, b, c]) -> [(0, a), (1, b), (2, c)]`
        # Questo ciclo scorre gli elementi (`x`) del vettore `nums`,
        #   associando a ciascuno il proprio indice (`i`)
        for i, x in enumerate(nums):
            for y in nums:
                if x + y <= K:  # Analogo al metodo 1
                    N_in += 1
            # Stima di π
            pi_array.append(N_in * 4 / (LEN * (i + 1)))

        # Stima finale di π (ultima stima calcolata)
        pi = pi_array[-1]

        # Disegna l'andamento della stima di π in funzione del numero di coordinate
        plt.plot(pi_array, marker=".", linestyle="")
        plt.plot([PI] * LEN, linestyle="dashed")
        plt.show()

    # ---------------------- Metodo pseudocasuali, O(n) -----------------------
    else:
        # Procedimento analogo al metodo 1, eccetto che i numeri "casuali" utilizzati sono
        #   generati in maniera pseudocasuale dal computer.

        # I valori sono 100 volte di più di quelli del metodo 1
        for i in range(LEN * 100):
            x = random.randint(0, 255)
            y = random.randint(0, 255)
            if x**2 + y**2 <= K:
                N_in = N_in + 1
                x_in.append(x)
                y_in.append(y)
            else:
                x_out.append(x)
                y_out.append(y)

            pi = N_in * 4 / (i + 1)  # Approssima π con i valori ottenuti finora
            pi_array.append(pi)  # Salva questa stima nella lista dedicata

        # Disegna i punti nel piano cartesiano
        plt.scatter(x_out, y_out, marker=".")  # type: ignore
        plt.scatter(x_in,  y_in,  marker=".")  # type: ignore
        plt.gca().set_aspect("equal", adjustable="box")
        plt.show()

        # Disegna l'andamento della stima di π in funzione del numero di coordinate
        plt.plot(pi_array)
        plt.plot([PI] * LEN * 100, linestyle="dashed")
        plt.show()

    # --- Stampa la stima finale di π ---
    # Converti i numeri in stringhe, rimuovendo il punto decimale (non conta come cifra uguale/diversa)
    spi = str(pi).replace(".", "")
    SPI = str(PI).replace(".", "")
    L = len(SPI)  # Per velocizzare i calcoli
    # Conta quante cifre sono corrette
    i = 0
    for i in range(L):
        if SPI[i] != spi[i]:
            break
    # Stampa i valori in un riquadro
    print(f"""\
,{'-'*(L+7)},
| π ≈ {pi} |
| π = {PI} |
|     {'+' if i else '^'}-{'+'*(i-1) if i else ''}{'^' if i else ''}{'~'*(L-i-1)} |
'{'-'*(L+7)}'\
""")


# Chiama "main()" quando il programma viene eseguito direttamente
if __name__ == "__main__":
    main()
