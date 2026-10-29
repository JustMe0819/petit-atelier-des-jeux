"""Vérification « au pixel » des jeux de différences.

Les deux scènes sont dessinées séparément avec le même code que dans le PDF,
puis rastérisées et comparées : chaque emplacement annoncé doit contenir une
différence visible, et aucun autre emplacement ne doit différer.
"""
from __future__ import annotations

import io

import numpy as np
import pypdfium2 as pdfium
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.observation import JeuDifferences, Scene
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_observation import dessiner_scene
from generation.pdf_builder.theme import Theme

LARGEUR = 150 * mm


def _raster(scene: Scene, theme: Theme, ratio: float, dpi: int = 100) -> np.ndarray:
    h = LARGEUR / ratio
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=(LARGEUR, h))
    dessiner_scene(c, Rect(0, 0, LARGEUR, h), scene, theme, cadre=False)
    c.showPage()
    c.save()
    pdf = pdfium.PdfDocument(buf.getvalue())
    img = pdf[0].render(scale=dpi / 72).to_pil().convert("L")
    pdf.close()
    return np.asarray(img, dtype=np.int16)


def emplacements_differents(jeu: JeuDifferences, theme: Theme, seuil_pixels: int = 25) -> list[int]:
    sc = jeu.scene_a
    ratio = sc.colonnes / sc.lignes * 0.92
    a = _raster(jeu.scene_a, theme, ratio)
    b = _raster(jeu.scene_b, theme, ratio)
    diff = np.abs(a - b) > 60
    h, w = diff.shape
    out = []
    for s in range(sc.colonnes * sc.lignes):
        col, lig = s % sc.colonnes, s // sc.colonnes
        x0, x1 = int(col * w / sc.colonnes), int((col + 1) * w / sc.colonnes)
        y0, y1 = int(lig * h / sc.lignes), int((lig + 1) * h / sc.lignes)
        if diff[y0:y1, x0:x1].sum() > seuil_pixels:
            out.append(s)
    return out


def verifier_differences_rendu(jeu: JeuDifferences, theme: Theme) -> list[str]:
    vus = emplacements_differents(jeu, theme)
    annonces = sorted(d["slot"] for d in jeu.differences)
    if vus != annonces:
        return [f"différences visibles aux emplacements {vus}, annoncées {annonces}"]
    return []
