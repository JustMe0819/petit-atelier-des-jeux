import random
from collections import deque

import pytest

from generation.generators import mazes


@pytest.fixture(scope="module")
def serie():
    return mazes.serie_progressive(random.Random(1101), par_niveau=10)


def test_labyrinthes_parfaits_et_valides(serie):
    assert len(serie) == 30
    for lab in serie:
        assert mazes.verifier(lab) == []
        # Parfait = arbre couvrant : n - 1 passages et toutes les cases atteignables.
        assert lab.nb_passages() == lab.lignes * lab.colonnes - 1


def test_solution_est_le_chemin_bfs_et_relie_depart_arrivee(serie):
    for lab in serie:
        sol = lab.solution
        assert sol[0] == lab.depart and sol[-1] == lab.arrivee
        assert sol == mazes.resoudre_bfs(lab)
        for a, b in zip(sol, sol[1:]):
            assert b in lab.voisins(a)


def test_un_chemin_existe_par_parcours_independant(serie):
    lab = serie[-1]
    vus = {lab.depart}
    file = deque([lab.depart])
    while file:
        for v in lab.voisins(file.popleft()):
            if v not in vus:
                vus.add(v)
                file.append(v)
    assert lab.arrivee in vus


def test_tailles_par_niveau_croissantes(serie):
    niveaux = [l.niveau for l in serie]
    assert niveaux == ["debutant"] * 10 + ["intermediaire"] * 10 + ["defi"] * 10
    surfaces = [l.lignes * l.colonnes for l in serie]
    assert surfaces == sorted(surfaces)
    for lab in serie:
        assert (lab.lignes, lab.colonnes) in mazes.TAILLES_NIVEAUX[lab.niveau]
    assert max(l.lignes * l.colonnes for l in serie if l.niveau == "debutant") < \
        min(l.lignes * l.colonnes for l in serie if l.niveau == "intermediaire")


def test_mur_casse_detecte():
    lab = mazes.generer(6, 6, random.Random(3))
    # On ouvre un mur supplémentaire : il y a alors un cycle, le labyrinthe n'est plus parfait.
    for l in range(5):
        for c in range(5):
            if "E" not in lab.ouvertures[l][c]:
                lab.ouvertures[l][c].add("E")
                lab.ouvertures[l][c + 1].add("O")
                assert any("parfait" in e for e in mazes.verifier(lab))
                return


def test_determinisme():
    a = mazes.generer(9, 9, random.Random(42))
    b = mazes.generer(9, 9, random.Random(42))
    assert a.ouvertures == b.ouvertures and a.solution == b.solution
