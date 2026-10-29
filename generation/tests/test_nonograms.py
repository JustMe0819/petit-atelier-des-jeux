import pytest

from generation.assets import pixel_designs as pd
from generation.generators import nonograms as ng

TOUS = [d for nom in dir(pd) if nom.isupper() and isinstance(getattr(pd, nom), list) for d in getattr(pd, nom)]


def test_indices_calcules():
    g = ng.depuis_texte("""
#.##.
#####
.....""")
    lignes, colonnes = ng.calculer_indices(g)
    assert lignes == [[1, 2], [5], [0]]
    assert colonnes == [[2], [1], [2], [2], [1]]


@pytest.mark.parametrize("dessin", TOUS, ids=lambda d: d.id)
def test_chaque_dessin_a_une_solution_unique(dessin):
    n = ng.Nonogramme(dessin.id, dessin.titre, dessin.indice, ng.depuis_texte(dessin.motif))
    assert n.largeur == n.hauteur and n.largeur in (5, 10)
    # Les indices reproduisent le dessin.
    assert ng.calculer_indices(n.dessin) == (n.lignes, n.colonnes)
    nb, sol = ng.compter_solutions(n.lignes, n.colonnes)
    assert nb == 1 and sol == n.dessin
    assert ng.verifier(n) == []


def test_grille_ambigue_detectee():
    # Diagonale 2 × 2 : indices [1],[1] / [1],[1] → deux solutions.
    lignes, colonnes = [[1], [1]], [[1], [1]]
    nb, _ = ng.compter_solutions(lignes, colonnes)
    assert nb == 2
    n = ng.Nonogramme("ambigu", "x", "", [[1, 0], [0, 1]])
    assert any("solution" in e for e in ng.verifier(n))


def test_grille_ambigue_5x5_detectee():
    n = ng.Nonogramme("bateau-ambigu", "x", "", ng.depuis_texte("""
..#..
..##.
..###
#####
.###."""))
    nb, _ = ng.compter_solutions(n.lignes, n.colonnes)
    assert nb >= 2
    assert ng.verifier(n) != []


def test_ids_uniques_et_reserves_disjointes():
    ids = [d.id for d in TOUS]
    assert len(ids) == len(set(ids))
    assert len(pd.PETITS_PACK) == 20 and len(pd.GRANDS_PACK) == 20


def test_etapes_guidees_aboutissent_au_dessin():
    n = ng.Nonogramme("x", "x", "", ng.depuis_texte(pd.PETITS_GRATUITS[0].motif))
    etapes = ng.etapes_guidees(n)
    assert etapes and etapes[-1]["etat"] == n.dessin
