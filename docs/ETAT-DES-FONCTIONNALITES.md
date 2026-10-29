# État des fonctionnalités

Légende : ✅ opérationnel et testé · 🔌 prêt, mais à brancher sur un service ou un compte externe · ✍️ à compléter par vous · 🔜 non réalisé

## Journal

- **29/10/2026** : thème « Fêtes & saisons » retiré. Coffret recomposé : 3 packs de grilles + Grand cahier (valeur 21,60 €), prix **11,90 €**, couverture « 4 produits en 1 ».
- **29/10/2026** : **Mission espace, Mission pirates et Mission magie générées** (46 pages chacune, 36 étapes d'histoire, 46 jeux vérifiés, version économie d'encre, QA OK). Statut `en_verification` : relecture humaine puis publication à faire. Couvertures du site encore provisoires.
- **29/10/2026** : site adapté à **Vercel + Turso** (base de commandes en ligne), e-mails via le Gmail dédié, **newsletter retirée**, **assistant FAQ** (sans IA) sur la page Contact, pages légales mises à jour (entrepreneur individuel, hébergeur Vercel, illustrations IA).

- **29/10/2026** : couvertures finales des 3 Missions (générées avec ChatGPT). Histoires réécrites : Mission espace = Filou le renard astronaute + Bip le robot ; Mission magie = Lila la princesse + Flamme le dragon. Les 8 produits et le coffret sont publiés (relus par Thylia Brouillard) ; espace et magie à relire après réécriture.

## Décisions de mise en ligne

- Hébergement : Vercel via un dépôt GitHub **privé** (les PDF payants sont dans le dépôt). Adresse : `petit-atelier-des-jeux.vercel.app`.
- ⚠️ L'offre gratuite Vercel (Hobby) est réservée à un usage non commercial : passer en **Pro** avant d'activer les vrais paiements.
- Base des commandes : Turso (compte à créer). Publier un produit = `npm run catalogue -- publier <id> --relu-par "Prénom"` puis commit + push.
- E-mails : `contact.petitatelierdesjeux@gmail.com` (SMTP Gmail, mot de passe d'application).
- Statut : micro-entreprise à créer ; nom commercial « Petit Atelier des Jeux » ; adresse personnelle + numéro de téléphone secondaire ; TVA « non applicable, art. 293 B du CGI » (à confirmer) ; médiateur à choisir.

## Site

| Fonctionnalité | État | Remarque |
|---|---|---|
| Pages Accueil, Boutique, Fiche produit, Panier, Commande | ✅ | Responsive, vérifié par captures |
| Activités gratuites (4 PDF réels) | ✅ | — |
| À propos, FAQ, Contact (+ assistant FAQ), Mes téléchargements | ✅ | — |
| Mentions légales, CGV, Confidentialité, Cookies | ✍️ | Identité, SIRET, adresse, téléphone, médiateur à compléter ; à faire relire |
| Recherche, filtres, tri | ✅ | Univers : animaux, dinosaures, espace, pirates, magie |
| Catalogue piloté par `catalogue.json` | ✅ | — |
| Produits non publiés « Bientôt disponible », non achetables | ✅ | — |

## Commandes et paiement

| Fonctionnalité | État | Remarque |
|---|---|---|
| Prix recalculés côté serveur, consentements horodatés, idempotence | ✅ | Testé |
| Stripe Checkout + webhook signé | 🔌 | Compte en mode test ; clés à saisir dans Vercel (`NODEJS_HELPERS=0` obligatoire) |
| Base des commandes Turso | 🔌 | Compte Turso à créer |
| Factures | 🔜 | Via Stripe ou un logiciel comptable |

## Téléchargements et e-mails

| Fonctionnalité | État | Remarque |
|---|---|---|
| Liens signés, temporaires, achat revérifié | ✅ | Testé |
| Renouvellement des liens par e-mail | ✅ | Testé |
| Envoi réel des e-mails | 🔌 | Gmail dédié + mot de passe d'application à saisir dans Vercel |

## Produits

| Produit | Contenu | Prix | Statut |
|---|---|---|---|
| Les labyrinthes des petits explorateurs | 30 labyrinthes + corrigés séparés | 3,90 € | relu, à publier |
| Les défis de la logique | 30 activités | 4,90 € | relu, à publier |
| Mes premiers nonogrammes | 40 grilles | 4,90 € | relu, à publier |
| Mon grand cahier d'activités | 40 pages + économie d'encre | 7,90 € | relu, à publier |
| Mission dinosaures | 46 pages + économie d'encre | 9,90 € | relu, à publier |
| Mission espace | 46 pages + économie d'encre | 9,90 € | en vérification (relecture à faire) |
| Mission pirates | 46 pages + économie d'encre | 9,90 € | en vérification (relecture à faire) |
| Mission magie | 46 pages + économie d'encre | 9,90 € | en vérification (relecture à faire) |
| Le grand coffret | Labyrinthes + Logique + Nonogrammes + Grand cahier | 11,90 € | publiable après ses 4 produits |

- ✅ 142 tests Python, 41 tests du site, parcours d'achat de bout en bout (46 contrôles).
