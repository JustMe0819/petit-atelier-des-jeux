"""Fichiers gratuits (téléchargement libre) : générés et vérifiés par les mêmes générateurs."""
from __future__ import annotations

import json
import random
from datetime import datetime

from generation import catalogue
from generation.assets import pixel_designs as pd
from generation.config import GRAINE_GRATUITS, GRATUITS, RACINE, SORTIES
from generation.generators import nonograms as ng
from generation.generators.activity_books import Composeur, Verif, assembler
from generation.pdf_builder.pages_speciales import page_comment_jouer, page_couverture
from generation.pdf_builder.theme import Theme
from generation.qa.pdf_qa import auditer_pdf
from generation.qa.previews import generer_apercu

THEME = Theme.depuis_hex("#2F8F9D", "#DDF0F2")
ENTETE = "Petit Atelier des Jeux · fichier gratuit"


def _labyrinthe(rng: random.Random):
    k = Composeur(rng, THEME, "gratuit-lab")
    k.labyrinthe((10, 10), "intermediaire", "renard", "terrier",
                 "Le petit renard rentre de promenade. Aide-le à rentrer dans son terrier.",
                 titre="Le labyrinthe du renard")
    return k, k.pages + k.pages_corriges("Solution"), 0


def _nonogramme(rng: random.Random):
    k = Composeur(rng, THEME, "gratuit-nono")
    d_ex = pd.PETITS_GRATUITS[0]
    exemple = ng.Nonogramme("gratuit-exemple", d_ex.titre, d_ex.indice, ng.depuis_texte(d_ex.motif))
    k.verifications.append(_verif(exemple.id, "nonogramme (exemple)", ng.verifier(exemple)))
    k.nonogrammes([pd.PETITS_GRATUITS[1]])
    pages = [page_comment_jouer(exemple, section="Mini-guide")] + k.pages + k.pages_corriges("Solution")
    return k, pages, 0


def _logique(rng: random.Random):
    k = Composeur(rng, THEME, "gratuit-logique")
    k.logique([("debutant", {"type": "suite_formes", "gabarit": "ABC"}),
               ("debutant", {"type": "suite_nombres", "regle": "2", "n": 6, "trous": [5]}),
               ("intermediaire", {"type": "intrus", "attribut": "motif", "n": 5, "varier": ["forme"]})])
    return k, k.pages + k.pages_corriges(), 0


def _mini_cahier(rng: random.Random):
    k = Composeur(rng, THEME, "gratuit-mini")
    k.labyrinthe((8, 8), "debutant", "herisson", "maison", "Aide le hérisson à rejoindre sa maison.")
    k.logique([("debutant", {"type": "suite_formes", "gabarit": "AB", "motif": True}),
               ("debutant", {"type": "association", "regle": "ombre", "n": 4})])
    k.nonogrammes([pd.PETITS_GRATUITS[2]])
    k.differences(5, ["arbre", "fleur", "soleil", "nuage", "champignon", "maison", "poisson", "oiseau"])
    couv = page_couverture("Mon mini-cahier découverte", "Quatre jeux pour essayer",
                           ["chouette", "herisson", "maison", "fleur", "lapin", "soleil"],
                           ["Labyrinthe, logique", "Nonogramme, observation", "Corrigés inclus"])
    return k, [couv] + k.pages + k.pages_corriges(), 1


def _verif(id_: str, type_: str, erreurs: list[str]) -> Verif:
    return Verif(id_, type_, erreurs)


GRATUITS_DEF = [
    {"id": "labyrinthe-du-renard", "titre": "Le labyrinthe du renard", "construire": _labyrinthe,
     "description": "Un labyrinthe de niveau intermédiaire pour aider le petit renard à rentrer dans son terrier. "
                    "La solution est sur la deuxième page.",
     "competences": ["Repérage dans l'espace", "Motricité fine", "Anticipation"]},
    {"id": "nonogramme-decouverte", "titre": "Mon premier nonogramme",
     "construire": _nonogramme,
     "description": "Un mini-guide pas à pas pour comprendre les nonogrammes, puis une grille 5 × 5 à résoudre "
                    "seul. Solution incluse.",
     "competences": ["Logique", "Lecture de consignes", "Concentration"]},
    {"id": "fiche-logique", "titre": "Ma fiche de logique", "construire": _logique,
     "description": "Trois petits défis : une suite de formes, une suite de nombres et un intrus. "
                    "Chaque activité a une seule bonne réponse. Corrigé inclus.",
     "competences": ["Raisonnement logique", "Observation", "Nombres jusqu'à 20"]},
    {"id": "mini-cahier-decouverte", "titre": "Mon mini-cahier découverte", "construire": _mini_cahier,
     "description": "Un petit cahier pour découvrir nos jeux : un labyrinthe, des défis de logique, "
                    "un nonogramme et un jeu des différences, avec les corrigés.",
     "competences": ["Repérage dans l'espace", "Logique", "Observation", "Concentration"]},
]


def construire_gratuits(maj_catalogue: bool = True) -> dict:
    rng_base = random.Random(GRAINE_GRATUITS)
    entrees, rapports = [], []
    for i, g in enumerate(GRATUITS_DEF):
        rng = random.Random(rng_base.randrange(1 << 30) + i)
        k, pages, page_apercu = g["construire"](rng)
        chemin = GRATUITS / f"{g['id']}.pdf"
        res = assembler(pages, chemin, g["titre"], ENTETE, THEME, "Fichier gratuit — Petit Atelier des Jeux")
        audit = auditer_pdf(res)
        verifs = [{"id": v.id, "type": v.type, "ok": not v.erreurs, "erreurs": v.erreurs} for v in k.verifications]
        ok = audit["ok"] and all(v["ok"] for v in verifs) and 1 <= res.nb_pages <= 6
        apercu = GRATUITS / f"{g['id']}.png"
        generer_apercu(chemin, page_apercu + 1, apercu, avec_filigrane=False)
        rapports.append({"id": g["id"], "ok": ok, "nb_pages": res.nb_pages, "nb_jeux": k.nb_jeux,
                         "verifications": verifs, "audit": {**audit, "fichier": str(chemin.relative_to(RACINE))}})
        if ok:
            entrees.append({"id": g["id"], "titre": g["titre"], "description": g["description"],
                            "fichier": f"/gratuit/{g['id']}.pdf", "apercu": f"/gratuit/{g['id']}.png",
                            "nb_pages": res.nb_pages, "competences": g["competences"], "age": "6-8 ans"})
    rapport = {"genere_le": datetime.now().astimezone().isoformat(timespec="seconds"),
               "valide_automatiquement": all(r["ok"] for r in rapports), "fichiers": rapports}
    sortie = SORTIES / "gratuits" / "rapport_qualite.json"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if maj_catalogue:
        catalogue.mettre_a_jour_gratuits(entrees)
    return rapport

