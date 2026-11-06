# Passe « anglais et traduction des exemples » — procédure d'une exécution

Lancée le 6 novembre 2026. 40 lots (≈ 400 exemples chacun, fiches dans l'ordre de la base), 2 lots par exécution (davantage en régime intensif) ; plusieurs exécutions peuvent tourner en même temps grâce aux réservations.
État : `etat.json` (lots faits, nombre de corrections). Consignes : `consignes.md`.

## Une exécution
1. `git clone https://github.com/jsiroteau/vocaben` (dépôt avec accès en écriture), se placer à sa racine.
2. `python3 tools/passe_exemples.py next N` (N = nombre de lots demandé par la tâche, 2 par défaut) → réserve et affiche les lots à traiter. **Committer et pousser aussitôt** `passes/exemples/etat.json` (« Passe exemples : réservation des lots … ») pour que les autres exécutions ne les prennent pas ; en cas de conflit au push, `git pull --rebase`, refaire `next` si besoin. Si la sortie est `TERMINÉ` ou `RIEN`, ne rien faire d'autre que le signaler. Une réservation non suivie d'application expire au bout de 6 heures.
3. Pour chaque lot k : `python3 tools/passe_exemples.py export k` (fichiers dans `passes/exemples/work/`, non versionnés).
4. Pour chaque lot, en parallèle : un agent **réviseur** (lit `consignes.md` et `work/lot_kk.txt`, écrit `work/lot_kk_rev.json`), puis un agent **vérificateur** indépendant (lit `consignes.md`, `work/lot_kk.txt` et `work/lot_kk_rev.json`, écrit `work/lot_kk_final.json`).
5. Contrôler soi-même la liste finale (JSON valide ; pas de correction de goût évidente ; espaces insécables), puis `python3 tools/passe_exemples.py apply k work/lot_kk_final.json`.
6. `python3 tools/vocab.py lint` (traiter les avertissements éventuels).
7. `git pull --rebase` (d'autres exécutions ont pu publier entre-temps ; en cas de conflit sur vocab.xlsx, repartir de origin/main et réappliquer les listes finales avec `apply`), puis commit (vocab.xlsx, passes/exemples/etat.json) sur main : « Passe exemples : lots k et k+1 », avec le nombre de corrections par catégorie et 3 ou 4 exemples marquants ; push.
8. Compte rendu court à Jennifer (5 lignes) : lots faits, corrections, exemples marquants, lots restants.
