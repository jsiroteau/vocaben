# Passe « mots confus » (colonne Confus)

Règle : voir docs/VocabEN_conventions.md, « Mots confus ».

1. `python3 tools/passe_confus.py candidats` → candidats.json (candidats par ligne et leur source).
2. `python3 tools/passe_confus.py pilote 100` → pilote.json (lignes tirées, graine fixe).
3. `python3 tools/passe_confus.py show pilote.json 0 25` : lire chaque ligne, ses exemples et ses candidats ; ne garder
   qu'un candidat faux dans tous les exemples et tentant ; chercher aussi dans la base des mots confus non proposés.
4. Décisions dans decisions_<lot>.json ({clé de ligne: [Mots]}, liste vide = aucun), puis
   `python3 tools/passe_confus.py apply decisions_<lot>.json` (contrôle que chaque Mot existe).

Pilote du 21 novembre 2026 : decisions_pilote.json. Sources utiles : traductions communes (pièges du français),
paronymes, autre sens d'un mot de la ligne. Sources peu utiles : « même fiche » (familles), chaînes de synonymes
(conviennent presque toujours dans un exemple).
