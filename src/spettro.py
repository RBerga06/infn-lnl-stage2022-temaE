#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=global-statement
"""Analisi dello spettro del segnale."""
from __future__ import annotations
from pathlib import Path
import sys
from typing import Dict, List, Literal, NamedTuple
import matplotlib.pyplot as plt
import root
from log import getLogger, taskLogger


class _Constants(NamedTuple):
    # Numero di samples da prendere per calcolare la baseline
    BASELINE_CALC_N: int   = 60
    # Valori di calibrazione
    PICCO_1436keV:   int   = 118900  # picco a 1436 keV
    PICCO_2600keV:   int   = 211400  # picco a 2600 keV
    # Parametri del grafico
    HIST_N_BINS:     int   = 2500    # numero di colonne dell'istogramma
    X_RIGHT_LIMIT:   int   = 221400  # limite destro dell'asse x
    Y_TOP_LIMIT:     float = 10000   # limite superiore dell'asse y
    Y_BOTTOM_LIMIT:  float = 0.7     # limite inferiore dell'asse y


# --- Costanti ---
# Cartella dei file
SRC = Path(__file__).parent.resolve()
# Logger per questo programma
L = getLogger(__name__)
# Distanza temporale tra due samples
T: float = 4  # µs
# Metodo di calcolo della baseline:
#   0: media delle medie
#   1: evento per evento
BASELINE_CALC_MODE: Literal[0, 1] = 0
# Punti di calibrazione dello spettro:
#   0: Origine e picco a 1436 keV
#   1: Picco a 1436 keV e picco a 2600 keV
CALIBRATION_MODE: Literal[0, 1] = 0
# Costanti condizionali: cambiano in base al file aperto
CONDITIONAL_CONSTANTS: Dict[Path, _Constants] = {
    SRC/"data.root": _Constants(
        BASELINE_CALC_N = 60,
        PICCO_1436keV   = 118_900,
        PICCO_2600keV   = 211_400,
        HIST_N_BINS     = 2_500,
        X_RIGHT_LIMIT   = 221400,
        Y_TOP_LIMIT     = 10000,
        Y_BOTTOM_LIMIT  = 0.7,
    ),
    SRC/"fondo.root": _Constants(
        BASELINE_CALC_N = 17,
        PICCO_1436keV   = 1_436,
        PICCO_2600keV   = 2_600,
        HIST_N_BINS     = 10_000,
        X_RIGHT_LIMIT   = 30_300,
        Y_TOP_LIMIT     = 100,
        Y_BOTTOM_LIMIT  = 0.7,
    ),
}
# File attualmente caricato
FILE: Path


def CC() -> _Constants:
    """Ritorna le costanti condizionali in base al file attualmente aperto."""
    return CONDITIONAL_CONSTANTS.get(FILE, _Constants())


# --- Modelli ----

class Event(NamedTuple):
    """Questa classe rappresenta un evento."""
    # Sono specificati soltanto gli attributi che ci interessano
    Samples: List[int]


# --- Utility ----

def mean(v: List[float] | List[int]) -> float:
    """Calcola la media degli elementi nel vettore `v`"""
    return sum(v) / len(v)


# Calcolo delle aree per ogni evento
@L.task(f"Calculating {'BASELINES and ' if BASELINE_CALC_MODE == 1 else ''}areas")
def aree(
    events: List[Event],
    BASELINE: float | None = None,
    max_area: float | None = None,
    min_samples: int = 0,
    max_samples: int | None = None,
) -> List[float]:
    """Calcola l'area di ogni evento."""
    logger = taskLogger(__name__)
    logger.debug(f"{max_area = }, samples range = [{min_samples}, {max_samples}], {BASELINE = }")

    aree_calcolate: List[float] = []
    for event in events:
        # Se necessario, calcola la BASELINE per questo evento
        if BASELINE_CALC_MODE == 1:
            BASELINE = mean(event.Samples[:CC().BASELINE_CALC_N])
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
    global FILE
    if len(sys.argv) > 1:
        file = Path(sys.argv[1])
    else:
        file = None
    if file is None or not (file.exists() and file.suffix == ".root"):
        FILE = Path(__file__).parent / "data.root"
    else:
        FILE = file
    FILE = FILE.resolve()
    t = root.read(FILE, "Data_R", cls=Event)

    # ------------------------ Calcolo della baseline -------------------------
    BASELINE = None
    if BASELINE_CALC_MODE == 0:
        with L.task("Calculating baseline...") as calc:
            medie = []
            for event in t:
                # Calcola della media dei primi `BASELINE_CALC_N` samples richiamando la funzione "mean"
                # Salva la media nel vettore "medie"
                medie.append(mean(event.Samples[:CC().BASELINE_CALC_N]))
            # Salva la media del vettore "medie" come "BASELINE"
            BASELINE = mean(medie)
            # BASELINE = 13313.683338704632      # già calcolata, all'occorrenza
            calc.result = f"it's {BASELINE}"

    # ---------------------- Calibrazione spettro in keV ----------------------
    X1 = CC().PICCO_1436keV
    X2 = CC().PICCO_2600keV
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
    plt.hist(list(map(calibrate, aree(t, BASELINE=BASELINE, min_samples=CC().BASELINE_CALC_N, max_samples=150))), bins=CC().HIST_N_BINS)
    plt.yscale("log")
    plt.xlabel("Energy [keV]")
    plt.ylabel("Counts")
    plt.xlim(left=0, right=calibrate(CC().X_RIGHT_LIMIT))
    plt.ylim(top=CC().Y_TOP_LIMIT, bottom=CC().Y_BOTTOM_LIMIT)
    plt.title("Background energy spectrum")
    plt.show()


# Chiama `main()` quando il programma viene eseguito direttamente
if __name__ == "__main__":
    main()
