"""Jeux d'observation : « Trouve les différences » et « Compte les … ».

Les scènes sont des listes d'objets (pictogrammes simples) posés sur une grille
d'emplacements légèrement décalés. Les différences sont connues par construction
et vérifiées (modèle + rendu, voir generation/qa/verif_rendu.py).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace

# Pictogrammes disponibles pour les scènes (dessinés par pdf_builder/pictos.py).
OBJETS_NATURE = ["arbre", "fleur", "soleil", "nuage", "champignon", "maison", "poisson",
                 "oiseau", "etoile", "coeur", "pomme", "escargot"]
ANIMAUX = ["herisson", "lapin", "souris", "chouette", "grenouille", "ours", "tortue",
           "poussin", "chat", "renard"]
DINOS = ["trex", "diplodocus", "triceratops", "stegosaure", "oeuf", "volcan", "fougere", "os"]
ESPACE = ["fusee", "planete", "lune", "etoile", "comete", "soucoupe", "alien", "robot"]
PIRATES = ["bateau", "coffre", "perroquet", "ancre", "piece", "palmier", "crabe", "carte"]
MAGIE = ["dragon", "baguette", "chapeau", "chateau", "potion", "cristal", "grimoire", "chouette"]

NOMS = {
    "arbre": ("arbre", "arbres"), "fleur": ("fleur", "fleurs"), "soleil": ("soleil", "soleils"),
    "nuage": ("nuage", "nuages"), "champignon": ("champignon", "champignons"),
    "maison": ("maison", "maisons"), "poisson": ("poisson", "poissons"), "oiseau": ("oiseau", "oiseaux"),
    "etoile": ("étoile", "étoiles"), "coeur": ("cœur", "cœurs"), "pomme": ("pomme", "pommes"),
    "escargot": ("escargot", "escargots"), "herisson": ("hérisson", "hérissons"),
    "lapin": ("lapin", "lapins"), "souris": ("souris", "souris"), "chouette": ("chouette", "chouettes"),
    "grenouille": ("grenouille", "grenouilles"), "ours": ("ours", "ours"), "tortue": ("tortue", "tortues"),
    "poussin": ("poussin", "poussins"), "chat": ("chat", "chats"), "renard": ("renard", "renards"),
    "trex": ("tyrannosaure", "tyrannosaures"), "diplodocus": ("diplodocus", "diplodocus"),
    "triceratops": ("tricératops", "tricératops"), "stegosaure": ("stégosaure", "stégosaures"),
    "oeuf": ("œuf", "œufs"), "volcan": ("volcan", "volcans"), "fougere": ("fougère", "fougères"),
    "os": ("os", "os"),
    "fusee": ("fusée", "fusées"), "planete": ("planète", "planètes"), "lune": ("lune", "lunes"),
    "comete": ("comète", "comètes"), "soucoupe": ("soucoupe volante", "soucoupes volantes"),
    "alien": ("extraterrestre", "extraterrestres"), "robot": ("robot", "robots"),
    "bateau": ("bateau", "bateaux"), "coffre": ("coffre", "coffres"), "perroquet": ("perroquet", "perroquets"),
    "ancre": ("ancre", "ancres"), "piece": ("pièce d'or", "pièces d'or"), "palmier": ("palmier", "palmiers"),
    "crabe": ("crabe", "crabes"), "carte": ("carte au trésor", "cartes au trésor"),
    "dragon": ("dragon", "dragons"), "baguette": ("baguette magique", "baguettes magiques"),
    "chapeau": ("chapeau pointu", "chapeaux pointus"), "chateau": ("château", "châteaux"),
    "potion": ("potion", "potions"), "cristal": ("cristal", "cristaux"), "grimoire": ("grimoire", "grimoires"),
}


def nom(kind: str, n: int = 1) -> str:
    return NOMS[kind][0 if n == 1 else 1]


@dataclass(frozen=True)
class Objet:
    kind: str
    x: float      # centre, en fraction de la largeur de la scène (0..1)
    y: float      # centre, en fraction de la hauteur (0..1)
    taille: float  # diamètre, en fraction de la plus petite dimension d'un emplacement
    slot: int = -1


@dataclass
class Scene:
    objets: list[Objet]
    colonnes: int = 5
    lignes: int = 3

    def par_slot(self) -> dict[int, Objet]:
        return {o.slot: o for o in self.objets}


@dataclass
class JeuDifferences:
    id: str
    scene_a: Scene
    scene_b: Scene
    differences: list[dict] = field(default_factory=list)  # {slot, type, texte}

    @property
    def n(self) -> int:
        return len(self.differences)


def _scene_base(rng: random.Random, kinds: list[str], colonnes: int, lignes: int, vides: int) -> Scene:
    slots = list(range(colonnes * lignes))
    rng.shuffle(slots)
    occupes = sorted(slots[vides:])
    objets = []
    for s in occupes:
        c, l = s % colonnes, s // colonnes
        jx = rng.uniform(-0.06, 0.06)  # léger décalage, l'objet reste dans son emplacement
        jy = rng.uniform(-0.06, 0.06)
        objets.append(Objet(rng.choice(kinds), (c + 0.5 + jx) / colonnes, (l + 0.5 + jy) / lignes,
                            rng.choice([0.7, 0.76]), s))
    return Scene(objets, colonnes, lignes)


def generer_differences(rng: random.Random, n: int, kinds: list[str], ident: str,
                        colonnes: int = 5, lignes: int = 3) -> JeuDifferences:
    vides = max(2, n // 2)
    a = _scene_base(rng, kinds, colonnes, lignes, vides)
    occupes = [o.slot for o in a.objets]
    libres = [s for s in range(colonnes * lignes) if s not in occupes]
    types = ["absent", "remplace", "taille", "ajout"]
    b_objets = {o.slot: o for o in a.objets}
    diffs: list[dict] = []
    candidats = list(occupes)
    rng.shuffle(candidats)
    for i in range(n):
        t = types[i % len(types)]
        if t == "ajout" and libres:
            s = libres.pop(rng.randrange(len(libres)))
            c, l = s % colonnes, s // colonnes
            k = rng.choice(kinds)
            b_objets[s] = Objet(k, (c + 0.5) / colonnes, (l + 0.5) / lignes, 0.74, s)
            diffs.append({"slot": s, "type": t, "texte": f"un {nom(k)} en plus" if not _feminin(k)
                          else f"une {nom(k)} en plus"})
            continue
        if t == "ajout":
            t = "absent"
        s = candidats.pop()
        o = b_objets[s]
        if t == "absent":
            del b_objets[s]
            diffs.append({"slot": s, "type": t, "texte": f"{_article(o.kind)} a disparu"})
        elif t == "remplace":
            k = rng.choice([k for k in kinds if k != o.kind])
            b_objets[s] = replace(o, kind=k)
            diffs.append({"slot": s, "type": t, "texte": f"{_article(o.kind)} est remplacé{'e' if _feminin(o.kind) else ''} "
                                                          f"par {_article(k, indef=True)}"})
        elif t == "taille":
            b_objets[s] = replace(o, taille=round(o.taille * 0.5, 3))
            diffs.append({"slot": s, "type": t, "texte": f"{_article(o.kind)} est plus petit{'e' if _feminin(o.kind) else ''}"})
    b = Scene(sorted(b_objets.values(), key=lambda o: o.slot), colonnes, lignes)
    return JeuDifferences(ident, a, b, sorted(diffs, key=lambda d: d["slot"]))


_FEM = {"fleur", "maison", "etoile", "pomme", "souris", "chouette", "grenouille", "tortue", "fougere",
        "fusee", "planete", "lune", "comete", "soucoupe", "ancre", "piece", "carte", "baguette", "potion"}


def _feminin(k: str) -> bool:
    return k in _FEM


def _article(k: str, indef: bool = False) -> str:
    n = nom(k)
    if indef:
        return ("une " if _feminin(k) else "un ") + n
    if n[0] in "aeiouéèêœh" and k not in ("herisson",):
        return "l'" + n
    return ("la " if _feminin(k) else "le ") + n


def verifier_differences(j: JeuDifferences) -> list[str]:
    e: list[str] = []
    pa, pb = j.scene_a.par_slot(), j.scene_b.par_slot()
    differents = sorted(s for s in set(pa) | set(pb) if pa.get(s) != pb.get(s))
    annonces = sorted(d["slot"] for d in j.differences)
    if differents != annonces:
        e.append(f"différences réelles {differents} ≠ annoncées {annonces}")
    if len(set(annonces)) != len(annonces):
        e.append("deux différences au même endroit")
    for s in differents:
        oa, ob = pa.get(s), pb.get(s)
        if oa and ob and oa.kind == ob.kind and abs(oa.taille - ob.taille) < 0.2 and (oa.x, oa.y) == (ob.x, ob.y):
            e.append(f"différence trop discrète à l'emplacement {s}")
    return e


# ---------------------------------------------------------------- comptage
@dataclass
class JeuComptage:
    id: str
    objets: list[Objet]
    kinds: list[str]
    reponses: dict[str, int]
    ratio: float = 1.6  # largeur / hauteur de la scène


def generer_comptage(rng: random.Random, kinds: list[str], mini: int, maxi: int, ident: str,
                     ratio: float = 1.3, taille: float | None = None) -> JeuComptage:
    """Objets posés au hasard sans chevauchement (taille = diamètre / hauteur de la scène).
    Par défaut, la taille s'adapte au nombre maximal d'objets pour rester lisible."""
    if taille is None:
        taille = min(0.16, math.sqrt(0.42 * ratio / (maxi * len(kinds))) / 1.12)
    for _ in range(200):
        cibles = {k: rng.randint(mini, maxi) for k in kinds}
        if len(set(cibles.values())) < len(kinds):
            continue  # des réponses toutes différentes : plus intéressant et sans confusion
        objets: list[Objet] = []
        ok = True
        ordre = [k for k in kinds for _ in range(cibles[k])]
        rng.shuffle(ordre)
        for k in ordre:
            for _essai in range(400):
                x = rng.uniform(taille / ratio * 0.6, 1 - taille / ratio * 0.6)
                y = rng.uniform(taille * 0.6, 1 - taille * 0.6)
                o = Objet(k, x, y, taille)
                if all(_distance(o, p, ratio) >= taille * 1.12 for p in objets):
                    objets.append(o)
                    break
            else:
                ok = False
                break
        if ok:
            return JeuComptage(ident, objets, list(kinds), cibles, ratio)
    raise RuntimeError("impossible de placer les objets sans chevauchement")


def _distance(a: Objet, b: Objet, ratio: float) -> float:
    # Distance exprimée en unités de hauteur de scène.
    return math.hypot((a.x - b.x) * ratio, a.y - b.y)


def verifier_comptage(j: JeuComptage) -> list[str]:
    e: list[str] = []
    for k in j.kinds:
        n = sum(1 for o in j.objets if o.kind == k)
        if n != j.reponses[k]:
            e.append(f"{k} : {n} objets dessinés pour une réponse de {j.reponses[k]}")
    for i, a in enumerate(j.objets):
        for b in j.objets[i + 1:]:
            if _distance(a, b, j.ratio) < a.taille * 1.05:
                e.append("deux objets se chevauchent")
                return e
        r = a.taille / 2
        if not (r / j.ratio <= a.x <= 1 - r / j.ratio and r <= a.y <= 1 - r):
            e.append("objet hors de la scène")
    return e
