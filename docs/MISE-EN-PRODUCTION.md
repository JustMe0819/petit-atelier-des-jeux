# Mise en production — pas à pas

Le site est mis en ligne avec quatre services :

| Service | Rôle | Compte |
|---|---|---|
| **GitHub** | garde le code, les PDF et le catalogue (dépôt **privé**) | gratuit |
| **Vercel** | héberge le site et le serveur, le remet en ligne à chaque modification | ⚠️ voir l'encadré ci-dessous |
| **Turso** | base de données des commandes | gratuit pour démarrer |
| **Gmail** (contact.petitatelierdesjeux@gmail.com) | envoie les e-mails de commande, reçoit le formulaire de contact | gratuit |
| **Stripe** | paiement | commission par vente |

> ⚠️ **Vercel et l'usage commercial.** L'offre gratuite de Vercel (« Hobby ») est réservée à un usage **personnel et non commercial** : un site qui encaisse des paiements doit passer à l'offre **Pro** (payante, par mois). Vous pouvez tout préparer et tester avec l'offre gratuite, mais passez en Pro avant d'activer les vrais paiements. Source : [Fair Use Guidelines de Vercel](https://vercel.com/docs/limits/fair-use-guidelines#commercial-usage).

## Avant d'ouvrir la boutique

- [ ] **Micro-entreprise créée** (guichet unique de l'INPI : gratuit, en ligne) et numéro SIRET reçu.
- [ ] `config/boutique.json` complété : nom et prénom, adresse, SIRET, immatriculation, téléphone (un numéro secondaire suffit), médiateur. Tant qu'un champ commence par « À COMPLÉTER », le site l'affiche surligné en rose.
- [ ] **Mention de TVA confirmée** : « TVA non applicable, art. 293 B du CGI » n'est valable qu'en franchise en base de TVA. Dans Stripe, ne faites pas collecter de TVA dans ce cas.
- [ ] **Médiateur de la consommation** choisi (obligatoire pour vendre à des particuliers).
- [ ] CGV, mentions légales, confidentialité et cookies **relues** (ce sont des modèles, voir `src/client/pages/Legal.tsx`).
- [ ] Chaque PDF relu, puis publié avec `npm run catalogue -- publier <id> --relu-par "Prénom"`.
- [ ] Un achat de test fait en ligne avec la carte de test Stripe `4242 4242 4242 4242`, puis un vrai achat avec une vraie carte, remboursé depuis Stripe.

## Étape 1 — Mettre le code sur GitHub (dépôt privé)

1. Installez **GitHub Desktop** et connectez-vous.
2. *File → Add local repository…* → choisissez le dossier `petit-atelier-des-jeux`. Si on vous propose d'en faire un dépôt (« create a repository »), acceptez.
3. Vérifiez que les fichiers `.env` et le dossier `data/` n'apparaissent **pas** dans la liste (ils sont exclus par `.gitignore`). Les PDF du dossier `storage/` apparaissent : c'est normal, Vercel en a besoin.
4. *Commit to main*, puis *Publish repository* en laissant **« Keep this code private » coché**. ⚠️ Le dépôt doit rester **privé** : il contient les PDF payants.

## Étape 2 — Créer la base Turso

1. Créez un compte sur [turso.tech](https://turso.tech) et créez une base (choisissez une région en Europe).
2. Notez son adresse (elle commence par `libsql://`) : c'est `TURSO_DATABASE_URL`.
3. Créez un jeton d'accès pour cette base (bouton « Create token » ou « Generate token ») : c'est `TURSO_AUTH_TOKEN`. Copiez-le tout de suite, il ne sera plus affiché.

Les tables sont créées automatiquement au premier démarrage du site.

## Étape 3 — Préparer Gmail

1. Sur le compte contact.petitatelierdesjeux@gmail.com, activez la **validation en deux étapes** (Compte Google → Sécurité).
2. Créez un **mot de passe d'application** (Compte Google → Sécurité → Mots de passe des applications, ou cherchez « mots de passe des applications »). Nommez-le « Site ». Google affiche 16 lettres : c'est `SMTP_PASS`.

Limite : Gmail envoie quelques centaines d'e-mails par jour, largement assez pour démarrer.

## Étape 4 — Créer le projet Vercel

1. Sur [vercel.com](https://vercel.com) : *Add New… → Project* → importez le dépôt GitHub `petit-atelier-des-jeux`.
2. Nom du projet : `petit-atelier-des-jeux` (l'adresse sera `petit-atelier-des-jeux.vercel.app`). Ne changez rien d'autre : les réglages sont dans `vercel.json`.
3. Avant de cliquer sur *Deploy*, ouvrez **Environment Variables** et ajoutez les variables ci-dessous (vous pourrez les modifier ensuite dans *Settings → Environment Variables* ; après une modification, refaites un déploiement : *Deployments → … → Redeploy*).

| Variable | Valeur |
|---|---|
| `NODE_ENV` | `production` |
| `URL_PUBLIQUE` | `https://petit-atelier-des-jeux.vercel.app` |
| `SECRET_LIENS` | 64 caractères aléatoires (commande dans `.env.example`) |
| `NODEJS_HELPERS` | `0` (**indispensable** pour que Stripe puisse confirmer les paiements) |
| `TURSO_DATABASE_URL` | adresse `libsql://…` (étape 2) |
| `TURSO_AUTH_TOKEN` | jeton Turso (étape 2) |
| `PAIEMENT_MODE` | `stripe` |
| `STRIPE_SECRET_KEY` | `sk_test_…` pour commencer, `sk_live_…` à l'ouverture |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` (étape 5) |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `contact.petitatelierdesjeux@gmail.com` |
| `SMTP_PASS` | mot de passe d'application Gmail (étape 3) |
| `EMAIL_EXPEDITEUR` | `Petit Atelier des Jeux <contact.petitatelierdesjeux@gmail.com>` |
| `EMAIL_BOUTIQUE` | `contact.petitatelierdesjeux@gmail.com` |

4. Cliquez sur *Deploy*. Au bout d'une à deux minutes, le site est en ligne.

Si une variable obligatoire manque, le site s'affiche mais les commandes répondent « boutique momentanément indisponible » : le message exact apparaît dans Vercel, *Logs*.

## Étape 5 — Brancher Stripe

Voir [CONFIGURATION-SERVICES.md](CONFIGURATION-SERVICES.md#1-stripe-paiement) : créer le webhook vers `https://petit-atelier-des-jeux.vercel.app/api/paiement/webhook`, copier son secret dans `STRIPE_WEBHOOK_SECRET`, puis redéployer.

## Au quotidien

**Publier ou modifier un produit**
1. Sur votre ordinateur : `npm run catalogue -- publier <id> --relu-par "Prénom"` (ou `prix`, `depublier`…).
2. Dans GitHub Desktop : *Commit to main*, puis *Push origin*.
3. Vercel remet le site à jour tout seul en une à deux minutes.

**Voir les commandes** : ajoutez `TURSO_DATABASE_URL` et `TURSO_AUTH_TOKEN` dans votre fichier `.env` local, puis `npm run commandes -- liste` (ou `liste --statut anomalie` pour les commandes à vérifier). Les paiements eux-mêmes se suivent dans le tableau de bord Stripe.

**Sauvegardes** : le code, les PDF et le catalogue sont sauvegardés par GitHub. Les commandes sont dans Turso ; exportez-les régulièrement (outil `turso db shell` ou tableau de bord Turso) : vous devez conserver les données comptables 10 ans.

## Ce qui est déjà en place

- Les prix sont recalculés côté serveur, les données envoyées sont validées, les formulaires et les paiements sont limités en nombre de demandes.
- Le webhook Stripe est vérifié par signature ; chaque événement n'est traité qu'une fois, même s'il arrive deux fois en même temps ; le montant payé est comparé au montant attendu.
- Une commande ne peut pas être créée en double (clé d'idempotence).
- Les PDF payants ne sont jamais servis directement : seulement par des liens signés et datés, avec vérification de l'achat à chaque téléchargement.
- Les jetons d'accès aux commandes ne sont stockés que sous forme d'empreinte.
- En-têtes de sécurité (CSP…), aucune ressource externe (polices et icônes hébergées sur le site).

**Limite connue** : sur Vercel, la limitation du nombre de demandes est comptée par instance du serveur ; elle freine les abus simples mais n'est pas un pare-feu. Si besoin, activez les règles de limitation du pare-feu Vercel (*Firewall*).

## Après l'ouverture

- Surveillez les commandes en « anomalie » : `npm run commandes -- liste --statut anomalie`.
- Dans Stripe, vérifiez que les webhooks sont bien délivrés (*Développeurs → Webhooks*).
- En cas de souci, les messages d'erreur du serveur sont dans Vercel, onglet *Logs*.
