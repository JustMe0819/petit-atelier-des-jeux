"""Produit « Les petits explorateurs — Mon grand cahier d'activités » (+ version économie d'encre)."""
from __future__ import annotations

import random

from generation.assets import colour_designs as cd
from generation.assets import pixel_designs as pd
from generation.config import ConfigProduit
from generation.pdf_builder.document import PageSpec
from generation.generators.activity_books import TYPES_JEUX, Composeur, assembler
from generation.pdf_builder.pages_speciales import page_consignes, page_couverture
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de
from generation.templates import charger

TITRE = "Les petits explorateurs — Mon grand cahier d'activités"
ENTETE = "Mon grand cahier d'activités"
NATURE = ["arbre", "fleur", "soleil", "nuage", "champignon", "maison", "poisson", "oiseau", "pomme", "escargot"]
ANIMAUX = ["herisson", "lapin", "souris", "chouette", "grenouille", "ours", "tortue", "poussin", "chat", "renard"]

# Plans de logique par page (2 activités par page), du plus facile au plus difficile.
LOGIQUE = [
    [("debutant", {"type": "suite_formes", "gabarit": "AB"}),
     ("debutant", {"type": "intrus", "attribut": "forme", "n": 4})],
    [("debutant", {"type": "suite_nombres", "regle": "2", "n": 6, "trous": [5]}),
     ("debutant", {"type": "association", "regle": "ombre", "n": 4})],
    [("intermediaire", {"type": "grille", "regles": ["forme"]}),
     ("intermediaire", {"type": "suite_formes", "gabarit": "ABB", "motif": True, "options": 4})],
    [("intermediaire", {"type": "suite_nombres", "regle": "5", "n": 6, "trous": [4]}),
     ("intermediaire", {"type": "association", "regle": "quantite", "n": 5, "maxi": 10})],
    [("defi", {"type": "intrus", "attribut": "motif", "n": 6, "varier": ["forme", "taille"]}),
     ("defi", {"type": "suite_nombres", "regle": "10", "n": 6, "trous": [1, 5]})],
    [("defi", {"type": "grille", "regles": ["forme", "motif"]}),
     ("defi", {"type": "suite_formes", "double": True})],
]


