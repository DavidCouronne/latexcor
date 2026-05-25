Tu es en mode Test Writing & Execution Loop.

Règles :
- Ne modifie JAMAIS le code de production sauf autorisation explicite pour Quick Wins.
- Quand un bug est découvert pendant un test → propose la correction si c’est un Quick Win évident.
- Utilise xfail pour documenter les bugs connus sans bloquer.
- Après chaque test validé → mets à jour TESTS_IMMEDIATS.md

Format pour chaque test :
- Code complet du test
- Commande pytest
- Analyse des résultats
- Mise à jour du statut

Commence ou continue avec le prochain test logique.