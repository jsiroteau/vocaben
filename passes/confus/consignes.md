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
7. Enchaîner les lots sans s'arrêter tant qu'il reste largement du temps et du contexte (retour à 1), sans rien
   demander à Jennifer (21 novembre 2026 : elle ne voit pas quand l'exécution s'arrête) ; jamais plus de 4 lots par
   exécution. À l'arrêt, relancer aussitôt la tâche planifiée pour que l'exécution suivante prenne le relais.

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

## Perfectionnement de la base : contrôles obligatoires sur chaque ligne (21 novembre 2026)
Jennifer tient autant à cet objectif qu'aux mots confus. Les lots 2 à 11 n'ont presque rien corrigé : chaque contrôle
ci-dessous doit être fait réellement, ligne par ligne, et ses résultats comptés dans le compte rendu.

A. Tout candidat écarté parce qu'il « convient dans un exemple » reçoit une décision explicite, jamais un simple rejet :
   1. vrai équivalent dans le sens de la ligne → ajout aux Synonymes des deux lignes (symétrie, construction et
      marques selon les conventions), formes admises dans chaque exemple où il convient (`B.setadm`), des deux côtés ;
   2. cas particulier ou sens plus large → renvoi à sens unique du particulier vers le général (LINT_OK) et glose
      du particulier qui montre sa restriction ;
   3. quasi-synonyme à nuance → les deux Traductions doivent laisser voir la différence (glose) ; sinon, en ajouter une.
   Même chose pour les fiches où « les voisins s'échangent dans les phrases » (lot 3 : bishop, block, gloomy, dreary) :
   ce sont presque toujours des synonymes manquants.
B. Synonymes existants : chacun doit convenir dans au moins un exemple de sa ligne (forme admise présente). Sinon :
   synonyme faux ou partiel (retrait, ou sens unique + glose), ou exemple à ajouter qui l'illustre.
C. Pièges du français retenus comme mots confus : si les deux Traductions se ressemblent (legacy « historique » /
   landmark « historique »), ajouter la glose qui les distingue, sur l'une ou les deux lignes.
D. Traduction et exemples : chaque équivalent de la Traduction illustré par un exemple, chaque traduction d'exemple
   reprenant un équivalent quand c'est naturel ; pas de calque ni de contresens ; anglais naturel, niveau The Economist.
E. Un sens par ligne : exemple qui relève d'un autre sens (le déplacer), ou ligne qui mêle deux sens à traductions
   différentes (scission → a_trancher.md).
F. Mot à trouver bien délimité, Mot noté selon les conventions (sb/sth, prépositions, « to be … »), Nature correcte.

Compte rendu de chaque lot : nombre de corrections par contrôle (A1, A2, A3, B, C, D, E, F), avec 2 ou 3 exemples.

## Lots à revoir (état « à revoir »)
Lots déjà passés avant ces contrôles : `next` les donne une fois tous les lots « à faire » terminés. Les mots confus y
sont déjà en place (affichés par `lot`) : appliquer seulement les contrôles A à F (et compléter un mot confus manquant
s'il y en a un évident), puis `done`, compte rendu « Lot NN (revue) », commit « Passe mots confus : revue lot NN ».

## À soumettre à Jennifer (passes/confus/a_trancher.md, sans appliquer)
Scission de ligne, nouvelle ligne ou fiche, retrait de ligne, arbitrage entre objectifs. Une ligne par cas :
lot, fiche, ligne, proposition, raison en une phrase.
