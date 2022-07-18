#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilizza il TRNG per stimare π tramite il metodo Monte Carlo."""
import os
import sys
import random
from math import pi as PI
from pathlib import Path
import matplotlib.pyplot as plt
from rand import TrueRandomGenerator
from log import getLogger, style, sprint


# Costanti
K = 255**2
SRC = Path(__file__).parent  # Cartella di questo file
L = getLogger(__name__)  # Logger per questo file

# Se l'output è formattato male, imposta questa flag a `False`
UNICODE_BOX: bool = True  # False


def bug(default: bool, /) -> bool:
    """Determina se è stato attivato il “bug” da riga di comando."""
    # $ python pi.py                 # --> di default
    # $ python pi.py --bug           # --> attivo
    # $ python pi.py --no-bug        # --> disattivato
    # $ python pi.py --no-bug --bug  # --> attivo      (--bug sovrascrive --no-bug)
    # $ python pi.py --bug --no-bug  # --> disattivato (--no-bug sovrascrive --bug)
    if "--bug" in sys.argv:
        if "--no-bug" in sys.argv:
            BUG = sys.argv[::-1].index("--bug") < sys.argv[::-1].index("--no-bug")
            sys.argv = [x for x in sys.argv if x not in ("--no-bug", "--bug")]
            return BUG
        sys.argv = [x for x in sys.argv if x != "--bug"]
        return True
    if "--no-bug" in sys.argv:
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
            _mode = int(eval(sys.argv[1]))
        except:
            # Gestione errori: se il modo selezionato dalla riga di comando
            #   non è valido, continua con la selezione interattiva
            pass
        else:
            # Controlla se il numero inserito è valido
            if 0 <= _mode <= 3:
                # Valido
                return _mode
            # Non valido: continua con la selezione interattiva
    # Selezione interattiva dell'algoritmo
    print("""
>>> Please choose an algorithm:
 [0] Interpret data as sequential (x, y) points.
 [1] Interpret data as adjacent/linked (x, y) points.
 [2] Generate every possible (x, y) combination.
 [3] Use pseudo-random (x, y) points.\
""")
    # Richiede all'utente l'algoritmo da utilizzare (il valore di "_mode")
    _mode: int
    while True:
        try:
            _mode = int(eval(input("> ")))
        # Gestione errori: per terminare il programma
        except (KeyboardInterrupt, EOFError, OSError):
            sys.exit(0)
        # Gestione errori: input non intero (chiede nuovamente)
        except:
            L.warning("Algorithm index has to be an integer (0|1|2|3)!")
            continue
        # Numero intero: ok
        else:
            # Troppo grande o troppo piccolo (chiede nuovamente)
            if _mode > 3 or _mode < 0:
                L.warning(f"Invalid integer `{_mode}` (has to be in [0, 3])!")
                continue
            # Tutto ok: "_mode" è impostato e si continua col programma
            return _mode  # questo 'return' interrompe il ciclo 'while' e ritorna il valore di '_mode'


