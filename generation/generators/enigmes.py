"""Énigmes vérifiables : code secret, petits problèmes, chemin des nombres."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from generation.generators.figures import FORMES, MOTIFS, Figure

# ---------------------------------------------------------------- code secret


@dataclass
class CodeSecret:
    id: str
    message: str                 # ex. « VOLCAN » (espaces autorisés entre les mots)
    cle: dict[str, Figure]       # lettre → symbole
    code: list[Figure | None]    # message codé (None = espace)


def generer_code(rng: random.Random, message: str, ident: str, nb_leurres: int = 3) -> CodeSecret:
    lettres = sorted({ch for ch in message if ch != " "})
    leurres = [ch for ch in "ABCDEFGHIJLMNOPRSTUV" if ch not in lettres]
    rng.shuffle(leurres)
    toutes = sorted(lettres + leurres[:nb_leurres])
    symboles = [Figure(f, m) for f in FORMES for m in MOTIFS]
    rng.shuffle(symboles)
    cle = {l: s for l, s in zip(toutes, symboles)}
    code = [None if ch == " " else cle[ch] for ch in message]
    return CodeSecret(ident, message, cle, code)


def decoder(c: CodeSecret) -> str:
    inverse = {v: k for k, v in c.cle.items()}
    return "".join(" " if s is None else inverse[s] for s in c.code)


def verifier_code(c: CodeSecret) -> list[str]:
    e = []
    if len(set(c.cle.values())) != len(c.cle):
        e.append("deux lettres ont le même symbole")
    if any(ch not in c.cle for ch in c.message if ch != " "):
        e.append("une lettre du message n'est pas dans la clé")
    if decoder(c) != c.message:
        e.append("le décodage ne redonne pas le message")
    return e


# ---------------------------------------------------------------- petits problèmes


@dataclass
class Probleme:
    texte: str
    operation: str   # « a + b », « a - b »…
    a: int
    b: int
    reponse: int
    unite: str = ""

    def calcul(self) -> int:
        return {"+": self.a + self.b, "-": self.a - self.b, "x": self.a * self.b}[self.operation]


def verifier_probleme(p: Probleme) -> list[str]:
    e = []
    if p.calcul() != p.reponse:
        e.append(f"réponse {p.reponse} ≠ calcul {p.calcul()}")
    if not 0 <= p.reponse <= 30:
        e.append("résultat hors de portée des 6-8 ans")
    for n in (p.a, p.b):
        if str(n) not in p.texte:
            e.append(f"le nombre {n} n'apparaît pas dans l'énoncé")
    return e


# ---------------------------------------------------------------- chemin des nombres


@dataclass
class CheminNombres:
    id: str
    grille: list[list[int]]
    pas: int
    depart: tuple[int, int]
    arrivee: tuple[int, int]
    chemin: list[tuple[int, int]] = field(default_factory=list)


def _voisins(l: int, c: int, h: int, w: int):
    for dl, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nl, nc = l + dl, c + dc
        if 0 <= nl < h and 0 <= nc < w:
            yield nl, nc


def chemins_valides(ch: CheminNombres) -> list[list[tuple[int, int]]]:
    """Tous les chemins qui partent du départ en ajoutant `pas` à chaque case et finissent à l'arrivée."""
    h, w = len(ch.grille), len(ch.grille[0])
    sols: list[list[tuple[int, int]]] = []

    def rec(chemin: list[tuple[int, int]]) -> None:
        l, c = chemin[-1]
        if (l, c) == ch.arrivee:
            sols.append(list(chemin))
            return
        for nl, nc in _voisins(l, c, h, w):
            if (nl, nc) not in chemin and ch.grille[nl][nc] == ch.grille[l][c] + ch.pas:
                chemin.append((nl, nc))
                rec(chemin)
                chemin.pop()
                if len(sols) > 1:
                    return

    rec([ch.depart])
    return sols


def generer_chemin(rng: random.Random, ident: str, lignes: int = 5, colonnes: int = 6,
                   pas: int = 2, longueur_min: int = 9, longueur_max: int = 14) -> CheminNombres:
    """Chemin de la colonne de gauche à la colonne de droite ; leurres placés autour."""
    for _ in range(5000):
        chemin = [(rng.randrange(lignes), 0)]
        while chemin[-1][1] < colonnes - 1 and len(chemin) <= longueur_max:
            l, c = chemin[-1]
            options = [v for v in _voisins(l, c, lignes, colonnes) if v not in chemin
                       and not any(abs(v[0] - a[0]) + abs(v[1] - a[1]) == 1 for a in chemin[:-1])]
            if not options:
                break
            chemin.append(rng.choice(sorted(options)))
        if not (longueur_min <= len(chemin) <= longueur_max and chemin[-1][1] == colonnes - 1):
            continue
        depart_val = pas * rng.randint(0, 3)
        grille = [[-1] * colonnes for _ in range(lignes)]
        for i, (l, c) in enumerate(chemin):
            grille[l][c] = depart_val + i * pas
        valeurs_chemin = sorted({grille[l][c] for l, c in chemin})
        for l in range(lignes):
            for c in range(colonnes):
                if grille[l][c] < 0:
                    # Leurres : nombres du chemin (mal placés) ou voisins de ces nombres.
                    grille[l][c] = rng.choice(valeurs_chemin + [v + 1 for v in valeurs_chemin])
        ch = CheminNombres(ident, grille, pas, chemin[0], chemin[-1], chemin)
        if len(chemins_valides(ch)) == 1 and not verifier_chemin(ch):
            return ch
    raise RuntimeError("chemin des nombres introuvable")


def verifier_chemin(ch: CheminNombres) -> list[str]:
    sols = chemins_valides(ch)
    if len(sols) != 1:
        return [f"{len(sols)} chemins possibles au lieu d'un"]
    if sols[0] != ch.chemin:
        return ["le chemin enregistré n'est pas le chemin valide"]
    if max(max(r) for r in ch.grille) > 100:
        return ["nombres trop grands"]
    return []


def generer_probleme(rng: random.Random, gabarit: dict) -> Probleme:
    """Tire les nombres d'un gabarit de problème (voir templates/enigmes.json)."""
    for _ in range(100):
        a = rng.randint(*gabarit["a"])
        b = rng.randint(*gabarit["b"])
        if gabarit["op"] == "-" and b >= a:
            continue
        p = Probleme(gabarit["texte"].format(a=a, b=b), gabarit["op"], a, b, 0, gabarit.get("unite", ""))
        p.reponse = p.calcul()
        if not verifier_probleme(p):
            return p
    raise RuntimeError(f"gabarit de problème impossible : {gabarit['texte']}")
