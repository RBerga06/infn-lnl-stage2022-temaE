import matplotlib.pyplot as plt
from cmath import log
from ROOT import *


# Costanti
T = 4   # Distanza temporale tra due samples


# Calcolo della media degli elementi contenuti nel vettore "v"
def mean(v):
    return sum(v)/len(v)


# Calcolo delle aree per ogni evento
def aree(t, BASELINE, max_area=None, min_samples=0, max_samples=None):
    print(f"--> aree({BASELINE=}, {max_area=})")

    aree = []
    for event in t:
        # Estrazione dei samples dell'evento tra "min_samples" e "max_samples"
        samples = [*event.Samples][min_samples:max_samples]

        # Calcolo dell'area:
        # ((Numero di samples · baseline) - somma dei samples) · distanza temporale
        temp_area = (len(samples) * BASELINE - sum(samples)) * T

        # Se non ci sono limiti all'area o area < del limite ...
        if max_area is None or temp_area < max_area:
            # ... salva l'area nel vettore "Aree"
            aree.append(temp_area)

    print("    aree calcolate.")
    return aree


# Funzione principale
def main():
    print("START")

    # ----------------------------- Apertura file -----------------------------
    print("--> open file")
    f = TFile("data.root")  # Apre file "data.root"
    t = f.Get("Data_R")     # Prende dati "Data_R" dal file

    # ------------------------ Calcolo della baseline -------------------------
    print("--> BASELINE")
    medie = []
    for event in t:
        # Calcola della media dei primi 17 samples richiamando la funzione "mean"
        # Salva la media nel vettore "medie"
        medie.append(mean([*event.Samples][:60]))
    # Salva la media del vettore "medie" nella "BASELINE"
    BASELINE = mean(medie)
    #BASELINE = 13313.683338704632      # già calcolata, all'occorrenza

    # ---------------------- Calibrazione spettro in keV ----------------------
    X1 = 118900  # picco a 1436 keV
    X2 = 211400  # picco a 2600 keV
    Y1 = 1436    # keV del decadimento 138La -> 138Ba (picco centrale)
    Y2 = 2600    # keV del decadimento 227Ac (primo picco)
    m = (Y1 - Y2) / (X1 - X2)
    q = Y1 - m * X1

    # Funzione di calibrazione
    def conv(x):
        return m * x + q

    # -------------------------------- Grafici --------------------------------   
    # Stampa i samples
#    for i, event in enumerate(t):
#        if i > 10:
#            break
#        plt.plot([*event.Samples])
#    plt.show()

    # Spettro, aree calcolate con tutti i samples di ogni evento
#    plt.hist(aree(t, BASELINE), bins = 10000)
#    plt.show

    # Spettro calibrato in keV, aree calcolate con samples nell'intervallo [60:150]
    plt.hist(list(map(conv, aree(t, BASELINE, min_samples=60, max_samples=150))), bins = 2500)
    plt.yscale("log")
    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.xlim(left = 0, right = conv(221400))
    plt.ylim(top = 10000, bottom = 0.7)
    plt.title("Background energy spectrum")
    plt.show()



# Esegue "main()" quando il programma viene eseguito
if __name__ == '__main__':
    main()
