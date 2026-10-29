"""Thème graphique d'un document : couleurs d'accent et mode « économie d'encre »."""
from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

LARGEUR_PAGE, HAUTEUR_PAGE = A4
MARGE = 15 * mm            # zone de sécurité : rien n'est dessiné en dehors
MARGE_CONTROLE_QA = 12 * mm  # bande vérifiée blanche par la QA (marge minimale exigée)
HAUTEUR_ENTETE = 13 * mm
HAUTEUR_PIED = 10 * mm

NOIR = black
BLANC = white
GRIS_TRAIT = HexColor("#555555")
GRIS_CLAIR = HexColor("#BBBBBB")
GRIS_TRES_CLAIR = HexColor("#EEEEEE")
SOLUTION = HexColor("#D9480F")  # tracé des solutions : orange soutenu, gris moyen en N&B

# Couleurs « crayon » pour les coloriages codés (nom affiché + pastille).
COULEURS_CRAYON: dict[str, str] = {
    "rouge": "#E03131",
    "orange": "#F08C00",
    "jaune": "#FCC419",
    "vert": "#37B24D",
    "vert foncé": "#2B8A3E",
    "bleu": "#1C7ED6",
    "bleu clair": "#74C0FC",
    "marron": "#8B5A2B",
    "noir": "#222222",
    "gris": "#909296",
    "rose": "#F783AC",
    "violet": "#7048E8",
}


@dataclass(frozen=True)
class Theme:
    accent: Color
    accent_clair: Color
    eco: bool = False  # version économie d'encre : aucun aplat ni couleur

    @classmethod
    def depuis_hex(cls, accent: str, accent_clair: str, eco: bool = False) -> "Theme":
        return cls(HexColor(accent), HexColor(accent_clair), eco)

    def version_eco(self) -> "Theme":
        return Theme(self.accent, self.accent_clair, True)

    # Couleur d'accent pour traits/textes décoratifs.
    @property
    def trait_deco(self) -> Color:
        return NOIR if self.eco else self.accent

    # Aplat décoratif léger (None = pas d'aplat en mode éco).
    @property
    def aplat_deco(self) -> Color | None:
        return None if self.eco else self.accent_clair

    @property
    def trace_solution(self) -> Color:
        return NOIR if self.eco else SOLUTION

    def remplissage(self, couleur: Color | str | None) -> Color | None:
        """Aplat d'illustration : conservé en version normale, supprimé en version éco."""
        if self.eco or couleur is None:
            return None
        return HexColor(couleur) if isinstance(couleur, str) else couleur
