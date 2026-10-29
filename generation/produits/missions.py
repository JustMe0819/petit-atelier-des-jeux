"""Cahiers-aventures « Mission espace », « Mission pirates » et « Mission magie ».

Même plan que « Mission dinosaures » (36 étapes d'histoire, une activité par étape, même
progression de difficulté) ; seuls l'univers, les dessins et les textes changent.
Chaque activité est générée puis vérifiée par programme, comme pour les autres produits.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from generation.assets import colour_designs as cd
from generation.assets import pixel_designs as pd
from generation.assets.colour_designs import DessinCouleur
from generation.assets.pixel_designs import Dessin
from generation.config import ConfigProduit
from generation.generators import observation as ob
from generation.generators.activity_books import TYPES_JEUX, Composeur, assembler
from generation.pdf_builder.document import PageSpec
from generation.pdf_builder.pages_activites import Recit
from generation.pdf_builder.pages_speciales import page_couverture, page_diplome, page_intro_aventure
from generation.produits.base import Apercu, ResultatProduit, Verification, chemins, theme_de
from generation.templates import charger

# Plan des défis de logique, identique à « Mission dinosaures » (progression éprouvée).
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


@dataclass(frozen=True)
class Univers:
    titre: str
    sous_titre: str
    prefixe: str
    histoire: str                      # nom du gabarit JSON de l'histoire
    enigmes: str                       # clé dans templates/enigmes.json
    heros: str                         # pictogramme du personnage principal
    nom_heros: str                     # « de Bip », « de Coco »…
    mission: str                       # consigne des labyrinthes
    objets: list[str]                  # pictogrammes de l'univers (jeux des différences, couverture)
    sections: tuple[str, str, str]
    petits: list[Dessin]               # 2 nonogrammes 5 × 5
    grands: list[Dessin]               # 3 nonogrammes 10 × 10
    coloriages: list[DessinCouleur]    # 3 coloriages codés, dans l'ordre de l'histoire
    messages: tuple[str, str, str, str]
    comptages: tuple[tuple[list[str], str], tuple[list[str], str], tuple[list[str], str]]
    labyrinthes: tuple[tuple[str, str], ...]   # 7 couples (départ, arrivée)
    chemins: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
    illustrations: tuple[list[str], list[str], list[str]]  # pour les 3 pages d'énigmes
    recits: dict[int, str]             # pictogramme particulier pour certaines étapes
    decor: tuple[tuple[str, float], ...]
    principal: str                     # grand pictogramme de la couverture


UNIVERS: dict[str, Univers] = {
    "mission-espace": Univers(
        titre="Mission espace", sous_titre="Un cahier-aventure dans les étoiles", prefixe="espace",
        histoire="histoire_espace", enigmes="espace", heros="astronaute", nom_heros="de Filou",
        mission="Aide Filou à trouver le bon chemin.", objets=ob.ESPACE,
        sections=("Partie 1 · la Lune", "Partie 2 · les planètes", "Partie 3 · la Voie lactée"),
        petits=pd.PETITS_ESPACE, grands=pd.GRANDS_ESPACE, coloriages=cd.ESPACE,
        messages=("LUNE", "ETOILE", "GLACE", "BRAVO FILOU"),
        comptages=((["etoile", "lune", "comete"], "Le ciel de la Lune"),
                   (["fusee", "soucoupe", "planete", "robot"], "Le port de l'espace"),
                   (["lune", "etoile", "comete", "planete"], "Le grand ciel étoilé")),
        labyrinthes=(("astronaute", "fusee"), ("fusee", "etoile"), ("fusee", "planete"), ("fusee", "planete"),
                     ("fusee", "lune"), ("fusee", "comete"), ("fusee", "planete")),
        chemins=(("astronaute", "etoile"), ("astronaute", "fusee"), ("astronaute", "planete")),
        illustrations=(["etoile", "fusee"], ["robot", "planete", "lune"], ["alien", "robot", "comete"]),
        recits={3: "alien", 5: "fusee", 8: "alien", 11: "robot", 17: "robot", 20: "alien", 24: "robot", 36: "robot"},
        decor=(("etoile", 0.13), ("planete", 0.3), ("robot", 0.7), ("comete", 0.87)), principal="astronaute",
    ),
    "mission-pirates": Univers(
        titre="Mission pirates", sous_titre="Un cahier-aventure sur la piste du trésor", prefixe="pirates",
        histoire="histoire_pirates", enigmes="pirates", heros="perroquet", nom_heros="de Coco",
        mission="Aide Coco à trouver le bon chemin.", objets=ob.PIRATES,
        sections=("Partie 1 · le port", "Partie 2 · la mer", "Partie 3 · l'île au trésor"),
        petits=pd.PETITS_PIRATES, grands=pd.GRANDS_PIRATES, coloriages=cd.PIRATES,
        messages=("ILE", "TRESOR", "PLAGE", "BRAVO COCO"),
        comptages=((["pomme", "poisson", "piece"], "Les provisions de l'équipage"),
                   (["bateau", "poisson", "carte", "coffre"], "Sur la mer"),
                   (["crabe", "palmier", "piece", "coffre"], "Sur la plage")),
        labyrinthes=(("bateau", "ancre"), ("bateau", "palmier"), ("bateau", "palmier"), ("bateau", "carte"),
                     ("perroquet", "palmier"), ("perroquet", "carte"), ("perroquet", "coffre")),
        chemins=(("perroquet", "bateau"), ("perroquet", "palmier"), ("perroquet", "coffre")),
        illustrations=(["piece", "pomme"], ["bateau", "coffre", "crabe"], ["coffre", "palmier", "crabe"]),
        recits={3: "crabe", 5: "carte", 13: "bateau", 17: "bateau", 24: "tortue", 32: "coffre"},
        decor=(("palmier", 0.13), ("bateau", 0.3), ("carte", 0.7), ("coffre", 0.87)), principal="bateau",
    ),
    "mission-magie": Univers(
        titre="Mission magie", sous_titre="Un cahier-aventure avec une petite princesse", prefixe="magie",
        histoire="histoire_magie", enigmes="magie", heros="princesse", nom_heros="de Lila",
        mission="Aide Lila à trouver le bon chemin.", objets=ob.MAGIE,
        sections=("Partie 1 · la forêt enchantée", "Partie 2 · le jardin des fées", "Partie 3 · le château"),
        petits=pd.PETITS_MAGIE, grands=pd.GRANDS_MAGIE, coloriages=[cd.POTION, cd.CHATEAU, cd.DRAGON],
        messages=("MAGIE", "POTION", "CHATEAU", "BRAVO LILA"),
        comptages=((["cristal", "potion", "etoile"], "Le sac de Lila"),
                   (["potion", "baguette", "chapeau", "grimoire"], "La boutique du sorcier"),
                   (["cristal", "baguette", "grimoire", "chouette"], "La grande salle")),
        labyrinthes=(("princesse", "champignon"), ("dragon", "arbre"), ("princesse", "fleur"), ("princesse", "cristal"),
                     ("dragon", "chateau"), ("princesse", "grimoire"), ("princesse", "chateau")),
        chemins=(("princesse", "champignon"), ("princesse", "chateau"), ("princesse", "grimoire")),
        illustrations=(["fleur", "potion"], ["chapeau", "grimoire", "cristal"], ["chateau", "etoile", "dragon"]),
        recits={3: "chouette", 5: "grimoire", 7: "dragon", 15: "potion", 17: "chapeau", 23: "dragon", 24: "chouette", 26: "grimoire", 32: "dragon"},
        decor=(("chateau", 0.13), ("dragon", 0.3), ("potion", 0.7), ("baguette", 0.87)), principal="princesse",
    ),
}


def composer(cfg: ConfigProduit) -> tuple[list[PageSpec], Composeur]:
    """Génère et vérifie toutes les activités ; renvoie les pages (sans rendu PDF)."""
    u = UNIVERS[cfg.id]
    rng = random.Random(cfg.graine)
    histoire = charger(u.histoire)
    gab = charger("enigmes")[u.enigmes]
    par_niveau = {n: [g for g in gab if g["niveau"] == n] for n in (1, 2, 3)}
    etapes = iter(enumerate(histoire["etapes"], start=1))
    k = Composeur(rng, theme_de(cfg), u.prefixe)

    def r() -> Recit:
        num, texte = next(etapes)
        return Recit(num, texte, u.recits.get(num, u.heros))

    s1, s2, s3 = u.sections
    lab = iter(u.labyrinthes)

    def labyrinthe(taille, niveau, section):
        d, a = next(lab)
        k.labyrinthe(taille, niveau, d, a, u.mission, r(), section)

    (c1, t1), (c2, t2), (c3, t3) = u.comptages
    m1, m2, m3, m4 = u.messages
    (d1, a1), (d2, a2), (d3, a3) = u.chemins
    i1, i2, i3 = u.illustrations
    col1, col2, col3 = u.coloriages

    labyrinthe((7, 7), "debutant", s1)
    k.comptage(c1, 2, 7, r(), s1, titre=t1)
    k.logique(L["1a"], r(), s1)
    k.nonogrammes([u.petits[0]], r(), s1)
    k.code(m1, r(), s1)
    k.differences(5, u.objets, r(), s1)
    labyrinthe((8, 8), "debutant", s1)
    k.problemes(par_niveau[1][:2], r(), s1, illustrations=i1)
    k.coloriage(col1, r(), s1)
    k.chemin(1, d1, a1, u.nom_heros, r(), s1)
    k.logique(L["1b"], r(), s1)
    labyrinthe((10, 10), "intermediaire", s2)
    k.nonogrammes([u.petits[1]], r(), s2)
    k.comptage(c2, 2, 8, r(), s2, titre=t2)
    k.code(m2, r(), s2)
    k.differences(6, u.objets, r(), s2)
    k.logique(L["2a"], r(), s2)
    labyrinthe((12, 11), "intermediaire", s2)
    k.problemes(par_niveau[2][:3], r(), s2, illustrations=i2)
    k.nonogrammes([u.grands[0]], r(), s2)
    k.coloriage(col2, r(), s2)
    k.chemin(5, d2, a2, u.nom_heros, r(), s2)
    labyrinthe((13, 12), "intermediaire", s2)
    k.logique(L["2b"], r(), s2)
    k.differences(7, u.objets, r(), s3)
    k.code(m3, r(), s3)
    k.nonogrammes([u.grands[1]], r(), s3)
    k.comptage(c3, 3, 10, r(), s3, titre=t3)
    labyrinthe((15, 14), "defi", s3)
    k.problemes(par_niveau[3][:3], r(), s3, illustrations=i3)
    k.logique(L["3a"], r(), s3)
    k.coloriage(col3, r(), s3)
    k.nonogrammes([u.grands[2]], r(), s3)
    k.chemin(10, d3, a3, u.nom_heros, r(), s3)
    labyrinthe((17, 15), "defi", s3)
    k.code(m4, r(), s3)
    restantes = list(etapes)
    if restantes:
        raise RuntimeError(f"{len(restantes)} étape(s) d'histoire non utilisée(s)")

    couverture = page_couverture(u.titre, u.sous_titre, u.objets,
                                 ["Une histoire en 36 étapes", "Labyrinthes, énigmes, logique", "Corrigés inclus"],
                                 principal=u.principal)
    intro = page_intro_aventure(histoire["titre_intro"], histoire["intro"], u.heros, histoire["objectifs"],
                                decor=u.decor)
    diplome = page_diplome(histoire["diplome_titre"],
                           histoire["diplome_texte"][0].upper() + histoire["diplome_texte"][1:]
                           + "<br/><br/><b>" + histoire["fin"] + "</b>", u.heros)
    pages = [couverture, intro] + k.pages + [diplome] + k.pages_corriges()
    return pages, k


def construire(cfg: ConfigProduit) -> ResultatProduit:
    u = UNIVERS[cfg.id]
    pages, k = composer(cfg)
    ch = chemins(cfg.id)
    res = assembler(pages, ch["pdf"], u.titre, u.titre, theme_de(cfg), "Cahier-aventure 6-8 ans")
    res_eco = assembler(pages, ch["encre_eco"], f"{u.titre} (économie d'encre)", u.titre, theme_de(cfg, eco=True),
                        "Cahier-aventure 6-8 ans — version économie d'encre")
    verifs = [Verification(v.id, v.type, v.erreurs) for v in k.verifications]
    premiere_solution = next(p.numero for p in res.pages if p.kind == "solution")
    apercus = [Apercu("pdf", 2, "Le début de l'histoire"), Apercu("pdf", 7, ""), Apercu("pdf", 14, ""),
               Apercu("pdf", 17, ""), Apercu("pdf", premiere_solution, "Extrait des corrigés")]
    compo = {TYPES_JEUX[t]: n for t, n in k.compte.items()}
    compo["Étapes d'histoire"] = len(charger(u.histoire)["etapes"])
    return ResultatProduit(cfg.id, {"pdf": res, "encre_eco": res_eco}, verifs, k.nb_jeux, apercus,
                           attendus={"pages_min": cfg.pages_min, "pages_max": cfg.pages_max}, composition=compo)
