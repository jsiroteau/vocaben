# Passe « sens mêlés et sens manquants » — procédure d'une exécution

Lancée le 6 novembre 2026. Mêmes 40 lots de fiches que la passe exemples (`passes/exemples/lots.json`). État : `etat.json`. Consignes : `consignes.md`. Outil : `tools/passe_sens.py` (format des opérations en tête du fichier).

1. `git clone https://github.com/jsiroteau/vocaben` (accès en écriture), se placer à sa racine.
2. `python3 tools/passe_sens.py next N` → réserve et affiche les lots ; **committer et pousser aussitôt** `passes/sens/etat.json`. Si la sortie est `TERMINÉ` ou `RIEN`, s'arrêter en le signalant.
3. Pour chaque lot k : `python3 tools/passe_sens.py export k` (fichiers dans `passes/sens/work/`, non versionnés).
4. Pour chaque lot, en parallèle : un agent **réviseur** (lit `consignes.md`, l'en-tête de `tools/passe_sens.py` et `work/lot_kk.txt` ; vérifie avec `python3 tools/vocab.py grep` qu'un sens ajouté n'existe pas déjà ailleurs ; écrit `work/lot_kk_rev.json`), puis un agent **vérificateur** indépendant (mêmes lectures + `work/lot_kk_rev.json` ; écrit `work/lot_kk_final.json`). Rappels à leur donner : nature dans "NAT" jamais dans "M" ; pas de virgule dans "M" (variantes séparées par « / ») ; ligne nouvelle au sens propre insérée avec "before".
5. Contrôler soi-même la liste finale (scissions justifiées par une traduction différente, ajouts rares et utiles, places), puis `python3 tools/passe_sens.py apply k work/lot_kk_final.json` — **une seule fois par lot** (l'outil refuse une seconde application).
6. `python3 tools/vocab.py lint` et traiter les avertissements.
7. `git pull --rebase`, commit (vocab.xlsx, passes/sens/etat.json) sur main avec la liste des scissions et des ajouts, push.
8. Compte rendu court à Jennifer (5 lignes).
