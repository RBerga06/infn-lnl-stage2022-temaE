from typing import overload
from ROOT import TFile  # type: ignore
from pathlib import Path
from manim import *  # type: ignore


@overload
def data(file: str, i: None = ...) -> list[list[int]]: ...
@overload
def data(file: str, i: int) -> list[int]: ...
def data(file: str, i: int | None = None) -> list[list[int]] | list[int]:
    f = TFile(file)
    t = f.Get("Data_R")
    if i is None:
        return [[*e.Samples] for e in t]
    return [*([e for e in t][i].Samples)]


class Areas(Scene):
    def construct(self):
        DATA_COLOR = WHITE
        BASELINE_COLOR = RED_C
        RECT_COLOR_POS = GREEN
        RECT_COLOR_NEG = YELLOW
        d = data(str(Path(__file__).parent.parent/"fondo.root"), 3)
        _BL = sum(d[:17])/17
        BL1 = _BL/100 - 131.5
        baseline = DashedLine(
            [-124/20, BL1, 0],
            [(len(d)-124)/20, BL1, 0],
            dash_length=.2,
            dashed_ratio=.75,
            color=BASELINE_COLOR,
        )
        d1 = [((i-124)/20, x/100 - 131.5) for i, x in enumerate(d)]
        d2 = [(i*4+18.6, x) for i, x in d1]
        g1 = VGroup(*[Dot([x, y, 0], radius=.02, color=DATA_COLOR) for x, y in d1])
        g2 = VGroup(*[Dot([x, y, 0], radius=.02, color=DATA_COLOR) for x, y in d2])
        dxd2 = d2[1][0] - d2[0][0]
        r = VGroup(*[
            Rectangle(
                color=RECT_COLOR_POS if BL1 > y else RECT_COLOR_NEG,
                height=abs(BL1-y),
                width=dxd2,
                fill_opacity=.5,
            ).move_to(
                [x, y, 0],
                aligned_edge=DOWN if BL1 > y else UP,
            )
            for x, y in d2
        ])
        self.play(Write(g1))
        self.wait(1)
        self.play(Write(baseline))
        self.add(baseline, g1)
        self.wait(1)
        self.play(g1.animate.become(g2))
        self.wait(1)
        self.play(DrawBorderThenFill(r))
        self.wait(1)
        self.add(r, g2)
        #self.play(Write(g))
