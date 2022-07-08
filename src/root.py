#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modulo che utilizza PyROOT (se installato), o uproot come backend."""
from __future__ import annotations
from collections import namedtuple
from pathlib import Path
from typing import Any, NamedTuple, Sequence, TypeVar, get_origin, get_type_hints, overload
import os


# ----- 1. Importa la libreria corretta ------ #

# Variabile che controlla la libreria da usare: True per PyROOT, False per uproot.
#   Il valore iniziale è determinato a partire variabile d'ambiente FORCE_UPROOT.
ROOT: bool = not eval(os.environ.get("FORCE_UPROOT", "0") or "0")

# Prova a importare PyROOT; se fallisci, prova con uproot.
#   Imposta la variabile `ROOT` di conseguenza.
try:
    if not ROOT:
        raise ModuleNotFoundError
    import ROOT as PyROOT
except ModuleNotFoundError:
    # Non c'è PyROOT: usiamo uproot
    import uproot

    ROOT = False
else:
    # nessun errore: PyROOT c'è.
    ROOT = True


if __debug__:
    print(f"[i] ROOT backend: {'PyROOT' if ROOT else 'uproot'}")


# ----- 2. Definisci la funzione di lettura ------ #

_T = TypeVar("_T", bound=NamedTuple)


# O si specifica la classe tramite il parametro `cls`...
@overload
def read(file: Path | str, tree: str, /, *, cls: type[_T]) -> list[_T]:
    ...


# ... oppure bisogna specificare `attributes`, `list_conv` e `cls_name`
@overload
def read(
    file: Path | str,
    tree: str,
    *attributes: str,
    list_conv: Sequence[str] | None = None,
    cls_name: str = "Data",
) -> list[Any]:
    ...


# La funzione vera e propria
def read(
    # File e tabella
    file: Path | str,
    tree: str,
    # Attributi da leggere (dedotti dalla classe - `cls=`, se definita)
    *attributes: str,
    list_conv: Sequence[str] | None = None,
    # Classe dove salvare i dati
    cls: type[_T] | None = None,
    cls_name: str = "Data",
) -> list[_T]:
    """Legge la tabella `table` dal file ROOT `file` e ritorna i valori come lista di oggetti.

    Parametri
    ---------
    file : Path | str.
        Il file da leggere.
    tree : str.
        L'albero da leggere.
    *attributes : tuple[str, ...], default ().
        I set di dati da leggere e da salvare come attributi.
        Vengono dedotti dalla classe (:param:`cls`), quando specificata.
    list_conv : Optional[list[str]], default None.
        I set di dati da convertire in liste.
        Vengono dedotti dalla classe (:param:`cls`), quando specificata.
    cls : Optional[type[NamedTuple]], default None.
        La classe degli oggetti dove salvare i dati.
        Deve essere una :func:`namedtuple(...)` (o una sottoclasse di `NamedTuple`).
        Viene generata automaticamente a partire dagli altri parametri, se necessario.
    cls_name : Optional[str], default "Data".
        Il nome della :class:`cls` generata automaticamente (vedi :param:`cls`).

    Utilizzo
    --------
    >>> # Dichiara gli attributi di interesse chiamando la funzione
    >>> root.read("file.root", "Data_R", "Timestamp", "Samples", list_conv=["Samples"])
    >>> # -- oppure --
    >>> # Dichiara gli attributi di interesse in una classe
    >>> from typing import NamedTuple
    >>> class Event(NamedTuple):
    ...     Timestamp: int
    ...     Samples: list[int]  # va convertito in lista
    >>> root.read("file.root", "Data_R", cls=Event)
    >>> # Per concatenare due file (o due alberi), basta utilizzare l'operatore `+` sui risultati:
    >>> root.read("file.root",  "Data_1", cls=Event) + root.read("file.root",  "Data_2", cls=Event)
    >>> root.read("file1.root", "Data_R", cls=Event) + root.read("file2.root", "Data_R", cls=Event)
    >>> root.read("file1.root", "Data_1", cls=Event) + root.read("file2.root", "Data_2", cls=Event)
    """

    if cls is None:
        # Non è stata specificata una classe: generane una adeguata ora.
        cls = namedtuple(cls_name, attributes)  # type: ignore
        # Se list_conv non è stato specificato, consideralo una lista vuota
        list_conv = [*(list_conv or ())]
    else:
        # La classe è stata specificata: determina `attributes` e `list_conv` a partire da quella.
        attributes = cls._fields
        list_conv = [
            name
            for name, t in get_type_hints(cls).items()
            if issubclass(get_origin(t) or t, list)
        ]

    # Inizializzazione variabili
    file = str(Path(file).expanduser().resolve())
    data: list[_T] = []  # Questo sarà il risultato della funzione
    # In `vals` vengono salvati i parametri da passare alla classe nella costruzione dell'oggetto
    vals: dict[str, Any] = {}

    if __debug__:
        print(f"--> Reading tree {tree!r} from file {file!r}")

    if ROOT:  # --- PyROOT ---
        # Termina il loop degli eventi di PyROOT, in modo che non interferisca con matplotlib
        PyROOT.keeppolling = 0  # type: ignore
        # Apri il file
        f = PyROOT.TFile(file)  # type: ignore
        # Leggi l'albero
        t = f.Get(tree)
        # Leggi e salva i dati di interesse
        for x in t:
            vals.clear()  # Svuota i parametri
            for attr in attributes:
                # Converti l'attributo in lista ove necessario
                if attr in list_conv:
                    vals[attr] = [*getattr(x, attr)]
                else:
                    vals[attr] = getattr(x, attr)
            # Crea l'oggetto e aggiungilo a `data`
            data.append(cls(**vals))  # type: ignore
        # Chiudi il file
        f.Close()

    else:  # --- uproot ---

        # Mappa vuota per i dati grezzi (associa al nome dell'attributo la lista dei valori, ancora da combinare negli oggetti)
        raw_data: dict[str, Any] = {}
        # Apri l'albero `tree` dal file `file`
        with uproot.open(f"{file}:{tree}") as t:
            # Salva i “rami” come mappa
            branches = {k: v for k, v in t.iteritems()}
            for attr in attributes:
                # Converti l'attributo in lista ove necessario
                if attr in list_conv:
                    raw_data[attr] = list(map(list, branches[attr].array()))
                else:
                    raw_data[attr] = list(branches[attr].array())

        # Converti i dati grezzi in lista di oggetti: scorri gli indici e associa gli attributi corrispondenti, creando l'oggetto
        #
        # i:      0   1   2   3  ...
        #         |   |   |   |
        #         V   V   V   V
        # attr0: x00 x01 x02 x03 ...  ¯|
        # attr1: x10 x11 x12 x13 ...   |--> raw_data
        # attr2: x20 x21 x22 x23 ...  _|
        #         |   |   |   |
        #         V   V   V   V
        # data:  ### ### ### ### ...
        #
        for i in range(len(raw_data[attributes[0]])):
            vals.clear()
            for attr in raw_data:
                vals[attr] = raw_data[attr][i]
            data.append(cls(**vals))  # type: ignore
    if __debug__:
        print(f"    done (read {len(data)} items).")
    return data


# "Esporta" i simboli di interesse
__all__ = ["read"]


if __name__ == "__main__":
    # Test
    class Event(NamedTuple):
        Timestamp: int
        Samples: list[int]

    data = read("src/fondo.root", "Data_R", cls=Event)
    assert isinstance(data[0], Event)
