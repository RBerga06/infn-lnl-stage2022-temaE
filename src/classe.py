#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per comprendere il funzionamento delle classi."""
# pylint: disable=protected-access,no-member

from __future__ import annotations


class Rettangolo:
    """Rappresenta un rettangolo."""
    a: float
    b: float

    def __init__(self, a: float, b: float) -> None:
        self.a = a
        self.b = b

    @property
    def area(self) -> float:
        """Calcola l'area del rettangolo."""
        return self.a * self.b

    @property
    def perimetro(self) -> float:
        """Calcola il perimetro del rettangolo."""
        return (self.a + self.b) * 2

    def __mul__(self, i: int | float) -> Rettangolo:
        if not isinstance(i, (int, float)):
            return NotImplemented
        return Rettangolo(self.a * i, self.b * i)

    def __repr__(self) -> str:
        return f"<Rettangolo {self.a} x {self.b}>"


class Quadrato(Rettangolo):
    """Sottoclasse di `Rettangolo`: eredita da essa tutti i metodi e gli attributi e ne (ri)definisce alcuni."""

    def __init__(self, lato: float) -> None:
        # Un quadrato è un rettangolo con i lati uguali
        super().__init__(lato, lato)

    def __repr__(self) -> str:
        return f"<Quadrato di lato {self.lato}>"

    def __mul__(self, i: int | float) -> Quadrato:
        # Va ridefinito perché deve ritornare un `Quadrato`, non un `Rettangolo`.
        return Quadrato(self.lato * i)

    @property
    def lato(self):
        """Il lato di questo quadrato."""
        return self.a  # o `self.b`, in realtà è indifferente


class Account:
    """Una classe per dimostrare l'utilizzo di `@property` e le variabili “private”."""
    __money: float

    def __init__(self) -> None:
        # Inizializza la variabile privata `__money` con €200
        self.__money = 200.0

    @property
    def money(self):
        """Permette all'utente di visualizzare il valore della variabile privata `__money`, ma non di modificarlo."""
        return self.__money

    def pay(self, price: float) -> None:
        """Paga (= rimuovi dal conto) €`price`."""
        # Senza `abs(...)` un prezzo negativo aumenterebbe i soldi sul conto.
        #   Così, il segno viene semplicemente ignorato.
        self.__money -= abs(price)

    def __repr__(self) -> str:
        return f"<Account bancario con €{self.money:.2f} di credito residuo>"


def private_var_example():
    """Dimostrazione delle variabili private in Python."""
    # type: ignore
    # print(f"{x:.2f}") -> stampa a schermo `x` con 2 cifre decimali
    a = Account()
    print(f"€{a.money:.2f}")  # €200.00
    a.pay(3.14)
    print(f"€{a.money:.2f}")  # €196.86
    # print(a.__money)          # AttributeError!
    # a.__money += 100          # AttributeError!
    # Purtroppo, però, in Python le variabili “private” non sono veramente private...
    #  per accedervi, utilizzare <oggetto>._<nome classe>__<nome privato>:
    print(f"€{a._Account__money:.2f}")  # €196.86
    a._Account__money += 100  # Modifico la variabile “privata”
    print(f"€{a.money:.2f}")            # €296.86


def inheritance_example():
    """Dimostrazione dell'«albero» delle classi."""
    a = Quadrato(3)
    print(f"{a.lato=}")
    print(f"{a.perimetro=}")
    print(f"{a.area=}")

    b = Quadrato(5)
    print(f"{b.lato=}")
    print(f"{b.perimetro=}")
    print(f"{b.area=}")

    print(f"{Quadrato(10).area=}")

    print(Quadrato(10))                 # Scrive la stringa ritornata da `Quadrato.__repr__(...)`
    print(Quadrato(10) * 2)             # Equivale a `Quadrato(10).__mul__(2)`
    print(Quadrato(10) * Quadrato(10))  # TypeError!
    # (`__mul__(...)`, ovvero l'operazione `*`, è definito solo per interi o decimali, non altri quadrati)


if __name__ == "__main__":
    print("~~~ classe.py ~~~")
    # # # # # # # # # # # # # # # # # # # # # # #
    # Decommenta la riga di interesse qua sotto #
    # # # # # # # # # # # # # # # # # # # # # # #
    #privatevar_example()
    #inheritance_example()
