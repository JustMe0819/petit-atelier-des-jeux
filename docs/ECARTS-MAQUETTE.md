# Écarts volontaires par rapport à la maquette Stitch

La maquette reste la référence visuelle : mêmes jetons de couleur, même typographie (Plus Jakarta Sans pour les titres, Nunito Sans pour le texte), mêmes icônes, cartes arrondies, mise en page des pages ordinateur et mobile, cartes pastel de la planche produits. Voici les seules différences, et leur raison.

| Élément de la maquette | Ce qui a été fait | Raison |
|---|---|---|
| Fond lavande `#fbf8ff` | Fond crème `#FFF9F0` ; surfaces chaudes, rose poudré ajouté | Palette de référence demandée et planche produits |
| Images hébergées chez Google (`lh3.googleusercontent.com`) | Couvertures et mascottes découpées dans la planche produits, puis hébergées sur le site | Les liens Google peuvent disparaître et sont inaccessibles depuis le serveur |
| Photos d'ambiance (bureau, crayons) | Composition avec les couvertures de la planche | Images d'origine indisponibles ; aucune image générique ajoutée |
| Aperçus intérieurs illustratifs | Vraies pages des PDF générés | Exigence « aperçus conformes au PDF réel » |
| Avis (« 4,9/5, 142 avis »), « +1 200 parents », « 12 000 familles », « Best-seller », « Top vente », « Populaire » | Supprimés | Aucun avis ni aucune vente réels à ce jour |
| Prix barrés, « -40 % », code ATELIER10 | Supprimés ; le coffret affiche la valeur réelle des produits achetés séparément | Pas de fausse promotion ; les vrais codes promo passent par Stripe |
| « Développé avec des instituteurs », « testé par des enfants », « réponse sous 2 h / 24 h », « support 7j/7 », « satisfaction garantie » | Supprimés ou remplacés par des faits vérifiables | Affirmations invérifiables |
| « 1 jeu offert chaque mois » (newsletter) | « Être prévenu des nouveautés », double confirmation | Ne rien promettre qui n'est pas organisé |
| Faux formulaire de carte bancaire et bouton « Apple Pay / G Pay » dans le panier | Redirection vers Stripe Checkout | Sécurité : la carte n'est jamais saisie sur le site |
| « Acheter en 1 clic » | « Acheter maintenant » (ajoute au panier puis ouvre le panier) | L'e-mail et les consentements sont obligatoires avant le paiement |
| Sélecteur de quantité | Quantité fixée à 1 | Un fichier numérique n'a pas besoin d'être acheté deux fois ; l'impression est illimitée dans le foyer |
| Bouton « Valider et télécharger mes jeux » | « Commander et payer X € » | Le libellé doit indiquer clairement l'obligation de paiement |
| Avatar « compte client » | Retiré | Pas de compte : l'accès se fait par lien sécurisé et renouvelable |
| Adresse e-mail `bonjour@petitatelierdesjeux.fr` | Champ à compléter | Coordonnées non inventées |
| Polices et icônes chargées depuis Google Fonts | Hébergées sur le site ; police d'icônes réduite de 4 Mo à 15 Ko | Vie privée (pas de transfert d'adresses IP à Google) et rapidité |
| Mascottes de la maquette sous forme d'icônes génériques | Renard de la planche utilisé comme logo, dino et renard en pied de page | Reprise des illustrations existantes |
