"""Pages spéciales : couverture, consignes, « comment jouer », diplôme, introduction d'histoire."""
from __future__ import annotations

from reportlab.lib.colors import white
from reportlab.lib.units import mm

from generation.config import MARQUE
from generation.generators.nonograms import INCONNU, Nonogramme, etapes_guidees
from generation.pdf_builder import fonts, pictos
from generation.pdf_builder.document import PageCtx, PageSpec
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import bloc_titre, etoile
from generation.pdf_builder.render_nonograms import dessiner_nonogramme
from generation.pdf_builder.text import ecrire, hauteur_paragraphe, largeur, paragraphe, taille_ajustee
from generation.pdf_builder.theme import NOIR


# ------------------------------------------------------------------ couverture
def page_couverture(titre: str, sous_titre: str, illustration: list[str], mentions: list[str],
                    pastille: str = "6-8 ans", principal: str | None = None) -> PageSpec:
    """Couverture dessinée dans la zone de sécurité (pas de fond perdu : impression maison)."""

    def draw(ctx: PageCtx) -> None:
        c, t = ctx.c, ctx.theme
        z = ctx.cadre
        c.saveState()
        c.setLineWidth(2.5)
        c.setStrokeColor(t.trait_deco)
        if t.aplat_deco is not None:
            c.setFillColor(t.aplat_deco)
            c.roundRect(z.x, z.y, z.w, z.h, 18, stroke=1, fill=1)
        else:
            c.roundRect(z.x, z.y, z.w, z.h, 18, stroke=1, fill=0)
        c.restoreState()
        interieur = z.inset(12 * mm, 12 * mm)
        ecrire(c, MARQUE, interieur.cx, interieur.top - 14, fonts.TITRE_DEMI, 14, align="center")
        # Titre sur une ou deux lignes.
        mots = titre.split()
        lignes_titre = [titre]
        if largeur(titre, fonts.TITRE, 34) > interieur.w:
            meilleur = None
            for i in range(1, len(mots)):
                a, b = " ".join(mots[:i]), " ".join(mots[i:])
                m = max(largeur(a, fonts.TITRE, 34), largeur(b, fonts.TITRE, 34))
                if meilleur is None or m < meilleur[0]:
                    meilleur = (m, [a, b])
            lignes_titre = meilleur[1] if meilleur else [titre]
        taille = min(taille_ajustee(l, fonts.TITRE, 36, interieur.w) for l in lignes_titre)
        y = interieur.top - 32 - taille
        for l in lignes_titre:
            ecrire(c, l, interieur.cx, y, fonts.TITRE, taille, align="center")
            y -= taille * 1.15
        ecrire(c, sous_titre, interieur.cx, y - 6, fonts.TEXTE, 16, align="center")
        # Illustration : grand pictogramme central entouré de petits.
        ill = Rect(interieur.x, interieur.y + 48 * mm, interieur.w, y - 20 - (interieur.y + 48 * mm))
        c.saveState()
        c.setFillColor(white)
        c.setStrokeColor(NOIR)
        c.setLineWidth(1.2)
        c.roundRect(ill.x, ill.y, ill.w, ill.h, 16, stroke=1, fill=1)
        c.restoreState()
        centre = principal or illustration[0]
        s = min(ill.h * 0.55, ill.w * 0.45)
        pictos.dessiner(c, centre, ill.cx, ill.cy + 4 * mm, s, t)
        autour = [k for k in illustration if k != centre]
        positions = [(0.14, 0.78), (0.86, 0.78), (0.12, 0.25), (0.88, 0.25), (0.32, 0.12), (0.68, 0.12),
                     (0.5, 0.9)]
        for k, (fx, fy) in zip(autour, positions):
            pictos.dessiner(c, k, ill.x + fx * ill.w, ill.y + fy * ill.h, min(26 * mm, ill.h * 0.2), t)
        # Mentions.
        y = interieur.y + 36 * mm
        for m in mentions[:3]:
            tw = largeur(m, fonts.TITRE_DEMI, 15) + 24
            c.saveState()
            c.setLineWidth(1.2)
            c.setStrokeColor(NOIR)
            c.setFillColor(white)
            c.roundRect(interieur.cx - tw / 2, y - 6, tw, 22, 11, stroke=1, fill=1)
            c.restoreState()
            ecrire(c, m, interieur.cx, y + 1, fonts.TITRE_DEMI, 15, align="center")
            y -= 27
        # Pastille d'âge.
        px, py = interieur.right - 18 * mm, interieur.y + 22 * mm
        c.saveState()
        c.setLineWidth(2)
        c.setStrokeColor(NOIR)
        c.setFillColor(t.accent if not t.eco else white)
        c.circle(px, py, 15 * mm, stroke=1, fill=1)
        c.restoreState()
        couleur_txt = white if not t.eco else NOIR
        ecrire(c, pastille, px, py - 6, fonts.TITRE, 17, align="center", couleur=couleur_txt)
        if t.eco:
            ecrire(c, "Version économie d'encre", interieur.x, interieur.y + 2, fonts.TEXTE, 11)
        else:
            ecrire(c, "PDF à imprimer · format A4", interieur.x, interieur.y + 2, fonts.TEXTE, 11)

    return PageSpec("couverture", "Couverture", draw, entete=False, numerotee=False)


