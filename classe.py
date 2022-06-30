# Per comprendere il funzionamento delle classi

class Rettangolo:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def area(self):
        return self.a * self.b
    def perimetro(self):
        return (self.a + self.b) * 2
    def __mul__(self, i):
        if not isinstance(i, (int, float)):
            return NotImplemented
        return Rettangolo(self.a * i, self.b * i)
    def __repr__(self):
        return f"<Rettangolo {self.a} x {self.b}>"


class Quadrato(Rettangolo):
    def __init__(self, lato):
        super().__init__(lato, lato)

    def __repr__(self):
        return f"<Quadrato di lato {self.lato}>"

    def __mul__(self, i):
        return Quadrato(self.lato * i)

    @property
    def lato(self):
        return self.a # o self.b, è indifferente


class Account:
    def __init__(self):
        self.__money = 200
    @property
    def money(self):
        return self.__money
    def pay(self, price):
        self.__money -= abs(price)

a = Quadrato(3)
print(f"{a.lato=}")
print(f"{a.perimetro()=}")
print(f"{a.area()=}")

b = Quadrato(5)
print(f"{b.lato=}")
print(f"{b.perimetro()=}")
print(f"{b.area()=}")

print(f"{Quadrato(10).area()=}")

print(Quadrato(10))
print(Quadrato(10)*2)
print(Quadrato(10)/Quadrato(2))
