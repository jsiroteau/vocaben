# Seconde passe formes admises : changement de registre (15 novembre 2026)

Décision de Jennifer : un synonyme de la ligne est admis au texte à trous dès que la phrase reste de l'anglais idiomatique avec lui et garde le même sens, même si le registre change (plus soutenu, plus familier, littéraire, vieilli). La première passe refusait ces cas : on réexamine donc les refus, et on ne fait qu'ajouter des formes admises.

11 lots d'environ 600 exemples (lignes où un exemple au moins n'admet pas tous les synonymes), 2 lots par exécution, une seule exécution à la fois.

## Procédure d'une exécution
1. Cloner le dépôt (accès en écriture), se placer à sa racine, lire ce fichier en entier.
2. `python3 tools/passe_admis.py next2 2` réserve deux lots et affiche leurs numéros : commit et push immédiats de `etat2.json`. EN COURS : une autre exécution travaille, s'arrêter sans rien modifier. TERMINÉ : s'arrêter (message de fin dans la consigne de la tâche).
3. Pour chaque lot : `python3 tools/passe_admis.py show2 <n>` l'affiche (lignes L0, L1…, exemples 0-4, formes déjà admises). Un agent réviseur puis un agent vérificateur indépendant par lot (les deux lots en parallèle) proposent les formes à ajouter ; contrôler soi-même la liste finale.
4. Décisions dans `passes/admis/decisions/reg<nn>.json`, au format `{"L3": {"0": "elapsed", "2": "bestowed / conferred"}}` : seulement les formes nouvelles. Puis, un lot après l'autre : `python3 tools/passe_admis.py add <n> passes/admis/decisions/reg<nn>.json` (ajoute sans rien retirer, marque le lot fait).
5. `python3 tools/vocab.py lint` sans avertissement, `git pull --rebase`, commit (message : lots, nombre de formes ajoutées, 3 ou 4 exemples), push.

## Consignes de jugement
- Pour chaque exemple, examiner chaque synonyme de la ligne (colonne syn, marques entre parenthèses ignorées) qui n'est pas déjà admis.
- Admettre si, une fois le mot à trouver remplacé par la forme proposée, la phrase est de l'anglais idiomatique, qu'un locuteur natif pourrait écrire, et dit la même chose. Un écart de registre ou de ton ne fait plus obstacle (went by → elapsed dans un texte soutenu ; money → dough dans une phrase familière ou neutre).
- Refuser encore : sens différent ou partiel dans cette phrase ; collocation non idiomatique (on ne dit pas « a sheer hill », « possess a car » pour une simple voiture reste admissible mais « prolong a deadline » non) ; construction grammaticale qui ne passe pas (préposition, complément intercalé, transitif / intransitif) ; expression figée ou nom composé (a safe bet, the oil lobby) ; mélange GB / US dans une ligne marquée d'une variété ; phrase qui deviendrait bizarre ou comique. Dans le doute, ne pas admettre.
- Forme exacte qui remplace le mot à trouver : fléchie comme dans la phrase, avec la préposition ou la particule si le mot à trouver l'inclut, majuscule si la phrase commence par lui ; plusieurs formes séparées par « / ».
- Ne rien modifier d'autre : ni Synonymes, ni Traductions, ni exemples ; pas de signalements dans cette passe.
