# Passe « sens mêlés et sens manquants » — consignes du réviseur et du vérificateur

Base VocabEN : vocabulaire anglais pour lire The Economist et des blogs d'idées (Rob Henderson, Roger Pielke). Une **fiche** = un mot-tête et sa famille ; chaque **ligne** = un Mot (avec sa construction), une nature, une Traduction (équivalents français séparés par des virgules, nuances entre parenthèses), des synonymes, des antonymes et 2 à 5 exemples (phrase anglaise, [mot à trouver], traduction). Les lignes marquées [See also] sont des mots hors famille associés à la fiche.

Les exemples viennent d'être relus pour l'anglais et la traduction : **ne pas y revenir**. Cette passe cherche trois défauts seulement.

## 1. Ligne qui mêle deux sens
Une ligne ne porte qu'un sens. Deux sens = deux lignes **quand la traduction française diffère** (ailing « souffrant » / « en difficulté » ; a revival « un renouveau » / « une reprise (pièce de théâtre) » ; footprints « empreintes de pas » / a footprint « empreinte carbone »). Si la traduction française est la même pour le sens propre et le sens figuré (to alleviate « soulager »), une seule ligne est correcte.
Signes : une Traduction qui juxtapose des équivalents de sens différents ; un exemple dont la traduction n'emploie aucun équivalent de la ligne parce qu'il relève d'un autre sens.
Correction : créer la ligne du second sens (`new`) et y déplacer les exemples concernés (`move`), puis resserrer la Traduction de la ligne d'origine (`T`). Chaque ligne doit garder au moins 2 exemples : compléter par des exemples nouveaux (dans la ligne créée) ou remplacer (`ex`) si besoin.

## 2. Exemple qui illustre un autre sens que sa ligne
Si le sens a sa ligne dans la fiche : déplacer l'exemple (`move`). Sinon : soit créer la ligne (cas 3), soit remplacer l'exemple par un exemple du bon sens (`ex`).

## 3. Sens important manquant
Ajouter une ligne seulement pour un sens **courant dans la presse économique et politique ou les essais**, que le lecteur ne devinerait pas à partir des lignes existantes, et dont la traduction diffère (ex. a shift « un poste, une équipe (de travail) » absent alors que to shift et to work in shifts y sont). Ne pas ajouter : sens basique, cognat transparent (même mot en français), sens qui se déduit des mots, sens rare ou technique pointu, sens argotique. **Être sélectif** : une fiche longue est plus difficile à mémoriser ; en cas de doute, ne rien ajouter. Ordre de grandeur attendu : quelques ajouts par lot, pas des dizaines.

## Rédaction d'une ligne nouvelle
- Mot : noms dénombrables avec article (a shift), indénombrables sans ; verbes avec « to » ; construction utile seulement (sb, sth, prépositions obligatoires sans parenthèses, facultatives entre parenthèses). Nature : noun, verb, adjective, adverb, phrase…
- Traduction : 1 à 3 équivalents exacts et naturels, séparés par des virgules, jamais de « ; » ; noms dénombrables avec article indéfini (« un poste, une équipe ») ; type de complément ou nuance entre parenthèses (« (de travail) »). Si le Mot porte sb/sth, la Traduction porte qn/qch.
- syn / ant : facultatifs, vrais équivalents seulement, séparés par des virgules ; sinon ne pas mettre le champ.
- 2 à 5 exemples de niveau presse (The Economist), situations claires sans contexte, sujets variés, traduction française idiomatique reprenant un équivalent de la Traduction ; unités anglo-saxonnes converties dans la traduction ; espaces insécables (U+00A0) avant : ; ? ! et à l'intérieur des guillemets « ».
- Mot à trouver : présent tel quel dans la phrase, une seule fois, en mots entiers, sans article ni mot hors du Mot ; avec la particule ou préposition finale si elle suit directement le verbe ; si un complément s'intercale, seulement la partie qui précède (en général le verbe) ; majuscule si la phrase commence par lui.
- `zipf_of` : le mot distinctif à sa forme de base (« shift »), pour le calcul de fréquence.
- `after` : la ligne après laquelle insérer — les sens proches restent côte à côte (le sens propre avant les sens figurés ; jamais une expression avant le mot seul ; jamais après les See also, sauf pour un See also).
- `assoc` : true seulement si la ligne d'origine est un See also.

## Ce qu'il ne faut PAS faire
Ne pas renommer ni supprimer de fiche ; ne pas toucher aux synonymes ni à l'ordre des lignes existantes ; ne pas reprendre l'anglais ou la traduction des exemples (déjà relus) ; pas de corrections de goût.

## Format de sortie (réviseur)
Une liste JSON, rien d'autre, avec les opérations décrites en tête de `tools/passe_sens.py` :
- `{"op": "ex", "id": "r12", "ex": 2, "en": "...", "mot": "...", "fr": "...", "motif": "..."}`
- `{"op": "new", "nid": "n1", "after": "r12", "M": "...", "NAT": "...", "T": "...", "zipf_of": "...", "ex": [["en", "mot", "fr"], ["en", "mot", "fr"]], "motif": "..."}` (+ "syn", "ant", "assoc" si utiles)
- `{"op": "move", "id": "r12", "en": "<phrase anglaise exacte>", "to": "r13" ou "n1", "motif": "..."}`
- `{"op": "T", "id": "r12", "T": "...", "motif": "..."}`
Motifs : `mêlés`, `hors sens`, `manquant`, suivis de « : explication courte ».

## Vérificateur
Il reçoit le lot et la liste du réviseur. Pour chaque opération : garder, amender ou écarter (ajout non justifié par la règle 3, scission alors que la traduction est la même, ligne sans 2 exemples, mot à trouver cassé, traduction inexacte, mauvaise place). Il veille à la cohérence des opérations liées (une scission = new + move + T). Il n'ajoute que des oublis manifestes. Il rend la liste finale au même format.