# Funzione principale
def main():
    """Calcola π tramite il metodo Monte Carlo, utilizzando il nostro TRNG."""
    # Stampa il titolo
    width = os.get_terminal_size().columns
    title = " Monte Carlo Method π Approximator "
    sprint(f"{title:=^{width}}", style="bold")  # see https://pyformat.info/ for why this works

    # Determina il valore di `BUG`, tenendo conto delle flag da riga di comando
    BUG = bug(True)  # Di default è attivo

    # Comunica se BUG è attivo (per sicurezza)
    L.info(f"BUG is {'en' if BUG else 'dis'}abled.")

    # Determina l'algoritmo da utilizzare
    MODE: int = mode()  # Usa la funzione sopra definita
    L.info(f"Using algorithm [{MODE}].")  # Stampa l'algoritmo, per sicurezza

    # Inizializzazione
    TRG = TrueRandomGenerator(bug=BUG)  # Il nostro generatore
    LEN = TRG.n_random_numbers  # Numero di valori casuali disponibili
    N_in:     int         = 0   # Numero di coordinate casuali all'interno del cerchio  # noqa
    x_in:     list[int]   = []  # Lista delle coordinate x all'interno del cerchio      # noqa
    y_in:     list[int]   = []  # Lista delle coordinate y all'interno del cerchio      # noqa
    x_out:    list[int]   = []  # Lista delle coordinate x all'esterno del cerchio      # noqa
    y_out:    list[int]   = []  # Lista delle coordinate y all'esterno del cerchio      # noqa
    pi_array: list[float] = []  # Lista delle stime di π nel tempo
    pi: float = 0  # Stima di π, ricalcolata ad ogni iterazione

    # Pre-calcolo dei quadrati, per ottimizzazione
    squares = [x**2 for x in TRG.random_numbers]

    # ------------------------- Metodo 1: base, O(n) --------------------------
    if MODE == 0:
        for i in range(LEN // 2):
            # Generazione di coordinate con due numeri casuali sequenziali
            x = TRG.random_number()
            y = TRG.random_number()

            # Se il punto di coordinate (x, y) appartiene cerchio di raggio 255:
            if x**2 + y**2 <= K:
                N_in += 1  # incrementa il numero di coordinate all'interno,
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
    elif MODE == 1:
        y = TRG.random_number()  # Assegnazione valore di default (pre-ciclo)
        for i in range(LEN):
            # L'`y` di prima diventa il nuovo `x`, mentre `y` diventa un nuovo numero casuale
            x, y = y, TRG.random_number()
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
        plt.plot([PI] * LEN, linestyle="dashed")
        plt.show()

    # ------------ Metodo 3: tutte le coordinate possibili, O(n^2) ------------
    elif MODE == 2:
        # `enumerate([a, b, c]) -> [(0, a), (1, b), (2, c)]`
        # Questo ciclo scorre gli elementi (`x`) del vettore `nums`,
        #   associando a ciascuno il proprio indice (`i`)
        for i, x in enumerate(squares):
            for y in squares:
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
    # Per velocizzare i calcoli
    l = len(str(PI)) - 1  # -1 perché ignoriamo il `.`
    #
    spi = f"{pi:01.{l-1}f}"
    sPI = f"{PI:01.{l-1}f}"
    # Conta quante cifre sono corrette
    i = 0
    for i, (digit, DIGIT) in enumerate(zip(spi.replace(".", ""), sPI.replace(".", ""))):
        if DIGIT != digit:
            break
    # Stampa i valori in un riquadro
    PI_STYLE = "green"          # il valore vero di π
    OK_STYLE = "bold green"     # le cifre corrette
    K0_STYLE = "bold yellow"    # la prima cifra errata
    KO_STYLE = "bright_red"     # le altre cifre errate
    # Margini del riquadro
    UL = "┌" if UNICODE_BOX else ","
    UR = "┐" if UNICODE_BOX else ","
    DL = "└" if UNICODE_BOX else "'"
    DR = "┘" if UNICODE_BOX else "'"
    H = "─" if UNICODE_BOX else "-"
    V = "│" if UNICODE_BOX else "|"
    sprint(f"""\
{UL}{H*(l+7)}{UR}
{V} π ≈ {style_pi(spi, i, OK_STYLE, K0_STYLE, KO_STYLE)} {V}
{V} π = {style_pi(sPI, i, PI_STYLE, OK_STYLE, PI_STYLE)} {V}
{V}     {
    style('+', OK_STYLE) if i else style('^', K0_STYLE)
}-{
    style('+', OK_STYLE)*(i-1) if i else ''
}{
    style('^', K0_STYLE) if i else ''
}{
    style('~', KO_STYLE)*(l-i-1)
} {V}
{DL}{H*(l+7)}{DR}\
""")


def style_pi(pi: str, i: int, OK: str, K0: str, KO: str) -> str:
    """Colora `pi` in base al numero di cifre corrette (`i`) e agli stili specificati."""
    s = ""
    for j, c in enumerate(pi.replace(".", "")):
        if j < i:
            s += style(c, OK)
        elif j == i:
            s += style(c, K0)
        else:
            s += style(c, KO)
        if j == 0:
            s += "."
    return s


# Chiama "main()" quando il programma viene eseguito direttamente
if __name__ == "__main__":
    main()
