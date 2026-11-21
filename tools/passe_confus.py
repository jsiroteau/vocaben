"""Passe « mots confus » : distracteurs du QCM de discrimination (colonne Confus).

Un mot confus d'une ligne est un Mot d'une autre ligne de la base, assez proche pour tenter
(même champ, traductions voisines, ancien synonyme partiel), mais faux dans CHACUN des exemples
de la ligne : l'appli peut alors le proposer quel que soit l'exemple tiré.

    python3 tools/passe_confus.py candidats          calcule passes/confus/candidats.json
    python3 tools/passe_confus.py pilote [n]         choisit n lignes (100) → passes/confus/pilote.json
    python3 tools/passe_confus.py show <fichier> [début] [nb]   affiche lignes, exemples et candidats
    python3 tools/passe_confus.py apply <decisions.json>        écrit la colonne Confus (contrôle des Mots)
"""
import json
import re
import sys
from collections import defaultdict

sys.path.insert(0, 'tools')
from vocab import *  # noqa
from vocab import _alts, _items, LINT_OK

D = 'passes/confus/'
STOP = {'un', 'une', 'le', 'la', 'les', "l'", 'des', 'du', 'de', "d'", 'se', "s'", 'qn', 'qch', 'à', 'au', 'aux', 'en', 'sur'}


def key(r):
    return f'{r[E]}|{r[M]}|{(r[T] or "")[:40]}'


def equivalents(tr):
    """Équivalents français d'une Traduction, gloses et articles retirés."""
    tr = re.sub(r'\([^()]*\)', ' ', tr or '')
    out = set()
    for part in tr.split(','):
        w = [x for x in re.split(r"\s+|(?<=')", part.strip().lower()) if x]
        w = [x for x in w if x not in STOP]
        if w and len(' '.join(w)) > 3:
            out.add(' '.join(w))
    return out


def candidats():
    B = Base()
    rows = B.rows
    idx = defaultdict(list)
    for r in rows:
        for k in _alts(r[M]):
            idx[k].append(r)

    def linked(a, b):
        ka, kb = _alts(a[M]), _alts(b[M])
        sa = {k for x in _items(a[SYN]) + _items(a[ANT]) for k in _alts(x)}
        sb = {k for x in _items(b[SYN]) + _items(b[ANT]) for k in _alts(x)}
        return bool(kb & sa or ka & sb)

    cand = defaultdict(dict)    # key(ligne) → {Mot candidat: source}

    def add(r, t, src):
        if t is r or t[M] == r[M] or linked(r, t) and src != 'sens unique':
            return
        if t[NAT] != r[NAT]:
            return
        cand[key(r)].setdefault(t[M], src)

    # 1. renvois à sens unique : A → B gardé, B ne renvoie pas ; pour la ligne B, A est un cas particulier
    for r in rows:
        for s in _items(r[SYN]):
            for t in {id(x): x for k in _alts(s) for x in idx.get(k, [])}.values():
                if t is r or t[NAT] != r[NAT]:
                    continue
                back = _alts(r[M]) & {k for x in _items(t[SYN]) for k in _alts(x)}
                if not back:
                    cand[key(t)].setdefault(r[M], 'sens unique')
    # 2. paires déliées citées dans les conventions (« x ≠ y ») et retirées des deux côtés
    txt = open('docs/VocabEN_conventions.md', encoding='utf-8').read()
    pairs = re.findall(r"([a-z][a-z' -]{2,30}?) ≠ ([a-z][a-z' -]{2,30}?)(?=[,)»])", txt)
    cr = open('passes/admis/suite_compte_rendu.md', encoding='utf-8').read()
    for seg in re.findall(r'Retirés des deux côtés : ([^.]*)\.', cr):
        pairs += [tuple(x.split(' / ')[:2]) for x in seg.split(', ') if ' / ' in x]
    for a, b in pairs:
        ra = [x for k in _alts(a.strip()) for x in idx.get(k, [])]
        rb = [x for k in _alts(b.strip()) for x in idx.get(k, [])]
        for x in ra:
            for y in rb:
                add(x, y, 'délié'); add(y, x, 'délié')
    # 3. traductions qui se recouvrent, lignes non reliées de même nature
    by_eq = defaultdict(list)
    for r in rows:
        if r[TYPE] == 'association' and not r[SYN]:
            pass
        for q in equivalents(r[T]):
            by_eq[q].append(r)
    for q, rs in by_eq.items():
        if 2 <= len(rs) <= 6:
            for x in rs:
                for y in rs:
                    if x is not y:
                        add(x, y, f'traduction « {q} »')
    # 4. même fiche, même nature, lignes non reliées (careless / reckless)
    fiches = defaultdict(list)
    for r in rows:
        fiches[r[E]].append(r)
    for rs in fiches.values():
        for x in rs:
            for y in rs:
                add(x, y, 'même fiche')
    # 5. chaînes de synonymes : A ~ B ~ C, A et C non reliés
    for r in rows:
        for s in _items(r[SYN]):
            for t in {id(x): x for k in _alts(s) for x in idx.get(k, [])}.values():
                for s2 in _items(t[SYN]):
                    for u in {id(x): x for k in _alts(s2) for x in idx.get(k, [])}.values():
                        add(r, u, f'chaîne via {t[M]}')
    out = {k: v for k, v in cand.items() if v}
    json.dump(out, open(D + 'candidats.json', 'w'), ensure_ascii=False, indent=0)
    n = sum(len(v) for v in out.values())
    src = defaultdict(int)
    for v in out.values():
        for s in v.values():
            src[s.split(' ')[0]] += 1
    print(f'{len(out)} lignes, {n} candidats', dict(src))


