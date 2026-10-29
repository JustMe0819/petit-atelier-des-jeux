"""Produit « Mes premiers nonogrammes » : 20 grilles 5 × 5 puis 20 grilles 10 × 10."""
from __future__ import annotations

from generation.assets import pixel_designs as pd
from generation.config import ConfigProduit
from generation.generators import nonograms as ng
from generation.pdf_builder import corriges
from generation.pdf_builder.document import Livre
from generation.pdf_builder.pages_activites import page_nonogramme
from generation.pdf_builder.pages_speciales import page_comment_jouer, page_couverture
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de

TITRE = "Mes premiers nonogrammes"


def charger_nonogrammes(dessins: list[pd.Dessin], prefixe: str) -> list[ng.Nonogramme]:
    return [ng.Nonogramme(f"{prefixe}-{d.id}", d.titre, d.indice, ng.depuis_texte(d.motif)) for d in dessins]


def exemple_guide() -> ng.Nonogramme:
    d = pd.PETITS_GRATUITS[0]
    return ng.Nonogramme(f"exemple-{d.id}", d.titre, d.indice, ng.depuis_texte(d.motif))


def construire(cfg: ConfigProduit) -> ResultatProduit:
    petits = charger_nonogrammes(pd.PETITS_PACK, "nono5")
    grands = charger_nonogrammes(pd.GRANDS_PACK, "nono10")
    # Progression : du plus simple au plus long à résoudre (nombre de déductions nécessaires).
    petits.sort(key=lambda n: (ng.difficulte(n), n.id))
    grands.sort(key=lambda n: (ng.difficulte(n), n.id))
    tous = petits + grands
    exemple = exemple_guide()
    verifs = [Verification(n.id, "nonogramme", ng.verifier(n)) for n in tous]
    verifs.append(Verification(exemple.id, "nonogramme (exemple)", ng.verifier(exemple)))

    theme = theme_de(cfg)
    livre = Livre(chemins(cfg.id)["pdf"], TITRE, TITRE, theme, "40 nonogrammes pour les 6-8 ans")
    livre.ajouter(page_couverture(TITRE, "Des grilles à colorier pour révéler un dessin",
                                  ["lapin", "chat", "poisson", "champignon", "fleur", "oiseau", "escargot"],
                                  ["40 grilles", "5 × 5 puis 10 × 10", "Solution unique vérifiée"]))
    livre.ajouter(page_comment_jouer(exemple))
    elements = []
    num = 1
    for i in range(0, len(petits), 2):
        paire = petits[i:i + 2]
        livre.ajouter(page_nonogramme(paire, [num, num + 1], [n.id for n in paire],
                                      section="Grilles 5 × 5 · niveau débutant"))
        num += 2
    for i, n in enumerate(grands):
        niveau = "intermédiaire" if i < len(grands) // 2 else "défi"
        livre.ajouter(page_nonogramme([n], [num], [n.id], section=f"Grilles 10 × 10 · niveau {niveau}"))
        num += 1
    for k, n in enumerate(tous, start=1):
        elements.append(corriges.nonogramme(n, f"Grille n°{k}", n.id))
    pages_corr = corriges.paginer(elements, "Solutions")
    for p in pages_corr:
        livre.ajouter(p)
    res = livre.enregistrer()

    premiere_solution = next(p.numero for p in res.pages if p.kind == "solution")
    apercus = [Apercu("pdf", 2, "Page « Comment jouer ? » pas à pas"),
               Apercu("pdf", 3, ""), Apercu("pdf", 16, ""), Apercu("pdf", 30, ""),
               Apercu("pdf", premiere_solution, "Extrait des solutions illustrées")]
    return ResultatProduit(cfg.id, {"pdf": res}, verifs, len(tous), apercus,
                           attendus={"nb_jeux": cfg.nb_jeux_attendu},
                           composition={"grilles 5 × 5": len(petits), "grilles 10 × 10": len(grands),
                                        "résolubles ligne par ligne": sum(
                                            ng.resoluble_par_lignes(n.lignes, n.colonnes) for n in tous)})
