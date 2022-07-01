import matplotlib.pyplot as plt
from ROOT import TFile  # type: ignore


# Generatore di numeri casuali che sfrutta la casualità dei dati del file "data.root"
class TrueRandomGenerator:

    # Metodo di inizializzazione: crea numeri casuali e li salva nel vettore "bytes"
    def __init__(self, file = "data.root", bug = False):
        f = TFile(file)      # Apre il file
        t = f.Get("Data_R")  # Prende i dati dal file

        # Salvataggio dei tempi degli eventi nel vettore "tempi"
        tempi = []
        for event in t:
            tempi.append(event.Timestamp)
        
        # Calcolo delle differenze dei tempi tra coppie di tempi adiacenti
        self.deltaT = []
        for i in range (1, len(tempi)):
            temp_deltaT = tempi[i] - tempi[i-1]    # Differenza tra il tempo "i" e il tempo "i-1"
            self.deltaT.append(temp_deltaT)        # Salva la differenza nel vettore "self.deltaT"

        # Applicazione della funzione "_rand" alle differenze dei tempi e salvataggio nel vettore "self.bits"
        self.bits = list(map(self._rand, self.deltaT))

        # Generazione di bytes
        self.randNumbers = []
        randNumbers_b = []
        # -------------------- Metodo 1 --------------------
        nBytesPossibili = len(self.bits)//8        # Numero di bytes possibili = divisione intera tra totale di bits e 8
        for i in range(nBytesPossibili):
            temp_byte = [0]*8                      # Dichiarazione di un vettore di lunghezza 8
            for j in range(8):
                temp_byte[j] = self.bits[i*8 + j]  # Si prendono 8 elementi da "self.bits" e si salvano su "temp_byte"
            
            # Conversione tramite la funzione "_conv" di "temp_byte" e salvataggio in "self.randNumbers"
            self.randNumbers.append(self._conv(temp_byte))
            if bug:
                randNumbers_b.append(self._conv2(temp_byte))

        if bug:
            self.randNumbers += randNumbers_b

        # -------------------- Metodo 2 --------------------
        #temp_byte = [0]*8
        #for i in len(self.bits):
        #    temp_byte[i%8] = self.bits[i]         # Associazione dell'i-esimo bit all'(i mod 8)-esima cella di "temp_byte"
        #    if i%8 == 7:
        #        self.randNumbers.append(self._conv(temp_byte))
        #    if bug:
        #        randNumbers_b.append(self._conv2(temp_byte))
        #if bug:
        #    self.randNumbers += randNumbers_b

        # Dichiarazione variabile d'istanza
        self._i = 0

    # Metodo statico: genera un bit dal paramentro "n"
    @staticmethod
    def _rand(n):
        return n%2

    # Metodo statico: converte il vettore di bit "v" in numero decimale
    @staticmethod
    def _conv(v):
        sum = 0
        for i in range(8):
            sum += v[7 - i] * 2**i
        return sum

    # Metodo statico: converte fasullamente il vettore di bit "v" in numero decimale
    @staticmethod
    def _conv2(v):
        sum = 0
        for i in range(8):
            sum += v[i] * 2**i  # <-- il bug è qui, i pesi dei bit sono in ordine inverso:
        return sum              #     il bit a sinistra vale 2^0, mentre quello a destra vale 2^7

    # Metodo: restituisce un numero casuale
    def random_number(self):
        n = self.randNumbers[self._i]
        # Incremento dell'indice, torna a 0 se si raggiunge l'ultimo numero casuale disponibile
        self._i = (self._i + 1) % len(self.randNumbers)
        return n


# Funzione per testare il generatore
def test():
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
    plt.hist(gen.bytes, bins = 256)
    plt.yscale("log")
    plt.xlabel("Bytes")
    plt.ylabel("Counts")
    plt.title("Bytes distribution")

    plt.show()



# Esegui "test()" quando il programma viene eseguito
if __name__ == '__main__':
    test()
