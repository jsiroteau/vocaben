# Suite de la passe formes admises : traitement des synonymes signalés

Objet : traiter les ≈ 330 synonymes de `signalements.md` qui ne conviennent dans aucun exemple de leur ligne, selon les décisions de Jennifer du 15 novembre 2026. Quatre tranches (A : lots 1 à 6, B : lots 7 à 12, C : lots 13 à 18, D : lots 19 à 24), une seule à la fois.

## Procédure d'une exécution
1. Cloner le dépôt (accès en écriture), se placer à sa racine. Lire ce fichier en entier, puis les sections « Notation » (Synonymes, Liens des synonymes) du fichier de conventions si besoin : les règles utiles sont résumées ci-dessous.
2. `python3 tools/passe_suite.py next` : affiche la tranche réservée (commit et push immédiats de `etat_suite.json`). EN COURS : une autre exécution travaille, s'arrêter sans rien faire. TERMINÉ : s'arrêter (voir le message de fin dans la consigne de la tâche).
3. Lire dans `signalements.md` les sections des lots de la tranche. Ignorer les lignes « Corrigé d'office » (déjà faites) et la section « Décisions de Jennifer » (déjà appliquée : tight / taut, youth, a make, handicapped).
4. Pour chaque signalement : relire la ligne et ses exemples (`python3 tools/vocab.py show "<entrée>"` ou `grep`), vérifier le motif, classer et corriger selon les règles ci-dessous, avec les fonctions de `tools/vocab.py`. Un agent réviseur puis un agent vérificateur indépendant par groupe de lots sont possibles pour proposer les décisions, mais une seule application, en série, dans la base.
5. `python3 tools/passe_admis.py orphans` : See also devenus sans lien avec leur fiche ; les déplacer dans la fiche de leur meilleur synonyme quand c'est évident (`B.move`), sinon les noter dans `a_trancher.md`.
6. `python3 tools/vocab.py lint` sans avertissement ; `python3 tools/passe_suite.py done <tranche>` ; ajouter à `suite_compte_rendu.md` une section pour la tranche (nombre de synonymes retirés, gardés à sens unique, gardés avec marque de registre, admis ajoutés, lignes créées avec leur liste complète) ; `git pull --rebase`, commit sur main, push.

## Règles de décision (Jennifer, 15 novembre 2026)

**A. Synonyme faux ou partiel** (il ne couvre qu'une partie du sens, ou un autre sens : to heal / to cure, a clue / a lead, steep / sheer). C'est le cas général.
- Le retirer de la ligne signalée.
- Renvoi inverse (la ligne du synonyme cite le mot) : le garder à sens unique si le synonyme est un cas particulier du mot et que le mot convient dans les exemples de la ligne du synonyme (a bill pour an invoice, tight pour taut) : ajouter le couple à LINT_OK. Sinon le retirer aussi.
- Si le synonyme convient à une autre ligne du même mot (autre sens), l'y placer s'il n'y est pas.
- Si la ligne du synonyme a une Traduction qui ne laisse pas voir pourquoi il n'est que partiel, préciser cette Traduction par une glose entre parenthèses (taut « tendu (corde, muscle, visage, nerfs) » ; sheer « à pic (falaise) »).
- Ne pas scinder de ligne, ne pas supprimer de ligne ni de fiche, ne renommer aucune Entrée. Une scission qui paraît s'imposer (la ligne mêle deux sens de traduction différente) est notée dans `a_trancher.md`, pas faite.

**B. Synonyme de bon sens mais de registre marqué** (soutenu, littéraire, familier, vieilli : to go by / to elapse, dough / brass, to own / to possess).
- L'admettre au texte à trous dans chaque exemple où la phrase reste de l'anglais idiomatique avec lui, même si le ton change (`B.setadm`, forme fléchie exacte, voir README). Ne pas l'admettre là où la phrase deviendrait fautive ou non idiomatique.
- Puis, selon que Jennifer le connaît sans doute déjà ou non :
  - mot courant (Zipf ≥ 4, `zipf('<mot>')`) ou mot qui a déjà une ligne dans la base : il reste dans les Synonymes ; ajouter après lui une marque de registre entre parenthèses quand la connotation compte : « (soutenu) », « (familier) », « (vieilli) », « (littéraire) », comme handicapped (vieilli, souvent jugé offensant) ;
  - mot moins courant et sans ligne : lui créer une ligne s'il la mérite (critères ci-dessous), en See also de la fiche (`assoc=True`, en fin de fiche), Traduction avec le registre entre parenthèses, 2 ou 3 exemples naturels qui font sentir ce registre, synonyme = le mot de départ ; sinon le retirer des Synonymes.

**C. Sens propres.** Les sens propres des mots abstraits ne sont dans les fiches que pour faciliter l'apprentissage du sens figuré. On ne développe pas leurs synonymes : pour une ligne de sens propre ou concret (étayer un mur, corde tendue, colline raide), on retire le synonyme partiel sans créer de ligne ni proposer de scission, sauf si le mot enrichit vraiment le champ lexical visé.

**D. Rien à faire.** Synonyme juste, qui ne convient dans aucun exemple pour une simple raison de construction (complément intercalé, expression figée, nom composé) : le laisser, sans marque.

## Critères pour créer une ligne
- Objectif de la base : lire The Economist et des newsletters (Substack) ; en second lieu, comprendre romans, séries et films.
- La presse reste le critère de création : mot utile à la lecture de la presse, Zipf ≥ 2, pas un cognat transparent, pas un mot basique, famille absente de la base (sinon rattacher à la fiche de la famille). Pour le vocabulaire concret, physique ou familier propre à la fiction, on ne crée de ligne que si le mot est très fréquent en fiction ; un tel mot qui a déjà sa ligne la garde.
- Ligne nouvelle : `B.row(entrée, mot, nature, traduction, syn=..., ex=[...], zipf_of='<mot à sa forme de base>', assoc=True)` puis `B.insert_after(B.fiche(entrée)[-1], ligne)` ; Zipf fixé à la main si le mot est un homographe d'un mot très courant. Vérifier d'abord avec `grep` que le Mot n'existe pas déjà dans la base (un Mot n'apparaît que dans une fiche). Exemples : phrases complètes, niveau The Economist, traduction naturelle, espaces insécables françaises, mot à trouver présent tel quel.
- Rester économe : la base ne doit pas grossir sans nécessité. Dans le doute, retirer le synonyme plutôt que créer une ligne.

## Rappels de notation
- Synonymes : virgule = séparateur ; prépositions et particules du Mot de la fiche cible ; sb/sth selon le Mot de la ligne de départ ; marque (GB) / (US) recopiée ; parenthèses ignorées par les renvois.
- Un synonyme très basique qui renverrait vers une fiche sans ce sens s'écrit avec sa construction complète (to make goods) ou se retire.
- Abréviations qn / qch ; pas de « ; » dans une Traduction.

## Fichiers
- `a_trancher.md` : cas laissés à Jennifer (scissions, See also sans lien non évidents, doutes sérieux), une ligne par cas avec le motif.
- `suite_compte_rendu.md` : une section par tranche.
- `etat_suite.json` : état des tranches.
