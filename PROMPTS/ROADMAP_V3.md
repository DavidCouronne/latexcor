Tu as analysé le codebase et généré les rapports d'audit. Produis maintenant le document `IMPLEMENTATION_ROADMAP.md`. 

Pour que ce document soit exploitable par une équipe de développement, applique une approche de gestion des risques ultra-pragmatique.

Règles d'estimations (Loi de Hofstadter) :
- Sois pessimiste. Un refactoring d'architecture (ex: extraire un moteur de compilation) demande l'écriture de nouveaux tests d'intégration et de la documentation. Compte cela en "Jours-Homme" (8h/jour) et non en heures isolées.
- Complexité Basse = < 0.5 jour | Moyenne = 1-3 jours | Haute = 5 jours et plus.

Structure obligatoire du document :

1. Résumé Exécutif
- Effort total cumulé (en Jours-Homme) et niveau de confiance de l'estimation.
- Risque global de la refondule (Faible/Modéré/Critique).

2. Quick Wins (Tableau)
- Uniquement des actions à forte valeur demandant moins de 4 heures de travail (Ex: flags CLI, diagnostics au démarrage).

3. Évaluation Détaillée par Finding
Tableau avec les colonnes suivantes : ID | Finding | Effort (JH) | Complexité (Basse/Moyenne/Haute) | Risque de Régression (1-5) | Stratégie d'implémentation (Comment modifier le code sans effets de bord).

4. Matrice Effort vs Valeur (Quadrant Markdown ou Liste catégorisée)

5. Plan Phasé de Transition (Maximum 4 phases)
- Chaque phase doit se terminer par un livrable testable et exécutable.
- Précise la stratégie de non-régression pour chaque phase (ex: "La phase 1 ne doit casser aucun test d'intégration existant").

6. Risques Majeurs d'Implémentation & Plans de Contingence
- Pour chaque risque majeur identifié (ex: deadlocks avec Watchdog/AsyncIO, permissions de volumes), fournis une solution de repli (Plan B) si l'implémentation cible échoue.

7. Recommandations d'Ingénierie
- Stratégie de branching (ex: branches de feature vs refactoring).
- Politique de versioning (SemVer) : identifie précisément quelles modifications vont déclencher une rupture de compatibilité (Major bump 1.0.0).

Sois d'une rigueur technique absolue. Évite le jargon managérial, concentre-toi sur la technique.