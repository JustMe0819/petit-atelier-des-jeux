"""Labyrinthes parfaits (un seul chemin entre deux cases) générés par parcours en profondeur.

Représentation : grille `lignes × colonnes`, chaque case garde l'ensemble des
directions ouvertes ("N", "S", "E", "O"). L'entrée est percée dans le bord haut,
la sortie dans le bord bas.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

Case = tuple[int, int]  # (ligne, colonne)

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
OPPOSE = {"N": "S", "S": "N", "E": "O", "O": "E"}

# Tailles (lignes, colonnes) par niveau, de la plus petite à la plus grande.
TAILLES_NIVEAUX: dict[str, list[tuple[int, int]]] = {
    "debutant": [(6, 6), (6, 6), (7, 7), (7, 7), (7, 7), (8, 8), (8, 8), (8, 8), (9, 9), (9, 9)],
    "intermediaire": [(10, 10), (10, 10), (11, 11), (11, 11), (12, 12),
                      (12, 12), (13, 12), (13, 12), (14, 13), (14, 13)],
    "defi": [(15, 14), (15, 14), (16, 15), (16, 15), (17, 15),
             (17, 16), (18, 16), (18, 16), (19, 17), (20, 17)],
}
NOMS_NIVEAUX = {"debutant": "débutant", "intermediaire": "intermédiaire", "defi": "défi"}


@dataclass
class Labyrinthe:
    lignes: int
    colonnes: int
    ouvertures: list[list[set[str]]]
    depart: Case
    arrivee: Case
    niveau: str = "debutant"
    solution: list[Case] = field(default_factory=list)

    def ouvert(self, case: Case, d: str) -> bool:
        return d in self.ouvertures[case[0]][case[1]]

    def voisins(self, case: Case) -> list[Case]:
        l, c = case
        out = []
        for d in sorted(self.ouvertures[l][c]):
            dl, dc = DIRECTIONS[d]
            nl, nc = l + dl, c + dc
            if 0 <= nl < self.lignes and 0 <= nc < self.colonnes:
                out.append((nl, nc))
        return out

    def nb_passages(self) -> int:
        """Nombre de passages intérieurs (arêtes de l'arbre couvrant)."""
        n = 0
        for l in range(self.lignes):
            for c in range(self.colonnes):
                for d in ("S", "E"):
                    if d in self.ouvertures[l][c]:
                        dl, dc = DIRECTIONS[d]
                        if 0 <= l + dl < self.lignes and 0 <= c + dc < self.colonnes:
                            n += 1
        return n


def generer(lignes: int, colonnes: int, rng: random.Random, niveau: str = "debutant") -> Labyrinthe:
    ouvertures: list[list[set[str]]] = [[set() for _ in range(colonnes)] for _ in range(lignes)]
    vus = [[False] * colonnes for _ in range(lignes)]
    pile: list[Case] = [(rng.randrange(lignes), rng.randrange(colonnes))]
    vus[pile[0][0]][pile[0][1]] = True
    while pile:
        l, c = pile[-1]
        options = []
        for d, (dl, dc) in DIRECTIONS.items():
            nl, nc = l + dl, c + dc
            if 0 <= nl < lignes and 0 <= nc < colonnes and not vus[nl][nc]:
                options.append((d, nl, nc))
        if not options:
            pile.pop()
            continue
        options.sort()
        d, nl, nc = rng.choice(options)
        ouvertures[l][c].add(d)
        ouvertures[nl][nc].add(OPPOSE[d])
        vus[nl][nc] = True
        pile.append((nl, nc))
    # Entrée sur le bord haut (moitié gauche), sortie sur le bord bas (moitié droite).
    depart = (0, rng.randrange(0, max(1, colonnes // 2)))
    arrivee = (lignes - 1, rng.randrange(colonnes // 2, colonnes))
    ouvertures[depart[0]][depart[1]].add("N")
    ouvertures[arrivee[0]][arrivee[1]].add("S")
    lab = Labyrinthe(lignes, colonnes, ouvertures, depart, arrivee, niveau)
    lab.solution = resoudre_bfs(lab)
    return lab


def resoudre_bfs(lab: Labyrinthe) -> list[Case]:
    """Plus court chemin (parcours en largeur) du départ à l'arrivée."""
    precedent: dict[Case, Case | None] = {lab.depart: None}
    file = deque([lab.depart])
    while file:
        case = file.popleft()
        if case == lab.arrivee:
            break
        for v in lab.voisins(case):
            if v not in precedent:
                precedent[v] = case
                file.append(v)
    if lab.arrivee not in precedent:
        return []
    chemin: list[Case] = []
    cur: Case | None = lab.arrivee
    while cur is not None:
        chemin.append(cur)
        cur = precedent[cur]
    return chemin[::-1]


def verifier(lab: Labyrinthe) -> list[str]:
    """Contrôles : labyrinthe parfait, cohérence des murs, solution valide = chemin BFS."""
    erreurs: list[str] = []
    n = lab.lignes * lab.colonnes
    # Symétrie des ouvertures intérieures.
    for l in range(lab.lignes):
        for c in range(lab.colonnes):
            for d in lab.ouvertures[l][c]:
                dl, dc = DIRECTIONS[d]
                nl, nc = l + dl, c + dc
                if 0 <= nl < lab.lignes and 0 <= nc < lab.colonnes:
                    if OPPOSE[d] not in lab.ouvertures[nl][nc]:
                        erreurs.append(f"mur incohérent en {(l, c)} direction {d}")
                elif (l, c) not in (lab.depart, lab.arrivee):
                    erreurs.append(f"ouverture sur le bord hors entrée/sortie en {(l, c)}")
    # Parfait : connexe et n-1 passages (arbre couvrant).
    if lab.nb_passages() != n - 1:
        erreurs.append(f"{lab.nb_passages()} passages au lieu de {n - 1} : labyrinthe non parfait")
    atteints = {lab.depart}
    file = deque([lab.depart])
    while file:
        for v in lab.voisins(file.popleft()):
            if v not in atteints:
                atteints.add(v)
                file.append(v)
    if len(atteints) != n:
        erreurs.append(f"seulement {len(atteints)}/{n} cases atteignables")
    # Solution.
    sol = lab.solution
    if not sol or sol[0] != lab.depart or sol[-1] != lab.arrivee:
        erreurs.append("la solution ne relie pas le départ à l'arrivée")
    for a, b in zip(sol, sol[1:]):
        if b not in lab.voisins(a):
            erreurs.append(f"pas de passage entre {a} et {b}")
            break
    if len(set(sol)) != len(sol):
        erreurs.append("la solution repasse par une même case")
    if sol != resoudre_bfs(lab):
        erreurs.append("la solution ne correspond pas au chemin BFS")
    if "N" not in lab.ouvertures[lab.depart[0]][lab.depart[1]] or lab.depart[0] != 0:
        erreurs.append("entrée non percée sur le bord haut")
    if "S" not in lab.ouvertures[lab.arrivee[0]][lab.arrivee[1]] or lab.arrivee[0] != lab.lignes - 1:
        erreurs.append("sortie non percée sur le bord bas")
    return erreurs


def serie_progressive(rng: random.Random, par_niveau: int = 10,
                      niveaux: tuple[str, ...] = ("debutant", "intermediaire", "defi")) -> list[Labyrinthe]:
    """Série de labyrinthes de difficulté croissante. Pour un niveau donné, on rejette les
    tirages dont le chemin-solution est trop court (labyrinthe trop facile pour sa taille)."""
    out: list[Labyrinthe] = []
    for niveau in niveaux:
        tailles = TAILLES_NIVEAUX[niveau]
        for i in range(par_niveau):
            l, c = tailles[min(len(tailles) - 1, i * len(tailles) // par_niveau)]
            out.append(generer_avec_longueur_min(l, c, rng, niveau))
    return out


def generer_avec_longueur_min(lignes: int, colonnes: int, rng: random.Random, niveau: str,
                              ratio_min: float = 0.25, essais: int = 50) -> Labyrinthe:
    meilleur = None
    for _ in range(essais):
        lab = generer(lignes, colonnes, rng, niveau)
        if meilleur is None or len(lab.solution) > len(meilleur.solution):
            meilleur = lab
        if len(lab.solution) >= ratio_min * lignes * colonnes:
            return lab
    assert meilleur is not None
    return meilleur
