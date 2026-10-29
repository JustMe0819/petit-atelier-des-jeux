"""Assemblage d'un PDF A4 page par page : en-tête, pied de page numéroté, métadonnées.

Chaque page est décrite par une `PageSpec` (type, légende, fonction de dessin).
La liste complète est connue avant le dessin : les numéros de page sont donc
cohérents et les corrigés peuvent renvoyer à la page d'une activité.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from reportlab.pdfgen.canvas import Canvas

from generation.config import MARQUE
from generation.pdf_builder import fonts
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.text import ecrire, largeur, taille_ajustee
from generation.pdf_builder.theme import (
    HAUTEUR_ENTETE, HAUTEUR_PAGE, HAUTEUR_PIED, LARGEUR_PAGE, MARGE, NOIR, Theme,
)

ZONE_SURE = Rect(MARGE, MARGE, LARGEUR_PAGE - 2 * MARGE, HAUTEUR_PAGE - 2 * MARGE)
CADRE_CONTENU = Rect(MARGE, MARGE + HAUTEUR_PIED, ZONE_SURE.w,
                     ZONE_SURE.h - HAUTEUR_PIED - HAUTEUR_ENTETE)


@dataclass
class PageCtx:
    c: Canvas
    theme: Theme
    cadre: Rect
    numero: int
    total: int
    livre: "Livre"

    def page_de(self, ref: str) -> int:
        return self.livre.page_de(ref)


@dataclass
class PageSpec:
    kind: str  # couverture | consignes | activite | solution | dessin | histoire | diplome
    legende: str
    draw: Callable[[PageCtx], None]
    section: str = ""
    numerotee: bool = True
    entete: bool = True
    refs: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


@dataclass
class PageRecord:
    numero: int
    kind: str
    legende: str
    refs: list[str]
    numerotee: bool
    meta: dict

    def en_dict(self) -> dict:
        return {"numero": self.numero, "type": self.kind, "legende": self.legende,
                "refs": self.refs, "numerotee": self.numerotee}


@dataclass
class ResultatLivre:
    chemin: Path
    pages: list[PageRecord]
    glyphes_manquants: list[str]

    @property
    def nb_pages(self) -> int:
        return len(self.pages)


class Livre:
    def __init__(self, chemin: Path, titre: str, entete: str, theme: Theme, sujet: str = "") -> None:
        self.chemin = Path(chemin)
        self.titre = titre
        self.entete = entete
        self.theme = theme
        self.sujet = sujet
        self.pages: list[PageSpec] = []
        self._refs: dict[str, int] = {}

    def ajouter(self, spec: PageSpec) -> None:
        self.pages.append(spec)

    def page_de(self, ref: str) -> int:
        if not self._refs:
            for i, p in enumerate(self.pages, start=1):
                for r in p.refs:
                    self._refs.setdefault(r, i)
        return self._refs[ref]

    # ------------------------------------------------------------------ dessin
    def _entete(self, c: Canvas, spec: PageSpec) -> None:
        t = self.theme
        y_base = HAUTEUR_PAGE - MARGE - HAUTEUR_ENTETE + 4
        haut = HAUTEUR_PAGE - MARGE
        # Pastille avec le nom du produit.
        taille = taille_ajustee(self.entete, fonts.TITRE_DEMI, 10, ZONE_SURE.w * 0.55)
        lg = largeur(self.entete, fonts.TITRE_DEMI, taille) + 14
        c.saveState()
        if t.aplat_deco is not None:
            c.setFillColor(t.aplat_deco)
            c.roundRect(MARGE, haut - 18, lg, 16, 8, stroke=0, fill=1)
        else:
            c.setStrokeColor(NOIR)
            c.setLineWidth(0.6)
            c.roundRect(MARGE, haut - 18, lg, 16, 8, stroke=1, fill=0)
        c.restoreState()
        ecrire(c, self.entete, MARGE + 7, haut - 13.5, fonts.TITRE_DEMI, taille, couleur=t.trait_deco)
        if spec.section:
            ecrire(c, spec.section, ZONE_SURE.right, haut - 13.5, fonts.TITRE_DEMI, 10,
                   align="right", couleur=NOIR)
        c.saveState()
        c.setStrokeColor(t.trait_deco)
        c.setLineWidth(0.8)
        c.line(MARGE, y_base, ZONE_SURE.right, y_base)
        c.restoreState()

    def _pied(self, c: Canvas, numero: int) -> None:
        t = self.theme
        cx, cy = LARGEUR_PAGE / 2, MARGE + 4.5
        c.saveState()
        c.setLineWidth(0.8)
        c.setStrokeColor(t.trait_deco)
        if t.aplat_deco is not None:
            c.setFillColor(t.aplat_deco)
            c.circle(cx, cy, 9, stroke=1, fill=1)
        else:
            c.circle(cx, cy, 9, stroke=1, fill=0)
        c.restoreState()
        ecrire(c, str(numero), cx, cy - 3.6, fonts.TITRE, 10.5, align="center")
        ecrire(c, MARQUE, ZONE_SURE.right, MARGE + 1.5, fonts.TEXTE, 7.5, align="right", couleur=NOIR)

    def enregistrer(self) -> ResultatLivre:
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        c = Canvas(str(self.chemin), pagesize=(LARGEUR_PAGE, HAUTEUR_PAGE), invariant=1,
                   initialFontName=fonts.TEXTE, initialFontSize=12,
                   pageCompression=1)
        c._pad_journal = set()  # type: ignore[attr-defined]
        c.setTitle(self.titre)
        c.setAuthor(MARQUE)
        c.setSubject(self.sujet or self.titre)
        c.setCreator(f"{MARQUE} — générateur Python")
        total = len(self.pages)
        records: list[PageRecord] = []
        for numero, spec in enumerate(self.pages, start=1):
            cadre = CADRE_CONTENU if spec.entete else Rect(
                ZONE_SURE.x, ZONE_SURE.y + (HAUTEUR_PIED if spec.numerotee else 0),
                ZONE_SURE.w, ZONE_SURE.h - (HAUTEUR_PIED if spec.numerotee else 0))
            if spec.entete:
                self._entete(c, spec)
            ctx = PageCtx(c, self.theme, cadre, numero, total, self)
            c.saveState()
            spec.draw(ctx)
            c.restoreState()
            if spec.numerotee:
                self._pied(c, numero)
            c.showPage()
            records.append(PageRecord(numero, spec.kind, spec.legende, list(spec.refs),
                                      spec.numerotee, dict(spec.meta)))
        c.save()
        manquants = sorted(f"{police}:{ch!r}" for police, ch in c._pad_journal  # type: ignore[attr-defined]
                           if not fonts.glyphe_disponible(police, ch))
        return ResultatLivre(self.chemin, records, manquants)
