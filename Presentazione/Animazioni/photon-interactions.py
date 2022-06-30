from itertools import chain
import numpy as np
from manim import *  # type: ignore


def crystal_lattice(N: int, step: float, **kwargs) -> VGroup:
    return VGroup(*chain.from_iterable([[Dot(
        [x * step, y * step, 0], **kwargs,
    ) for y in range(N)] for x in range(N)]))


def photon(A: float = .2, λ: float = .5, min: float = 0, max: float = 4, stroke_width: float = 1, color: str = YELLOW, **kwargs) -> FunctionGraph:
    k = 2*PI/λ
    return FunctionGraph(
        lambda x: A*np.sin(k*x),
        x_range=[min, max],
        color=color,
        stroke_width = stroke_width,
        **kwargs,
    )


def orbitals(center: list[float], *radii: float, color: str = BLUE_E) -> VGroup:
    g = VGroup()
    for r in radii:
        g += Circle(r, color=color).move_to(center, aligned_edge=ORIGIN)
    return g


def electron(r: float = .4, dr: float = .2, symbol: str = "-", color: str = BLUE, txt_color: str = WHITE) -> tuple[VGroup, Circle]:
    return VGroup(
        Circle(r, color=color, fill_opacity=1),
        Text(symbol, color=txt_color, font_size=96),
    ), Circle(r + dr, color=color, fill_opacity=.25, stroke_width=0),


class ComptonEffect(Scene):
    def construct(self) -> None:
        gamma = photon(λ=.25).move_to([-7, 0, 0], aligned_edge=RIGHT)
        gamma2 = photon(λ=1).rotate_about_origin(60*DEGREES).move_to([-4, -8, 0], aligned_edge=ORIGIN)
        black  = Rectangle(BLACK, .8, 4, fill_opacity=1).move_to(ORIGIN, aligned_edge=LEFT)
        black2 = Rectangle(BLACK, 14, 6, fill_opacity=1).move_to([0, -.4, 0], aligned_edge=UP)
        e, e_crown = electron()
        orbs = orbitals([8, 0, 0], 10, 8, 6, 4, 2)
        self.add(gamma, black, gamma2, black2, orbs, e_crown, e)
        self.play(
            gamma.animate.move_to(ORIGIN, aligned_edge=LEFT),
            gamma2.animate.move_to([3, 6, 0], aligned_edge=ORIGIN),
            FadeIn(e_crown),
        )
        self.play(e.animate.move_to([2.5, -5, 0]), e_crown.animate.move_to([2.5, -5, 0]))


class PhotoelectricEffect(Scene):
    def construct(self) -> None:
        gamma = photon(λ=.25).move_to([-7, 0, 0], aligned_edge=RIGHT)
        black = Rectangle(BLACK, 1, 4, fill_opacity=1).move_to(ORIGIN, aligned_edge=LEFT)
        e, e_crown = electron()
        orbs = orbitals([8, 0, 0], 10, 8, 6, 4, 2)
        self.add(gamma, black, orbs, e)
        self.play(gamma.animate.move_to(ORIGIN, aligned_edge=LEFT), FadeIn(e_crown))
        self.play(e.animate.move_to([-8, 0, 0]), e_crown.animate.move_to([-8, 0, 0]))

