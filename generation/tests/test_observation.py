import random
from dataclasses import replace

import pytest

from generation.assets import colour_designs as cd
from generation.generators import coloriage as gc
from generation.generators import enigmes as ge
from generation.generators import observation as ob
from generation.pdf_builder import pictos
from generation.pdf_builder.theme import Theme
from generation.qa.verif_rendu import emplacements_differents, verifier_differences_rendu

THEME = Theme.depuis_hex("#2F8F9D", "#DDF0F2")


def test_tous_les_objets_ont_un_pictogramme():
    for k in ob.OBJETS_NATURE + ob.ANIMAUX + ob.DINOS + ob.ESPACE + ob.PIRATES + ob.MAGIE:
        assert k in pictos.PICTOS and k in ob.NOMS


@pytest.mark.parametrize("n,graine", [(5, 1), (6, 2), (7, 3), (8, 4)])
def test_nombre_de_differences_modele_et_rendu(n, graine):
    jeu = ob.generer_differences(random.Random(graine), n, ob.OBJETS_NATURE, "t")
    assert jeu.n == n
    assert ob.verifier_differences(jeu) == []
    # Vérification au pixel : exactement n emplacements diffèrent à l'écran.
    assert len(emplacements_differents(jeu, THEME)) == n
    assert verifier_differences_rendu(jeu, THEME) == []


def test_difference_non_annoncee_detectee():
    jeu = ob.generer_differences(random.Random(9), 5, ob.ANIMAUX, "t")
    # On retire une différence de la liste annoncée : le contrôle doit échouer.
    jeu.differences = jeu.differences[:-1]
    assert ob.verifier_differences(jeu)
    assert verifier_differences_rendu(jeu, THEME)


def test_comptage_reponses_et_chevauchements():
    for g in range(5):
        jeu = ob.generer_comptage(random.Random(g), ["lapin", "souris", "poussin", "chat"], 3, 10, "t")
        assert ob.verifier_comptage(jeu) == []
        for k in jeu.kinds:
            assert sum(o.kind == k for o in jeu.objets) == jeu.reponses[k]


def test_comptage_faux_detecte():
    jeu = ob.generer_comptage(random.Random(1), ["lapin", "souris"], 2, 6, "t")
    jeu.reponses["lapin"] += 1
    assert ob.verifier_comptage(jeu)
    jeu.reponses["lapin"] -= 1
    jeu.objets.append(replace(jeu.objets[0]))  # objet superposé
    assert ob.verifier_comptage(jeu)


@pytest.mark.parametrize("dessin", cd.CAHIER + cd.DINO + cd.ESPACE + cd.PIRATES + cd.MAGIE, ids=lambda d: d.id)
def test_coloriages_codes(dessin):
    cc = gc.depuis_dessin(dessin, dessin.id)
    assert gc.verifier(cc, dessin) == []


def test_code_secret_et_chemin_des_nombres():
    rng = random.Random(5)
    for msg in ("NID", "VOLCAN", "BRAVO PICO", "BRAVO FILOU", "BRAVO COCO", "BRAVO LILA"):
        c = ge.generer_code(rng, msg, "t")
        assert ge.verifier_code(c) == [] and ge.decoder(c) == msg
    for pas in (1, 2, 5, 10):
        ch = ge.generer_chemin(rng, "t", pas=pas)
        assert ge.verifier_chemin(ch) == [] and len(ge.chemins_valides(ch)) == 1


def test_problemes_calcul_verifie():
    from generation.templates import charger
    rng = random.Random(3)
    for g in [g for cle in ("dinosaures", "espace", "pirates", "magie") for g in charger("enigmes")[cle]]:
        p = ge.generer_probleme(rng, g)
        assert ge.verifier_probleme(p) == [] and p.reponse == p.calcul()
    faux = ge.Probleme("Il y a 3 œufs et 4 œufs.", "+", 3, 4, 8)
    assert ge.verifier_probleme(faux)


@pytest.mark.parametrize("univers", ["ESPACE", "PIRATES", "MAGIE"])
def test_differences_des_cahiers_aventures(univers):
    jeu = ob.generer_differences(random.Random(11), 7, getattr(ob, univers), "t")
    assert ob.verifier_differences(jeu) == []
    assert verifier_differences_rendu(jeu, THEME) == []