def pilote(n=100):
    import random
    cand = json.load(open(D + 'candidats.json'))
    strong = [k for k, v in cand.items() if any(not s.startswith('traduction') for s in v.values())]
    weak = [k for k in cand if k not in strong]
    random.seed(21112026)
    pick = random.sample(strong, min(len(strong), n * 2 // 5)) + random.sample(weak, n - min(len(strong), n * 2 // 5))
    json.dump(sorted(pick), open(D + 'pilote.json', 'w'), ensure_ascii=False, indent=0)
    print(len(pick), 'lignes')


def show(path, start=0, nb=10):
    B = Base()
    cand = json.load(open(D + 'candidats.json'))
    keys = json.load(open(path))[start:start + nb]
    rows = {key(r): r for r in B.rows}
    bymot = defaultdict(list)
    for r in B.rows:
        bymot[r[M]].append(r)
    for i, k in enumerate(keys, start):
        r = rows[k]
        print(f'\n#{i} [{r[E]}] {r[M]} ({r[NAT]}) = {r[T]}   syn: {r[SYN] or "-"}')
        for a, m, t in getex(r):
            print(f'   · {a}   [{m}]')
        for c, s in list(cand.get(k, {}).items())[:10]:
            print(f'   ? {c} = {" / ".join(x[T] for x in bymot[c])[:70]}   ({s[:25]})')


def apply(path):
    B = Base()
    dec = json.load(open(path))
    rows = {key(r): r for r in B.rows}
    mots = {r[M] for r in B.rows}
    n = 0
    for k, lst in dec.items():
        r = rows[k]
        bad = [c for c in lst if c not in mots or c == r[M]]
        assert not bad, f'{k} : Mots inconnus {bad}'
        r[CONF] = ', '.join(lst) or None
        n += bool(lst)
    B.save()
    print(n, 'lignes avec mots confus')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'candidats':
        candidats()
    elif cmd == 'pilote':
        pilote(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
    elif cmd == 'show':
        show(sys.argv[2], *(int(x) for x in sys.argv[3:5]))
    elif cmd == 'apply':
        apply(sys.argv[2])
