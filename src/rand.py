#!/usr/bin/env python3
"""Questo modulo contiene un generatore di numeri veramente casuali (TRNG)."""
from pathlib import Path
from typing import Literal, NamedTuple
import root

# Determina la cartella dove si trova questo file
SRC = Path(__file__).parent


class Event(NamedTuple):
    """Questa classe rappresenta un evento."""
    # Sono specificati soltanto gli attributi che ci interessano
    Timestamp: int


# Switch per il ciclo da utilizzare per il raggruppamento dei bit in byte.
#   0: più intuitivo
#   1: più performante
_BYTES_GENERATION_METHOD: Literal[0, 1] = 1


# Generatore di numeri casuali che sfrutta la casualità dei dati del file "data.root"
class TrueRandomGenerator:
    """Un generatore di numeri veramente casuali."""
    deltaT:         list[int]
    randomBits:     list[int]
    randomNumbers:  list[int]
    nRandomNumbers: int

    # Metodo di inizializzazione: crea numeri casuali e li salva nel vettore "randomNumbers"
    def __init__(self, file: Path | str = SRC/"data.root", bug: bool = False) -> None:
        # Apri il file `file` e leggi la tabella "Data_R", salvando i dati come lista di eventi (oggeti di tipo `Event`)
        t = root.read(file, "Data_R", cls=Event)

        # Salvataggio dei tempi degli eventi nel vettore "tempi"
        tempi = []
        for event in t:
            tempi.append(event.Timestamp)

        if __debug__:
            print("--> calculating time differences")
        # Calcolo delle differenze dei tempi tra coppie di tempi adiacenti
        self.deltaT = []
        for i in range(1, len(tempi)):
            temp_deltaT = tempi[i] - tempi[i-1]    # Differenza tra il tempo "i" e il tempo "i-1"
            self.deltaT.append(temp_deltaT)        # Salva la differenza nel vettore "self.deltaT"
        if __debug__:
            print("    done.")

        if __debug__:
            print("--> generating random bits")
        # Applicazione della funzione "_rand" alle differenze dei tempi e salvataggio nel vettore "self.bits"
        self.randomBits = list(map(self._rand, self.deltaT))
        if __debug__:
            print("    done.")

        if __debug__:
            print("--> generating random numbers")
        # Generazione di bytes
        self.randomNumbers = []
        randomNumbers_b    = []
        temp_byte = [0]*8                               # Inizializzazione di un vettore di lunghezza 8 (pieno di zeri)

        if _BYTES_GENERATION_METHOD == 0:
            # -------------------- Metodo 1 --------------------
            nBytesPossibili = len(self.randomBits)//8       # Numero di bytes possibili = ⌊ <numero di bit> / 8 ⌋  ('//' è la divisione intera)
            for i in range(nBytesPossibili):
                for j in range(8):
                    temp_byte[j] = self.randomBits[i*8 + j] # Si prendono 8 elementi da "self.randomBits" e si salvano su "temp_byte"
                
                # Conversione tramite la funzione "_conv" di "temp_byte" e salvataggio in "self.randomNumbers"
                self.randomNumbers.append(self._conv(temp_byte))
                if bug:
                    randomNumbers_b.append(self._conv2(temp_byte))

        else:
            # -------------------- Metodo 2 --------------------
            for i in range(len(self.randomBits)):
                temp_byte[i%8] = self.randomBits[i]  # Scrittura dell'i-esimo bit nell'(i mod 8)-esima cella di "temp_byte"
                if i%8 == 7:
                    # Il byte è completo: convertiamolo in numero decimale e salviamolo
                    self.randomNumbers.append(self._conv(temp_byte))
                    if bug:
                        randomNumbers_b.append(self._conv2(temp_byte))
    
        if bug:
            self.randomNumbers += randomNumbers_b

        if __debug__:
            print("    done.")

        # Salva la lunghezza di "self.randomNumbers" per un accesso più rapido
        self.nRandomNumbers = len(self.randomNumbers)

        # Dichiarazione variabile d'istanza che tiene traccia del punto a cui siamo arrivati a leggere i byte casuali
        self._i = 0

    # Metodo statico: genera un bit dal paramentro "n"
    @staticmethod
    def _rand(n: int) -> int:
        return n%2

    # Metodo statico: converte il vettore di bit "v" in numero decimale
    @staticmethod
    def _conv(v: list[int]) -> int:
        sum = 0
        for i in range(8):
            sum += v[7 - i] * 2**i
        return sum

    # Metodo statico: converte fasullamente il vettore di bit "v" in numero decimale
    @staticmethod
    def _conv2(v: list[int]) -> int:
        sum = 0
        for i in range(8):
            sum += v[i] * 2**i  # <-- il bug è qui, i pesi dei bit sono in ordine inverso:
        return sum              #     il bit a sinistra vale 2^0, mentre quello a destra vale 2^7

    # Metodo: restituisce un numero casuale tra 0 e 255 (ogni volta diverso: scorre ciclicamente lungo i byte casuali)
    def random_number(self) -> int:
        n = self.randomNumbers[self._i]
        # Incremento dell'indice, torna a 0 se si raggiunge l'ultimo numero casuale disponibile
        self._i = (self._i + 1) % self.nRandomNumbers
        return n