# ------------------------------------------------------------------ consignes d'un cahier
def page_consignes(titre: str, intro: str, rubriques: list[tuple[str, str, str]], conseils: list[str],
                   ref_corriges: str = "__corriges__") -> PageSpec:
    """rubriques : (pictogramme, nom, explication)."""

    def draw(ctx: PageCtx) -> None:
        c, t = ctx.c, ctx.theme
        zone = bloc_titre(c, ctx.cadre, titre, intro, t)
        h_rub = min(23 * mm, (zone.h * 0.62) / max(1, len(rubriques)))
        y = zone.top
        for k, nom_r, expl in rubriques:
            pictos.dessiner(c, k, zone.x + 10 * mm, y - h_rub / 2, min(17 * mm, h_rub * 0.85), t)
            ecrire(c, nom_r, zone.x + 24 * mm, y - 8 * mm + 2, fonts.TITRE, 14)
            paragraphe(c, expl, Rect(zone.x + 24 * mm, y - h_rub, zone.w - 24 * mm, h_rub - 9 * mm),
                       fonts.TEXTE, 12)
            y -= h_rub
        page_corr = ctx.page_de(ref_corriges)
        texte = ("<b>Pour les parents.</b> " + " ".join(conseils) +
                 f" Les corrigés se trouvent à la fin du cahier, à partir de la page {page_corr}.")
        h = hauteur_paragraphe(texte, zone.w - 16 * mm, fonts.TEXTE, 12) + 12 * mm
        boite = Rect(zone.x, zone.y, zone.w, min(h, y - zone.y - 4 * mm))
        c.saveState()
        c.setLineWidth(1)
        c.setStrokeColor(t.trait_deco)
        c.roundRect(boite.x, boite.y, boite.w, boite.h, 10, stroke=1, fill=0)
        c.restoreState()
        paragraphe(c, texte, boite.inset(8 * mm, 6 * mm), fonts.TEXTE, 12)

    return PageSpec("consignes", "Page de consignes", draw, section="Bienvenue")


