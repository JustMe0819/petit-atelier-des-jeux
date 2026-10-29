"""Produit « Les labyrinthes des petits explorateurs » : 30 labyrinthes + corrigés séparés."""
from __future__ import annotations

import random

from reportlab.lib.units import mm

from generation.config import ConfigProduit
from generation.generators import mazes
from generation.pdf_builder import corriges
from generation.pdf_builder.document import Livre
from generation.pdf_builder.pages_activites import page_labyrinthe
from generation.pdf_builder.pages_speciales import page_couverture
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de
from generation.templates import charger

TITRE = "Les labyrinthes des petits explorateurs"


def construire(cfg: ConfigProduit) -> ResultatProduit:
    rng = random.Random(cfg.graine)
    labs = mazes.serie_progressive(rng, par_niveau=10)
    missions = charger("missions_labyrinthes")["missions"]
    verifs = [Verification(f"labyrinthe-{i + 1:02d}", "labyrinthe", mazes.verifier(l)) for i, l in enumerate(labs)]

    theme = theme_de(cfg)
    ch = chemins(cfg.id)
    livre = Livre(ch["pdf"], TITRE, TITRE, theme, "30 labyrinthes progressifs pour les 6-8 ans")
    livre.ajouter(page_couverture(TITRE, "30 labyrinthes progressifs",
                                  ["herisson", "maison", "lapin", "carotte", "chouette", "renard", "souris"],
                                  ["30 labyrinthes progressifs", "3 niveaux de difficulté", "Corrigés séparés"]))
    elements = []
    for i, lab in enumerate(labs):
        m = missions[i % len(missions)]
        ref = f"labyrinthe-{i + 1:02d}"
        niveau = mazes.NOMS_NIVEAUX[lab.niveau]
        livre.ajouter(page_labyrinthe(lab, i + 1, m["depart"], m["arrivee"], m["texte"], ref,
                                      section=f"Niveau {niveau}"))
        h = 62 * mm if lab.niveau == "debutant" else 98 * mm
        elements.append(corriges.labyrinthe(lab, f"Labyrinthe n°{i + 1}", ref, m["depart"], m["arrivee"], h))
    res_pdf = livre.enregistrer()

    # Corrigés séparés : les numéros de page renvoient au PDF des labyrinthes.
    livre_c = Livre(ch["corriges"], f"{TITRE} — corrigés", f"{TITRE} — corrigés", theme)
    pages_lab = {f"labyrinthe-{i + 1:02d}": i + 2 for i in range(len(labs))}
    for e in elements:
        e.titre = f"{e.titre} · page {pages_lab[e.ref]}"
        e.ref = None
    for p in corriges.paginer(elements, "Corrigés des labyrinthes"):
        livre_c.ajouter(p)
    res_c = livre_c.enregistrer()

    apercus = [
        Apercu("pdf", 4, "Labyrinthe n°3 (niveau débutant)"),
        Apercu("pdf", 15, "Labyrinthe n°14 (niveau intermédiaire)"),
        Apercu("pdf", 27, "Labyrinthe n°26 (niveau défi)"),
        Apercu("corriges", 1, "Extrait des corrigés (fichier séparé)"),
    ]
    tailles = {lv: [f"{l.lignes}×{l.colonnes}" for l in labs if l.niveau == lv] for lv in mazes.TAILLES_NIVEAUX}
    return ResultatProduit(cfg.id, {"pdf": res_pdf, "corriges": res_c}, verifs, len(labs), apercus,
                           attendus={"nb_jeux": cfg.nb_jeux_attendu, "pages_pdf": len(labs) + 1},
                           composition={"labyrinthes": len(labs), "tailles_par_niveau": tailles})
