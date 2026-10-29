"""Produit « Les défis de la logique » : 30 activités progressives, corrigés en fin de fichier."""
from __future__ import annotations

import random

from generation.config import ConfigProduit
from generation.generators import logic_puzzles as lp
from generation.pdf_builder import corriges
from generation.pdf_builder.document import Livre
from generation.pdf_builder.pages_activites import page_logique
from generation.pdf_builder.pages_speciales import page_couverture
from generation.pdf_builder.render_common import NOMS_NIVEAUX
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de

TITRE = "Les défis de la logique"


def construire(cfg: ConfigProduit) -> ResultatProduit:
    rng = random.Random(cfg.graine)
    acts = lp.serie(rng, lp.PLAN_PACK, "logique")
    verifs = [Verification(a.id, a.type, lp.verifier(a)) for a in acts]

    theme = theme_de(cfg)
    livre = Livre(chemins(cfg.id)["pdf"], TITRE, TITRE, theme, "30 activités de logique pour les 6-8 ans")
    livre.ajouter(page_couverture(TITRE, "Suites, intrus, associations et petits défis",
                                  ["chouette", "etoile", "coeur", "soleil", "fleur", "lapin", "renard"],
                                  ["30 activités", "Difficulté progressive", "Corrigés à la fin"]))
    for i in range(0, len(acts), 2):
        paire = acts[i:i + 2]
        livre.ajouter(page_logique(paire, section=f"Niveau {NOMS_NIVEAUX[paire[0].niveau]}"))
    elements = [corriges.logique(a) for a in acts]
    pages_corr = corriges.paginer(elements, "Corrigés")
    pages_corr[0].refs.append("__corriges__")
    for p in pages_corr:
        livre.ajouter(p)
    res = livre.enregistrer()

    premiere_solution = next(p.numero for p in res.pages if p.kind == "solution")
    apercus = [Apercu("pdf", 2, ""), Apercu("pdf", 8, ""), Apercu("pdf", 14, ""),
               Apercu("pdf", premiere_solution, "Extrait des corrigés")]
    compo: dict[str, int] = {}
    for a in acts:
        compo[a.nom_type] = compo.get(a.nom_type, 0) + 1
    return ResultatProduit(cfg.id, {"pdf": res}, verifs, len(acts), apercus,
                           attendus={"nb_jeux": cfg.nb_jeux_attendu}, composition=compo)
