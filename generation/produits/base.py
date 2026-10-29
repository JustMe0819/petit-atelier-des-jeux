"""Types communs aux constructeurs de produits."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from generation.config import PRODUITS_PRIVES, ConfigProduit
from generation.pdf_builder.document import ResultatLivre
from generation.pdf_builder.theme import Theme


@dataclass
class Verification:
    id: str
    type: str
    erreurs: list[str]

    @property
    def ok(self) -> bool:
        return not self.erreurs


@dataclass
class Apercu:
    fichier: str   # clé dans ResultatProduit.livres : « pdf », « corriges »…
    page: int
    legende: str


@dataclass
class ResultatProduit:
    id: str
    livres: dict[str, ResultatLivre]
    verifications: list[Verification]
    nb_jeux: int
    apercus: list[Apercu]
    attendus: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    composition: dict = field(default_factory=dict)  # nombre d'activités par type


def chemins(id_produit: str) -> dict[str, Path]:
    d = PRODUITS_PRIVES / id_produit
    return {
        "pdf": d / f"{id_produit}.pdf",
        "corriges": d / f"{id_produit}-corriges.pdf",
        "encre_eco": d / f"{id_produit}-encre-eco.pdf",
    }


def theme_de(cfg: ConfigProduit, eco: bool = False) -> Theme:
    return Theme.depuis_hex(cfg.accent, cfg.accent_clair, eco)
