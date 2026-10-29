# Petit Atelier des Jeux

Boutique en ligne de jeux et cahiers d'activités **à imprimer** (PDF A4) pour les enfants de 6 à 8 ans.

Le projet contient trois parties qui partagent un même catalogue (`catalogue/catalogue.json`) :

| Partie | Dossier | Rôle |
|---|---|---|
| Site | `src/client/` | Pages de la boutique (React + Tailwind), fidèles à la maquette Stitch |
| Serveur | `src/server/` | Commandes, paiement Stripe, webhook, téléchargements sécurisés, e-mails (en ligne : fonction Vercel `api/index.mjs`) |
| Générateurs | `generation/` | Fabrication des jeux et des PDF en Python, avec contrôles automatiques |

👉 Ce qui fonctionne déjà et ce qui reste à brancher : **[docs/ETAT-DES-FONCTIONNALITES.md](docs/ETAT-DES-FONCTIONNALITES.md)**.
👉 Mettre le site en ligne (GitHub + Vercel + Turso + Gmail) : **[docs/MISE-EN-PRODUCTION.md](docs/MISE-EN-PRODUCTION.md)**.

---

## 1. Installation (une seule fois)

Il faut **Node.js 22.13 ou plus récent** et **Python 3.11 ou plus récent**.

```bash
npm install                                   # dépendances du site et du serveur
pip install -r generation/requirements.txt    # dépendances des générateurs PDF
cp .env.example .env                          # puis ouvrez .env et suivez les commentaires
```

Pour tester en local, laissez `PAIEMENT_MODE=simulation` dans `.env` : aucun compte Stripe n'est nécessaire et aucun argent n'est en jeu.

## 2. Lancer le site en local

```bash
npm run dev
```

Ouvrez **http://localhost:5173**. Le serveur tourne en parallèle sur le port 8787.

Un bandeau noir en haut du site rappelle le mode de paiement actif (simulation, test Stripe ou non configuré). Il disparaît uniquement en production avec une clé Stripe réelle.

En local, les commandes sont enregistrées dans le fichier `data/boutique.sqlite` (aucun compte nécessaire). En ligne, elles sont enregistrées dans la base Turso.

## 3. Fabriquer les PDF

```bash
npm run generer -- --tous          # les 5 produits + les activités gratuites
npm run generer -- --produit mes-premiers-nonogrammes
python3 -m pytest generation/tests -q
```

Chaque fabrication contrôle les jeux et le PDF (format A4, marges, pages vides, solutions), écrit un rapport dans `generation/output/<produit>/rapport_qualite.json` et range les fichiers payants dans `storage/` (dossier **privé**, jamais servi directement). Détails : [generation/README.md](generation/README.md).

## 4. Publier un produit (relecture humaine obligatoire)

Un produit fabriqué passe au statut `en_verification` : il est visible sur le site comme « Bientôt disponible » mais **ne peut pas être acheté**. Après avoir relu entièrement le PDF :

```bash
npm run catalogue -- liste
npm run catalogue -- publier labyrinthes-petits-explorateurs --relu-par "Votre prénom"
npm run catalogue -- prix defis-de-la-logique 4.90
npm run catalogue -- depublier mission-dinosaures
```

Le coffret ne peut être publié qu'une fois tous ses produits publiés. En local, le serveur relit le catalogue automatiquement, sans redémarrage.

**Pour que la publication arrive sur le site en ligne**, enregistrez la modification dans GitHub (dans GitHub Desktop : « Commit to main » puis « Push origin », ou en ligne de commande `git commit -am "Publication" && git push`). Vercel remet le site en ligne tout seul en une à deux minutes.

## 5. Tester un achat complet (simulation)

1. Publiez au moins un produit (étape 4).
2. Ajoutez-le au panier, indiquez un e-mail, cochez les deux cases, cliquez sur « Commander et payer ».
3. La page « Simulateur de paiement » remplace Stripe : choisissez « réussi » ou « échec ».
4. La page de commande affiche les boutons de téléchargement. L'e-mail de confirmation est écrit dans `data/boite-envoi/`.

**Démonstration rapide sans rien publier** : `npm run build` puis `npm run demo`, et ouvrez http://localhost:8787. Une copie du catalogue où tout est affiché comme publié est utilisée (le vrai catalogue n'est pas modifié), avec paiement simulé.

Pour tester avec le vrai Stripe en mode test : [docs/CONFIGURATION-SERVICES.md](docs/CONFIGURATION-SERVICES.md).

## 6. Tests

```bash
npm test                              # 41 tests du serveur : prix, webhook signé, accès aux fichiers, assistant…
npm run typecheck                     # vérification TypeScript
python3 -m pytest generation/tests -q # 112 tests des générateurs

# Parcours d'achat complet dans un vrai navigateur (mobile + ordinateur) :
npx playwright install chromium       # une seule fois
npm run build && npm run demo         # dans un premier terminal
npm run test:e2e                      # dans un second terminal
```

## 7. Mise en production

Le site est hébergé sur **Vercel** (le code vient d'un dépôt GitHub **privé**), les commandes sont stockées dans **Turso** et les e-mails partent de la boîte **Gmail** de l'atelier.

Pas à pas : [docs/MISE-EN-PRODUCTION.md](docs/MISE-EN-PRODUCTION.md). Réglages de chaque service : [docs/CONFIGURATION-SERVICES.md](docs/CONFIGURATION-SERVICES.md).

## Autres commandes utiles

| Commande | Rôle |
|---|---|
| `npm run build` puis `npm start` | Compile le site, puis lance le serveur qui sert le site et l'API sur un seul port (hébergement hors Vercel) |
| `npm run vercel-build` | Ce que Vercel exécute à chaque mise en ligne : compile le site et regroupe le serveur dans `build-serveur/` |
| `npm run commandes -- liste` | Liste des commandes (`--statut payee` pour filtrer). Avec `TURSO_DATABASE_URL` et `TURSO_AUTH_TOKEN` dans `.env`, lit la base en ligne |
| `npm run commandes -- voir PAD-XXXX-XXXX` | Détail d'une commande et de ses téléchargements |
| `npm run icones` | Recalcule la police d'icônes après l'ajout d'une icône dans le code |

## Organisation des fichiers

```
catalogue/catalogue.json   catalogue partagé (prix en centimes, statuts, fichiers)
config/boutique.json       informations légales et de contact (champs « À COMPLÉTER »)
src/client/                site React (pages/, components/, lib/)
src/server/                serveur Express (boutique.ts = logique métier, app.ts = routes, vercel.ts = entrée Vercel)
api/index.mjs              fonction Vercel (reçoit toutes les adresses /api/*)
vercel.json                réglages Vercel (compilation, redirections, fichiers embarqués)
src/shared/                types et fonctions communs au site et au serveur
generation/                générateurs Python, assemblage PDF, contrôles qualité, tests
public/                    images, aperçus des PDF, activités gratuites (publics)
storage/                   PDF payants : versionnés dans le dépôt GitHub, qui doit donc rester PRIVÉ ; jamais servis directement
data/                      base locale des commandes et boîte d'envoi de test (non versionné)
tests/                     tests automatiques du serveur
docs/                      documentation
```
