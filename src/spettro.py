#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analisi dello spettro del segnale."""
from __future__ import annotations
from pathlib import Path
from typing import Literal, NamedTuple
import matplotlib.pyplot as plt
import root
from log import getLogger, taskLogger


# --- Costanti ---
# Logger per questo programma
L = getLogger(__name__)
# Distanza temporale tra due samples
T: float = 4  # µs
# Numero di samples da prendere per calcolare la baseline
BASELINE_CALC_N: int = 60  # 17 per il file 'fondo.root'
# Metodo di calcola della baseline:
#   0: media delle medie
#   1: evento per evento
BASELINE_CALC_MODE: Literal[0, 1] = 0
# Punti di calibrazione dello spettro:
#   0: Origine e picco a 1436 keV
#   1: Picco a 1436 keV e picco a 2600 keV
CALIBRATION_MODE: Literal[0, 1] = 0


# --- Modelli ----

class Event(NamedTuple):
    """Questa classe rappresenta un evento."""
    # Sono specificati soltanto gli attributi che ci interessano
    Samples: list[int]


# --- Utility ----

def mean(v: list[float] | list[int]) -> float:
    """Calcola la media degli elementi nel vettore `v`"""
    return sum(v) / len(v)


# Calcolo delle aree per ogni evento
@L.task(f"Calculating {'BASELINES and ' if BASELINE_CALC_MODE == 1 else ''}areas")
def aree(
    events: list[Event],
    BASELINE: float | None = None,
    max_area: float | None = None,
    min_samples: int = 0,
    max_samples: int | None = None,
) -> list[float]:
    """Calcola l'area di ogni evento."""
    logger = taskLogger(__name__)
    logger.debug(f"{max_area=}, samples range = [{min_samples}, {max_samples}]")

    aree_calcolate: list[float] = []
    for event in events:
        # Se necessario, calcola la BASELINE per questo evento
        if BASELINE_CALC_MODE == 1:
            BASELINE = mean(event.Samples[:BASELINE_CALC_N])
        assert BASELINE is not None

        # Estrazione dei samples dell'evento tra `min_samples` e `max_samples`
        samples = event.Samples[min_samples:max_samples]

        # Calcolo dell'area:
        #    area = ((numero di samples · baseline) - somma dei samples) · distanza temporale
        temp_area = (len(samples) * BASELINE - sum(samples)) * T

        # Se non sono stati impostati limiti all'area o area < del limite ...
        if max_area is None or temp_area < max_area:
            # ... salva l'area nel vettore `aree_calcolate`
            aree_calcolate.append(temp_area)

    return aree_calcolate


# --- Programma principale ----

def main():
    """Funzione principale."""

    # ----------------------------- Apertura file -----------------------------
    SRC = Path(__file__).parent
    t = root.read(SRC / "data.root", "Data_R", cls=Event)

    # ------------------------ Calcolo della baseline -------------------------
    BASELINE = None
    if BASELINE_CALC_MODE == 0:
        with L.task("Calculating baseline...") as calc:
            medie = []
            for event in t:
                # Calcola della media dei primi `BASELINE_CALC_N` samples richiamando la funzione "mean"
                # Salva la media nel vettore "medie"
                medie.append(mean(event.Samples[:BASELINE_CALC_N]))
            # Salva la media del vettore "medie" come "BASELINE"
            BASELINE = mean(medie)
            # BASELINE = 13313.683338704632      # già calcolata, all'occorrenza
            calc.result = f"it's {BASELINE}"

    # ---------------------- Calibrazione spettro in keV ----------------------
    X1 = 118900  # picco a 1436 keV
    X2 = 211400  # picco a 2600 keV
    Y1 = 1436    # keV del decadimento 138La -> 138Ba (picco centrale)
    Y2 = 2600    # keV del decadimento 227Ac (primo picco)
    if CALIBRATION_MODE == 0:
        m = Y1 / X1
        q = 0
    else:
        m = (Y1 - Y2) / (X1 - X2)
        q = Y1 - m * X1

    # Funzione di calibrazione
    def calibrate(x):
        return m * x + q

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
    plt.hist(list(map(calibrate, aree(t, BASELINE=BASELINE, min_samples=BASELINE_CALC_N, max_samples=150))), bins=2500)
    plt.yscale("log")
    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.xlim(left=0, right=calibrate(221400))
    plt.ylim(top=2500 * T, bottom=0.175 * T)
    plt.title("Background energy spectrum")
    plt.show()


# Chiama `main()` quando il programma viene eseguito direttamente
if __name__ == "__main__":
    main()
