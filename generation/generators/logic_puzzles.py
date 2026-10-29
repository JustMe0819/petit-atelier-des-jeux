"""Activités de logique à réponse unique, vérifiée par programme.

Types :
- suite_formes   : suite de figures périodique, choisir la figure suivante (QCM) ;
- suite_nombres  : suite de nombres (+1, +2, +5, +10, -1, -2, ×2), compléter les cases ;
- intrus         : une seule figure diffère selon l'attribut NOMMÉ dans la consigne ;
- grille         : grille 3 × 3 (carré latin), trouver la figure manquante (QCM) ;
- association    : relier selon une règle explicite (une seule façon de tout relier).
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Any

from generation.generators.figures import ATTRIBUTS, FORMES, MOTIFS, Figure, nom_figure

LETTRES = "ABCDEF"
NOMS_TYPES = {
    "suite_formes": "Suite de formes",
    "suite_nombres": "Suite de nombres",
    "intrus": "L'intrus",
    "grille": "La case manquante",
    "association": "Associations",
}


@dataclass
class Activite:
    id: str
    numero: int
    niveau: str
    type: str
    consigne: str
    donnees: dict[str, Any]
    reponse: Any
    explication: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def nom_type(self) -> str:
        return NOMS_TYPES[self.type]


# ======================================================================= vérifications
def periode_minimale(seq: list[Any]) -> int:
    for q in range(1, len(seq) + 1):
        if all(seq[i] == seq[i + q] for i in range(len(seq) - q)):
            return q
    return len(seq)


def _verifier_suite_formes(a: Activite) -> list[str]:
    e = []
    unite, k, options = a.donnees["unite"], a.donnees["nb_affiches"], a.donnees["options"]
    affiches = a.donnees["affiches"]
    if affiches != [unite[i % len(unite)] for i in range(k)]:
        e.append("figures affichées incohérentes avec le motif")
    if k < 2 * len(unite):
        e.append("le motif n'est pas montré au moins deux fois")
    if periode_minimale(affiches) != len(unite):
        e.append("la période visible n'est pas celle attendue")
    attendu = unite[k % len(unite)]
    bons = [i for i, o in enumerate(options) if o == attendu]
    if len(bons) != 1:
        e.append(f"{len(bons)} options correctes au lieu d'une")
    elif bons[0] != a.reponse:
        e.append("la réponse enregistrée n'est pas la bonne option")
    if len(set(options)) != len(options):
        e.append("options en double")
    return e


def regles_numeriques_compatibles(termes: list[int | None]) -> set[tuple[int, ...]]:
    """Valeurs des cases vides selon toutes les règles candidates compatibles avec
    les termes visibles (arithmétiques de pas -20..20, géométriques ×2 ou ×3)."""
    visibles = [(i, t) for i, t in enumerate(termes) if t is not None]
    trous = [i for i, t in enumerate(termes) if t is None]
    reponses: set[tuple[int, ...]] = set()
    (i0, t0) = visibles[0]
    for d in range(-20, 21):
        if d == 0:
            continue
        if all(t == t0 + (i - i0) * d for i, t in visibles):
            reponses.add(tuple(t0 + (i - i0) * d for i in trous))
    for r in (2, 3):
        for a in range(1, 51):
            if all(t == a * r ** i for i, t in visibles):
                reponses.add(tuple(a * r ** i for i in trous))
    return reponses


def _verifier_suite_nombres(a: Activite) -> list[str]:
    e = []
    termes, trous = a.donnees["termes"], a.donnees["trous"]
    visibles: list[int | None] = [None if i in trous else t for i, t in enumerate(termes)]
    rep = regles_numeriques_compatibles(visibles)
    attendu = tuple(termes[i] for i in trous)
    if len(rep) != 1:
        e.append(f"{len(rep)} réponses possibles selon les règles candidates")
    elif rep.pop() != attendu or tuple(a.reponse) != attendu:
        e.append("la réponse ne correspond pas à la règle")
    if any(t < 0 or t > 100 for t in termes):
        e.append("nombres hors de l'intervalle 0–100")
    if sum(1 for i in range(len(termes)) if i not in trous) < 3:
        e.append("moins de trois nombres visibles")
    return e


def _verifier_intrus(a: Activite) -> list[str]:
    e = []
    figs: list[Figure] = a.donnees["figures"]
    cible = a.donnees["attribut"]
    n = len(figs)
    valeurs = [f.attr(cible) for f in figs]
    commun = max(set(valeurs), key=valeurs.count)
    differents = [i for i, v in enumerate(valeurs) if v != commun]
    if len(differents) != 1 or valeurs.count(commun) != n - 1:
        e.append("il n'y a pas exactement un intrus pour l'attribut demandé")
    elif differents[0] != a.reponse:
        e.append("la réponse enregistrée n'est pas l'intrus")
    for autre in ATTRIBUTS:
        if autre == cible:
            continue
        vals = [f.attr(autre) for f in figs]
        if max(vals.count(v) for v in set(vals)) == n - 1:
            e.append(f"l'attribut « {autre} » désigne aussi un intrus (ambiguïté)")
    return e


def _grille_valide(grille: list[list[Figure]], regles: list[str]) -> bool:
    for attr in regles:
        for r in range(3):
            if len({grille[r][c].attr(attr) for c in range(3)}) != 3:
                return False
        for c in range(3):
            if len({grille[r][c].attr(attr) for r in range(3)}) != 3:
                return False
    for attr in ATTRIBUTS:
        if attr not in regles and len({grille[r][c].attr(attr) for r in range(3) for c in range(3)}) != 1:
            return False  # un attribut hors règle doit rester constant
    return True


def _verifier_grille(a: Activite) -> list[str]:
    e = []
    grille, trou, options = a.donnees["grille"], a.donnees["trou"], a.donnees["options"]
    regles = a.donnees["regles"]
    bons = []
    for i, o in enumerate(options):
        g = [row[:] for row in grille]
        g[trou[0]][trou[1]] = o
        if _grille_valide(g, regles):
            bons.append(i)
    if len(bons) != 1:
        e.append(f"{len(bons)} options valides au lieu d'une")
    elif bons[0] != a.reponse:
        e.append("la réponse enregistrée n'est pas la bonne option")
    if len(set(options)) != len(options):
        e.append("options en double")
    return e


def compatible(regle: str, g: Any, d: Any) -> bool:
    if regle == "ombre":
        return g.forme == d.forme
    if regle == "quantite":
        return g == d
    if regle == "meme_forme_motif":
        return g.forme == d.forme and g.motif == d.motif
    raise ValueError(regle)


def appariements_parfaits(regle: str, gauche: list[Any], droite: list[Any]) -> list[tuple[int, ...]]:
    return [p for p in itertools.permutations(range(len(droite)))
            if all(compatible(regle, gauche[i], droite[p[i]]) for i in range(len(gauche)))]


def _verifier_association(a: Activite) -> list[str]:
    e = []
    sols = appariements_parfaits(a.donnees["regle"], a.donnees["gauche"], a.donnees["droite"])
    if len(sols) != 1:
        e.append(f"{len(sols)} façons de tout relier au lieu d'une")
    elif tuple(a.reponse) != sols[0]:
        e.append("la réponse enregistrée ne correspond pas à la règle")
    return e


VERIFICATEURS = {
    "suite_formes": _verifier_suite_formes,
    "suite_nombres": _verifier_suite_nombres,
    "intrus": _verifier_intrus,
    "grille": _verifier_grille,
    "association": _verifier_association,
}


def verifier(a: Activite) -> list[str]:
    return VERIFICATEURS[a.type](a)


# ======================================================================= génération
def _options_qcm(rng: random.Random, bonne: Figure, candidats: list[Figure], n: int) -> tuple[list[Figure], int]:
    pool = sorted({c for c in candidats if c != bonne})
    rng.shuffle(pool)
    options = [bonne] + pool[: n - 1]
    rng.shuffle(options)
    return options, options.index(bonne)


def gen_suite_formes(rng: random.Random, gabarit: str, avec_motif: bool, nb_options: int = 3) -> dict:
    """gabarit : suite de lettres décrivant le motif répété, ex. « AB », « AAB », « ABC »."""
    lettres = sorted(set(gabarit))
    formes = rng.sample(FORMES, len(lettres))
    if avec_motif:
        motifs = rng.sample(MOTIFS, len(lettres))
        table = {l: Figure(f, m) for l, f, m in zip(lettres, formes, motifs)}
    else:
        motif = rng.choice(["vide", "plein"])
        table = {l: Figure(f, motif) for l, f in zip(lettres, formes)}
    unite = [table[l] for l in gabarit]
    p = len(unite)
    k = 2 * p + rng.randrange(0, p) if p <= 3 else 2 * p + 1
    k = min(k, 9)
    affiches = [unite[i % p] for i in range(k)]
    bonne = unite[k % p]
    # Distracteurs : autres figures du motif + variantes proches (même forme, autre motif…).
    candidats = list(table.values())
    candidats += [bonne.avec(motif=m) for m in MOTIFS]
    candidats += [Figure(f, bonne.motif) for f in FORMES]
    options, rep = _options_qcm(rng, bonne, candidats, nb_options)
    return {"donnees": {"unite": unite, "nb_affiches": k, "affiches": affiches, "options": options,
                        "gabarit": gabarit},
            "reponse": rep,
            "explication": f"Le motif se répète : la figure suivante est {nom_figure(bonne)}."}


def gen_suite_formes_double(rng: random.Random) -> dict:
    """Deux attributs qui changent selon des rythmes différents (forme ABAB, motif AABB)."""
    f1, f2 = rng.sample(FORMES, 2)
    m1, m2 = rng.sample(MOTIFS, 2)
    unite = [Figure(f1, m1), Figure(f2, m1), Figure(f1, m2), Figure(f2, m2)]
    k = 9
    affiches = [unite[i % 4] for i in range(k)]
    bonne = unite[k % 4]
    candidats = [bonne.avec(motif=m1 if bonne.motif == m2 else m2), bonne.avec(forme=f1 if bonne.forme == f2 else f2)]
    candidats += [Figure(rng.choice([f for f in FORMES if f not in (f1, f2)]), bonne.motif)]
    options, rep = _options_qcm(rng, bonne, candidats, 4)
    return {"donnees": {"unite": unite, "nb_affiches": k, "affiches": affiches, "options": options,
                        "gabarit": "double"},
            "reponse": rep,
            "explication": f"La forme change à chaque fois et le motif toutes les deux figures : "
                           f"la suivante est {nom_figure(bonne)}."}


def gen_suite_nombres(rng: random.Random, regle: str, nb_termes: int, trous: list[int]) -> dict:
    if regle == "x2":
        depart = rng.choice([1, 2, 3])
        termes = [depart * 2 ** i for i in range(nb_termes)]
        texte = "On double à chaque fois (× 2)."
    else:
        pas = int(regle)
        if pas > 0:
            depart = rng.randrange(0, max(1, 100 - pas * (nb_termes - 1)) if pas >= 5 else 12)
            if pas == 10:
                depart = rng.randrange(1, 10)
            elif pas == 5:
                depart = rng.choice([0, 5, 10, 15, 20])
        else:
            depart = rng.randrange(-pas * (nb_termes - 1) + 2, -pas * (nb_termes - 1) + 12)
        termes = [depart + i * pas for i in range(nb_termes)]
        texte = (f"On ajoute {pas} à chaque fois." if pas > 0 else f"On enlève {-pas} à chaque fois.")
    return {"donnees": {"termes": termes, "trous": trous, "regle": regle},
            "reponse": [termes[i] for i in trous],
            "explication": texte}


def gen_intrus(rng: random.Random, attribut: str, n: int, varier: list[str]) -> dict:
    """Une figure diffère par `attribut` ; les attributs de `varier` changent sans désigner d'intrus."""
    base = Figure(rng.choice(FORMES), rng.choice(["vide", "plein", "rayé"]), "grand")
    autre_valeur = {
        "forme": lambda: rng.choice([f for f in FORMES if f != base.forme]),
        "motif": lambda: rng.choice([m for m in MOTIFS if m != base.motif]),
        "taille": lambda: "petit",
    }[attribut]()
    figs = [base] * n
    # Variation d'autres attributs : au moins deux figures par valeur, pour ne pas créer de faux intrus.
    for attr in varier:
        pool = {"forme": FORMES, "motif": MOTIFS, "taille": ["grand", "petit"]}[attr]
        v1 = getattr(base, attr)
        v2 = rng.choice([v for v in pool if v != v1])
        idx = list(range(n))
        rng.shuffle(idx)
        nb = rng.randrange(2, n - 1)
        for i in idx[:nb]:
            figs[i] = figs[i].avec(**{attr: v2})
    pos = rng.randrange(n)
    figs = list(figs)
    figs[pos] = figs[pos].avec(**{attribut: autre_valeur})
    return {"donnees": {"figures": figs, "attribut": attribut},
            "reponse": pos,
            "explication": f"L'intrus est {nom_figure(figs[pos], avec_taille=attribut == 'taille')} : "
                           f"c'est la seule figure avec "
                           f"{ {'forme': 'une autre forme', 'motif': 'un autre motif', 'taille': 'une autre taille'}[attribut] }."}


