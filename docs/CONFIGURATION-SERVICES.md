# Configurer les services externes

En local, tous les réglages se font dans le fichier `.env` (copie de `.env.example`). En ligne, les mêmes variables se saisissent dans Vercel : *Settings → Environment Variables*, puis *Redeploy*. Ces valeurs sont des secrets : ne les mettez jamais sur GitHub ni dans un e-mail.

## 1. Stripe (paiement)

### Pourquoi Stripe Checkout ?
La page de paiement est hébergée par Stripe : le site ne voit jamais les numéros de carte. Le serveur :
1. crée la session de paiement avec les prix **recalculés à partir du catalogue** ;
2. attend le **webhook signé** de Stripe pour confirmer la commande ;
3. vérifie que le montant payé correspond au montant attendu, sinon la commande passe en « anomalie ».

### En ligne, en mode test (à faire en premier)
1. Dans Stripe, restez en **mode test** (interrupteur en haut à droite).
2. *Développeurs → Clés API* : copiez la clé secrète `sk_test_…` dans `STRIPE_SECRET_KEY` (Vercel).
3. *Développeurs → Webhooks → Ajouter un point de terminaison* :
   - URL : `https://petit-atelier-des-jeux.vercel.app/api/paiement/webhook`
   - Événements : `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `checkout.session.expired`
4. Copiez le **secret de signature** `whsec_…` dans `STRIPE_WEBHOOK_SECRET` (Vercel), vérifiez que `NODEJS_HELPERS=0` est bien présent, puis *Redeploy*.
5. Faites un achat avec la carte de test `4242 4242 4242 4242` (date future, code quelconque). Carte refusée : `4000 0000 0000 0002`. 3-D Secure : `4000 0027 6000 3184`.

> Sans `NODEJS_HELPERS=0`, Vercel lit le contenu de la requête avant le serveur : la signature Stripe ne peut plus être vérifiée et les paiements restent « en attente ». Le message « corps brut indisponible » apparaît alors dans les *Logs* Vercel.

### Mode réel (ouverture de la boutique)
1. Activez votre compte Stripe (identité, SIRET, IBAN).
2. Refaites l'étape 3 **en mode réel** : le webhook réel a son propre secret `whsec_…`.
3. Remplacez dans Vercel `STRIPE_SECRET_KEY` par `sk_live_…` et `STRIPE_WEBHOOK_SECRET` par le nouveau secret, puis *Redeploy*.

### TVA
Si vous êtes en franchise en base de TVA (cas courant d'une micro-entreprise qui démarre), vous ne facturez pas de TVA : la mention « TVA non applicable, art. 293 B du CGI » figure sur le site et **Stripe Tax ne doit pas ajouter de TVA**. Dans Stripe, *Paramètres → Taxes* : n'ajoutez aucune immatriculation fiscale tant que vous êtes en franchise. Faites confirmer votre situation par l'URSSAF ou un comptable.

### Sécurités intégrées
- une clé `sk_live_` est refusée hors production ;
- `PAIEMENT_MODE=simulation` est refusé en production ;
- sans `STRIPE_WEBHOOK_SECRET`, le serveur refuse de démarrer en mode Stripe.

### Codes promo (facultatif)
Créez des codes dans *Produits → Coupons* sur Stripe, puis mettez `STRIPE_CODES_PROMO=true`.

## 2. Base de données (Turso)

- En local, rien à faire : les commandes vont dans `data/boutique.sqlite`.
- En ligne, la base Turso est **obligatoire** (Vercel n'a pas de disque permanent) : variables `TURSO_DATABASE_URL` (`libsql://…`) et `TURSO_AUTH_TOKEN`. Les tables se créent seules au premier démarrage.
- Pour consulter les commandes en ligne depuis votre ordinateur, mettez ces deux variables dans votre `.env`, puis `npm run commandes -- liste`. Retirez-les ensuite pour retravailler sur la base locale.

## 3. E-mails (Gmail)

Le site envoie : la confirmation de commande (avec la preuve de votre accord pour l'accès immédiat), les nouveaux liens d'accès, et vous transfère les messages du formulaire de contact.

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=contact.petitatelierdesjeux@gmail.com
SMTP_PASS=xxxxxxxxxxxxxxxx        # mot de passe d'application (16 lettres, sans espaces)
EMAIL_EXPEDITEUR="Petit Atelier des Jeux <contact.petitatelierdesjeux@gmail.com>"
EMAIL_BOUTIQUE=contact.petitatelierdesjeux@gmail.com
```

- Le mot de passe d'application se crée dans le compte Google après avoir activé la validation en deux étapes. Ce n'est **pas** le mot de passe du compte.
- Le port 465 utilise une connexion chiffrée directe (le port 587 fonctionne aussi).
- L'adresse d'expédition doit être celle du compte Gmail, sinon Gmail la remplace.
- Sans SMTP en local, les e-mails sont écrits dans `data/boite-envoi/`. En ligne sans SMTP, ils ne partent pas (un avertissement apparaît dans les *Logs* Vercel).
- Le jour où vous aurez votre propre nom de domaine, un service comme Resend ou Brevo améliorera la délivrabilité : il suffira de changer ces variables.

## 4. Intelligence artificielle (facultatif, génération des PDF uniquement)

Les générateurs fonctionnent **sans IA payante**. Un point d'accroche désactivé par défaut existe dans `generation/ia/` ; il ne concerne que la machine qui fabrique les PDF, jamais le site. L'assistant de la page Contact n'utilise **aucune** IA : il compare les mots de la question à une liste de réponses (`src/client/components/AssistantFaq.tsx`).
