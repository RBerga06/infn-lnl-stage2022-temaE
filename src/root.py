#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=no-member,used-before-assignment
"""Modulo che utilizza PyROOT (se installato), o uproot come backend."""
from __future__ import annotations
from typing import Any, NamedTuple, Sequence, TypeVar, get_origin, get_type_hints, overload
from collections import namedtuple
from pathlib import Path
import sys
import os
from log import getLogger


L = getLogger(__name__)


# ----- 1. Importa la libreria corretta ------ #

# Variabile che controlla la libreria da usare: True per PyROOT, False per uproot.
#   Il valore iniziale è determinato a partire dalla variabile d'ambiente `FORCE_UPROOT`.
FORCE_UPROOT = eval(os.environ.get("FORCE_UPROOT", "0") or "0")

# Prova a importare PyROOT; se fallisci, prova con uproot.
#   Imposta la variabile `ROOT` di conseguenza.
ROOT: bool
try:
    L.debug(f"Environment variable `FORCE_UPROOT` is {'' if FORCE_UPROOT else 'not '}set.")
    if FORCE_UPROOT:
        raise ModuleNotFoundError
    L.debug("Trying to import `PyROOT`")
    import ROOT as PyROOT
except ModuleNotFoundError:
    try:
        # Non c'è PyROOT: usiamo uproot
        L.debug("Trying to import `uproot`")
        import uproot
    except ModuleNotFoundError:
        # Non c'è né PyROOT né uproot:
        L.critical("No ROOT backend available: please install either PyROOT (`root`) or `uproot`.")
        sys.exit(1)
    else:
        ROOT = False
else:
    # nessun errore: PyROOT c'è.
    ROOT = True


L.info(f"ROOT backend: {'PyROOT' if ROOT else 'uproot'}")

# ----- 2. Definisci la funzione di lettura ------ #


_T = TypeVar("_T", bound=NamedTuple)


def _read(
    file: str | Path,
    cls: type[_T],
    tree: str,
    attributes: list[str],
    list_conv: list[str],
) -> list[_T]:
    # Inizializzazione variabili
    file = str(Path(file).expanduser().resolve())
    data: list[_T] = []  # Questo sarà il risultato della funzione
    # In `vals` vengono salvati i parametri da passare alla classe nella costruzione dell'oggetto
    vals: dict[str, Any] = {}

    with L.task(f"Reading tree {tree!r} from file {file!r}...") as reading:

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

            # Mappa vuota per i dati grezzi
            #   (associa al nome dell'attributo la lista dei valori, ancora da combinare negli oggetti)
            raw_data: dict[str, Any] = {}
            # Apri l'albero `tree` dal file `file`
            with uproot.open(f"{file}:{tree}") as t:
                # Salva i “rami” come mappa
                branches = dict(t.iteritems())
                for attr in attributes:
                    # Converti l'attributo in lista ove necessario
                    if attr in list_conv:
                        raw_data[attr] = list(map(list, branches[attr].array()))
                    else:
                        raw_data[attr] = list(branches[attr].array())

            # Converti i dati grezzi in lista di oggetti:
            #   scorri gli indici e associa gli attributi corrispondenti, creando l'oggetto
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
                data.append(cls(**{name: val[i] for name, val in raw_data.items()}))  # type: ignore

        reading.result = f"read {len(data)} items"
    return data


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

    return _read(file, cls, tree, list(attributes), list_conv)  # type: ignore


# "Esporta" i simboli di interesse
__all__ = ["read"]


def test():
    """Testa il funzionamento di `read()`"""

    class Event(NamedTuple):
        """Rappresenta un evento."""

        # Cosa leggere
        Timestamp: int
        Samples: list[int]

    SRC = Path(__file__).parent
    DEFAULT = SRC / "fondo.root"
    if len(sys.argv) > 1:
        file = Path(sys.argv[1])
        if not file.exists():
            file = DEFAULT
    else:
        file = DEFAULT
    data = read(file, "Data_R", cls=Event)
    assert isinstance(data[0], Event)


if __name__ == "__main__":
    test()
