"""Fabriques de pages d'activités (une `PageSpec` par page)."""
from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import mm

from generation.generators.coloriage import ColoriageCode
from generation.generators.enigmes import CheminNombres, CodeSecret, Probleme
from generation.generators.logic_puzzles import Activite
from generation.generators.mazes import NOMS_NIVEAUX, Labyrinthe
from generation.generators.nonograms import Nonogramme
from generation.generators.observation import JeuComptage, JeuDifferences
from generation.pdf_builder import fonts
from generation.pdf_builder.document import PageCtx, PageSpec
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import bloc_titre, cadre
from generation.pdf_builder.render_enigmes import dessiner_chemin, dessiner_code, dessiner_problemes
from generation.pdf_builder.render_logic import dessiner_activite, entete_activite
from generation.pdf_builder.render_mazes import dessiner_labyrinthe
from generation.pdf_builder.render_nonograms import dessiner_nonogramme
from generation.pdf_builder.render_observation import (
    dessiner_coloriage, dessiner_comptage, dessiner_differences,
)
from generation.pdf_builder.text import ecrire, hauteur_paragraphe, paragraphe
from generation.pdf_builder.theme import NOIR


@dataclass
class Recit:
    """Bandeau d'histoire affiché en haut d'une page (cahier-aventure)."""
    etape: int
    texte: str
    picto: str = "triceratops"


def bloc_recit(ctx: PageCtx, rect: Rect, recit: Recit) -> Rect:
    from generation.pdf_builder import pictos
    c, t = ctx.c, ctx.theme
    pad = 6
    larg_txt = rect.w - 2 * pad - 24 * mm
    texte = f"<b>Étape {recit.etape} :</b> {recit.texte}"
    h = max(hauteur_paragraphe(texte, larg_txt, fonts.TEXTE, 13) + 2 * pad, 22 * mm)
    boite = Rect(rect.x, rect.top - h, rect.w, h)
    c.saveState()
    c.setLineWidth(1.1)
    c.setStrokeColor(t.trait_deco)
    c.setDash(4, 3)
    c.roundRect(boite.x, boite.y, boite.w, boite.h, 10, stroke=1, fill=0)
    c.restoreState()
    pictos.dessiner(c, recit.picto, boite.x + pad + 10 * mm, boite.cy, 18 * mm, t)
    paragraphe(c, texte, Rect(boite.x + pad + 22 * mm, boite.y + pad, larg_txt, boite.h - 2 * pad),
               fonts.TEXTE, 13)
    _, reste = rect.take_top(h, gap=4 * mm)
    return reste


def _zone(ctx: PageCtx, titre: str, consigne: str | None, niveau: str | None = None,
          recit: Recit | None = None) -> Rect:
    r = ctx.cadre
    if recit:
        r = bloc_recit(ctx, r, recit)
    return bloc_titre(ctx.c, r, titre, consigne, ctx.theme, niveau,
                      taille_titre=19 if recit else 21)


# ------------------------------------------------------------------ labyrinthes
def page_labyrinthe(lab: Labyrinthe, numero: int, depart: str, arrivee: str, mission: str, ref: str,
                    section: str = "Labyrinthes", recit: Recit | None = None, titre: str | None = None,
                    avec_niveau: bool = True) -> PageSpec:
    titre = titre or f"Labyrinthe n°{numero}"

    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, f"{mission} Trace le chemin avec ton crayon, sans traverser les murs.",
                     lab.niveau if avec_niveau else None, recit)
        dessiner_labyrinthe(ctx.c, zone, lab, ctx.theme, depart, arrivee)

    return PageSpec("activite", f"{titre} (niveau {NOMS_NIVEAUX[lab.niveau]})", draw, section=section,
                    refs=[ref], meta={"type_activite": "labyrinthe"})


# ------------------------------------------------------------------ logique
def page_logique(activites: list[Activite], section: str = "Logique", recit: Recit | None = None,
                 titre: str | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = ctx.cadre
        if recit:
            zone = bloc_recit(ctx, zone, recit)
        if titre:
            zone = bloc_titre(ctx.c, zone, titre, None, ctx.theme)
        parts = zone.split_v(len(activites), gap=6 * mm)
        for a, part in zip(activites, parts):
            cadre(ctx.c, part, ctx.theme, rayon=10, epaisseur=1.0, deco=True)
            interieur = part.inset(7 * mm, 5 * mm)
            contenu = entete_activite(ctx.c, interieur, a, ctx.theme)
            dessiner_activite(ctx.c, contenu, a, ctx.theme)

    noms = ", ".join(a.nom_type.lower() for a in activites)
    nums = " et ".join(str(a.numero) for a in activites)
    leg = f"Activité{'s' if len(activites) > 1 else ''} {nums} : {noms}"
    return PageSpec("activite", leg, draw, section=section, refs=[a.id for a in activites],
                    meta={"type_activite": "logique"})


# ------------------------------------------------------------------ nonogrammes
CONSIGNE_NONO = ("Les nombres disent combien de cases colorier à la suite, dans l'ordre. "
                 "Colorie les cases et découvre le dessin caché !")


def page_nonogramme(nonos: list[Nonogramme], numeros: list[int], refs: list[str], section: str = "Nonogrammes",
                    recit: Recit | None = None, titre: str | None = None, montrer_indice: bool = True) -> PageSpec:
    titre = titre or (f"Nonogramme n°{numeros[0]}" if len(nonos) == 1
                      else f"Nonogrammes n°{numeros[0]} et n°{numeros[1]}")

    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, CONSIGNE_NONO, recit=recit)
        parts = zone.split_v(len(nonos), gap=5 * mm)
        for n, num, part in zip(nonos, numeros, parts):
            haut, reste = part.take_top(9 * mm)
            sous = f"Grille n°{num}" + (f" — Indice : {n.indice}" if montrer_indice else "")
            ecrire(ctx.c, sous, haut.x, haut.y + 6, fonts.TITRE_DEMI, 13)
            bas, grille = reste.take_bottom(11 * mm, gap=3 * mm)
            dessiner_nonogramme(ctx.c, grille, n, ctx.theme,
                                cell_max=(13.5 * mm if n.largeur > 5 else 14 * mm if len(nonos) > 1 else 22 * mm))
            ecrire(ctx.c, "J'ai découvert :", bas.x + bas.w * 0.2, bas.y + 8, fonts.TITRE_DEMI, 13)
            ctx.c.saveState()
            ctx.c.setLineWidth(0.8)
            ctx.c.setDash(2, 3)
            ctx.c.line(bas.x + bas.w * 0.2 + 110, bas.y + 7, bas.right - bas.w * 0.15, bas.y + 7)
            ctx.c.restoreState()

    leg = f"{titre} ({nonos[0].largeur} × {nonos[0].hauteur})"
    return PageSpec("activite", leg, draw, section=section, refs=refs, meta={"type_activite": "nonogramme"})