def gen_grille(rng: random.Random, regles: list[str]) -> dict:
    formes = rng.sample(FORMES, 3)
    perm_l = rng.sample(range(3), 3)
    perm_c = rng.sample(range(3), 3)
    motifs = rng.sample(MOTIFS, 3)
    motif_fixe = rng.choice(["vide", "plein"])
    decalage = 2  # carrés latins orthogonaux : chaque couple (forme, motif) est différent
    grille: list[list[Figure]] = []
    for r in range(3):
        row = []
        for c in range(3):
            i, j = perm_l[r], perm_c[c]
            f = formes[(i + j) % 3]
            m = motifs[(i + decalage * j) % 3] if "motif" in regles else motif_fixe
            row.append(Figure(f, m))
        grille.append(row)
    trou = (rng.randrange(3), rng.randrange(3))
    bonne = grille[trou[0]][trou[1]]
    if "motif" in regles:
        candidats = [bonne.avec(motif=m) for m in motifs] + [bonne.avec(forme=f) for f in formes]
        candidats += [Figure(f, m) for f in formes for m in motifs]
    else:
        candidats = [Figure(f, motif_fixe) for f in formes] + [Figure(rng.choice(FORMES), motif_fixe)]
    options, rep = _options_qcm(rng, bonne, candidats, 4 if "motif" in regles else 3)
    grille_trou = [row[:] for row in grille]
    return {"donnees": {"grille": grille_trou, "trou": trou, "options": options, "regles": regles,
                        "solution": grille},
            "reponse": rep,
            "explication": f"Il manque {nom_figure(bonne, avec_motif='motif' in regles)}."}


