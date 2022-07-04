#!/usr/bin/env python3
"""Questo modulo contiene un generatore di numeri veramente casuali (TRNG)."""
from pathlib import Path
from typing import NamedTuple
import root

# Determina la cartella dove si trova questo file
SRC = Path(__file__).parent


class Event(NamedTuple):
    """Questa classe rappresenta un evento."""
    # Sono specificati soltanto gli attributi che ci interessano
    Timestamp: int


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
        for i in range (1, len(tempi)):
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
        randomNumbers_b = []
        # -------------------- Metodo 1 --------------------
        nBytesPossibili = len(self.randomBits)//8       # Numero di bytes possibili = ⌊ <numero di bit> / 8 ⌋  ('//' è la divisione intera)
        for i in range(nBytesPossibili):
            temp_byte = [0]*8                           # Inizializzazione di un vettore di lunghezza 8 (pieno di zeri)
            for j in range(8):
                temp_byte[j] = self.randomBits[i*8 + j] # Si prendono 8 elementi da "self.randomBits" e si salvano su "temp_byte"
            
            # Conversione tramite la funzione "_conv" di "temp_byte" e salvataggio in "self.randomNumbers"
            self.randomNumbers.append(self._conv(temp_byte))
            if bug:
                randomNumbers_b.append(self._conv2(temp_byte))

        if bug:
            self.randomNumbers += randomNumbers_b
        if __debug__:
            print("    done.")

        self.nRandomNumbers = len(self.randomNumbers)

        # -------------------- Metodo 2 --------------------
        #temp_byte = [0]*8
        #for i in len(self.randomBits):
        #    temp_byte[i%8] = self.randomBits[i]        # Associazione dell'i-esimo bit all'(i mod 8)-esima cella di "temp_byte"
        #    if i%8 == 7:
        #        self.randomNumbers.append(self._conv(temp_byte))
        #    if bug:
        #        randomNumbers_B.append(self._conv2(temp_byte))
        #if bug:
        #    self.randNumbers += randomNumbers_B

        # Dichiarazione variabile d'istanza
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

    # Metodo: restituisce un numero casuale
    def random_number(self) -> int:
        n = self.randomNumbers[self._i]
        # Incremento dell'indice, torna a 0 se si raggiunge l'ultimo numero casuale disponibile
        self._i = (self._i + 1) % self.nRandomNumbers
        return n


# Funzione per testare il generatore
def test():
    # La libreria matplotlib serve soltanto qua: importarla all'inizio di tutto il programma è sconveniente
    import matplotlib.pyplot as plt

    gen = TrueRandomGenerator()

    # -------------------------------- Utility --------------------------------
    #print(len(gen.deltaT))                 # stampa deltaT disponibili
    #print(*gen.randNumbers, sep="\n")      # stampa numeri casuali disponibili
    #plt.hist(gen.bits)                     # istogramma per confrontare 0 e 1 (bits)
    #plt.hist(gen.randNumbers, bins = 256)  # istogramma con numeri casuali
    #plt.show()

    # ----------------- Confronta frequenze di 0 e 1 in bits ------------------
    #zero = 0
    #uno = 0
    #for i in gen.bits:
    #    if i:
    #        uno += 1
    #    else:
    #        zero += 1
    #print(zero/(zero+uno))
    #print(uno/(zero+uno))


    # ------------------------ Plot per presentazione -------------------------
    # Differenze di tempo
    #plt.hist(gen.deltaT, bins = 500)
    #plt.yscale("log")
    #plt.xlabel("Time difference between two conecutive events [Digitizer Clock Periods]")
    #plt.ylabel("Counts")
    #plt.title("Time difference between two conecutive events")

    # Bits (0, 1)
    #plt.hist(gen.bits, bins = 3)
    #plt.yscale("log")
    #plt.xlabel("Bit")
    #plt.ylabel("Counts")
    #plt.title("Bits distribution")

    # Numeri casuali
    if __debug__:
        print("--> plotting random numbers as an histogram")
    plt.hist(gen.randomNumbers, bins=256)
    plt.yscale("log")
    plt.xlabel("Bytes")
    plt.ylabel("Counts")
    plt.title("Bytes distribution")
    if __debug__:
        print("    done.")

    plt.show()



# Chiama "test()" quando il programma viene eseguito direttamente
if __name__ == '__main__':
    test()
