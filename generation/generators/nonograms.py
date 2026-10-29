"""Nonogrammes : calcul des indices, solveur par lignes + retour arrière, comptage des solutions.

Une grille n'est acceptée que si :
- ses indices reproduisent exactement le dessin ;
- le solveur trouve UNE seule solution (comptage arrêté à 2) ;
- (recommandé pour les 6-8 ans) elle se résout par simple raisonnement ligne par ligne,
  sans devoir « essayer au hasard ».
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

Grille = list[list[int]]  # 1 = case coloriée, 0 = case vide
Indices = list[list[int]]

INCONNU, VIDE, PLEIN = -1, 0, 1


@dataclass
class Nonogramme:
    id: str
    titre: str
    indice: str  # petit indice affiché sur la page (« C'est un animal. »)
    dessin: Grille
    lignes: Indices = field(default_factory=list)
    colonnes: Indices = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.lignes:
            self.lignes, self.colonnes = calculer_indices(self.dessin)

    @property
    def hauteur(self) -> int:
        return len(self.dessin)

    @property
    def largeur(self) -> int:
        return len(self.dessin[0])


def depuis_texte(motif: str) -> Grille:
    lignes = [l.strip() for l in motif.strip().splitlines() if l.strip()]
    return [[1 if ch == "#" else 0 for ch in l] for l in lignes]


def indices_ligne(ligne: list[int]) -> list[int]:
    out, n = [], 0
    for v in ligne:
        if v == 1:
            n += 1
        elif n:
            out.append(n)
            n = 0
    if n:
        out.append(n)
    return out or [0]


def calculer_indices(dessin: Grille) -> tuple[Indices, Indices]:
    lignes = [indices_ligne(r) for r in dessin]
    colonnes = [indices_ligne([dessin[r][c] for r in range(len(dessin))]) for c in range(len(dessin[0]))]
    return lignes, colonnes


@lru_cache(maxsize=None)
def placements(indice: tuple[int, ...], n: int) -> tuple[tuple[int, ...], ...]:
    """Toutes les façons de placer les blocs d'un indice dans une ligne de longueur n."""
    blocs = [b for b in indice if b > 0]
    if not blocs:
        return (tuple([0] * n),)
    out: list[tuple[int, ...]] = []

    def rec(i: int, pos: int, acc: list[int]) -> None:
        if i == len(blocs):
            out.append(tuple(acc + [0] * (n - len(acc))))
            return
        reste = sum(blocs[i + 1:]) + len(blocs) - i - 1
        for debut in range(pos, n - reste - blocs[i] + 1):
            nouv = acc + [0] * (debut - len(acc)) + [1] * blocs[i]
            if i < len(blocs) - 1:
                nouv = nouv + [0]
            rec(i + 1, len(nouv), nouv)

    rec(0, 0, [])
    return tuple(out)


def resoudre_ligne(indice: list[int], ligne: list[int]) -> list[int] | None:
    """Déductions sûres pour une ligne ; None si contradiction."""
    possibles = [p for p in placements(tuple(indice), len(ligne))
                 if all(c == INCONNU or c == v for c, v in zip(ligne, p))]
    if not possibles:
        return None
    out = list(ligne)
    for i in range(len(ligne)):
        if out[i] == INCONNU:
            vals = {p[i] for p in possibles}
            if len(vals) == 1:
                out[i] = vals.pop()
    return out


def propager(lignes: Indices, colonnes: Indices, grille: Grille,
             etapes: list[dict] | None = None) -> bool:
    """Propagation ligne/colonne jusqu'au point fixe. False si contradiction.
    Si `etapes` est fourni, chaque déduction y est consignée (pour la page « comment jouer »)."""
    h, w = len(lignes), len(colonnes)
    change = True
    while change:
        change = False
        for r in range(h):
            res = resoudre_ligne(lignes[r], grille[r])
            if res is None:
                return False
            if res != grille[r]:
                nouvelles = [c for c in range(w) if grille[r][c] == INCONNU and res[c] != INCONNU]
                grille[r] = res
                change = True
                if etapes is not None:
                    etapes.append({"type": "ligne", "index": r, "cases": nouvelles,
                                   "etat": [row[:] for row in grille]})
        for c in range(w):
            col = [grille[r][c] for r in range(h)]
            res = resoudre_ligne(colonnes[c], col)
            if res is None:
                return False
            if res != col:
                nouvelles = [r for r in range(h) if col[r] == INCONNU and res[r] != INCONNU]
                for r in range(h):
                    grille[r][c] = res[r]
                change = True
                if etapes is not None:
                    etapes.append({"type": "colonne", "index": c, "cases": nouvelles,
                                   "etat": [row[:] for row in grille]})
    return True