def gen_association(rng: random.Random, regle: str, n: int, maxi: int = 10) -> dict:
    if regle == "ombre":
        formes = rng.sample(FORMES, n)
        gauche = [Figure(f, rng.choice(["vide", "rayé", "pois"])) for f in formes]
        droite = [Figure(f, "plein") for f in formes]
    elif regle == "quantite":
        valeurs = rng.sample(range(1, maxi + 1), n)
        gauche = valeurs
        droite = list(valeurs)
    elif regle == "meme_forme_motif":
        f1, f2 = rng.sample(FORMES, 2)
        motifs = rng.sample(["vide", "plein", "rayé", "pois"], 2 if n <= 4 else 3)
        combis = [Figure(f, m) for f in (f1, f2) for m in motifs]
        gauche = rng.sample(combis, n)
        droite = [g.avec(taille="petit") for g in gauche]
    else:
        raise ValueError(regle)
    perm = list(range(n))
    rng.shuffle(perm)
    droite_melangee = [None] * n
    for i, p in enumerate(perm):
        droite_melangee[p] = droite[i]
    return {"donnees": {"regle": regle, "gauche": gauche, "droite": droite_melangee},
            "reponse": perm,
            "explication": ""}


CONSIGNES = {
    "suite_formes": "Observe la suite. Quelle figure vient ensuite ? Entoure la bonne réponse.",
    "suite_nombres": "Trouve la règle et écris les nombres qui manquent.",
    "intrus_forme": "Une seule figure n'a pas la même FORME que les autres. Entoure-la.",
    "intrus_motif": "Une seule figure n'a pas le même MOTIF que les autres. Entoure-la.",
    "intrus_taille": "Une seule figure n'a pas la même TAILLE que les autres. Entoure-la.",
    "grille_forme": "Dans chaque ligne et chaque colonne, chaque forme apparaît une seule fois. "
                    "Quelle figure manque ? Entoure-la.",
    "grille_forme_motif": "Dans chaque ligne et chaque colonne, chaque forme ET chaque motif "
                          "apparaissent une seule fois. Quelle figure manque ? Entoure-la.",
    "association_ombre": "Relie chaque figure à son ombre.",
    "association_quantite": "Compte les points et relie chaque groupe au bon nombre.",
    "association_meme_forme_motif": "Relie chaque grande figure à la petite figure qui a la même forme "
                                    "et le même motif.",
}


