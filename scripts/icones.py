"""Réduit la police d'icônes Material Symbols (4 Mo) aux seules icônes utilisées par le site.

Usage : python3 scripts/icones.py   (à relancer après avoir ajouté une nouvelle icône)
Dépendances : pip install fonttools brotli
"""
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "node_modules/material-symbols/material-symbols-outlined.woff2"
CIBLE = RACINE / "src/client/assets/icones.woff2"

police = TTFont(SOURCE)
glyphes_police = set(police.getGlyphOrder())

# Toutes les chaînes du code qui ressemblent à un nom d'icône et existent dans la police.
mots: set[str] = set()
for fichier in list((RACINE / "src/client").rglob("*.ts*")) + list((RACINE / "src/shared").rglob("*.ts")):
    mots |= set(re.findall(r"['\"`]([a-z][a-z0-9_]{1,40})['\"`]", fichier.read_text(encoding="utf-8")))
    mots |= set(re.findall(r"nom=\"([a-z][a-z0-9_]+)\"", fichier.read_text(encoding="utf-8")))

# Table des ligatures : « texte » -> glyphe (certains noms sont des alias, ex. card_giftcard -> redeem).
cmap = police.getBestCmap()
car_vers_glyphe = {chr(c): g for c, g in cmap.items()}
ligatures: dict[tuple[str, ...], str] = {}
for lookup in police["GSUB"].table.LookupList.Lookup:
    for st in lookup.SubTable:
        st = getattr(st, "ExtSubTable", st)
        if hasattr(st, "ligatures"):
            for premier, ligs in st.ligatures.items():
                for lig in ligs:
                    ligatures[(premier, *lig.Component)] = lig.LigGlyph


def glyphe_pour(mot: str) -> str | None:
    cle = tuple(car_vers_glyphe.get(c, "") for c in mot)
    return ligatures.get(cle)


icones = sorted(m for m in mots if glyphe_pour(m))
cibles = {glyphe_pour(m) for m in icones}

glyphes = set(cibles) | {f"{g}.fill" for g in cibles if f"{g}.fill" in glyphes_police}
lettres = "abcdefghijklmnopqrstuvwxyz0123456789_"
options = subset.Options()
options.layout_closure = False
options.flavor = "woff2"
options.layout_features = ["liga", "rlig", "calt", "rvrn"]
s = subset.Subsetter(options)
s.populate(glyphs=sorted(glyphes), text=lettres)
s.subset(police)
# On fige ensuite les axes inutilisés (graisse 400, grade 0, taille optique 24) ; on garde l'axe FILL.
police = instancer.instantiateVariableFont(police, {"wght": 400, "GRAD": 0, "opsz": 24})
CIBLE.parent.mkdir(parents=True, exist_ok=True)
police.flavor = "woff2"
police.save(CIBLE)
print(f"{len(icones)} icônes conservées → {CIBLE.relative_to(RACINE)} ({CIBLE.stat().st_size // 1024} Ko)")
