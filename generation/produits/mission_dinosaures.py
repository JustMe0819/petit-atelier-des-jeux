"""Produit « Mission dinosaures » : cahier-aventure avec histoire suivie (+ version économie d'encre)."""
from __future__ import annotations

import random

from generation.assets import colour_designs as cd
from generation.assets import pixel_designs as pd
from generation.config import ConfigProduit
from generation.pdf_builder.document import PageSpec
from generation.generators.activity_books import TYPES_JEUX, Composeur, assembler
from generation.pdf_builder.pages_activites import Recit
from generation.pdf_builder.pages_speciales import page_couverture, page_diplome, page_intro_aventure
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de
from generation.templates import charger

TITRE = "Mission dinosaures"
DINOS = ["trex", "diplodocus", "triceratops", "stegosaure", "oeuf", "volcan", "fougere", "os"]

L = {
    "1a": [("debutant", {"type": "suite_formes", "gabarit": "AB"}),
           ("debutant", {"type": "suite_nombres", "regle": "1", "n": 6, "trous": [5]})],
    "1b": [("debutant", {"type": "intrus", "attribut": "forme", "n": 5}),
           ("debutant", {"type": "association", "regle": "quantite", "n": 4, "maxi": 6})],
    "2a": [("intermediaire", {"type": "grille", "regles": ["forme"]}),
           ("intermediaire", {"type": "suite_nombres", "regle": "-2", "n": 6, "trous": [5]})],
    "2b": [("intermediaire", {"type": "suite_formes", "gabarit": "AAB", "motif": True}),
           ("intermediaire", {"type": "association", "regle": "ombre", "n": 5})],
    "3a": [("defi", {"type": "intrus", "attribut": "taille", "n": 6, "varier": ["forme", "motif"]}),
           ("defi", {"type": "suite_nombres", "regle": "x2", "n": 6, "trous": [5]})],
}