def construire(rng: random.Random, spec: dict, numero: int, niveau: str, prefixe: str) -> Activite:
    """Construit une activité depuis une spécification ; régénère tant que la vérification échoue."""
    t = spec["type"]
    for _ in range(200):
        if t == "suite_formes":
            if spec.get("double"):
                res = gen_suite_formes_double(rng)
            else:
                res = gen_suite_formes(rng, spec["gabarit"], spec.get("motif", False), spec.get("options", 3))
            consigne = CONSIGNES["suite_formes"]
        elif t == "suite_nombres":
            res = gen_suite_nombres(rng, spec["regle"], spec.get("n", 6), spec.get("trous", [5]))
            consigne = CONSIGNES["suite_nombres"]
        elif t == "intrus":
            res = gen_intrus(rng, spec["attribut"], spec.get("n", 5), spec.get("varier", []))
            consigne = CONSIGNES[f"intrus_{spec['attribut']}"]
        elif t == "grille":
            res = gen_grille(rng, spec["regles"])
            consigne = CONSIGNES["grille_" + "_".join(spec["regles"])]
        elif t == "association":
            res = gen_association(rng, spec["regle"], spec.get("n", 4), spec.get("maxi", 10))
            consigne = CONSIGNES[f"association_{spec['regle']}"]
        else:
            raise ValueError(t)
        a = Activite(f"{prefixe}-{numero:02d}", numero, niveau, t, consigne, res["donnees"],
                     res["reponse"], res["explication"])
        if not verifier(a):
            return a
    raise RuntimeError(f"impossible de générer une activité valide : {spec}")


