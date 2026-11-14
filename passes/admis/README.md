# Passe « formes admises » (texte à trous)

Objet : pour chaque exemple d'une ligne qui a des synonymes, lister dans la colonne « Admis k » les synonymes de la ligne (y compris ceux en bleu clair, absents de la base) qui peuvent remplacer le mot à trouver dans cette phrase. Dans l'appli, une forme admise est comptée fausse (pour réviser le mot attendu), avec le message « “x” also works here, but this card is about y ».

## Consignes
- Seuls les synonymes de la ligne sont examinés (décision de Jennifer, 14 novembre 2026).
- Admis = même sens dans la phrase, tournure naturelle, collocation idiomatique, registre compatible. Dans le doute, ne pas admettre.
- Écrire la forme qui remplace exactement le mot à trouver : fléchie comme dans la phrase (buttressed → bolstered), avec la préposition si le mot à trouver l'inclut (reliance on → dependence on ; breeding ground for → hotbed of), majuscule si la phrase commence par le mot. Plusieurs formes séparées par « / ».
- Pas de forme admise quand un complément s'intercale (gave him away : le mot à trouver « gave » ne peut pas être remplacé par betrayed) ni dans une expression figée (a safe bet, compulsory redundancies, the affluent society).
- Relever à part les synonymes qui ne conviennent dans aucun exemple de leur ligne : faux synonymes ou synonymes partiels, à revoir avec Jennifer.
- Outil : `B.setadm(r, k, 'a / b')` ; `setex` conserve les formes admises d'un exemple inchangé ; `check` refuse une forme vide ou identique au mot à trouver.

## État
- Lot 0 (pilote, 14 novembre 2026) : 100 lignes tirées au hasard (graine 1114), 306 exemples ; 197 exemples reçoivent au moins une forme admise. Décisions dans `lot00_pilote.py` (indices de ligne valables pour la base du 14 novembre).
