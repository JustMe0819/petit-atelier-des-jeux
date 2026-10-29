# Génération des produits — Petit Atelier des Jeux

Cette partie Python fabrique les PDF imprimables (jeux pour les 6-8 ans), les vérifie
automatiquement, rend les images d'aperçu **à partir des PDF finaux** et met à jour le
catalogue partagé `catalogue/catalogue.json`.

> Aucune IA ni API payante n'est utilisée : chaque jeu est produit par un algorithme avec
> une graine fixe (reconstruction identique), puis vérifié par programme.

## Installation

```bash
pip install -r generation/requirements.txt      # (ajouter --break-system-packages si besoin)
```

## Commandes (depuis la racine du dépôt)

```bash
python -m generation.build --produit labyrinthes-petits-explorateurs   # un produit
python -m generation.build --tous            # les 8 produits + les 4 fichiers gratuits
python -m generation.build --gratuits        # seulement les fichiers gratuits
python -m generation.build --tous --sans-catalogue   # sans toucher au catalogue
python -m pytest generation/tests -q         # tests
```

Code de sortie : `0` si tout a passé la QA, `2` si au moins un produit a échoué.

## Ce que fait une construction

1. **Génération** des activités (graine par produit dans `config.py`).
2. **Vérification** de chaque jeu : labyrinthe parfait et solution = chemin BFS ; nonogramme à
   solution unique (solveur avec comptage arrêté à 2) et résoluble ligne par ligne ;
   activité de logique à une seule bonne réponse ; différences contrôlées sur le modèle **et au
   pixel** ; comptages sans chevauchement ; codes secrets bijectifs ; problèmes recalculés…
3. **Assemblage** des PDF (ReportLab, A4 portrait, polices embarquées, pages numérotées).
4. **QA automatique des PDF** : format A4, nombre de pages, polices embarquées, glyphes
   disponibles, aucune page vide (taux d'encre), bande de 12 mm blanche (marges), numéros de
   page lus dans le PDF, texte extractible avec accents, absence de couleur dans la version
   économie d'encre.
5. **Aperçus** : 3 ou 4 pages d'activités + 1 page de corrigés, rendues depuis le PDF final
   (800 px de large, filigrane « APERÇU ») dans `public/apercus/<id>/`.
6. **Catalogue** : mise à jour des seuls champs `fichiers`, `contenu`, `apercus`, `qa`,
   `statut` (et `gratuits`). Le statut passe à `en_verification` si toute la QA passe, sinon il
   reste `brouillon` (raisons dans le rapport). **Le passage à `publie` reste une décision
   humaine** : le code refuse de l'écrire.

Rapports : `generation/output/<id>/rapport_qualite.json` (et `generation/output/gratuits/`).

## Où vont les fichiers

| Fichiers | Emplacement | Accès |
| --- | --- | --- |
| PDF payants (+ corrigés, + économie d'encre) | `storage/produits/<id>/` | privé |
| Aperçus des produits | `public/apercus/<id>/apercu-0N.png` | public |
| Fichiers gratuits + aperçu | `public/gratuit/*.pdf`, `*.png` | public |

## Organisation du code

```
generation/
  build.py              CLI : génération → vérification → PDF → QA → aperçus → catalogue
  config.py             chemins, graines, objectifs par produit
  catalogue.py          lecture/écriture du catalogue (format d'origine conservé)
  generators/           modèles de jeux + vérifications (sans dessin)
    mazes.py  nonograms.py  logic_puzzles.py  figures.py  observation.py
    enigmes.py  coloriage.py  activity_books.py (composition des cahiers)
  pdf_builder/          mise en page ReportLab
    document.py (livre, en-tête, pied de page)  theme.py  fonts.py  text.py  layout.py
    pictos.py (pictogrammes vectoriels)  shapes.py (formes + motifs)
    render_*.py  pages_activites.py  pages_speciales.py  corriges.py
  produits/             un module par produit (missions.py : espace, pirates, magie) + gratuits.py
  qa/                   pdf_qa.py, previews.py, verif_rendu.py (différences au pixel)
  assets/               polices (OFL) + dessins en pixels (nonogrammes, coloriages)
  templates/            textes : missions, histoires des 4 cahiers-aventures, énigmes
  ia/                   accroche IA facultative, désactivée (voir ia/README.md)
  tests/                pytest
```

## Polices

- **Andika** (SIL International) — conçue pour les lecteurs débutants : textes et consignes.
- **Nunito** (ExtraBold / Bold) — arrondie : titres et nombres.

Licence SIL Open Font License 1.1 (`assets/fonts/OFL-*.txt`). Récupérées depuis les
paquets npm `@expo-google-fonts/*` (Google Fonts n'est pas accessible depuis l'environnement
de génération). Repli automatique sur DejaVu Sans si les fichiers manquent.

## Ajouter du contenu

- **Nonogramme** : ajouter un `Dessin` dans `assets/pixel_designs.py` (`#` = case coloriée).
  Les tests refusent tout dessin ambigu ou non résoluble ligne par ligne.
- **Coloriage codé** : `assets/colour_designs.py` (lettre → couleur de `theme.COULEURS_CRAYON`).
- **Textes** : `templates/*.json` (missions de labyrinthe, histoire, gabarits d'énigmes).
- **Pictogramme** : fonction dans `pdf_builder/pictos.py`, à déclarer dans `PICTOS`.

## Choix et limites connues

- Les couvertures sont dessinées dans la zone de sécurité (pas de fond perdu : impression
  maison). Les illustrations sont de simples pictogrammes géométriques originaux.
- La couleur est réservée aux couvertures et au décor (en-têtes, pastilles, pictogrammes) ;
  les jeux restent lisibles en noir et blanc (motifs plutôt que couleurs). Les versions
  « économie d'encre » n'ont aucun pixel coloré (contrôlé).
- Les objectifs de pages des cahiers sont informatifs : aucune page n'est ajoutée pour les
  atteindre ; les pages de dessin/écriture sont limitées à 2.