# Plan progressif des 30 activités du pack « Les défis de la logique ».
PLAN_PACK: list[tuple[str, dict]] = [
    ("debutant", {"type": "suite_formes", "gabarit": "AB"}),
    ("debutant", {"type": "suite_nombres", "regle": "1", "n": 6, "trous": [5]}),
    ("debutant", {"type": "intrus", "attribut": "forme", "n": 4}),
    ("debutant", {"type": "association", "regle": "ombre", "n": 3}),
    ("debutant", {"type": "suite_formes", "gabarit": "ABC"}),
    ("debutant", {"type": "suite_nombres", "regle": "2", "n": 6, "trous": [5]}),
    ("debutant", {"type": "grille", "regles": ["forme"]}),
    ("debutant", {"type": "intrus", "attribut": "forme", "n": 5}),
    ("debutant", {"type": "association", "regle": "quantite", "n": 4, "maxi": 5}),
    ("debutant", {"type": "suite_nombres", "regle": "-1", "n": 6, "trous": [5]}),
    ("intermediaire", {"type": "suite_formes", "gabarit": "AAB", "motif": True}),
    ("intermediaire", {"type": "suite_nombres", "regle": "5", "n": 6, "trous": [5]}),
    ("intermediaire", {"type": "intrus", "attribut": "motif", "n": 5, "varier": ["forme"]}),
    ("intermediaire", {"type": "grille", "regles": ["forme"]}),
    ("intermediaire", {"type": "association", "regle": "quantite", "n": 5, "maxi": 10}),
    ("intermediaire", {"type": "suite_formes", "gabarit": "ABB", "motif": True, "options": 4}),
    ("intermediaire", {"type": "suite_nombres", "regle": "10", "n": 6, "trous": [5]}),
    ("intermediaire", {"type": "intrus", "attribut": "motif", "n": 6, "varier": ["forme"]}),
    ("intermediaire", {"type": "association", "regle": "ombre", "n": 5}),
    ("intermediaire", {"type": "suite_nombres", "regle": "-2", "n": 6, "trous": [5]}),
    ("defi", {"type": "suite_formes", "gabarit": "ABCB", "motif": True, "options": 4}),
    ("defi", {"type": "suite_nombres", "regle": "10", "n": 6, "trous": [2]}),
    ("defi", {"type": "intrus", "attribut": "taille", "n": 6, "varier": ["forme", "motif"]}),
    ("defi", {"type": "grille", "regles": ["forme", "motif"]}),
    ("defi", {"type": "association", "regle": "meme_forme_motif", "n": 4}),
    ("defi", {"type": "suite_nombres", "regle": "x2", "n": 6, "trous": [5]}),
    ("defi", {"type": "suite_formes", "double": True}),
    ("defi", {"type": "suite_nombres", "regle": "5", "n": 7, "trous": [3, 6]}),
    ("defi", {"type": "intrus", "attribut": "motif", "n": 6, "varier": ["forme", "taille"]}),
    ("defi", {"type": "grille", "regles": ["forme", "motif"]}),
]


def serie(rng: random.Random, plan: list[tuple[str, dict]], prefixe: str, debut: int = 1) -> list[Activite]:
    return [construire(rng, spec, debut + i, niveau, prefixe) for i, (niveau, spec) in enumerate(plan)]
