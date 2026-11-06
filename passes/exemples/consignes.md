# Passe « anglais et traduction des exemples » — consignes du réviseur et du vérificateur

Base VocabEN : vocabulaire anglais pour lire The Economist et des blogs d'idées. Chaque ligne a un Mot, une Traduction (équivalents français séparés par des virgules, nuances entre parenthèses) et 2 à 5 exemples. Chaque exemple a une phrase anglaise (EN), un « mot à trouver » (la partie de la phrase que l'apprenant doit retrouver) et une traduction française (FR).

## Ce qu'il faut corriger (et seulement cela)
1. **Anglais fautif ou peu naturel** : faute d'accord, de temps, d'article ou de préposition ; tournure impropre ou qu'un locuteur natif instruit n'écrirait pas (*It would be mistaken to think* → *It would be a mistake to think* ; *He was puzzled over the meaning* → *puzzled about*) ; phrase maladroite ou scolaire (*Finding a parking spot is not likely on weekends*). Corriger au plus près, ou remplacer la phrase par une phrase naturelle de niveau presse si elle est irrécupérable. L'anglais britannique et l'américain sont acceptés tous les deux.
2. **Traduction française de l'exemple** :
   - contresens ou faux sens (*manufacturers are bound to play down* ≠ « sont tenus de minimiser » ; c'est « ne manqueront pas de ») ;
   - calque ou français non idiomatique (« prospérer sur la défiance » → « se nourrir de la défiance » ; « subir des coûts » → « engager des coûts » ; un rythme n'est pas « éblouissant » mais « fulgurant ») ;
   - terme technique inexact (économie, droit, finance : prendre ferme, déposer le bilan, engager des frais) ;
   - omission ou ajout de sens notable ; lourdeur nette (« un congé pour décès après le décès de son père ») ;
   - unités anglo-saxonnes non converties (40 yards → « moins de 40 mètres »).
3. **Concordance avec la Traduction de la ligne** : la traduction de l'exemple reprend un équivalent de la Traduction quand c'est naturel. Si un bon équivalent de la Traduction n'est illustré par aucun exemple, adapter la traduction d'un exemple. Si l'exemple traduit le mot par un équivalent meilleur et absent de la Traduction, proposer d'ajouter cet équivalent à la Traduction (champ "T"), sans dépasser 3 ou 4 équivalents.
4. **Connotation et registre** concordants entre le mot, sa traduction et l'exemple.
5. **Exemple qui n'illustre pas le sens de sa ligne** (autre sens du mot) : le remplacer par un exemple du bon sens.

## Ce qu'il ne faut PAS faire
- Ne pas réécrire une phrase correcte pour des raisons de goût ; ne pas « améliorer » une traduction juste. En cas de doute, ne rien changer.
- Attention aux fausses fautes : une hypothèse se traduit à l'imparfait (« even if they wanted to » → « même s'ils le voulaient », correct même après un présent).
- Ne pas toucher au Mot, aux synonymes, à l'ordre des lignes.
- Ne jamais supprimer d'exemple.
- Le mot à trouver doit rester présent tel quel dans la phrase, une seule fois, en mots entiers ; si la phrase change, l'adapter (forme conjuguée exacte, sans article ni mot hors du Mot, avec la particule ou préposition finale quand elle suit directement le verbe).
- Les mots à trouver (casse) et les espaces insécables ont déjà été corrigés automatiquement dans toute la base (6 novembre) : inutile de les signaler ; veiller seulement à les respecter dans les phrases que l'on réécrit.
- Typographie française : espaces insécables avant « : ; ? ! » et à l'intérieur des guillemets « », apostrophe typographique ou droite comme dans le reste de la phrase.

## Format de sortie (réviseur)
Une liste JSON, rien d'autre. Un élément par correction :
`{"id": "r12", "ex": 2, "en": "...", "mot": "...", "fr": "...", "motif": "catégorie : explication courte"}`
— ne mettre que les champs modifiés parmi en / mot / fr ; `ex` est le numéro de l'exemple (1 à 5).
Pour la Traduction de la ligne : `{"id": "r12", "T": "nouvelle Traduction complète", "motif": "..."}`.
Catégories de motif : `anglais`, `contresens`, `calque`, `terme`, `omission`, `concordance`, `registre`, `sens`, `unité`.

## Vérificateur
Il reçoit les lignes d'origine et la liste du réviseur. Pour chaque correction : la garder, l'amender ou l'écarter (correction de goût, nouvelle erreur, mot à trouver cassé, traduction moins juste). Il peut ajouter une correction manifeste oubliée, mais n'en cherche pas activement. Il rend la liste finale au même format, puis une ligne de bilan sur la sortie d'erreur ou après la liste, séparée par une ligne `---`.
