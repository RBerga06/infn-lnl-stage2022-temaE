#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Questo modulo contiene un generatore di numeri veramente casuali (TRNG)."""
from __future__ import annotations
from pathlib import Path
from typing import Literal, NamedTuple, overload
from enum import Flag, auto
from log import getLogger
import root

# Determina la cartella dove si trova questo file
SRC = Path(__file__).parent
L = getLogger(__name__)  # Il logger associato a questo modulo


class Event(NamedTuple):
    """Questa classe rappresenta un evento."""

    # Sono specificati soltanto gli attributi che ci interessano
    #   in modo tale da non dover leggere *tutti* i dati dai file
    Timestamp: int


# Switch per il ciclo da utilizzare per il raggruppamento dei bit in byte.
#   0: più intuitivo
#   1: più performante
_BYTES_GENERATION_METHOD: Literal[0, 1] = 1


# Generatore di numeri casuali che sfrutta la casualità dei dati raccolti
class TrueRandomGenerator:
    """Un generatore di numeri veramente casuali (TRNG)."""

    # --- Variabili d'istanza ---
    # pubbliche
    delta_times:      list[int]  # Differenze dei tempi
    random_bits:      list[int]  # Bit (0|1) casuali
    random_numbers:   list[int]  # Numeri casuali (da 0 a 255)
    n_random_numbers: int        # Numero di numeri casuali
    # protette
    _i:               int        # Indice per il metodo `random_number()`

    # --- Metodo di inizializzazione ---

    # O si specifica il parametro `file=`...
    @overload
    def __init__(
        self, /, *, events: list[Event] | None = ..., file: Path | str | None = ..., bug: bool = False
    ) -> None: ...

    # ... oppure `files=`...
    @overload
    def __init__(
        self, /, *, events: list[Event] | None = ..., files: list[Path | str] | None = ..., bug: bool = False
    ) -> None: ...
    # ... ma non entrambi.

    # Metodo vero e proprio.
    #   Ottieni i dati, genera da questi bit e numeri casuali e salvali nelle variabili d'istanza.
    def __init__(
        self, *,
        # Fonti di dati
        events: list[Event] | None = None,  # Eventi passati direttamente
        file: Path | str | None = None,  # Apri un file
        files: list[Path | str] | None = None,  # Apri uno o più file
        # Comportamento
        bug: bool = False,
    ) -> None:

        # --- 0. Lettura dei dati (eventi) ---
        # Se nessuno fra `events=`, `file=` e `files` è stato specificato, usa il file di default (`data.root`)
        if events is file is files is None:
            files = [SRC / "data.root"]
        # Se `events=` è stato specificato, utilizzane una copia; altrimenti, inizia con una lista vuota
        events = [] if events is None else events.copy()
        # Se `files=` non è stato specificato, ma `file=` sì, allora usa quel file
        #   Se invece nemmeno `file=` è stato specificato, non usare alcun file
        files = ([] if file is None else [file]) if files is None else files.copy()
        # Apri i file in `files` e leggi l'albero "Data_R", aggiungendo i dati a `t`
        for file in files:
            events += root.read(file, "Data_R", cls=Event)
        # Se non ci sono abbastanza eventi, riporta un errore e termina il programma
        if len(events) < 9:
            raise ValueError(
                f"Not enough data to generate a random byte: only {len(events)} events!"
            )

        # --- 1. Calcolo delle differenze dei tempi tra coppie di tempi adiacenti ---
        with L.task("Calculating time differences"):

            self.delta_times = []
            for i in range(1, len(events)):
                # ∆t = (tempo dell'`i`-esimo evento) - (tempo dell'`i-1`-esimo evento)
                delta_time = events[i].Timestamp - events[i - 1].Timestamp
                # Salva ∆t (`delta_time`) nel vettore dedicato
                self.delta_times.append(delta_time)

        # --- 2. Generazione dei bit casuali ---
        with L.task("Generating random bits"):
            # Applicazione del metodo (statico) `self._rand(...)` alle
            #   differenze dei tempi e salvataggio nel vettore `self.bits`
            self.random_bits = list(map(self._rand, self.delta_times))

        # --- 3. Generazione dei numeri casuali (da 0 a 255) ---
        with L.task("Generating random numbers"):

            self.random_numbers = []
            random_numbers_b = []
            # Inizializza un vettore di lunghezza 8 (pieno di zeri)
            byte = [0] * 8

            if _BYTES_GENERATION_METHOD == 0:
                # -------------------- Metodo 1 --------------------
                # <numero di byte> = ⌊ <numero di bit> / 8 ⌋  ('//' è la divisione intera)
                n_bytes = len(self.random_bits) // 8
                for i in range(n_bytes):
                    for j in range(8):
                        # Prendi 8 elementi da `self.randomBits` e salvali in `byte`
                        byte[j] = self.random_bits[i * 8 + j]

                    # Converti `byte` in un numero da 0 a 255 tramite il metodo (statico) `_conv()`;
                    #   salva poi il risultato nella variabile di istanza.
                    self.random_numbers.append(self._conv(byte))
                    # Se il `bug` è attivo, rifallo con il metodo (statico) `_conv2()`
                    if bug:
                        random_numbers_b.append(self._conv2(byte))

            else:
                # -------------------- Metodo 2 --------------------
                for i, bit in enumerate(self.random_bits):
                    # Copia l'`i`-esimo bit nell'(`i` mod 8)-esima cella di `byte`
                    byte[i % 8] = bit
                    if i % 8 == 7:
                        # Il byte è completo: convertilo in numero decimale e salvalo
                        self.random_numbers.append(self._conv(byte))
                        if bug:
                            random_numbers_b.append(self._conv2(byte))

            if bug:
                self.random_numbers += random_numbers_b

        # Salva la lunghezza di "self.randomNumbers" per un accesso più rapido
        self.n_random_numbers = len(self.random_numbers)

        # Dichiara la variabile d'istanza che tiene traccia del punto a cui siamo arrivati a leggere i byte casuali
        self._i = 0

    # Metodo statico: genera un bit dal numero che gli viene passato
    @staticmethod
    def _rand(num: int) -> int:
        return num % 2

    # Metodo statico: converte il vettore di bit `byte` in numero decimale
    @staticmethod
    def _conv(byte: list[int]) -> int:
        # indici di `byte` (`7-i`):  [ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 ]
        # esponenti di 2    (`i`) :  [ 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 ]
        num = 0
        for i in range(8):
            num += byte[7 - i] * 2**i
        return num

    # Metodo statico: converte in modo errato il vettore di bit `byte` in numero decimale
    @staticmethod
    def _conv2(byte: list[int]) -> int:
        # indici di `byte` (`i`):  [ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 ]
        # esponenti di 2   (`i`):  [ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 ]
        num = 0
        for i in range(8):
            num += byte[i] * 2**i  # <-- il bug è qui, i pesi dei bit sono in ordine inverso
        return num

    # Metodo: restituisce un numero casuale tra 0 e 255 (ogni volta diverso: scorre ciclicamente lungo i byte casuali)
    def random_number(self) -> int:
        """Restituisce un numero casuale da 0 a 255."""
        num = self.random_numbers[self._i]
        # Incremento dell'indice, torna a 0 se si raggiunge l'ultimo numero casuale disponibile
        self._i = (self._i + 1) % self.n_random_numbers
        return num


