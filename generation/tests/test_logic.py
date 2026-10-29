import random

import pytest

from generation.generators import logic_puzzles as lp
from generation.generators.figures import Figure


@pytest.fixture(scope="module")
def pack():
    return lp.serie(random.Random(2202), lp.PLAN_PACK, "logique")


def test_trente_activites_progressives(pack):
    assert len(pack) == 30
    ordre = {"debutant": 0, "intermediaire": 1, "defi": 2}
    niveaux = [ordre[a.niveau] for a in pack]
    assert niveaux == sorted(niveaux)
    assert {a.type for a in pack} == set(lp.NOMS_TYPES)


def test_chaque_activite_a_exactement_une_bonne_reponse(pack):
    for a in pack:
        assert lp.verifier(a) == [], a.id
        if a.type in ("suite_formes",):
            unite, k = a.donnees["unite"], a.donnees["nb_affiches"]
            attendu = unite[k % len(unite)]
            assert sum(o == attendu for o in a.donnees["options"]) == 1
        if a.type == "association":
            assert len(lp.appariements_parfaits(a.donnees["regle"], a.donnees["gauche"], a.donnees["droite"])) == 1
        if a.type == "suite_nombres":
            visibles = [None if i in a.donnees["trous"] else t for i, t in enumerate(a.donnees["termes"])]
            assert len(lp.regles_numeriques_compatibles(visibles)) == 1


@pytest.mark.parametrize("graine", range(15))
def test_generation_robuste_sur_plusieurs_graines(graine):
    for a in lp.serie(random.Random(graine), lp.PLAN_PACK, "t"):
        assert lp.verifier(a) == []


def test_ambiguite_detectee_suite_de_nombres():
    # 2, 4, ? : « +2 » donne 6 mais « ×2 » donne 8 → refusé.
    a = lp.Activite("x", 1, "debutant", "suite_nombres", "", {"termes": [2, 4, 6], "trous": [2]}, [6])
    assert lp.verifier(a)


def test_ambiguite_detectee_intrus():
    figs = [Figure("rond", "plein"), Figure("rond", "plein"), Figure("rond", "plein"), Figure("carré", "vide")]
    # L'intrus diffère par la forme ET par le motif : la consigne « forme » n'est pas univoque.
    a = lp.Activite("x", 1, "debutant", "intrus", "", {"figures": figs, "attribut": "forme"}, 3)
    assert any("ambiguïté" in e for e in lp.verifier(a))


def test_qcm_avec_deux_bonnes_options_refuse(pack):
    a = next(x for x in pack if x.type == "grille")
    opts = list(a.donnees["options"])
    opts[(a.reponse + 1) % len(opts)] = opts[a.reponse]
    b = lp.Activite(a.id, a.numero, a.niveau, a.type, a.consigne, {**a.donnees, "options": opts}, a.reponse)
    assert lp.verifier(b)


def test_association_a_deux_solutions_refusee():
    a = lp.Activite("x", 1, "debutant", "association", "",
                    {"regle": "ombre", "gauche": [Figure("rond", "rayé"), Figure("rond", "pois")],
                     "droite": [Figure("rond", "plein"), Figure("rond", "plein")]}, [0, 1])
    assert lp.verifier(a)
