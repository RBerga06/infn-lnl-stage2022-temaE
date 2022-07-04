"""Modulo che utilizza PyROOT (se installato), o uproot come backend."""

from __future__ import annotations
from collections import namedtuple
from typing import Any, NamedTuple, TypeVar, get_origin, get_type_hints
import os


# ----- 1. Importa la libreria corretta ------ #

# Variabile che controlla la libreria da usare: True per PyROOT, False per uproot.
#   Il valore iniziale è determinato a partire variabile d'ambiente FORCE_UPROOT.
ROOT: bool = not eval(os.environ.get("FORCE_UPROOT", "0") or "0")

# Prova a importare PyROOT; se fallisci, prova con uproot. Imposta la variabile `ROOT` di conseguenza.
try:
    if not ROOT:
        raise ModuleNotFoundError
    from ROOT import TFile      # type: ignore
except ModuleNotFoundError:
    # Non c'è PyROOT: usiamo uproot
    from uproot import open     # type: ignore
    ROOT = False
else:
    # nessun errore: PyROOT c'è.
    ROOT = True


if __debug__:
    print(f"[i] ROOT backend: {'PyROOT' if ROOT else 'uproot'}")


# ----- 2. Definisci la funzione di lettura ------ #

_T = TypeVar("_T", bound=NamedTuple)

def read(
    # File e tabella
    file: str,
    table: str,
    # Attributi da leggere (dedotti dalla classe - `cls=`, se definita)
    *attributes: str,
    list_conv: list[str] | None = None,
    # Classe dove salvare i dati
    cls: type[_T] | None = None,
    cls_name: str = "Data"
) -> list[_T]:
    """Legge la tabella `table` dal file ROOT `file` e ritorna i valori come lista di oggetti con gli attributi in `attributes`."""
    if __debug__:
        print(f"--> Reading table {table} of file {file}")
    # Genera la classe giusta in runtime, se non ne è stata specificata una
    if cls is None:
        cls = namedtuple(cls_name, attributes)  # type: ignore
        list_conv = list_conv or []
    else:
        attributes = cls._fields
        list_conv = [name for name, t in get_type_hints(cls).items() if issubclass(get_origin(t) or t, list)]
    data: list[_T] = []
    vals: dict[str, Any] = {}
    if ROOT:
        f = TFile(file)
        t = f.Get(table)
        for x in t:
            vals.clear()
            for attr in attributes:
                if attr in list_conv:
                    vals[attr] = [*getattr(x, attr)]
                else:
                    vals[attr] = getattr(x, attr)
            data.append(cls(**vals))  # type: ignore
    else:
        raw_data = {}
        with open(f"{file}:{table}") as f:
            branches = {k: v for k, v in f.iteritems()}
            for attr in attributes:
                if attr in list_conv:
                    raw_data[attr] = list(map(list, branches[attr].array()))
                else:
                    raw_data[attr] = list(branches[attr].array())
        for i in range(len(raw_data[attributes[0]])):
            vals.clear()
            for attr in raw_data:
                vals[attr] = raw_data[attr][i]
            data.append(cls(**vals))  # type: ignore
    if __debug__:
        print(f"    done (read {len(data)} items)")
    return data



if __name__ == "__main__":
    # Test
    class Event(NamedTuple):
        Timestamp: int
        Samples: list[int]

    data = read("src/fondo.root", "Data_R", cls=Event)
    assert isinstance(data[0], Event)
