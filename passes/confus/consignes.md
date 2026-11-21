# Passe complète « mots confus » — consignes d'un lot

Objectif double (demande de Jennifer, 21 novembre 2026) : remplir la colonne Confus, et profiter de la relecture pour
perfectionner la base (elle signale encore chaque jour des corrections). Règles complètes : docs/VocabEN_conventions.md
(lire au moins « Mots confus », « Synonymes », « Synonyme partiel », « Formes admises », « Gloses »).

## Déroulement d'une exécution
1. `python3 tools/passe_confus.py next` : réserve le lot suivant. « OCCUPÉ » → s'arrêter sans rien modifier.
   « TERMINÉ » → s'arrêter.
2. `python3 tools/passe_confus.py lot <n> 0 50`, puis `lot <n> 50 60` : chaque ligne, ses exemples
   (formes admises entre accolades) et des candidats triés par source.
3. Pour chaque ligne, choisir 0 à 3 mots confus (voir ci-dessous) ; les candidats ne sont qu'une aide : chercher aussi
   dans la base (`python3 tools/vocab.py grep <regex>`) les mots proches non proposés, surtout les pièges du français.
4. Écrire passes/confus/decisions_lotNN.json ({clé affichée par la ligne : [Mots]} — la clé est
   « Entrée|Mot|40 premiers caractères de la Traduction » ; liste vide = aucun), puis
   `python3 tools/passe_confus.py apply passes/confus/decisions_lotNN.json`.
5. Corrections de la base (après l'apply), avec les fonctions de tools/vocab.py, voir ci-dessous.
6. `python3 tools/vocab.py lint` (0 avertissement, ou LINT_OK justifié), `python3 tools/passe_confus.py done <n>`,
   compte rendu du lot ajouté à passes/confus/compte_rendu.md (5 à 10 lignes : nombre de lignes avec mots confus,
   corrections faites, cas soumis), commit « Passe mots confus : lot NN » sur main, push.
7. S'il reste du temps et du contexte, enchaîner un second lot (retour à 1). Jamais plus de 2 lots par exécution.

## Mot confus
- Mot d'une autre ligne de la base, écrit exactement comme son Mot, même nature.
- Tentant : traduction française commune (piège du français : legacy « historique », to undergo « subir »,
  free « gratuit », a yardstick « règle », turnout « participation »), paronyme (praise / appraise, glut / glutton),
  autre sens d'un mot de la ligne (set off « déclencher » → to trigger (off)), quasi-synonyme à nuance distincte,
  ancien synonyme partiel.
- Faux dans CHACUN des exemples de la ligne, par le sens ou la collocation, pas seulement par la construction.
  L'exercice n'affiche pas la traduction : un mot qui donne une phrase naturelle de sens différent (currently dans
  « few voters actually believe ») n'est pas faux pour l'apprenant, l'écarter. Dans le doute, ne pas le retenir.
  Ne jamais prendre un synonyme ou une forme admise de la ligne, ni un Mot identique à celui de la ligne (autre sens :
  an alien « extraterrestre » ne peut pas servir pour an alien « étranger », l'apply le refuse).
- Viser les distracteurs difficiles : l'exercice doit obliger à choisir entre des mots proches. Un mot sans rapport
  ne sert à rien (le hasard en fournit déjà).

## Corrections faites d'office (signalées dans le compte rendu)
- Un candidat qui convient dans au moins un exemple et qui est un vrai équivalent dans le sens de la ligne :
  l'ajouter aux Synonymes des deux lignes (symétrie, construction et marques selon les conventions), puis ses formes
  admises dans chaque exemple où il convient (`B.setadm`), des deux côtés. Exemples du pilote : mischievous / malicious
  (« malveillant »), careless / reckless (si reckless convient dans tous les sens de la ligne), a thug / a rowdy.
  Un quasi-synonyme à nuance (convient dans un exemple mais pas dans le sens général) : marquer la différence par une
  glose dans la Traduction si les deux Traductions se recouvrent au point de les faire passer pour synonymes.
- Défauts couverts par les conventions repérés au passage : exemple fautif ou peu naturel, traduction inexacte ou
  calquée, mot à trouver mal délimité, glose manquante, synonyme faux ou partiel.

## À soumettre à Jennifer (passes/confus/a_trancher.md, sans appliquer)
Scission de ligne, nouvelle ligne ou fiche, retrait de ligne, arbitrage entre objectifs. Une ligne par cas :
lot, fiche, ligne, proposition, raison en une phrase.
