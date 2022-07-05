#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from typing import NamedTuple
import matplotlib.pyplot as plt
import root


# --- Costanti ---
# Distanza temporale tra due samples
T: float = 4  # µs
# Numero di samples da prendere per calcolare la baseline
BASELINE_CALC_N: int = 60  # 17 per il file 'fondo.root'


# --- Modelli ----

class Event(NamedTuple):
    """Questa classe rappresenta un evento."""
    # Sono specificati soltanto gli attributi che ci interessano
    Samples: list[int]



# --- Utility ----

# Calcolo della media degli elementi contenuti nel vettore "v"
def mean(v):
    return sum(v) / len(v)


# Calcolo delle aree per ogni evento
def aree(
    events:      list[Event],
    BASELINE:    float,
    max_area:    float | None = None,
    min_samples: int          = 0,
    max_samples: int   | None = None,
) -> list[float]:

    if __debug__:
        print(f"--> calculating areas ({BASELINE=}, {max_area=}, samples range = [{min_samples}, {max_samples}])")

    aree: list[float] = []
    for event in events:
        # Estrazione dei samples dell'evento tra "min_samples" e "max_samples"
        samples = event.Samples[min_samples:max_samples]

        # Calcolo dell'area:
        #    area = ((numero di samples · baseline) - somma dei samples) · distanza temporale
        temp_area = (len(samples) * BASELINE - sum(samples)) * T

        # Se non sono stati impostati limiti all'area o area < del limite ...
        if max_area is None or temp_area < max_area:
            # ... salva l'area nel vettore "Aree"
            aree.append(temp_area)

    if __debug__:
        print("    done.")
    return aree


# --- Programma principale ----

# Funzione principale
def main():
    if __debug__:
        print("START")

    # ----------------------------- Apertura file -----------------------------
    SRC = Path(__file__).parent
    t = root.read(SRC/"data.root", "Data_R", cls=Event)

    # ------------------------ Calcolo della baseline -------------------------
    if __debug__:
        print("--> calculating baseline")
    medie = []
    for event in t:
        # Calcola della media dei primi `BASELINE_CALC_N` samples richiamando la funzione "mean"
        # Salva la media nel vettore "medie"
        medie.append(mean(event.Samples[:BASELINE_CALC_N]))
    # Salva la media del vettore "medie" come "BASELINE"
    if __debug__:
        print("    done.")
    BASELINE = mean(medie)
    #BASELINE = 13313.683338704632      # già calcolata, all'occorrenza

    # ---------------------- Calibrazione spettro in keV ----------------------
    # X1 = 118900  # picco a 1436 keV
    # X2 = 211400  # picco a 2600 keV
    # Y1 = 1436    # keV del decadimento 138La -> 138Ba (picco centrale)
    # Y2 = 2600    # keV del decadimento 227Ac (primo picco)
    # m = (Y1 - Y2) / (X1 - X2)
    # q = Y1 - m * X1
    X = 118900  # picco a 1436 keV
    Y = 1436    # keV del decadimento 138La -> 138Ba (picco centrale)
    m = Y/X

    # Funzione di calibrazione
    def conv(x):
        return m * x #+ q

    # -------------------------------- Grafici --------------------------------   
    # # Stampa i samples
    # for i, event in enumerate(t):
    #     if i > 10:
    #         break
    #     plt.plot([*event.Samples])
    # plt.show()

    # # Spettro, aree calcolate con tutti i samples di ogni evento
    # plt.hist(aree(t, BASELINE), bins = 10000)
    # plt.show

    # Spettro calibrato in keV, aree calcolate con samples nell'intervallo [BASELINE_CALC_N, 150]
    plt.hist(list(map(conv, aree(t, BASELINE, min_samples=BASELINE_CALC_N, max_samples=150))), bins = 2500)
    plt.yscale("log")
    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.xlim(left=0, right=conv(221400))
    plt.ylim(top=2500*T, bottom=.175*T)
    plt.title("Background energy spectrum")
    plt.show()



# Chiama "main()" quando il programma viene eseguito direttamente
if __name__ == '__main__':
    main()
