"""Composition des cahiers d'activités (grand cahier, mission dinosaures, mini-cahier).

Le `Composeur` génère chaque activité, la vérifie, ajoute sa page et son corrigé,
et tient le compte exact des jeux produits. Les mêmes pages servent à la version
normale et à la version « économie d'encre » (seul le thème change au rendu).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

from generation.assets.colour_designs import DessinCouleur
from generation.assets.pixel_designs import Dessin
from generation.generators import coloriage as gc
from generation.generators import enigmes as ge
from generation.generators import logic_puzzles as lp
from generation.generators import mazes
from generation.generators import nonograms as ng
from generation.generators import observation as ob
from generation.pdf_builder import corriges
from generation.pdf_builder.document import Livre, PageSpec, ResultatLivre
from generation.pdf_builder.pages_activites import (
    Recit, page_chemin, page_code, page_coloriage, page_comptage, page_differences, page_dessin,
    page_labyrinthe, page_logique, page_nonogramme, page_problemes,
)
from generation.pdf_builder.theme import Theme
from reportlab.lib.units import mm

TYPES_JEUX = {
    "labyrinthe": "Labyrinthes", "logique": "Activités de logique", "nonogramme": "Nonogrammes",
    "differences": "Jeux des différences", "comptage": "Jeux de comptage", "coloriage": "Coloriages codés",
    "code": "Messages codés", "probleme": "Énigmes (problèmes)", "chemin": "Chemins des nombres",
}


@dataclass
class Verif:
    id: str
    type: str
    erreurs: list[str]


@dataclass
class Composeur:
    rng: random.Random
    theme_rendu: Theme  # utilisé pour la vérification au pixel des différences
    prefixe: str
    pages: list[PageSpec] = field(default_factory=list)
    elements: list[corriges.ElementCorrige] = field(default_factory=list)
    verifications: list[Verif] = field(default_factory=list)
    compte: dict[str, int] = field(default_factory=dict)
    numeros: dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------ outils
    def _num(self, typ: str, n: int = 1) -> int:
        debut = self.numeros.get(typ, 0) + 1
        self.numeros[typ] = debut + n - 1
        self.compte[typ] = self.compte.get(typ, 0) + n
        return debut

    def _ref(self, typ: str, num: int) -> str:
        return f"{self.prefixe}-{typ}-{num:02d}"

    def ajouter_page(self, page: PageSpec) -> None:
        self.pages.append(page)

    @property
    def nb_jeux(self) -> int:
        return sum(self.compte.values())

    # ------------------------------------------------------------------ activités
    def labyrinthe(self, taille: tuple[int, int], niveau: str, depart: str, arrivee: str, mission: str,
                   recit: Recit | None = None, section: str = "Labyrinthe", titre: str | None = None) -> None:
        num = self._num("labyrinthe")
        lab = mazes.generer_avec_longueur_min(taille[0], taille[1], self.rng, niveau)
        ref = self._ref("labyrinthe", num)
        self.verifications.append(Verif(ref, "labyrinthe", mazes.verifier(lab)))
        self.pages.append(page_labyrinthe(lab, num, depart, arrivee, mission, ref, section=section,
                                          recit=recit, titre=titre))
        h = (62 if lab.lignes <= 9 else 76) * mm
        self.elements.append(corriges.labyrinthe(lab, titre or f"Labyrinthe n°{num}", ref, depart, arrivee, h))

    def logique(self, plan: list[tuple[str, dict]], recit: Recit | None = None, section: str = "Logique") -> None:
        debut = self._num("logique", len(plan))
        acts = lp.serie(self.rng, plan, f"{self.prefixe}-logique", debut=debut)
        for a in acts:
            self.verifications.append(Verif(a.id, f"logique/{a.type}", lp.verifier(a)))
            self.elements.append(corriges.logique(a))
        self.pages.append(page_logique(acts, section=section, recit=recit))

    def nonogrammes(self, dessins: list[Dessin], recit: Recit | None = None, section: str = "Nonogramme",
                    montrer_indice: bool = True) -> None:
        debut = self._num("nonogramme", len(dessins))
        nonos = [ng.Nonogramme(self._ref("nonogramme", debut + i), d.titre, d.indice, ng.depuis_texte(d.motif))
                 for i, d in enumerate(dessins)]
        for n in nonos:
            self.verifications.append(Verif(n.id, "nonogramme", ng.verifier(n)))
        nums = [debut + i for i in range(len(nonos))]
        self.pages.append(page_nonogramme(nonos, nums, [n.id for n in nonos], section=section, recit=recit,
                                          montrer_indice=montrer_indice))
        for n, k in zip(nonos, nums):
            self.elements.append(corriges.nonogramme(n, f"Nonogramme n°{k}", n.id))

    def differences(self, n: int, kinds: list[str], recit: Recit | None = None,
                    section: str = "Observation") -> None:
        num = self._num("differences")
        ref = self._ref("differences", num)
        jeu = ob.generer_differences(self.rng, n, kinds, ref)
        from generation.qa.verif_rendu import verifier_differences_rendu
        err = ob.verifier_differences(jeu) + verifier_differences_rendu(jeu, self.theme_rendu)
        self.verifications.append(Verif(ref, "différences (modèle + rendu)", err))
        titre = f"Les {n} différences"
        self.pages.append(page_differences(jeu, titre, ref, section=section, recit=recit))
        self.elements.append(corriges.differences(jeu, f"{titre} (jeu n°{num})", ref))

    def comptage(self, kinds: list[str], mini: int, maxi: int, recit: Recit | None = None,
                 section: str = "Observation", titre: str | None = None) -> None:
        num = self._num("comptage")
        ref = self._ref("comptage", num)
        jeu = ob.generer_comptage(self.rng, kinds, mini, maxi, ref)
        self.verifications.append(Verif(ref, "comptage", ob.verifier_comptage(jeu)))
        noms = ", ".join(ob.nom(k, 2) for k in kinds[:-1]) + " et " + ob.nom(kinds[-1], 2)
        titre = titre or "Compte bien !"
        self.pages.append(page_comptage(jeu, titre, f"Compte les {noms}. Écris chaque nombre dans sa case. "
                                        "Astuce : barre chaque dessin quand tu l'as compté.", ref,
                                        section=section, recit=recit))
        self.elements.append(corriges.comptage(jeu, f"{titre} (jeu n°{num})", ref))

    def coloriage(self, dessin: DessinCouleur, recit: Recit | None = None, section: str = "Coloriage codé") -> None:
        num = self._num("coloriage")
        ref = self._ref("coloriage", num)
        cc = gc.depuis_dessin(dessin, ref)
        self.verifications.append(Verif(ref, "coloriage codé", gc.verifier(cc, dessin)))
        titre = f"Coloriage codé n°{num}"
        self.pages.append(page_coloriage(cc, titre, ref, section=section, recit=recit))
        self.elements.append(corriges.coloriage(cc, titre, ref))

    def code(self, message: str, recit: Recit | None = None, section: str = "Message secret") -> None:
        num = self._num("code")
        ref = self._ref("code", num)
        cs = ge.generer_code(self.rng, message, ref)
        self.verifications.append(Verif(ref, "code secret", ge.verifier_code(cs)))
        titre = f"Message secret n°{num}"
        self.pages.append(page_code(cs, titre, ref, section=section, recit=recit))
        self.elements.append(corriges.code(cs, titre, ref))

    def problemes(self, gabarits: list[dict], recit: Recit | None = None, section: str = "Énigmes",
                  illustrations: list[str] | None = None) -> None:
        debut = self._num("probleme", len(gabarits))
        probs = [ge.generer_probleme(self.rng, g) for g in gabarits]
        ref = self._ref("probleme", debut)
        for i, p in enumerate(probs):
            self.verifications.append(Verif(f"{ref}-{i + 1}", "problème", ge.verifier_probleme(p)))
        titre = f"Énigmes n°{debut} à {debut + len(probs) - 1}" if len(probs) > 1 else f"Énigme n°{debut}"
        self.pages.append(page_problemes(probs, titre, ref, section=section, recit=recit,
                                         illustrations=illustrations))
        self.elements.append(corriges.problemes(probs, titre, ref))

    def chemin(self, pas: int, depart: str, arrivee: str, nom_depart: str, recit: Recit | None = None,
               section: str = "Défi") -> None:
        num = self._num("chemin")
        ref = self._ref("chemin", num)
        ch = ge.generer_chemin(self.rng, ref, pas=pas)
        self.verifications.append(Verif(ref, "chemin des nombres", ge.verifier_chemin(ch)))
        titre = f"Le chemin des nombres n°{num}"
        self.pages.append(page_chemin(ch, titre, ref, depart, arrivee, nom_depart, section=section, recit=recit))
        el = corriges.chemin(ch, titre, ref, depart, arrivee)
        el.large = True
        self.elements.append(el)

    def dessin(self, titre: str, consigne: str, recit: Recit | None = None) -> None:
        self.pages.append(page_dessin(titre, consigne, recit=recit))

    # ------------------------------------------------------------------ assemblage
    def pages_corriges(self, titre: str = "Corrigés") -> list[PageSpec]:
        pages = corriges.paginer(self.elements, titre)
        pages[0].refs.append("__corriges__")
        return pages


def assembler(pages: list[PageSpec], chemin: Path, titre: str, entete: str, theme: Theme,
              sujet: str = "") -> ResultatLivre:
    livre = Livre(chemin, titre, entete, theme, sujet)
    for p in pages:
        livre.ajouter(p)
    return livre.enregistrer()
