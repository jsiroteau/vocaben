# Passe « formes admises » (texte à trous)

Objet : pour chaque exemple d'une ligne qui a des synonymes, lister dans la colonne « Admis k » les synonymes de la ligne (y compris ceux en bleu clair, absents de la base) qui peuvent remplacer le mot à trouver dans cette phrase. Dans l'appli, une forme admise est comptée fausse (pour réviser le mot attendu), avec le message « “x” also works here, but this card is about y ».

## Consignes
- Seuls les synonymes de la ligne sont examinés (décision de Jennifer, 14 novembre 2026).
- Admis = même sens dans la phrase, tournure naturelle, collocation idiomatique, registre compatible. Dans le doute, ne pas admettre.
- Écrire la forme qui remplace exactement le mot à trouver : fléchie comme dans la phrase (buttressed → bolstered), avec la préposition si le mot à trouver l'inclut (reliance on → dependence on ; breeding ground for → hotbed of), majuscule si la phrase commence par le mot. Plusieurs formes séparées par « / ».
- Pas de forme admise quand un complément s'intercale (gave him away : le mot à trouver « gave » ne peut pas être remplacé par betrayed) ni dans une expression figée (a safe bet, compulsory redundancies, the affluent society).
- Relever à part les synonymes qui ne conviennent dans aucun exemple de leur ligne : faux synonymes ou synonymes partiels, à revoir avec Jennifer.
- Effets de bord à traiter à chaque lot : un synonyme retiré peut laisser un See also sans lien avec aucun mot de sa fiche (ni synonyme, ni antonyme, ni vraie association). Pour chacun : le placer dans la fiche de son meilleur synonyme, lui donner sa fiche s'il a plusieurs sens utiles (comme to creep, sorti de to crawl), ou proposer à Jennifer de le retirer s'il ne mérite pas sa place (économie, Zipf). Un synonyme qui n'est qu'un cas particulier du mot (invoice pour bill) est retiré de la ligne générale mais peut rester à sens unique sur la ligne particulière (LINT_OK).
- Outil : `B.setadm(r, k, 'a / b')` ; `setex` conserve les formes admises d'un exemple inchangé ; `check` refuse une forme vide ou identique au mot à trouver.

## Procédure d'un lot (exécutions planifiées)
1. `git clone --depth 1 https://github.com/jsiroteau/vocaben` (accès en écriture), puis travailler à sa racine ; lire ce fichier en entier.
2. `python3 tools/passe_admis.py next 2` réserve les deux prochains lots (état « en cours ») et affiche leurs numéros : commit et push immédiats de la réservation. TERMINÉ = plus rien à faire. `python3 tools/passe_admis.py show <n>` affiche un lot.
3. Pour chaque lot, un agent réviseur puis un agent vérificateur indépendant (lots en parallèle) : juger chaque exemple selon les consignes ci-dessus et écrire les décisions dans `passes/admis/decisions/lot<nn>.json` (format : `{"L3": {"0": "bolstered / shored up"}}`, seulement les exemples qui ont des formes admises). Contrôler soi-même la liste finale avant de l'appliquer.
4. `python3 tools/passe_admis.py apply <n> passes/admis/decisions/lot<nn>.json`.
5. Synonymes qui ne conviennent dans aucun exemple de leur ligne : les noter dans `signalements.md` (lot, ligne, synonyme, motif). Corriger d'office les cas nets selon les conventions : faux synonyme retiré des deux côtés ; synonyme qui n'est qu'un cas particulier retiré de la ligne générale et gardé à sens unique sur la ligne particulière (ajouter le couple à LINT_OK). Ne pas trancher seul une scission de ligne, une nouvelle fiche ou un retrait de ligne : les noter dans `signalements.md` pour Jennifer. Un synonyme juste qui ne convient dans aucun exemple pour une raison de construction (complément intercalé, expression figée, nom composé comme « the oil lobby ») n'est pas un défaut : ne rien noter.
6. See also signalés orphelins par `apply` : déplacer dans la fiche de leur meilleur synonyme quand c'est évident (B.move), sinon noter dans `signalements.md`.
7. `python3 tools/vocab.py lint` sans avertissement, puis commit (message : lot, nombre d'exemples admis, corrections) et push sur main.

## État
- Découpage (14 novembre 2026) : 24 lots d'environ 400 exemples (3 157 lignes), état dans `etat.json` ; lignes du pilote exclues (`lot00_cles.json`) ; See also déjà sans lien au départ dans `see_also_orphelins_depart.json` (308, en majorité de vraies associations thématiques).
- Lot 0 (pilote, 14 novembre 2026) : 100 lignes tirées au hasard (graine 1114), 306 exemples ; 197 exemples reçoivent au moins une forme admise. Décisions dans `lot00_pilote.py` (indices de ligne valables pour la base du 14 novembre).
- Après le pilote : faux synonymes retirés (rivalry, patron pour backer, to overrule pour to overturn, to flame, a clout pour a blow, to prod, a bust pour a collapse, an invoice pour a bill, to follow pour to keep track, la périphrase de to subscribe to) ; rough scindé (« rugueux » / « accidenté, inégal ») ; an insane person devenu insane « aliéné, dément » (les exemples étaient adjectivaux) ; an atrocity / an outrage conservés (vrais synonymes, simplement peu naturels dans les exemples).