def composer(cfg: ConfigProduit) -> tuple[list[PageSpec], Composeur]:
    """Génère et vérifie toutes les activités ; renvoie les pages (sans rendu PDF)."""
    rng = random.Random(cfg.graine)
    histoire = charger("histoire_dinosaures")
    gab = charger("enigmes")["dinosaures"]
    par_niveau = {n: [g for g in gab if g["niveau"] == n] for n in (1, 2, 3)}
    etapes = iter(enumerate(histoire["etapes"], start=1))
    k = Composeur(rng, theme_de(cfg), "dino")

    def r(picto: str = "triceratops") -> Recit:
        num, texte = next(etapes)
        return Recit(num, texte, picto)

    s1, s2, s3 = "Partie 1 · la forêt", "Partie 2 · la plaine", "Partie 3 · le volcan"
    pico = "Aide Pico à trouver le bon chemin."
    k.labyrinthe((7, 7), "debutant", "triceratops", "fougere", pico, r(), s1)
    k.comptage(["oeuf", "fougere", "os"], 2, 7, r(), s1, titre="Les provisions de Pico")
    k.logique(L["1a"], r("tortue"), s1)
    k.nonogrammes([pd.PETITS_DINO[0]], r(), s1)
    k.code("NID", r("diplodocus"), s1)
    k.differences(5, DINOS, r(), s1)
    k.labyrinthe((8, 8), "debutant", "triceratops", "fougere", pico, r(), s1)
    k.problemes(par_niveau[1][:2], r("diplodocus"), s1, illustrations=["fougere", "oeuf"])
    k.coloriage(cd.DINO_VERT, r(), s1)
    k.chemin(1, "triceratops", "fougere", "de Pico", r(), s1)
    k.logique(L["1b"], r(), s1)
    k.labyrinthe((10, 10), "intermediaire", "triceratops", "fougere", pico, r(), s2)
    k.nonogrammes([pd.PETITS_DINO[1]], r(), s2)
    k.comptage(["trex", "diplodocus", "stegosaure", "triceratops"], 2, 8, r(), s2, titre="Les dinosaures de la plaine")
    k.code("PONT", r(), s2)
    k.differences(6, DINOS, r(), s2)
    k.logique(L["2a"], r("stegosaure"), s2)
    k.labyrinthe((12, 11), "intermediaire", "triceratops", "fougere", pico, r(), s2)
    k.problemes(par_niveau[2][:3], r(), s2, illustrations=["fougere", "stegosaure", "os"])
    k.nonogrammes([pd.GRANDS_DINO[0]], r(), s2)
    k.coloriage(cd.VOLCAN, r(), s2)
    k.chemin(5, "triceratops", "volcan", "de Pico", r(), s2)
    k.labyrinthe((13, 12), "intermediaire", "triceratops", "volcan", pico, r(), s2)
    k.logique(L["2b"], r("trex"), s2)
    k.differences(7, DINOS, r(), s3)
    k.code("VOLCAN", r(), s3)
    k.nonogrammes([pd.GRANDS_DINO[1]], r(), s3)
    k.comptage(["oeuf", "trex", "fougere", "volcan"], 3, 10, r(), s3, titre="Au pied du volcan")
    k.labyrinthe((15, 14), "defi", "triceratops", "volcan", pico, r(), s3)
    k.problemes(par_niveau[3][:3], r(), s3, illustrations=["triceratops", "diplodocus", "oeuf"])
    k.logique(L["3a"], r(), s3)
    k.coloriage(cd.OEUF, r(), s3)
    k.nonogrammes([pd.GRANDS_DINO[2]], r(), s3)
    k.chemin(10, "triceratops", "oeuf", "de Pico", r(), s3)
    k.labyrinthe((17, 15), "defi", "triceratops", "oeuf", pico, r(), s3)
    k.code("BRAVO PICO", r(), s3)
    restantes = list(etapes)
    if restantes:
        raise RuntimeError(f"{len(restantes)} étape(s) d'histoire non utilisée(s)")

    couverture = page_couverture(TITRE, "Un cahier-aventure chez les dinosaures",
                                 ["trex", "diplodocus", "triceratops", "stegosaure", "oeuf", "volcan", "fougere", "os"],
                                 ["Une histoire en 36 étapes", "Labyrinthes, énigmes, logique", "Corrigés inclus"],
                                 principal="trex")
    intro = page_intro_aventure(histoire["titre_intro"], histoire["intro"], "triceratops", histoire["objectifs"])
    diplome = page_diplome(histoire["diplome_titre"],
                           histoire["diplome_texte"][0].upper() + histoire["diplome_texte"][1:]
                           + "<br/><br/><b>" + histoire["fin"] + "</b>", "triceratops")
    pages = [couverture, intro] + k.pages + [diplome] + k.pages_corriges()
    return pages, k


def construire(cfg: ConfigProduit) -> ResultatProduit:
    pages, k = composer(cfg)

    ch = chemins(cfg.id)
    res = assembler(pages, ch["pdf"], TITRE, TITRE, theme_de(cfg), "Cahier-aventure 6-8 ans")
    res_eco = assembler(pages, ch["encre_eco"], f"{TITRE} (économie d'encre)", TITRE, theme_de(cfg, eco=True),
                        "Cahier-aventure 6-8 ans — version économie d'encre")
    verifs = [Verification(v.id, v.type, v.erreurs) for v in k.verifications]
    premiere_solution = next(p.numero for p in res.pages if p.kind == "solution")
    apercus = [Apercu("pdf", 2, "Le début de l'histoire"), Apercu("pdf", 7, ""), Apercu("pdf", 14, ""),
               Apercu("pdf", 17, ""), Apercu("pdf", premiere_solution, "Extrait des corrigés")]
    compo = {TYPES_JEUX[t]: n for t, n in k.compte.items()}
    compo["Étapes d'histoire"] = len(charger("histoire_dinosaures")["etapes"])
    return ResultatProduit(cfg.id, {"pdf": res, "encre_eco": res_eco}, verifs, k.nb_jeux, apercus,
                           attendus={"pages_min": cfg.pages_min, "pages_max": cfg.pages_max}, composition=compo)