# ------------------------------------------------------------------ observation
def page_differences(jeu: JeuDifferences, titre: str, ref: str, section: str = "Observation",
                     recit: Recit | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, f"Observe bien les deux images. Trouve les {jeu.n} différences "
                                 f"et entoure-les sur l'image 2.", recit=recit)
        ra, rb = dessiner_differences(ctx.c, zone, jeu, ctx.theme)
        meta_scenes.update({"scene_a": [ra.x, ra.y, ra.w, ra.h], "scene_b": [rb.x, rb.y, rb.w, rb.h]})

    meta_scenes: dict = {}
    spec = PageSpec("activite", titre, draw, section=section, refs=[ref],
                    meta={"type_activite": "differences", "scenes": meta_scenes, "n": jeu.n})
    return spec


def page_comptage(jeu: JeuComptage, titre: str, consigne: str, ref: str, section: str = "Observation",
                  recit: Recit | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, consigne, recit=recit)
        dessiner_comptage(ctx.c, zone, jeu, ctx.theme)

    return PageSpec("activite", titre, draw, section=section, refs=[ref], meta={"type_activite": "comptage"})


def page_coloriage(cc: ColoriageCode, titre: str, ref: str, section: str = "Coloriage codé",
                   recit: Recit | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, "Colorie chaque case avec la couleur de son numéro. "
                                 "Les cases sans numéro restent blanches.", recit=recit)
        dessiner_coloriage(ctx.c, zone, cc, ctx.theme)

    return PageSpec("activite", titre, draw, section=section, refs=[ref], meta={"type_activite": "coloriage"})


# ------------------------------------------------------------------ énigmes
def page_code(code: CodeSecret, titre: str, ref: str, section: str = "Énigme", recit: Recit | None = None,
              consigne: str | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, consigne or "Utilise la clé : sous chaque symbole, écris la lettre "
                                             "qui lui correspond. Tu vas lire le message secret !", recit=recit)
        dessiner_code(ctx.c, zone, code, ctx.theme)

    return PageSpec("activite", titre, draw, section=section, refs=[ref], meta={"type_activite": "code"})


def page_problemes(problemes: list[Probleme], titre: str, ref: str, section: str = "Énigmes",
                   recit: Recit | None = None, illustrations: list[str] | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, "Lis chaque énigme, fais ton calcul sur un brouillon "
                                 "et écris la réponse dans la case.", recit=recit)
        dessiner_problemes(ctx.c, zone, problemes, ctx.theme, illustrations)

    return PageSpec("activite", titre, draw, section=section, refs=[ref], meta={"type_activite": "problemes"})


def page_chemin(ch: CheminNombres, titre: str, ref: str, depart: str, arrivee: str, nom_depart: str,
                section: str = "Défi", recit: Recit | None = None) -> PageSpec:
    a = ch.grille[ch.depart[0]][ch.depart[1]]
    suite = ", ".join(str(a + i * ch.pas) for i in range(3))

    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, f"Pars de la case encadrée à côté {nom_depart} et avance de case en case "
                                 f"(pas en diagonale) en comptant de {ch.pas} en {ch.pas} : {suite}… "
                                 f"Colorie le chemin jusqu'à la case encadrée de l'arrivée.", recit=recit)
        dessiner_chemin(ctx.c, zone, ch, ctx.theme, depart=depart, arrivee=arrivee)

    return PageSpec("activite", titre, draw, section=section, refs=[ref], meta={"type_activite": "chemin"})


# ------------------------------------------------------------------ dessin / écriture (limité)
def page_dessin(titre: str, consigne: str, nb_lignes: int = 3, section: str = "À toi de jouer",
                recit: Recit | None = None) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = _zone(ctx, titre, consigne, recit=recit)
        lignes_h = nb_lignes * 13 * mm
        dessin, _ = zone.take_top(zone.h - lignes_h - 6 * mm)
        c = ctx.c
        c.saveState()
        c.setLineWidth(1.4)
        c.setStrokeColor(NOIR)
        c.roundRect(dessin.x, dessin.y, dessin.w, dessin.h, 12, stroke=1, fill=0)
        c.setLineWidth(0.8)
        for i in range(nb_lignes):
            y = zone.y + i * 13 * mm + 4
            c.line(zone.x + 4, y, zone.right - 4, y)
        c.restoreState()

    return PageSpec("dessin", titre, draw, section=section, meta={"type_activite": "dessin"})
