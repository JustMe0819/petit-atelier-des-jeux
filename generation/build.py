"""Point d'entrée : génération → vérification → PDF → QA → aperçus → catalogue.

Exemples (depuis la racine du dépôt) :
    python -m generation.build --produit labyrinthes-petits-explorateurs
    python -m generation.build --tous          # les 8 produits + les fichiers gratuits
    python -m generation.build --gratuits
    python -m generation.build --produit mission-dinosaures --sans-catalogue
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from importlib import import_module

from generation import catalogue
from generation.config import APERCUS, BUNDLES, PRODUITS, RACINE, SORTIES, STOCKAGE
from generation.produits.base import ResultatProduit
from generation.qa.pdf_qa import auditer_pdf, controle
from generation.qa.previews import generer_apercu

MODULES = {
    "labyrinthes-petits-explorateurs": "generation.produits.labyrinthes",
    "defis-de-la-logique": "generation.produits.logique",
    "mes-premiers-nonogrammes": "generation.produits.nonogrammes",
    "grand-cahier-petits-explorateurs": "generation.produits.grand_cahier",
    "mission-dinosaures": "generation.produits.mission_dinosaures",
    "mission-espace": "generation.produits.missions",
    "mission-pirates": "generation.produits.missions",
    "mission-magie": "generation.produits.missions",
}


def _rel(chemin, base=RACINE) -> str:
    return str(chemin.resolve().relative_to(base.resolve())).replace("\\", "/")


def controles_produit(res: ResultatProduit) -> list[dict]:
    out = []
    ko = [{"id": v.id, "type": v.type, "erreurs": v.erreurs} for v in res.verifications if not v.ok]
    out.append(controle("solutions_validees", not ko and bool(res.verifications),
                        ko or f"{len(res.verifications)} jeux vérifiés par programme, tous valides"))
    att = res.attendus
    if att.get("nb_jeux") is not None:
        out.append(controle("nombre_de_jeux", res.nb_jeux == att["nb_jeux"],
                            {"generes": res.nb_jeux, "attendus": att["nb_jeux"]}))
    if att.get("pages_pdf") is not None:
        out.append(controle("pages_du_pdf", res.livres["pdf"].nb_pages == att["pages_pdf"],
                            {"pdf": res.livres["pdf"].nb_pages, "attendues": att["pages_pdf"]}))
    if att.get("pages_min") is not None:
        n = res.livres["pdf"].nb_pages
        out.append(controle("objectif_de_pages", att["pages_min"] <= n <= att["pages_max"],
                            {"pages": n, "objectif": f"{att['pages_min']} à {att['pages_max']}",
                             "note": "informatif : aucune page n'est ajoutée artificiellement"},
                            bloquant=False))
    if att.get("max_pages_dessin") is not None:
        n = sum(1 for p in res.livres["pdf"].pages if p.kind == "dessin")
        out.append(controle("pages_dessin_limitees", n <= att["max_pages_dessin"],
                            {"pages_dessin": n, "maximum": att["max_pages_dessin"]}))
    tous = [p for l in res.livres.values() for p in l.pages]
    out.append(controle("corriges_presents", any(p.kind == "solution" for p in tous),
                        f"{sum(p.kind == 'solution' for p in tous)} page(s) de corrigés"))
    if "encre_eco" in res.livres:
        a, b = res.livres["pdf"], res.livres["encre_eco"]
        meme = [p.legende for p in a.pages] == [p.legende for p in b.pages]
        out.append(controle("version_eco_identique", meme and a.nb_pages == b.nb_pages,
                            {"pages_normale": a.nb_pages, "pages_eco": b.nb_pages}))
    return out


def construire_produit(id_produit: str, maj_catalogue: bool = True) -> dict:
    t0 = time.time()
    cfg = PRODUITS[id_produit]
    res: ResultatProduit = import_module(MODULES[id_produit]).construire(cfg)
    audits = {cle: auditer_pdf(livre, eco=(cle == "encre_eco")) for cle, livre in res.livres.items()}
    ctrl = controles_produit(res)
    valide = all(c["ok"] for c in ctrl if c["bloquant"]) and all(a["ok"] for a in audits.values())

    # Aperçus rendus depuis les PDF finaux.
    dossier = APERCUS / id_produit
    if dossier.exists():
        shutil.rmtree(dossier)
    apercus = []
    for i, ap in enumerate(res.apercus, start=1):
        livre = res.livres[ap.fichier]
        rec = livre.pages[ap.page - 1]
        sortie = dossier / f"apercu-{i:02d}.png"
        generer_apercu(livre.chemin, ap.page, sortie)
        apercus.append({"src": f"/apercus/{id_produit}/{sortie.name}", "legende": ap.legende or rec.legende})

    genere_le = datetime.now().astimezone().isoformat(timespec="seconds")
    statut = "en_verification" if valide else "brouillon"
    rapport = {
        "produit": id_produit,
        "genere_le": genere_le,
        "graine": cfg.graine,
        "valide_automatiquement": valide,
        "statut_propose": statut,
        "raisons_echec": [c["nom"] for c in ctrl if c["bloquant"] and not c["ok"]]
                         + [f"{cle}:{c['nom']}" for cle, a in audits.items() for c in a["controles"]
                            if c["bloquant"] and not c["ok"]],
        "nb_jeux": res.nb_jeux,
        "composition": res.composition,
        "controles_produit": ctrl,
        "fichiers": {cle: {**a, "fichier": _rel(res.livres[cle].chemin)} for cle, a in audits.items()},
        "verifications": [{"id": v.id, "type": v.type, "ok": v.ok, "erreurs": v.erreurs} for v in res.verifications],
        "apercus": apercus,
        "notes": res.notes,
        "duree_s": round(time.time() - t0, 1),
    }
    chemin_rapport = SORTIES / id_produit / "rapport_qualite.json"
    chemin_rapport.parent.mkdir(parents=True, exist_ok=True)
    chemin_rapport.write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if maj_catalogue:
        fichiers = {"pdf": None, "corriges": None, "encre_eco": None}
        for cle, livre in res.livres.items():
            fichiers[cle] = _rel(livre.chemin, STOCKAGE)
        catalogue.mettre_a_jour_produit(id_produit, {
            "fichiers": fichiers,
            "contenu": {"nb_pages": res.livres["pdf"].nb_pages, "nb_jeux": res.nb_jeux, "genere_le": genere_le},
            "apercus": apercus,
            "qa": {"rapport": _rel(chemin_rapport), "valide_automatiquement": valide},
            "statut": statut,
        })
    return rapport


def resume(r: dict) -> str:
    pages = ", ".join(f"{k} {v['nb_pages']} p." for k, v in r["fichiers"].items())
    etat = "QA OK → en_verification" if r["valide_automatiquement"] else f"QA ÉCHEC ({r['raisons_echec']}) → brouillon"
    return f"• {r['produit']} : {r['nb_jeux']} jeux, {pages} — {etat} ({r['duree_s']} s)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m generation.build",
                                 description="Génère les PDF du Petit Atelier des Jeux.")
    ap.add_argument("--produit", action="append", default=[], help="identifiant du produit (répétable)")
    ap.add_argument("--tous", action="store_true", help="tous les produits et les fichiers gratuits")
    ap.add_argument("--gratuits", action="store_true", help="les fichiers gratuits")
    ap.add_argument("--sans-catalogue", action="store_true", help="ne pas modifier catalogue/catalogue.json")
    args = ap.parse_args(argv)

    ids = list(MODULES) if args.tous else args.produit
    for i in ids:
        if i in BUNDLES:
            print(f"• {i} : offre groupée, aucun fichier propre à générer.")
            continue
        if i not in MODULES:
            ap.error(f"produit inconnu : {i} (connus : {', '.join(MODULES)})")
    if not ids and not (args.gratuits or args.tous):
        ap.print_help()
        return 1
    ok = True
    for i in ids:
        if i in BUNDLES:
            continue
        r = construire_produit(i, not args.sans_catalogue)
        ok &= r["valide_automatiquement"]
        print(resume(r), flush=True)
    if args.gratuits or args.tous:
        from generation.produits.gratuits import construire_gratuits
        r = construire_gratuits(not args.sans_catalogue)
        ok &= r["valide_automatiquement"]
        for g in r["fichiers"]:
            print(f"• gratuit {g['id']} : {g['nb_pages']} p. — {'QA OK' if g['ok'] else 'QA ÉCHEC'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