def compter_solutions(lignes: Indices, colonnes: Indices, limite: int = 2) -> tuple[int, Grille | None]:
    """Compte les solutions (arrêt dès `limite`). Renvoie (nombre, une solution)."""
    h, w = len(lignes), len(colonnes)
    trouvee: list[Grille] = []

    def rec(grille: Grille) -> int:
        if not propager(lignes, colonnes, grille):
            return 0
        for r in range(h):
            for c in range(w):
                if grille[r][c] == INCONNU:
                    total = 0
                    for v in (PLEIN, VIDE):
                        g = [row[:] for row in grille]
                        g[r][c] = v
                        total += rec(g)
                        if total >= limite:
                            return total
                    return total
        if calculer_indices(grille) == (lignes, colonnes):
            if not trouvee:
                trouvee.append(grille)
            return 1
        return 0

    n = rec([[INCONNU] * w for _ in range(h)])
    return n, (trouvee[0] if trouvee else None)


def resoluble_par_lignes(lignes: Indices, colonnes: Indices) -> bool:
    grille = [[INCONNU] * len(colonnes) for _ in range(len(lignes))]
    return propager(lignes, colonnes, grille) and all(v != INCONNU for row in grille for v in row)


def verifier(n: Nonogramme, exiger_logique: bool = True) -> list[str]:
    erreurs: list[str] = []
    if any(len(r) != n.largeur for r in n.dessin):
        erreurs.append("dessin non rectangulaire")
        return erreurs
    if calculer_indices(n.dessin) != (n.lignes, n.colonnes):
        erreurs.append("les indices ne reproduisent pas le dessin")
    nb, sol = compter_solutions(n.lignes, n.colonnes, limite=2)
    if nb != 1:
        erreurs.append(f"{nb if nb < 2 else 'plusieurs'} solution(s) au lieu d'une seule")
    elif sol != n.dessin:
        erreurs.append("la solution unique diffère du dessin")
    if exiger_logique and nb == 1 and not resoluble_par_lignes(n.lignes, n.colonnes):
        erreurs.append("non résoluble par simple raisonnement ligne par ligne")
    if sum(map(sum, n.dessin)) == 0:
        erreurs.append("dessin vide")
    return erreurs


def etapes_guidees(n: Nonogramme) -> list[dict]:
    """Déductions dans un ordre pédagogique : à chaque étape, la ligne ou la colonne qui
    permet de colorier/barrer le plus de cases (les lignes « faciles » d'abord)."""
    etapes: list[dict] = []
    grille = [[INCONNU] * n.largeur for _ in range(n.hauteur)]
    while True:
        meilleur = None
        for r in range(n.hauteur):
            res = resoudre_ligne(n.lignes[r], grille[r])
            if res is None:
                return etapes
            nouv = [c for c in range(n.largeur) if grille[r][c] == INCONNU and res[c] != INCONNU]
            if nouv and (meilleur is None or len(nouv) > len(meilleur[2])):
                meilleur = ("ligne", r, nouv, res)
        for c in range(n.largeur):
            col = [grille[r][c] for r in range(n.hauteur)]
            res = resoudre_ligne(n.colonnes[c], col)
            if res is None:
                return etapes
            nouv = [r for r in range(n.hauteur) if col[r] == INCONNU and res[r] != INCONNU]
            if nouv and (meilleur is None or len(nouv) > len(meilleur[2])):
                meilleur = ("colonne", c, nouv, res)
        if meilleur is None:
            return etapes
        typ, i, nouv, res = meilleur
        if typ == "ligne":
            grille[i] = res
        else:
            for r in range(n.hauteur):
                grille[r][i] = res[r]
        etapes.append({"type": typ, "index": i, "cases": nouv, "etat": [row[:] for row in grille]})


def difficulte(n: Nonogramme) -> int:
    """Indice de difficulté : nombre de déductions ligne/colonne nécessaires."""
    return len(etapes_guidees(n))