# ------------------------------------------------------------------ comment jouer (nonogrammes)
def page_comment_jouer(exemple: Nonogramme, section: str = "Comment jouer ?") -> PageSpec:
    etapes = etapes_guidees(exemple)
    # On choisit quatre moments : grille vide, première déduction, milieu, fin.
    choix = [None, etapes[0], etapes[len(etapes) // 2], etapes[-1]]

    def legende(i: int, e: dict | None) -> str:
        if e is None:
            return ("<b>1.</b> Lis les nombres. « 3 » veut dire : 3 cases coloriées à la suite. "
                    "S'il y a plusieurs nombres, comme « 1 1 », on laisse au moins une case blanche "
                    "entre les groupes.")
        mot = "ligne" if e["type"] == "ligne" else "colonne"
        ind = exemple.lignes[e["index"]] if e["type"] == "ligne" else exemple.colonnes[e["index"]]
        indice = " ".join(map(str, ind))
        taille = exemple.largeur if e["type"] == "ligne" else exemple.hauteur
        if i == 1:
            if sum(ind) + len(ind) - 1 == taille:
                fin = f"il n'y a qu'une seule façon de la remplir : colorie toute la {mot} !"
            else:
                fin = "certaines cases sont coloriées dans tous les cas : colorie-les."
            return (f"<b>2.</b> Commence par une {mot} facile : la {mot} {e['index'] + 1} "
                    f"a pour indice « {indice} » ; {fin}")
        if i == 2:
            return ("<b>3.</b> Avance ligne par ligne, puis colonne par colonne. Mets une petite croix "
                    "dans les cases qui restent blanches pour ne pas te tromper.")
        return (f"<b>4.</b> Quand toutes les lignes et toutes les colonnes respectent leurs nombres, "
                f"le dessin apparaît : c'est {exemple.titre.lower()} !")

    def draw(ctx: PageCtx) -> None:
        c, t = ctx.c, ctx.theme
        zone = bloc_titre(c, ctx.cadre, "Comment jouer aux nonogrammes ?",
                          "Les nombres placés à gauche des lignes et au-dessus des colonnes indiquent "
                          "les cases à colorier. Voici un exemple, pas à pas.", t)
        lignes = zone.split_v(2, gap=6 * mm)
        cases = [r for l in lignes for r in l.split_h(2, gap=8 * mm)]
        for i, (e, r) in enumerate(zip(choix, cases)):
            txt = legende(i, e)
            h_txt = hauteur_paragraphe(txt, r.w, fonts.TEXTE, 12) + 4
            haut, bas = r.take_top(r.h - h_txt - 2 * mm, gap=2 * mm)
            etat = [[INCONNU] * exemple.largeur for _ in range(exemple.hauteur)] if e is None else e["etat"]
            surl = None if e is None or i == 3 else (e["type"], e["index"])
            dessiner_nonogramme(c, haut, exemple, t, etat=etat, surligne=surl, cell_max=11 * mm)
            paragraphe(c, txt, bas, fonts.TEXTE, 12)

    return PageSpec("consignes", "Comment jouer aux nonogrammes ?", draw, section=section)


# ------------------------------------------------------------------ introduction d'aventure
DECOR_DINOSAURES = (("volcan", 0.13), ("fougere", 0.3), ("fougere", 0.7), ("oeuf", 0.87))


def page_intro_aventure(titre: str, paragraphes: list[str], personnage: str, objectifs: list[str],
                        decor: tuple[tuple[str, float], ...] = DECOR_DINOSAURES) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        c, t = ctx.c, ctx.theme
        zone = bloc_titre(c, ctx.cadre, titre, None, t)
        illu, reste = zone.take_top(62 * mm, gap=6 * mm)
        c.saveState()
        c.setLineWidth(1.2)
        c.roundRect(illu.x, illu.y, illu.w, illu.h, 14, stroke=1, fill=0)
        c.restoreState()
        pictos.dessiner(c, personnage, illu.cx, illu.cy, 50 * mm, t)
        for k, fx in decor:
            pictos.dessiner(c, k, illu.x + fx * illu.w, illu.cy - 6 * mm, 30 * mm, t)
        y = reste.top
        for p in paragraphes:
            h = paragraphe(c, p, Rect(reste.x, reste.y, reste.w, y - reste.y), fonts.TEXTE, 14.5)
            y -= h + 4 * mm
            reste = Rect(reste.x, reste.y, reste.w, y - reste.y)
        ecrire(c, "Pendant ta mission, tu vas :", reste.x, y - 16, fonts.TITRE, 15)
        y -= 38
        for o in objectifs:
            etoile(c, reste.x + 8, y + 4, 6, True, t)
            ecrire(c, o, reste.x + 22, y, fonts.TEXTE, 13.5)
            y -= 20

    return PageSpec("histoire", titre, draw, section="Ta mission")


# ------------------------------------------------------------------ diplôme
def page_diplome(titre: str, texte: str, picto: str) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        c, t = ctx.c, ctx.theme
        z = ctx.cadre.inset(4 * mm, 6 * mm)
        c.saveState()
        c.setLineWidth(3)
        c.setStrokeColor(t.trait_deco)
        c.roundRect(z.x, z.y, z.w, z.h, 16, stroke=1, fill=0)
        c.setLineWidth(1)
        c.roundRect(z.x + 6, z.y + 6, z.w - 12, z.h - 12, 12, stroke=1, fill=0)
        c.restoreState()
        ecrire(c, titre, z.cx, z.top - 30 * mm, fonts.TITRE, taille_ajustee(titre, fonts.TITRE, 34, z.w - 20 * mm),
               align="center")
        for i in range(5):
            etoile(c, z.cx + (i - 2) * 16 * mm, z.top - 45 * mm, 6 * mm, True, t)
        ecrire(c, "Ce diplôme est décerné à :", z.cx, z.top - 70 * mm, fonts.TEXTE, 16, align="center")
        c.saveState()
        c.setDash(2, 3)
        c.line(z.x + 25 * mm, z.top - 88 * mm, z.right - 25 * mm, z.top - 88 * mm)
        c.restoreState()
        paragraphe(c, texte, Rect(z.x + 20 * mm, z.top - 130 * mm, z.w - 40 * mm, 34 * mm), fonts.TEXTE, 15,
                   align="center")
        pictos.dessiner(c, picto, z.cx, z.y + 62 * mm, 55 * mm, t)
        ecrire(c, "Date :", z.x + 20 * mm, z.y + 20 * mm, fonts.TEXTE, 14)
        c.saveState()
        c.setDash(2, 3)
        c.line(z.x + 38 * mm, z.y + 19 * mm, z.cx - 5 * mm, z.y + 19 * mm)
        c.restoreState()

    return PageSpec("diplome", titre, draw, section="Bravo !")
