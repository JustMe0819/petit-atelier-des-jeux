"""Configuration centrale de la génération : chemins, graines et objectifs par produit."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent  # racine du dépôt
GENERATION = RACINE / "generation"
CATALOGUE = RACINE / "catalogue" / "catalogue.json"
STOCKAGE = RACINE / "storage"
PRODUITS_PRIVES = STOCKAGE / "produits"
APERCUS = RACINE / "public" / "apercus"
GRATUITS = RACINE / "public" / "gratuit"
SORTIES = GENERATION / "output"
POLICES = GENERATION / "assets" / "fonts"
GABARITS = GENERATION / "templates"

MARQUE = "Petit Atelier des Jeux"
LARGEUR_APERCU_PX = 800


@dataclass(frozen=True)
class ConfigProduit:
    id: str
    graine: int
    # Objectifs annoncés (vérifiés par la QA ; une page-objectif hors cible est signalée
    # à titre d'information mais n'est jamais « comblée » artificiellement).
    nb_jeux_attendu: int | None = None
    pages_min: int | None = None
    pages_max: int | None = None
    accent: str = "#2F8F9D"
    accent_clair: str = "#DCEFF1"
    options: dict = field(default_factory=dict)


PRODUITS: dict[str, ConfigProduit] = {
    "labyrinthes-petits-explorateurs": ConfigProduit(
        id="labyrinthes-petits-explorateurs", graine=1101, nb_jeux_attendu=30,
        accent="#2F8F9D", accent_clair="#DDF0F2",
    ),
    "defis-de-la-logique": ConfigProduit(
        id="defis-de-la-logique", graine=2202, nb_jeux_attendu=30,
        accent="#D9694A", accent_clair="#FBE5DD",
    ),
    "mes-premiers-nonogrammes": ConfigProduit(
        id="mes-premiers-nonogrammes", graine=3303, nb_jeux_attendu=40,
        accent="#3D7EA6", accent_clair="#DFECF5",
    ),
    "grand-cahier-petits-explorateurs": ConfigProduit(
        id="grand-cahier-petits-explorateurs", graine=4404, pages_min=35, pages_max=40,
        accent="#E39B2D", accent_clair="#FCEFD9",
    ),
    "mission-dinosaures": ConfigProduit(
        id="mission-dinosaures", graine=5505, pages_min=40, pages_max=50,
        accent="#4E8F3A", accent_clair="#E3F1DC",
    ),
    "mission-espace": ConfigProduit(
        id="mission-espace", graine=5606, pages_min=40, pages_max=50,
        accent="#4C5BA6", accent_clair="#E3E6F5",
    ),
    "mission-pirates": ConfigProduit(
        id="mission-pirates", graine=5707, pages_min=40, pages_max=50,
        accent="#1F6F8B", accent_clair="#DCEEF4",
    ),
    "mission-magie": ConfigProduit(
        id="mission-magie", graine=5808, pages_min=40, pages_max=50,
        accent="#7A55B0", accent_clair="#EDE5F7",
    ),
}

# Produits groupés : aucun fichier propre, rien à générer.
BUNDLES = {"grand-coffret-explorateurs"}

GRAINE_GRATUITS = 7707