# Flag che controlla cosa mostrare nei grafici
_PLOT_LOCAL_MEANS: bool = True


# Funzione per testare il generatore
def test():
    # La libreria matplotlib serve soltanto qua: importarla all'inizio di tutto il programma è sconveniente
    import matplotlib.pyplot as plt

    gen = TrueRandomGenerator()

    # -------------------------------- Utility --------------------------------
    # print(len(gen.deltaT))                 # stampa deltaT disponibili
    # print(*gen.randNumbers, sep="\n")      # stampa numeri casuali disponibili
    # plt.hist(gen.bits)                     # istogramma per confrontare 0 e 1 (bits)
    # plt.hist(gen.randNumbers, bins = 256)  # istogramma con numeri casuali
    # plt.show()

    # ----------------- Confronta frequenze di 0 e 1 in bits ------------------
    # zero = 0
    # uno = 0
    # for i in gen.bits:
    #     if i:
    #         uno += 1
    #     else:
    #         zero += 1
    # print(zero/(zero+uno))
    # print(uno/(zero+uno))


    # ------------------------ Plot per presentazione -------------------------
    # Differenze di tempo
    # plt.hist(gen.deltaT, bins = 500)
    # plt.yscale("log")
    # plt.xlabel("Time difference between two conecutive events [Digitizer Clock Periods]")
    # plt.ylabel("Counts")
    # plt.title("Time difference between two conecutive events")

    # Bits (0, 1)
    # plt.hist(gen.bits, bins = 3)
    # plt.yscale("log")
    # plt.xlabel("Bit")
    # plt.ylabel("Counts")
    # plt.title("Bits distribution")

    # Numeri casuali
    if __debug__:
        print("--> plotting random numbers as an histogram")

    # Salva nel namespace locale per velocizzare l'accesso
    numbers = gen.randomNumbers

    plt.hist(numbers, bins=256, alpha=.75 if _PLOT_LOCAL_MEANS else 1)

    if _PLOT_LOCAL_MEANS:
        # Funzione per calcolare la media locale (ciclica)
        def local_means(v: list[int], spread: int = 5) -> list[float]:
            # 'v' è il vettore con i dati
            # 'spread' è quanti valori prendere
            left = (spread - 1) // 2
            L = len(v)
            return [sum([v[(i + j - left) % L] for j in range(spread)])/spread for i in range(L)]

        # Conta quanti numeri casuali vengono generati in base al loro valore
        #   "plt.hist()"" lo fa in automatico, ma poiché dobbiamo fare le medie
        #   locali abbiamo bisogno di questi conteggi
        vals = [0]*256
        for x in numbers:
            vals[x] += 1
        plt.plot(local_means(vals, spread=32))

    plt.yscale("log")
    plt.xlabel("Bytes")
    plt.ylabel("Counts")
    plt.ylim(.7, 85)
    plt.title("Bytes distribution")
    if __debug__:
        print("    done.")

    plt.show()



# Chiama "test()" quando il programma viene eseguito direttamente
if __name__ == '__main__':
    test()
