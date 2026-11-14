"""Passe « formes admises » (colonnes Admis 1-5) : découpage en lots, affichage, application.

Usage (depuis la racine du dépôt) :
    python3 tools/passe_admis.py init                 découpe les lignes à synonymes en lots (une seule fois)
    python3 tools/passe_admis.py next [k]             réserve les k prochains lots (« en cours ») et affiche leurs numéros
    python3 tools/passe_admis.py show <n>             affiche le lot n (lignes L0, L1… et exemples 0-4)
    python3 tools/passe_admis.py apply <n> <f.json>   applique les décisions du lot n et le marque fait
    python3 tools/passe_admis.py orphans              See also devenus sans lien avec leur fiche (hors liste de départ)

Décisions (f.json) : {"L3": {"0": "bolstered / shored up", "2": "bolstered"}, ...}
Une ligne ou un exemple absent du fichier n'a aucune forme admise (les formes existantes sont effacées).
Consignes : passes/admis/README.md.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from vocab import *  # noqa: E402,F403
from vocab import _alts, _items  # noqa: E402

DIR = 'passes/admis'
LOTS, ETAT, ORPH = f'{DIR}/lots.json', f'{DIR}/etat.json', f'{DIR}/see_also_orphelins_depart.json'
TARGET = 400  # exemples par lot


def key(r):
    return f'{r[E]}|{r[M]}|{r[T]}'


def has_syn(r):
    return bool(_items(r[SYN]))


def orphans(B):
    """See also dont aucun synonyme/antonyme ne renvoie vers un mot de la fiche, et qu'aucun mot de la fiche ne cite."""
    out = []
    for e in dict.fromkeys(r[E] for r in B.rows):
        f = B.fiche(e)
        for r in f:
            if not r[TYPE]:
                continue
            others = [x for x in f if x is not r]
            mine = set().union(*[_alts(x) for x in _items(r[SYN]) + _items(r[ANT])]) if _items(r[SYN]) + _items(r[ANT]) else set()
            linked = any(mine & _alts(x[M]) for x in others)
            cited = any(_alts(r[M]) & set().union(*[_alts(y) for y in _items(x[SYN]) + _items(x[ANT])] or [set()]) for x in others)
            if not linked and not cited:
                out.append(key(r))
    return out


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def save_json(p, o):
    json.dump(o, open(p, 'w'), ensure_ascii=False, indent=1)


def init(B):
    assert not os.path.exists(LOTS), 'lots déjà découpés'
    pilot = set(load(f'{DIR}/lot00_cles.json', []))
    lots, cur, n = {}, [], 0
    for e in dict.fromkeys(r[E] for r in B.rows):
        f = [r for r in B.fiche(e) if has_syn(r) and B.getex(r) and key(r) not in pilot]
        cur += [key(r) for r in f]
        n += sum(len(B.getex(r)) for r in f)
        if n >= TARGET:
            lots[str(len(lots) + 1)] = cur
            cur, n = [], 0
    if cur:
        lots[str(len(lots) + 1)] = cur
    save_json(LOTS, lots)
    save_json(ETAT, {k: 'à faire' for k in lots})
    save_json(ORPH, orphans(B))
    print(f'{len(lots)} lots, {sum(map(len, lots.values()))} lignes')


def rows_of(B, n):
    idx = {key(r): r for r in B.rows}
    return [(k, idx.get(k)) for k in load(LOTS, {})[str(n)]]


def show(B, n):
    for i, (k, r) in enumerate(rows_of(B, n)):
        if r is None:
            print(f'L{i} [ligne introuvable, modifiée depuis le découpage : {k}]')
            continue
        print(f'L{i} | {r[E]} | {r[M]} = {r[T]} | syn: {r[SYN]}')
        for j, ((a, m, t), adm) in enumerate(zip(B.getex(r), B.getadm(r))):
            print(f'   {j}. {a} [{m}]' + (f' (admis : {adm})' if adm else ''))


def apply(B, n, path):
    dec = json.load(open(path))
    done = 0
    for i, (k, r) in enumerate(rows_of(B, n)):
        if r is None:
            assert f'L{i}' not in dec, f'L{i} introuvable : {k}'
            continue
        d = dec.get(f'L{i}', {})
        exs = B.getex(r)
        for j in range(len(exs)):
            f = d.get(str(j))
            if f:
                f = ' / '.join(x.strip() for x in f.split('/') if x.strip())
                assert all(x.lower() != exs[j][1].lower() for x in f.split(' / ')), f'L{i}.{j} : forme = mot à trouver'
            B.setadm(r, j, f)
            done += bool(f)
        assert all(int(j) < len(exs) for j in d), f'L{i} : exemple inexistant'
    B.save()
    etat = load(ETAT, {})
    etat[str(n)] = 'fait'
    save_json(ETAT, etat)
    print(f'lot {n} appliqué : {done} exemples avec formes admises')
    new = [o for o in orphans(B) if o not in set(load(ORPH, []))]
    if new:
        print('See also devenus orphelins :', *new, sep='\n  ')


if __name__ == '__main__':
    cmd = sys.argv[1]
    B = Base()
    if cmd == 'init':
        init(B)
    elif cmd == 'next':
        etat = load(ETAT, {})
        todo = [k for k, v in etat.items() if v == 'à faire'][:int(sys.argv[2]) if len(sys.argv) > 2 else 1]
        for k in todo:
            etat[k] = 'en cours'
        save_json(ETAT, etat)
        print(' '.join(todo) or 'TERMINÉ')
    elif cmd == 'show':
        show(B, int(sys.argv[2]))
    elif cmd == 'apply':
        apply(B, int(sys.argv[2]), sys.argv[3])
    elif cmd == 'orphans':
        base = set(load(ORPH, []))
        print(*[o for o in orphans(B) if o not in base], sep='\n')