def composer(cfg: ConfigProduit) -> tuple[list[PageSpec], Composeur]:
    """Génère et vérifie toutes les activités ; renvoie les pages (sans rendu PDF)."""
    rng = random.Random(cfg.graine)
    missions = charger("missions_labyrinthes")["missions"]
    k = Composeur(rng, theme_de(cfg), "cahier")
    m = iter(missions[3:] + missions[:3])

    def lab(taille, niveau, section):
        mi = next(m)
        k.labyrinthe(taille, niveau, mi["depart"], mi["arrivee"], mi["texte"], section=section)

    f, moy, dif = "Niveau 1 · facile", "Niveau 2 · moyen", "Niveau 3 · difficile"
    # ---- niveau 1
    lab((7, 7), "debutant", f)
    k.logique(LOGIQUE[0], section=f)
    k.nonogrammes(pd.PETITS_CAHIER[0:2], section=f)
    k.comptage(["lapin", "poussin", "souris"], 2, 7, section=f, titre="Compte les animaux")
    k.coloriage(cd.COCCINELLE, section=f)
    lab((8, 8), "debutant", f)
    k.differences(5, NATURE, section=f)
    k.logique(LOGIQUE[1], section=f)
    k.chemin(2, "herisson", "maison", "du hérisson", section=f)
    k.dessin("Mon animal préféré", "Dessine ton animal préféré dans le cadre, puis écris son nom "
                                   "et une phrase pour le présenter.")
    # ---- niveau 2
    lab((11, 11), "intermediaire", moy)
    k.logique(LOGIQUE[2], section=moy)
    k.nonogrammes(pd.PETITS_CAHIER[2:4], section=moy)
    k.differences(6, ANIMAUX, section=moy)
    k.nonogrammes([pd.GRANDS_CAHIER[0]], section=moy)
    k.comptage(["etoile", "coeur", "soleil", "nuage"], 3, 9, section=moy, titre="Compte les dessins")
    k.coloriage(cd.POISSON, section=moy)
    lab((13, 12), "intermediaire", moy)
    k.logique(LOGIQUE[3], section=moy)
    k.nonogrammes([pd.GRANDS_CAHIER[1]], section=moy)
    # ---- niveau 3
    lab((15, 14), "defi", dif)
    k.differences(7, NATURE + ANIMAUX[:4], section=dif)
    k.logique(LOGIQUE[4], section=dif)
    k.nonogrammes([pd.GRANDS_CAHIER[2]], section=dif)
    k.comptage(["herisson", "escargot", "champignon", "pomme"], 4, 11, section=dif,
               titre="Le grand comptage de la forêt")
    k.coloriage(cd.CHAMPIGNON, section=dif)
    lab((17, 15), "defi", dif)
    k.logique(LOGIQUE[5], section=dif)
    k.nonogrammes([pd.GRANDS_CAHIER[3]], section=dif)
    k.dessin("Mon carnet d'explorateur", "Quelles activités as-tu préférées dans ce cahier ? Dessine ton "
                                         "moment préféré, puis écris pourquoi tu l'as aimé.")
    lab((19, 17), "defi", dif)

    consignes = page_consignes(
        "Bienvenue, petit explorateur !",
        "Ce cahier est rangé du plus facile au plus difficile. Fais les pages dans l'ordre, à ton rythme. "
        "Lis bien la consigne en haut de chaque page.",
        [("renard", "Les labyrinthes", "Trace le chemin du départ jusqu'à l'arrivée sans traverser les murs."),
         ("chouette", "La logique", "Observe les formes et les nombres, trouve la règle, puis entoure ou écris la réponse."),
         ("lapin", "Les nonogrammes", "Les nombres disent combien de cases colorier à la suite : un dessin apparaît."),
         ("soleil", "L'observation", "Trouve les différences entre deux images ou compte les dessins."),
         ("fleur", "Les coloriages codés", "Chaque numéro correspond à une couleur."),
         ("escargot", "Le chemin des nombres", "Avance de case en case en comptant de 2 en 2.")],
        ["Laissez l'enfant chercher seul, puis aidez-le avec une question plutôt qu'avec la réponse.",
         "Une ou deux pages par jour suffisent.",
         "Une version « économie d'encre » du cahier est fournie : elle s'imprime sans aplats de couleur."],
    )
    couverture = page_couverture(
        "Mon grand cahier d'activités", "Les petits explorateurs",
        ["renard", "chouette", "lapin", "arbre", "champignon", "escargot", "fleur", "soleil"],
        ["Labyrinthes, logique, observation", "Nonogrammes et coloriages codés", "Du plus facile au plus difficile"])
    pages = [couverture, consignes] + k.pages + k.pages_corriges()
    return pages, k


def construire(cfg: ConfigProduit) -> ResultatProduit:
    pages, k = composer(cfg)

    ch = chemins(cfg.id)
    res = assembler(pages, ch["pdf"], TITRE, ENTETE, theme_de(cfg), "Cahier d'activités 6-8 ans")
    res_eco = assembler(pages, ch["encre_eco"], f"{TITRE} (économie d'encre)", ENTETE,
                        theme_de(cfg, eco=True), "Cahier d'activités 6-8 ans — version économie d'encre")

    verifs = [Verification(v.id, v.type, v.erreurs) for v in k.verifications]
    premiere_solution = next(p.numero for p in res.pages if p.kind == "solution")
    apercus = [Apercu("pdf", 3, ""), Apercu("pdf", 9, ""), Apercu("pdf", 14, ""), Apercu("pdf", 17, ""),
               Apercu("pdf", premiere_solution, "Extrait des corrigés")]
    compo = {TYPES_JEUX[t]: n for t, n in k.compte.items()}
    compo["Pages de dessin / écriture"] = sum(1 for p in pages if p.kind == "dessin")
    return ResultatProduit(cfg.id, {"pdf": res, "encre_eco": res_eco}, verifs, k.nb_jeux, apercus,
                           attendus={"pages_min": cfg.pages_min, "pages_max": cfg.pages_max,
                                     "max_pages_dessin": 2},
                           composition=compo)
