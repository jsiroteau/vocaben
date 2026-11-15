"""Fréquence des verbes à particule (15 novembre 2026).

Problème : la règle « Zipf du mot distinctif, particules exclues » donnait aux verbes à
particule le Zipf de leur verbe de base (to bear up = Zipf de bear), d'où ≈ 300 verbes à
particule classés en Fréq 1.

Méthode : Zipf de la combinaison verbe + particule, toutes formes fléchies du verbe
additionnées (break down + breaks down + broke down + broken down + breaking down), d'après
le dictionnaire de bigrammes anglais distribué avec symspellpy (tiré de Google Books Ngram).
Échelle : log10(somme / N × 10^9), N = 10^13,3 calé sur des bigrammes dont le second mot
n'apparaît presque qu'en leur sein (vice versa, status quo) ; un bigramme absent du
dictionnaire (seuil ≈ 6,4 millions d'occurrences) vaut 2,5. Le nouveau Zipf ne dépasse
jamais l'ancien (min). Seuls les Mots de la forme « to V [sb/sth] particule [sb/sth]
[préposition] » sont traités ; les locutions (to go out of business) gardent leur Zipf.
Limite : les formes disjointes (pick it up) ne sont pas comptées, ce qui sous-estime un peu
les verbes transitifs.

Usage : python3 tools/passe_frequence_vap.py <bigrams.txt> [--apply]
"""
import json
import math
import re
import sys

sys.path.insert(0, 'tools')
from vocab import *  # noqa

LOG_N = 13.3
ABSENT = 2.5
PART = ('up down out off in on over away back around round about through along across by '
        'forward forth aside apart together ahead behind upon').split()
OBJ = r"(?:sb|sth|sb/sth|sth/sb|oneself|sb's|one's|yourself|it)"
PREP = r"(?:to|with|on|of|from|for|against|at|into|in|about|by|over|as)"


def clean(m):
    """Retire les parenthèses : formes irrégulières, compléments facultatifs, (doing), (US)…"""
    while re.search(r"\([^()]*\)", m):
        m = re.sub(r"\s*\([^()]*\)", " ", m)
    m = re.sub(r"\bdoing sth\b|\bdoing\b|\bthat\b", "sth", m)
    return re.sub(r"\s+", " ", m).strip()


def parse(mot):
    """Renvoie [(verbe, [particules])] pour un Mot de verbe à particule, None sinon."""
    out = []
    for var in re.split(r"\s+/\s+", clean(mot)):
        be = re.match(r"to be (\w+ed|\w+en|laid|put|run|sworn|set|bound) (.*)", var)
        if be:                                   # passif : to be laid up → lay up
            from lemminflect import getLemma
            var = 'to ' + getLemma(be.group(1), upos='VERB')[0] + ' ' + be.group(2)
        if var.startswith('to do sth'):          # to queue up for sth / to do sth
            continue
        mm = re.fullmatch(r"to (\w+)(?: " + OBJ + r")? ([a-z]+(?:/[a-z]+)*)(?: " + OBJ + r")?"
                          r"(?: " + PREP + r"(?:/" + PREP + r")?(?: " + OBJ + r")?)?(?: to do sth)?", var)
        if not mm:
            return None
        v, parts = mm.group(1), mm.group(2).split('/')
        if v in ('be', 'have') or not all(p in PART for p in parts):
            return None
        out.append((v, parts))
    return out or None


def forms(v):
    from lemminflect import getAllInflections
    f = {v}
    for t in getAllInflections(v, upos='VERB').values():
        f.update(t)
    return f


def main():
    big = {}
    for l in open(sys.argv[1]):
        a, b, c = l.split()
        big[a + ' ' + b] = int(c)
    B = Base()
    changes = []
    for r in B.rows:
        if 'verb' not in str(r[NAT]) or not r[M]:
            continue
        p = parse(r[M])
        if not p:
            continue
        best = None
        for v, parts in p:
            for part in parts:
                n = sum(big.get(f + ' ' + part, 0) for f in forms(v))
                z = round(math.log10(n) - LOG_N + 9, 2) if n else ABSENT
                best = z if best is None else max(best, z)
        old_z = float(r[ZIPF]) if r[ZIPF] not in (None, '') else None
        new_z = min(best, old_z) if old_z is not None else best
        new_f = freq_class(new_z)
        if old_z is None or abs(new_z - old_z) > 1e-9 or str(new_f) != str(r[FREQ]):
            changes.append(dict(entree=r[E], mot=r[M], zipf_avant=old_z, freq_avant=r[FREQ],
                                zipf=new_z, freq=new_f))
            if '--apply' in sys.argv:
                r[ZIPF], r[FREQ] = new_z, new_f
    json.dump(changes, open('passes/frequence/changements.json', 'w'), ensure_ascii=False, indent=1)
    print(len(changes), 'lignes modifiées')
    if '--apply' in sys.argv:
        B.save()


if __name__ == '__main__':
    main()
