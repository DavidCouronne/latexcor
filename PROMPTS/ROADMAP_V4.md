Tu as analysé le codebase, traqué les failles, les bugs logiques ainsi que les dualismes de patterns (os/pathlib, pydantic/dataclasses, bilinguisme FR/EN). Produis maintenant le document `IMPLEMENTATION_ROADMAP.md` au format Markdown brut (sans blabla d'introduction ni de conclusion).

Pour que ce document soit exploitable par une équipe de développement, applique une approche de gestion des risques ultra-pragmatique.

Règles d'estimations (Loi de Hofstadter) :
- Sois pessimiste. Un chantier d'homogénéisation (ex: migrer tout un module de 'os' vers 'pathlib') ou un refactoring d'architecture demande la réécriture de tests unitaires/intégration et la mise à jour de la doc. Compte cela en "Jours-Homme" (JH, 8h/jour) et non en heures isolées.
- Complexité Basse = < 0.5 jour | Moyenne = 1-3 jours | Haute = 5 jours et plus.

Structure obligatoire du document :

1. Résumé Exécutif
- Effort total cumulé (en Jours-Homme) et niveau de confiance de l'estimation.
- Risque global de la refonte (Faible/Modéré/Critique).

2. Quick Wins (Tableau)
- Actions à forte valeur / faible risque demandant moins de 4 heures de travail (Ex: flags CLI, diagnostics au démarrage, uniformisation des docstrings FR/EN via un linter, script de renommage global).

3. Évaluation Détaillée par Finding & Dualisme
Tableau avec les colonnes suivantes : ID | Finding/Dualisme | Effort (JH) | Complexité (Basse/Moyenne/Haute) | Risque de Régression (1-5) | Stratégie d'implémentation (Comment basculer de pattern sans effets de bord, ex: stratégie de shadow-typing ou feature-flipping).

4. Matrice Effort vs Valeur (Liste catégorisée en 4 quadrants : High Value/Low Effort, High Value/High Effort, Low Value/Low Effort, Low Value/High Effort)

5. Plan Phasé de Transition (Maximum 4 phases)
- Priorise d'abord la Sécurité et les Quick Wins, puis l'Homogénéisation (Chantiers pivots), puis le Refactoring lourd.
- Chaque phase doit se terminer par un livrable testable et exécutable.
- Précise la stratégie de non-régression pour chaque phase (ex: "La phase 2 de bascule Pydantic ne doit impacter aucun schéma d'API externe et valider à 100% la suite de tests existante").

6. Risques Majeurs d'Implémentation & Plans de Contingence
- Pour chaque risque technique majeur (ex: deadlocks AsyncIO, rupture de compatibilité de typage avec Pydantic v2, erreurs de chemins OS inter-plateformes), fournis une solution de repli (Plan B).

7. Recommandations d'Ingénierie & Outillage
- Stratégie de branching (ex: branches de feature vs isolation des refactorings de style pour éviter les conflits de merge).
- Automatisation : Propose des outils spécifiques (ex: Ruff, Black, Sourcery) pour accélérer l'alignement des dualismes identifiés.
- Politique de versioning (SemVer) : identifie précisément quelles modifications (notamment dans la modélisation des données ou les signatures de fonctions) vont déclencher un Major bump (1.0.0).

Sois d'une rigueur technique absolue. Évite le jargon managérial, concentre-toi sur la technique pure et le code Python.