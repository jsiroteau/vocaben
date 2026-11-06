"""Passe « anglais et traduction des exemples » (novembre 2026), par lots.

    python3 tools/passe_exemples.py lots            crée passes/exemples/lots.json (une fois)
    python3 tools/passe_exemples.py next [n]        affiche les n prochains lots à traiter (défaut 2)
    python3 tools/passe_exemples.py export <k>      écrit passes/exemples/work/lot_<k>.txt (texte pour le réviseur)
                                                    et lot_<k>.json (lignes d'origine, pour l'application)
    python3 tools/passe_exemples.py apply <k> <corrections.json>
                                                    applique les corrections validées, enregistre vocab.xlsx,
                                                    marque le lot comme fait dans passes/exemples/etat.json

Format des corrections (liste JSON) — chaque élément :
    {"id": "r12", "ex": 2, "en": "...", "mot": "...", "fr": "...", "motif": "..."}   (exemple n° 1-5 ; champs facultatifs)
    {"id": "r12", "T": "...", "motif": "..."}                                        (Traduction de la ligne)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from vocab import Base, getex, setex, E, M, T, NAT  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'passes', 'exemples')
LOTS = os.path.join(ROOT, 'lots.json')
ETAT = os.path.join(ROOT, 'etat.json')
WORK = os.path.join(ROOT, 'work')
NB_LOTS = 40


def load(p, default):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


def dump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def make_lots():
    B = Base()
    fiches = list(dict.fromkeys(r[E] for r in B.rows))
    n = {f: 0 for f in fiches}
    for r in B.rows:
        n[r[E]] += len(getex(r))
    total, cible = sum(n.values()), sum(n.values()) / NB_LOTS
    lots, cur, acc = [], [], 0
    for f in fiches:
        cur.append(f)
        acc += n[f]
        if acc >= cible * (len(lots) + 1) and len(lots) < NB_LOTS - 1:
            lots.append(cur)
            cur = []
    lots.append(cur)
    dump(LOTS, lots)
    dump(ETAT, {'faits': {}})
    print(f'{len(lots)} lots, {total} exemples')


def rows_of(B, k):
    fiches = set(load(LOTS, [])[k - 1])
    return [r for r in B.rows if r[E] in fiches]


def export(k):
    B = Base()
    rows = rows_of(B, k)
    orig, out = {}, []
    for i, r in enumerate(rows, 1):
        rid = f'r{i}'
        ex = getex(r)
        orig[rid] = {'E': r[E], 'M': r[M], 'T': r[T], 'ex': ex}
        out.append(f'### {rid} | fiche « {r[E]} » | {r[M]} ({r[NAT]}) = {r[T]}')
        for j, (en, mot, fr) in enumerate(ex, 1):
            out.append(f'  {j}. EN: {en}\n     [mot à trouver : {mot}]\n     FR: {fr}')
    dump(os.path.join(WORK, f'lot_{k:02d}.json'), orig)
    p = os.path.join(WORK, f'lot_{k:02d}.txt')
    open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(p, f'— {len(rows)} lignes, {sum(len(o["ex"]) for o in orig.values())} exemples')


def apply(k, path):
    B = Base()
    orig = load(os.path.join(WORK, f'lot_{k:02d}.json'), {})
    corr = json.load(open(path, encoding='utf-8'))
    done, skipped = 0, []
    for c in corr:
        o = orig.get(c['id'])
        r = next((x for x in B.rows if o and x[E] == o['E'] and x[M] == o['M'] and x[T] == o['T']), None)
        if not r:
            skipped.append((c['id'], 'ligne introuvable (modifiée entre-temps ?)'))
            continue
        if 'T' in c:
            r[T] = c['T']
            done += 1
            continue
        ex = getex(r)
        j = c['ex'] - 1
        if j >= len(ex) or ex[j] != tuple(o['ex'][j]):
            skipped.append((c['id'], f'exemple {c["ex"]} modifié entre-temps'))
            continue
        en, mot, fr = ex[j]
        en, mot, fr = c.get('en', en), c.get('mot', mot), c.get('fr', fr)
        if mot not in en:
            skipped.append((c['id'], f'mot à trouver « {mot} » absent de la phrase'))
            continue
        ex[j] = (en, mot, fr)
        setex(r, ex)
        done += 1
    for s in skipped:
        print('  ignoré :', *s)
    B.save()
    etat = load(ETAT, {'faits': {}})
    etat['faits'][str(k)] = {'corrections': done, 'ignorées': len(skipped)}
    dump(ETAT, etat)
    print(f'lot {k} : {done} corrections appliquées, {len(skipped)} ignorées')


def nxt(n=2):
    lots, etat = load(LOTS, []), load(ETAT, {'faits': {}})
    rest = [k for k in range(1, len(lots) + 1) if str(k) not in etat['faits']]
    print(' '.join(map(str, rest[:n])) if rest else 'TERMINÉ')
    print(f'# {len(lots) - len(rest)}/{len(lots)} lots faits', file=sys.stderr)


if __name__ == '__main__':
    a = sys.argv[1:]
    {'lots': lambda: make_lots(), 'next': lambda: nxt(int(a[1]) if len(a) > 1 else 2),
     'export': lambda: export(int(a[1])), 'apply': lambda: apply(int(a[1]), a[2])}.get(
        a[0] if a else '', lambda: print(__doc__))()
