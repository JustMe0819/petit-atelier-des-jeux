"""Coloriages codés : grille de nombres + légende nombre → couleur, dérivée d'un dessin."""
from __future__ import annotations

from dataclasses import dataclass

from generation.assets.colour_designs import DessinCouleur
from generation.pdf_builder.theme import COULEURS_CRAYON


@dataclass
class ColoriageCode:
    id: str
    titre: str
    grille: list[list[int]]        # 0 = case blanche, sinon numéro de couleur
    legende: dict[int, str]        # numéro → nom de couleur
    lettres: list[list[str]]


def depuis_dessin(d: DessinCouleur, ident: str) -> ColoriageCode:
    lignes = [l.strip() for l in d.motif.strip().splitlines()]
    ordre = list(d.legende)  # ordre de la légende = ordre des numéros
    numeros = {lettre: i + 1 for i, lettre in enumerate(ordre)}
    grille = [[numeros.get(ch, 0) for ch in l] for l in lignes]
    legende = {numeros[l]: d.legende[l] for l in ordre}
    return ColoriageCode(ident, d.titre, grille, legende, [list(l) for l in lignes])


def verifier(cc: ColoriageCode, d: DessinCouleur) -> list[str]:
    e = []
    largeurs = {len(r) for r in cc.grille}
    if len(largeurs) != 1:
        e.append("grille non rectangulaire")
    lettres_utilisees = {ch for row in cc.lettres for ch in row if ch != "."}
    if lettres_utilisees - set(d.legende):
        e.append(f"lettres sans couleur : {sorted(lettres_utilisees - set(d.legende))}")
    if set(d.legende) - lettres_utilisees:
        e.append("couleur de légende inutilisée")
    for nom in cc.legende.values():
        if nom not in COULEURS_CRAYON:
            e.append(f"couleur inconnue : {nom}")
    if len(set(cc.legende.values())) != len(cc.legende):
        e.append("deux numéros pour la même couleur")
    # Le dessin colorié selon la légende redonne exactement le dessin d'origine.
    inverse = {n: l for l, n in zip(d.legende, range(1, len(d.legende) + 1))}
    reconstruit = ["".join(inverse.get(n, ".") for n in row) for row in cc.grille]
    if reconstruit != [l.strip() for l in d.motif.strip().splitlines()]:
        e.append("la grille codée ne redonne pas le dessin")
    return e
