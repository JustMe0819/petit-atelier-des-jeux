"""Images d'aperçu rendues DEPUIS le PDF final (fidèles au produit), avec filigrane « APERÇU »."""
from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

from generation.config import LARGEUR_APERCU_PX
from generation.pdf_builder.fonts import TITRE, chemin_police


def rendre_page(pdf_path: Path, numero: int, largeur_px: int = LARGEUR_APERCU_PX) -> Image.Image:
    pdf = pdfium.PdfDocument(str(pdf_path))
    page = pdf[numero - 1]
    echelle = largeur_px / page.get_width()
    img = page.render(scale=echelle).to_pil().convert("RGB")
    page.close()
    pdf.close()
    return img


def filigrane(img: Image.Image, texte: str = "APERÇU") -> Image.Image:
    w, h = img.size
    calque = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    police = ImageFont.truetype(str(chemin_police(TITRE)), int(w * 0.2))
    d = ImageDraw.Draw(calque)
    bbox = d.textbbox((0, 0), texte, font=police)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bloc = Image.new("RGBA", (tw + 40, th + 60), (0, 0, 0, 0))
    ImageDraw.Draw(bloc).text((20 - bbox[0], 30 - bbox[1]), texte, font=police, fill=(120, 120, 120, 38))
    bloc = bloc.rotate(55, expand=True, resample=Image.BICUBIC)
    calque.alpha_composite(bloc, ((w - bloc.width) // 2, (h - bloc.height) // 2))
    return Image.alpha_composite(img.convert("RGBA"), calque).convert("RGB")


def generer_apercu(pdf_path: Path, numero: int, sortie: Path, avec_filigrane: bool = True) -> dict:
    img = rendre_page(pdf_path, numero)
    if avec_filigrane:
        img = filigrane(img)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie, "PNG", optimize=True)
    return {"fichier": str(sortie), "largeur": img.width, "hauteur": img.height}
