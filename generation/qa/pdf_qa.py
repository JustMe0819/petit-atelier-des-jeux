"""Contrôle qualité automatique des PDF produits.

Chaque contrôle renvoie {"nom", "ok", "details", "bloquant"}. Un contrôle non bloquant
(informatif) est consigné dans le rapport sans empêcher la validation automatique.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pdfplumber
import pypdfium2 as pdfium
from pypdf import PdfReader

from generation.pdf_builder.document import ResultatLivre
from generation.pdf_builder.theme import HAUTEUR_PAGE, LARGEUR_PAGE, MARGE, MARGE_CONTROLE_QA

DPI_QA = 72
SEUIL_ENCRE = 0.004      # proportion minimale de pixels non blancs pour qu'une page ne soit pas « vide »
SEUIL_BLANC = 235        # un pixel est « encré » si une de ses composantes est sous ce seuil
SEUIL_SATURATION = 40    # écart max entre composantes RVB pour un pixel considéré comme gris


def controle(nom: str, ok: bool, details, bloquant: bool = True) -> dict:
    return {"nom": nom, "ok": bool(ok), "bloquant": bloquant, "details": details}


def rendre_pages(chemin: Path, dpi: int = DPI_QA) -> list[np.ndarray]:
    pdf = pdfium.PdfDocument(str(chemin))
    images = []
    for page in pdf:
        img = page.render(scale=dpi / 72).to_pil().convert("RGB")
        images.append(np.asarray(img))
        page.close()
    pdf.close()
    return images


def verifier_format_a4(reader: PdfReader) -> dict:
    mauvaises = []
    for i, p in enumerate(reader.pages, start=1):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        if abs(w - LARGEUR_PAGE) > 1 or abs(h - HAUTEUR_PAGE) > 1:
            mauvaises.append({"page": i, "taille_pt": [round(w, 1), round(h, 1)]})
    return controle("format_a4", not mauvaises, mauvaises or "toutes les pages sont en A4 portrait")


def polices(reader: PdfReader) -> dict[str, bool]:
    """Nom de police → embarquée ?"""
    out: dict[str, bool] = {}
    for p in reader.pages:
        res = p.get("/Resources") or {}
        fonts = res.get("/Font") or {}
        for _, ref in fonts.items():
            f = ref.get_object()
            nom = str(f.get("/BaseFont"))
            desc = f.get("/FontDescriptor")
            if desc is None and "/DescendantFonts" in f:
                desc = f["/DescendantFonts"][0].get_object().get("/FontDescriptor")
            desc = desc.get_object() if desc is not None else {}
            out[nom] = any(k in desc for k in ("/FontFile", "/FontFile2", "/FontFile3"))
    return out


def verifier_polices(reader: PdfReader) -> dict:
    p = polices(reader)
    non = [n for n, ok in p.items() if not ok]
    return controle("polices_embarquees", bool(p) and not non,
                    {"polices": sorted(p), "non_embarquees": non})


def taux_encre(img: np.ndarray) -> float:
    return float((img.min(axis=2) < SEUIL_BLANC).mean())


def verifier_pages_non_vides(images: list[np.ndarray]) -> dict:
    taux = [round(taux_encre(im), 4) for im in images]
    vides = [i + 1 for i, t in enumerate(taux) if t < SEUIL_ENCRE]
    return controle("pages_non_vides", not vides,
                    {"pages_vides": vides, "taux_encre_min": min(taux) if taux else None})


def pixels_dans_marges(img: np.ndarray, marge_pt: float = MARGE_CONTROLE_QA, dpi: int = DPI_QA) -> int:
    b = int(round(marge_pt * dpi / 72))
    encre = img.min(axis=2) < SEUIL_BLANC
    masque = np.zeros_like(encre)
    masque[:b, :] = True
    masque[-b:, :] = True
    masque[:, :b] = True
    masque[:, -b:] = True
    return int((encre & masque).sum())


def verifier_marges(images: list[np.ndarray]) -> dict:
    fautes = [{"page": i + 1, "pixels": n} for i, im in enumerate(images) if (n := pixels_dans_marges(im))]
    return controle("contenu_dans_les_marges", not fautes,
                    fautes or f"bande de {MARGE_CONTROLE_QA / 72 * 25.4:.0f} mm blanche sur toutes les pages "
                               f"(zone de sécurité du contenu : {MARGE / 72 * 25.4:.0f} mm)")


def verifier_sans_couleur(images: list[np.ndarray]) -> dict:
    fautes = []
    for i, im in enumerate(images):
        sat = (im.max(axis=2).astype(int) - im.min(axis=2).astype(int)) > SEUIL_SATURATION
        if sat.sum():
            fautes.append({"page": i + 1, "pixels_colores": int(sat.sum())})
    return controle("encre_eco_sans_couleur", not fautes, fautes or "aucun pixel coloré")


def verifier_pagination(chemin: Path, livre: ResultatLivre) -> dict:
    """Le numéro imprimé en pied de page correspond à la position réelle de la page."""
    fautes = []
    with pdfplumber.open(str(chemin)) as pdf:
        for rec, page in zip(livre.pages, pdf.pages):
            if not rec.numerotee:
                continue
            bas = page.crop((LARGEUR_PAGE / 2 - 20, HAUTEUR_PAGE - MARGE - 12, LARGEUR_PAGE / 2 + 20,
                             HAUTEUR_PAGE - MARGE + 1))
            texte = (bas.extract_text() or "").strip()
            if texte != str(rec.numero):
                fautes.append({"page": rec.numero, "lu": texte})
        nb = len(pdf.pages)
    if nb != livre.nb_pages:
        fautes.append({"nb_pages_pdf": nb, "nb_pages_prevues": livre.nb_pages})
    return controle("pagination", not fautes, fautes or f"{sum(r.numerotee for r in livre.pages)} pages numérotées "
                                                        "correctement")


def verifier_texte(reader: PdfReader) -> dict:
    texte = "".join((p.extract_text() or "") for p in reader.pages)
    probleme = "�" in texte
    accents = sum(texte.count(ch) for ch in "éèàçêù")
    return controle("texte_extractible_accents", not probleme and accents > 0,
                    {"caracteres": len(texte), "lettres_accentuees": accents,
                     "caractere_de_remplacement": probleme})


def auditer_pdf(livre: ResultatLivre, eco: bool = False) -> dict:
    chemin = livre.chemin
    reader = PdfReader(str(chemin))
    images = rendre_pages(chemin)
    controles = [
        controle("nombre_de_pages", len(reader.pages) == livre.nb_pages and len(reader.pages) > 0,
                 {"pdf": len(reader.pages), "prevu": livre.nb_pages}),
        verifier_format_a4(reader),
        verifier_polices(reader),
        controle("glyphes_disponibles", not livre.glyphes_manquants, livre.glyphes_manquants or "tous présents"),
        verifier_pages_non_vides(images),
        verifier_marges(images),
        verifier_pagination(chemin, livre),
        verifier_texte(reader),
    ]
    if eco:
        controles.append(verifier_sans_couleur(images))
    return {
        "fichier": str(chemin),
        "nb_pages": len(reader.pages),
        "taille_octets": chemin.stat().st_size,
        "pages": [r.en_dict() for r in livre.pages],
        "controles": controles,
        "ok": all(c["ok"] for c in controles if c["bloquant"]),
    }
