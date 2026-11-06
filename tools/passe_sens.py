"""Passe « sens mêlés et sens manquants » (novembre 2026), par lots de fiches (mêmes lots que la passe exemples).

    python3 tools/passe_sens.py next [n]        réserve et affiche les n prochains lots (committer et pousser etat.json aussitôt)
    python3 tools/passe_sens.py export <k>      écrit passes/sens/work/lot_<k>.txt et lot_<k>.json
    python3 tools/passe_sens.py apply <k> <corrections.json>

Opérations (liste JSON), appliquées dans cet ordre : ex, new, move, T.
    {"op": "ex", "id": "r12", "ex": 2, "en": "...", "mot": "...", "fr": "...", "motif": "..."}   remplacer un exemple
    {"op": "new", "nid": "n1", "after": "r12", "M": "...", "NAT": "noun", "T": "...",
     "syn": "...", "ant": "...", "zipf_of": "mot", "assoc": false,
     "ex": [["en", "mot", "fr"], ...], "motif": "..."}         nouvelle ligne (2 à 5 exemples) ; "before": "r12" au lieu de "after" pour l'insérer avant
    {"op": "move", "id": "r12", "en": "<phrase anglaise exacte de l'exemple>", "to": "r13" | "n1", "motif": "..."}
    {"op": "T", "id": "r12", "T": "...", "motif": "..."}                                      Traduction de la ligne
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from vocab import Base, getex, setex, E, M, T, NAT, SYN, ANT, TYPE  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', 'passes', 'sens')
LOTS = os.path.join(os.path.dirname(__file__), '..', 'passes', 'exemples', 'lots.json')
ETAT = os.path.join(ROOT, 'etat.json')
WORK = os.path.join(ROOT, 'work')


def load(p, default):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


def dump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def export(k):
    B = Base()
    fiches = load(LOTS, [])[k - 1]
    orig, out, i = {}, [], 0
    for f in fiches:
        rows = [r for r in B.rows if r[E] == f]
        if not rows:
            continue
        out.append(f'\n======== FICHE « {f} » ========')
        for r in rows:
            i += 1
            rid = f'r{i}'
            ex = getex(r)
            orig[rid] = {'E': r[E], 'M': r[M], 'T': r[T], 'ex': ex}
            see = ' [See also]' if r[TYPE] == 'association' else ''
            out.append(f'### {rid} | {r[M]} ({r[NAT]}){see} = {r[T]}  | syn : {r[SYN] or "-"} | ant : {r[ANT] or "-"}')
            for j, (en, mot, fr) in enumerate(ex, 1):
                out.append(f'  {j}. {en}  [{mot}]  → {fr}')
    dump(os.path.join(WORK, f'lot_{k:02d}.json'), orig)
    open(os.path.join(WORK, f'lot_{k:02d}.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f'lot {k} : {i} lignes')


def apply(k, path):
    if str(k) in load(ETAT, {'faits': {}})['faits']:
        sys.exit(f'lot {k} déjà appliqué : refus (une seconde application dupliquerait les lignes nouvelles)')
    B = Base()
    orig = load(os.path.join(WORK, f'lot_{k:02d}.json'), {})
    ops = json.load(open(path, encoding='utf-8'))
    order = {'ex': 0, 'new': 1, 'move': 2, 'T': 3}
    ops.sort(key=lambda c: order[c['op']])

    def find(rid):
        o = orig.get(rid)
        return next((x for x in B.rows if o and x[E] == o['E'] and x[M] == o['M'] and x[T] == o['T']), None), o

    rows, done, skipped = {}, 0, []
    for rid in {c.get(f) for c in ops for f in ('id', 'after', 'before', 'to')}:
        if rid and rid in orig:
            rows[rid] = find(rid)[0]
    for c in ops:
        try:
            if c['op'] == 'ex':
                r, o = rows.get(c['id']), orig[c['id']]
                ex = getex(r)
                j = c['ex'] - 1
                if ex[j] != tuple(o['ex'][j]):
                    raise ValueError('exemple modifié entre-temps')
                en, mot, fr = ex[j]
                en, mot, fr = c.get('en', en), c.get('mot', mot), c.get('fr', fr)
                if mot not in en:
                    raise ValueError(f'mot à trouver « {mot} » absent')
                ex[j] = (en, mot, fr)
                setex(r, ex)
            elif c['op'] == 'new':
                ref = rows[c.get('after') or c['before']]
                exs = [tuple(x) for x in c['ex']]
                if not 1 <= len(exs) <= 5 or any(m not in e for e, m, _ in exs):
                    raise ValueError('nouvelle ligne : 1 à 5 exemples (2 au moins avec les move), mot à trouver présent')
                nr = B.row(ref[E], c['M'], c['NAT'], c['T'], syn=c.get('syn'), ant=c.get('ant'),
                           ex=exs, zipf_of=c.get('zipf_of'), assoc=c.get('assoc', False))
                if c.get('before'):
                    B.rows.insert(B.rows.index(ref), nr)
                else:
                    B.insert_after(ref, nr)
                rows[c['nid']] = nr
            elif c['op'] == 'move':
                src, dst = rows[c['id']], rows[c['to']]
                ex = getex(src)
                e = next(x for x in ex if x[0] == c['en'])
                if len(getex(dst)) >= 5:
                    raise ValueError('ligne cible pleine (5 exemples)')
                ex.remove(e)
                setex(src, ex)
                setex(dst, getex(dst) + [e])
            elif c['op'] == 'T':
                rows[c['id']][T] = c['T']
            done += 1
        except Exception as err:  # noqa: BLE001
            skipped.append((c.get('id') or c.get('nid'), c['op'], str(err) or type(err).__name__))
    for s in skipped:
        print('  ignoré :', *s)
    for rid, r in rows.items():
        if r is not None and len(getex(r)) < 2:
            print(f'  attention : {rid} « {r[M]} » n\'a plus que {len(getex(r))} exemple(s)')
    B.save()
    etat = load(ETAT, {'faits': {}})
    etat['faits'][str(k)] = {'opérations': done, 'ignorées': len(skipped)}
    etat['en_cours'] = {x: t for x, t in etat.get('en_cours', {}).items() if x != str(k)}
    dump(ETAT, etat)
    print(f'lot {k} : {done} opérations appliquées, {len(skipped)} ignorées')


def nxt(n=2):
    lots, etat = load(LOTS, []), load(ETAT, {'faits': {}})
    now = time.time()
    enc = {x: t for x, t in etat.get('en_cours', {}).items() if now - t < 6 * 3600 and x not in etat['faits']}
    rest = [k for k in range(1, len(lots) + 1) if str(k) not in etat['faits'] and str(k) not in enc]
    pick = rest[:n]
    for k in pick:
        enc[str(k)] = now
    etat['en_cours'] = enc
    dump(ETAT, etat)
    left = len(lots) - len(etat['faits'])
    print(' '.join(map(str, pick)) if pick else ('TERMINÉ' if left == 0 else 'RIEN (lots restants déjà réservés)'))
    print(f'# {len(etat["faits"])}/{len(lots)} lots faits, {len(enc)} réservés', file=sys.stderr)


if __name__ == '__main__':
    a = sys.argv[1:]
    {'next': lambda: nxt(int(a[1]) if len(a) > 1 else 2), 'export': lambda: export(int(a[1])),
     'apply': lambda: apply(int(a[1]), a[2])}.get(a[0] if a else '', lambda: print(__doc__))()