# Classe che contiene le flag per scegliere cosa mostrare nei grafici
class PLOT(Flag):
    """Flag che controllano cosa mostrare nei grafici"""

    NOTHING = 0
    # Differenze di tempo
    TIME_DELTAS = auto()
    # Distribuzione dei bit
    BITS_DISTRIBUTION = auto()
    # Distribuzione dei byte
    BYTES_DISTRIBUTION = auto()  # istogramma principale
    BYTES_DISTRIBUTION_LOCAL_MEANS = auto()  # medie locali


# Specifica cosa mostrare usando le flag appena definite.
#   Per combinarle, usare l'operatore «|»
#   In pratica, basta commentare qua sotto le righe corrispondenti ad elementi o grafici da *non* mostrare
TO_PLOT: PLOT = (
    PLOT.NOTHING
    | PLOT.TIME_DELTAS
    | PLOT.BITS_DISTRIBUTION
    | PLOT.BYTES_DISTRIBUTION
    | PLOT.BYTES_DISTRIBUTION_LOCAL_MEANS
)


# Funzione per calcolare le medie locali (ciclicamente)
def cyclic_local_means(data: list[int], spread: int = 5) -> list[float]:
    """Calcola ciclicamente le medie locali del vettore `data`, con lo `spread` specificato.

    Esempio
    -------
    >>> for i in range(1, 7):
    ...     print(f"spread={i} --> {cyclic_local_means(list(range(6)), spread=i)}")
    spread=1 --> [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    spread=2 --> [0.5, 1.5, 2.5, 3.5, 4.5, 2.5]
    spread=3 --> [2.0, 1.0, 2.0, 3.0, 4.0, 3.0]
    spread=4 --> [2.0, 1.5, 2.5, 3.5, 3.0, 2.5]
    spread=5 --> [2.4, 2.2, 2.0, 3.0, 2.8, 2.6]
    spread=6 --> [2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
    """
    left = (spread - 1) // 2
    length = len(data)
    return [sum(data[(i + j - left) % length] for j in range(spread)) / spread for i in range(length)]


