# Accroche IA (facultative, désactivée)

La génération des produits **n'utilise aucune IA** : labyrinthes, nonogrammes, logique,
observation et énigmes sont produits par des algorithmes avec graine fixe, puis vérifiés
par programme. Aucune API payante n'est appelée.

Ce module montre seulement **où** une IA pourrait aider un humain, en amont :

- proposer des idées de thèmes (ex. « la mer », « la ferme ») et de missions de labyrinthe ;
- reformuler des consignes ou des étapes d'histoire pour les 6-8 ans ;
- rédiger un premier jet de description de produit pour la boutique.

Règles :

1. Désactivé par défaut. Activation explicite : `PAD_IA_ACTIVE=1` **et** `ANTHROPIC_API_KEY`
   dans l'environnement (jamais dans le dépôt).
2. Les propositions sont relues par un humain puis copiées à la main dans
   `generation/templates/*.json`. Rien n'est injecté automatiquement dans un PDF.
3. Aucune activité (solution, grille, différence…) n'est produite par l'IA : tout ce qui
   doit être juste reste calculé et vérifié par le code.

```python
from generation.ia import proposer
print(proposer("Propose 5 missions de labyrinthe sur le thème de la mer, une phrase simple chacune."))
# → None tant que l'accroche n'est pas activée
```
