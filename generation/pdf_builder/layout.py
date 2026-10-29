"""Rectangles de mise en page (unités : points PDF, origine en bas à gauche)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def top(self) -> float:
        return self.y + self.h

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def inset(self, dx: float, dy: float | None = None) -> "Rect":
        dy = dx if dy is None else dy
        return Rect(self.x + dx, self.y + dy, self.w - 2 * dx, self.h - 2 * dy)

    def take_top(self, h: float, gap: float = 0) -> tuple["Rect", "Rect"]:
        """Découpe une bande de hauteur h en haut ; renvoie (bande, reste)."""
        bande = Rect(self.x, self.top - h, self.w, h)
        reste = Rect(self.x, self.y, self.w, max(0.0, self.h - h - gap))
        return bande, reste

    def take_bottom(self, h: float, gap: float = 0) -> tuple["Rect", "Rect"]:
        bande = Rect(self.x, self.y, self.w, h)
        reste = Rect(self.x, self.y + h + gap, self.w, max(0.0, self.h - h - gap))
        return bande, reste

    def split_v(self, n: int, gap: float = 0, poids: list[float] | None = None) -> list["Rect"]:
        """Découpe verticale en n bandes empilées, de haut en bas."""
        poids = poids or [1.0] * n
        total = sum(poids)
        dispo = self.h - gap * (n - 1)
        out, y = [], self.top
        for p in poids:
            hh = dispo * p / total
            out.append(Rect(self.x, y - hh, self.w, hh))
            y -= hh + gap
        return out

    def split_h(self, n: int, gap: float = 0, poids: list[float] | None = None) -> list["Rect"]:
        """Découpe horizontale en n colonnes, de gauche à droite."""
        poids = poids or [1.0] * n
        total = sum(poids)
        dispo = self.w - gap * (n - 1)
        out, x = [], self.x
        for p in poids:
            ww = dispo * p / total
            out.append(Rect(x, self.y, ww, self.h))
            x += ww + gap
        return out

    def centered(self, w: float, h: float) -> "Rect":
        return Rect(self.cx - w / 2, self.cy - h / 2, w, h)

    def contains(self, other: "Rect", tol: float = 0.01) -> bool:
        return (other.x >= self.x - tol and other.y >= self.y - tol
                and other.right <= self.right + tol and other.top <= self.top + tol)