# Funzione per testare il generatore
def test():
    """Testa il generatore di numeri veramente casuali."""

    # La libreria `matplotlib` serve soltanto qua: importarla all'inizio di tutto il programma è sconveniente
    import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

    gen = TrueRandomGenerator()

    # Salva alcuni valori utili nel namespace locale
    #   per velocizzare l'accesso
    bits = gen.random_bits
    nums = gen.random_numbers

    if TO_PLOT:
        with L.task("Plotting required items") as plotting:
            _plot_item_message: str = " * {}"

            # ------------------------ Differenze di tempo -------------------------
            if PLOT.TIME_DELTAS in TO_PLOT:
                plotting.info(_plot_item_message.format(PLOT.TIME_DELTAS))
                plt.hist(gen.delta_times, bins=500)
                plt.yscale("log")
                plt.xlabel("Time difference between two conecutive events [Digitizer Clock Periods]")
                plt.ylabel("Counts")
                plt.title("Time difference between two conecutive events")
                plt.show()

            # ------------------------ Distribuzione dei bit -------------------------
            if PLOT.BITS_DISTRIBUTION in TO_PLOT:
                plotting.info(_plot_item_message.format(PLOT.BITS_DISTRIBUTION))
                # print(len(gen.deltaT))                  # stampa il numero di deltaT disponibili
                # print(*gen.randomNumbers, sep="\n")     # stampa numeri casuali disponibili
                # # Confronta frequenze di 0 e 1 in bits
                # n0 = gen.randomBits.count(0)
                # print(n0/len(bits), (len(bits)-n0)/len(bits))
                plt.hist(bits, bins=2)  # istogramma per confrontare 0 e 1 (i bit)
                plt.xlabel("Bit")
                plt.ylabel("Counts")
                plt.ylim(bottom=0)
                plt.title("Bits distribution")
                plt.show()

            # ------------------------ Distribuzione dei byte -------------------------

            if PLOT.BYTES_DISTRIBUTION in TO_PLOT:
                plotting.info(_plot_item_message.format(PLOT.BYTES_DISTRIBUTION))
                # Numeri casuali
                plt.hist(
                    nums,
                    bins=256,
                    alpha=0.75 if PLOT.BYTES_DISTRIBUTION_LOCAL_MEANS in TO_PLOT else 1,
                )

            if PLOT.BYTES_DISTRIBUTION_LOCAL_MEANS in TO_PLOT:
                plotting.info(_plot_item_message.format(PLOT.BYTES_DISTRIBUTION_LOCAL_MEANS))
                # Conta quanti numeri casuali vengono generati in base al loro valore:
                #   `plt.hist()` lo fa in automatico, ma poiché dobbiamo fare le medie
                #   locali abbiamo bisogno di ottenere questi conteggi “manualmente”
                vals = [0] * 256
                for x in nums:
                    vals[x] += 1
                # Disegna le medie locali
                plt.plot(cyclic_local_means(vals, spread=32))

            if PLOT.BYTES_DISTRIBUTION in TO_PLOT or PLOT.BYTES_DISTRIBUTION_LOCAL_MEANS in TO_PLOT:
                plt.xlabel("Bytes")
                plt.ylabel("Counts")
                plt.ylim(0, 85)
                plt.title("Bytes distribution")
                plt.show()


# Chiama "test()" quando il programma viene eseguito direttamente
if __name__ == "__main__":
    test()
