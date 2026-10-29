"""Cahiers (pagination, pages non vides, limites) et fonctions de QA PDF."""
import random

import numpy as np
import pytest
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader

from generation import catalogue
from generation.config import PRODUITS
from generation.generators.activity_books import assembler
from generation.pdf_builder.theme import Theme
from generation.produits import gratuits, grand_cahier, mission_dinosaures, missions
from generation.qa import pdf_qa

THEME = Theme.depuis_hex("#2F8F9D", "#DDF0F2")


@pytest.fixture(scope="module")
def mini(tmp_path_factory):
    k, pages, _ = gratuits._mini_cahier(random.Random(1))
    d = tmp_path_factory.mktemp("mini")
    normal = assembler(pages, d / "mini.pdf", "Mini", "Mini", THEME)
    eco = assembler(pages, d / "mini-eco.pdf", "Mini", "Mini", THEME.version_eco())
    return k, normal, eco


def test_mini_cahier_complet_et_qa_ok(mini):
    k, normal, eco = mini
    assert 4 <= normal.nb_pages <= 6
    assert k.nb_jeux == 5  # 1 labyrinthe + 2 logique + 1 nonogramme + 1 différences
    assert all(not v.erreurs for v in k.verifications)
    a = pdf_qa.auditer_pdf(normal)
    assert a["ok"], [c for c in a["controles"] if not c["ok"]]
    e = pdf_qa.auditer_pdf(eco, eco=True)
    assert e["ok"], [c for c in e["controles"] if not c["ok"]]
    assert [p.numero for p in normal.pages] == list(range(1, normal.nb_pages + 1))


def test_grand_cahier_composition():
    pages, k = grand_cahier.composer(PRODUITS["grand-cahier-petits-explorateurs"])
    assert 35 <= len(pages) <= 40
    assert sum(p.kind == "dessin" for p in pages) <= 2
    assert pages[0].kind == "couverture" and pages[1].kind == "consignes"
    assert pages[-1].kind == "solution"
    assert all(not v.erreurs for v in k.verifications)
    assert k.nb_jeux == sum(k.compte.values()) > 30


def test_mission_dinosaures_composition():
    pages, k = mission_dinosaures.composer(PRODUITS["mission-dinosaures"])
    assert 40 <= len(pages) <= 50
    recits = [p for p in pages if p.kind == "activite"]
    assert len(recits) == 36  # une page d'activité par étape de l'histoire
    assert all(not v.erreurs for v in k.verifications)


@pytest.mark.parametrize("id_produit", ["mission-espace", "mission-pirates", "mission-magie"])
def test_missions_composition(id_produit):
    pages, k = missions.composer(PRODUITS[id_produit])
    assert 40 <= len(pages) <= 50
    assert pages[0].kind == "couverture" and pages[-1].kind == "solution"
    assert len([p for p in pages if p.kind == "activite"]) == 36  # une activité par étape d'histoire
    assert all(not v.erreurs for v in k.verifications)


# ------------------------------------------------------------------ fonctions de QA
def _pdf(chemin, dessin, taille=A4, police="Helvetica"):
    c = Canvas(str(chemin), pagesize=taille)
    c.setFont(police, 12)
    dessin(c)
    c.showPage()
    c.save()
    return chemin


def test_qa_detecte_page_blanche(tmp_path):
    p = _pdf(tmp_path / "blanc.pdf", lambda c: None)
    imgs = pdf_qa.rendre_pages(p)
    assert not pdf_qa.verifier_pages_non_vides(imgs)["ok"]


def test_qa_detecte_contenu_dans_la_marge(tmp_path):
    p = _pdf(tmp_path / "marge.pdf", lambda c: c.rect(5, 5, 100, 100, fill=1))
    assert not pdf_qa.verifier_marges(pdf_qa.rendre_pages(p))["ok"]
    p2 = _pdf(tmp_path / "ok.pdf", lambda c: c.rect(100, 100, 300, 300, fill=1))
    assert pdf_qa.verifier_marges(pdf_qa.rendre_pages(p2))["ok"]


def test_qa_detecte_format_non_a4_et_police_non_embarquee(tmp_path):
    p = _pdf(tmp_path / "letter.pdf", lambda c: c.drawString(100, 100, "Bonjour"), taille=letter)
    r = PdfReader(str(p))
    assert not pdf_qa.verifier_format_a4(r)["ok"]
    assert not pdf_qa.verifier_polices(r)["ok"]  # Helvetica n'est pas embarquée


def test_qa_detecte_couleur_en_version_eco():
    img = np.full((50, 50, 3), 255, dtype=np.uint8)
    assert pdf_qa.verifier_sans_couleur([img])["ok"]
    img[10:20, 10:20] = (220, 40, 40)
    assert not pdf_qa.verifier_sans_couleur([img])["ok"]


# ------------------------------------------------------------------ catalogue
def test_catalogue_format_identique_et_publication_interdite(tmp_path):
    from generation.config import CATALOGUE
    copie = tmp_path / "catalogue.json"
    copie.write_text(CATALOGUE.read_text(encoding="utf-8"), encoding="utf-8")
    assert catalogue.formater(catalogue.lire(copie)) + "\n" == copie.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        catalogue.mettre_a_jour_produit("defis-de-la-logique", {"statut": "publie"}, copie)
    with pytest.raises(ValueError):
        catalogue.mettre_a_jour_produit("defis-de-la-logique", {"prix_centimes": 1}, copie)
    avant = catalogue.lire(copie)
    catalogue.mettre_a_jour_produit("defis-de-la-logique", {"statut": "brouillon"}, copie)
    apres = catalogue.lire(copie)
    p_av = next(p for p in avant["produits"] if p["id"] == "defis-de-la-logique")
    p_ap = next(p for p in apres["produits"] if p["id"] == "defis-de-la-logique")
    assert {k: v for k, v in p_av.items() if k != "statut"} == {k: v for k, v in p_ap.items() if k != "statut"}
