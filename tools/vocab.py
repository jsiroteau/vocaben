"""Outil de travail pour vocab.xlsx (base VocabEN).

Usage en ligne de commande (depuis la racine du dépôt) :
    python3 tools/vocab.py show <entrée> [<entrée>...]   affiche une ou plusieurs fiches
    python3 tools/vocab.py grep <regex>                    lignes dont Mot/Traduction/Synonymes correspondent
    python3 tools/vocab.py check                           contrôles automatiques (bloquants, dont mot à trouver en mot entier)
    python3 tools/vocab.py lint                            avertissements : défauts probables à revoir (LINT_OK pour les cas admis)

Usage en Python :
    import sys; sys.path.insert(0, 'tools'); from vocab import *
    B = Base()                       # charge vocab.xlsx
    r = B.find('to grieve', 'to grieve')          # une ligne (liste modifiable)
    r[T] = 'nouvelle traduction'; B.setex(r, [(ex, mot, trad), ...])
    B.insert_after(r, B.row('to grieve', 'to grieve sb', 'verb', 'peiner qn', ex=[...], zipf_of='grieve'))
    B.save()                         # contrôle puis enregistre (refuse si erreur)
"""
import re
import sys

import openpyxl
from openpyxl.styles import Font

FILE = 'vocab.xlsx'
# Index des colonnes
E, M, NAT, T, SYN, ANT, FA = range(7)
FREQ, ZIPF, TYPE = 22, 23, 24
ADM = 25              # Admis 1-5 (colonnes 25 à 29) : formes admises dans le texte à trous, séparées par « / »
NCOL = 30
HEADER_ADM = [f'Admis {k}' for k in range(1, 6)]


def zipf(word):
    try:
        from wordfreq import zipf_frequency
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'wordfreq', '--break-system-packages'])
        from wordfreq import zipf_frequency
    return round(zipf_frequency(word, 'en'), 2)


def freq_class(z):
    return 1 if z >= 4.87 else 2 if z >= 4.16 else 3 if z >= 3.5 else 4


def getex(r):
    return [(r[7 + 3 * k], r[8 + 3 * k], r[9 + 3 * k]) for k in range(5) if r[7 + 3 * k]]


def getadm(r):
    """Formes admises de chaque exemple (liste parallèle à getex), chaînes vides si aucune."""
    return [r[ADM + k] or '' for k in range(5) if r[7 + 3 * k]]


def setadm(r, k, forms):
    """forms : liste de formes (ou chaîne « a / b ») admises pour l'exemple k (0-4)."""
    if isinstance(forms, (list, tuple)):
        forms = ' / '.join(f for f in forms if f)
    r[ADM + k] = forms or None


def setex(r, ex):
    """ex : triplets (exemple, mot à trouver, traduction), ou quadruplets avec les formes admises.
    Sans 4e élément, un exemple inchangé (même phrase, même mot à trouver) garde ses formes admises."""
    assert len(ex) <= 5, 'cinq exemples au plus'
    old = {(r[7 + 3 * k], r[8 + 3 * k]): r[ADM + k] for k in range(5) if r[7 + 3 * k]}
    for k in range(5):
        r[7 + 3 * k] = r[8 + 3 * k] = r[9 + 3 * k] = r[ADM + k] = None
    for k, x in enumerate(ex):
        a, b, c = x[:3]
        r[7 + 3 * k], r[8 + 3 * k], r[9 + 3 * k] = a, b, c
        r[ADM + k] = (' / '.join(x[3]) if isinstance(x[3], (list, tuple)) else x[3]) if len(x) > 3 else old.get((a, b))
        r[ADM + k] = r[ADM + k] or None


class Base:
    def __init__(self, path=FILE):
        self.path = path
        ws = openpyxl.load_workbook(path)['Vocab']
        self.header = [c.value for c in ws[1]][:NCOL]
        if len(self.header) < NCOL:
            assert self.header[:ADM] and self.header[TYPE] == 'Type', 'colonnes inattendues'
            self.header = self.header[:ADM] + HEADER_ADM
        assert self.header[ADM:] == HEADER_ADM, 'colonnes Admis 1-5 attendues après Type'
        self.rows = [list(r)[:NCOL] + [None] * (NCOL - len(r)) for r in ws.iter_rows(min_row=2, values_only=True)]

    setex = staticmethod(setex)
    getex = staticmethod(getex)
    getadm = staticmethod(getadm)
    setadm = staticmethod(setadm)

    def fiche(self, entree):
        return [r for r in self.rows if r[E] == entree]

    def find(self, entree, mot, tr=None):
        """Ligne unique (Entrée, Mot), tr = début de la Traduction pour départager."""
        o = [r for r in self.rows if r[E] == entree and r[M] == mot and (tr is None or (r[T] or '').startswith(tr))]
        assert len(o) == 1, f'{len(o)} ligne(s) pour {entree!r} / {mot!r} / {tr!r}'
        return o[0]

    def row(self, entree, mot, nature, trad, syn=None, ant=None, fa=None, ex=(), zipf_of=None, assoc=False):
        """Nouvelle ligne ; zipf_of = mot distinctif sur lequel calculer la fréquence."""
        r = [None] * NCOL
        r[:7] = [entree, mot, nature, trad, syn, ant, fa]
        setex(r, list(ex))
        if zipf_of:
            r[ZIPF] = zipf(zipf_of)
            r[FREQ] = freq_class(r[ZIPF])
        r[TYPE] = 'association' if assoc else None
        return r

    def insert_after(self, ref, *new):
        i = self.rows.index(ref)
        self.rows[i + 1:i + 1] = list(new)

    def move(self, r, entree, after=None):
        """Déplace une ligne vers une autre fiche (à la fin, ou après la ligne `after`)."""
        self.rows.remove(r)
        r[E] = entree
        if after is None:
            last = max(i for i, x in enumerate(self.rows) if x[E] == entree)
            self.rows.insert(last + 1, r)
        else:
            self.insert_after(after, r)

    def add_entry(self, entree, rows):
        """Nouvelle fiche, insérée à sa place alphabétique."""
        assert not self.fiche(entree), 'la fiche existe déjà'
        names = []
        for r in self.rows:
            if r[E] not in names:
                names.append(r[E])
        nxt = next((n for n in sorted(names + [entree]) if n > entree), None)
        i = len(self.rows) if nxt is None else next(k for k, r in enumerate(self.rows) if r[E] == nxt)
        self.rows[i:i] = rows

    def check(self):
        issues, seen = [], set()
        for r in self.rows:
            for a, m, t in getex(r):
                if not m or m.lower() not in a.lower():
                    issues.append(f'mot à trouver absent : {r[M]} | {a} | {m}')
                if not t:
                    issues.append(f'traduction d\'exemple manquante : {r[M]} | {a}')
                # l'appli remplace la première occurrence (sous-chaîne) : elle doit être un mot entier
                i = a.lower().find(m.lower()) if m else -1
                if i >= 0 and not m.startswith('-') and (
                        (i > 0 and a[i - 1].isalpha()) or (i + len(m) < len(a) and a[i + len(m)].isalpha())):
                    issues.append(f'mot à trouver d\'abord trouvé dans un autre mot : {r[M]} | {a} | {m}')
            if r[T] and ';' in r[T]:
                issues.append(f'« ; » dans Traduction : {r[M]}')
            k = (r[E], r[M], r[T])
            if k in seen:
                issues.append(f'doublon : {k}')
            seen.add(k)
            for k in range(5):
                if r[ADM + k] and not r[7 + 3 * k]:
                    issues.append(f'formes admises sans exemple : {r[M]} | Admis {k + 1}')
                elif r[ADM + k]:
                    forms = [f.strip() for f in str(r[ADM + k]).split('/')]
                    if any(not f for f in forms) or any(f.lower() == (r[8 + 3 * k] or '').lower() for f in forms):
                        issues.append(f'formes admises vides ou identiques au mot à trouver : {r[M]} | {r[ADM + k]}')
            ex = [x[0] for x in getex(r)]
            if len(ex) != len(set(ex)):
                issues.append(f'exemple répété : {r[M]}')
        return issues

    def save(self, force=False):
        issues = self.check()
        if issues and not force:
            raise SystemExit('Contrôle en échec :\n' + '\n'.join(issues[:50]))
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Vocab'
        ws.append(self.header)
        for c in ws[1]:
            c.font = Font(name='Calibri', size=11, bold=True)
        for r in self.rows:
            ws.append(r)
        wb.save(self.path)
        print(f'{len(self.rows)} lignes enregistrées, contrôle OK')


# ── Avertissements (lint) : défauts probables, à revoir à la main ──────────
# Chaque cas revu et jugé correct va dans LINT_OK (catégorie, Mot, cible) pour ne plus être signalé.
LINT_OK = {
    # revus le 6 novembre 2026 : synonyme partiel admis à sens unique
    ('symétrie', 'to assert oneself', 'to stand up for oneself'), ('symétrie', 'bait', 'a lure'),
    ('symétrie', 'to quell sth', 'to crush sth'), ('symétrie', 'to bear witness against sb', 'to testify (against sb)'),
    ('symétrie', 'a longing for sth / a longing to do sth', 'a desire'),
    # renvoi vers une autre nature admis (mot basique ou même famille)
    ('nature', 'a concern (for/about/over)', 'a worry'), ('nature', 'patronage', 'support'), ('nature', 'strain', 'pressure'),
    ('nature', 'a bet', 'a wager'), ('nature', 'a hinge', 'a pivot'), ('nature', 'to match', 'to equal'),
    ('nature', 'a prop', 'a support'), ('nature', '(a) pursuit', 'a search'), ('nature', 'rotten', 'corrupt'),
    ('nature', 'to bill', 'to invoice'), ('nature', 'to stabilize', 'to steady'), ('nature', 'to stabilize sth', 'to steady sth'),
    ('nature', 'to carry on (about)', 'to make a fuss (about/over)'), ('nature', 'to kick up a fuss', 'to make a fuss (about/over)'),
    ('nature', 'to make a fuss (about/over sth) / a fuss', 'to kick up a fuss'),
    ('nature', 'to make a fuss (about/over sth) / a fuss', 'to carry on (about)'),
    ('symétrie', 'an invoice', 'a bill'), ('symétrie', 'a clout', 'a blow'), ('symétrie', 'a patron', 'a backer'),
    ('symétrie', 'a bust', 'a collapse'),  # cas particuliers du mot cible (14 novembre 2026)  # invoice = cas particulier de bill (facture commerciale) : renvoi à sens unique
    ('symétrie', 'largely', 'to a large extent'),  # la cible regroupe plusieurs expressions
    ('GB/US', 'zeal', 'fervour'), ('GB/US', 'to leap (leapt/leaped)', 'to spring'),
    ('symétrie', 'a rise', 'a raise (US)'),  # a raise porte a pay rise (GB)  # marque d'orthographe, pas de variété lexicale
}
# Verbes dont la forme irrégulière est archaïque ou rare (forme régulière usuelle) : formes non exigées
IRREG_OK = {'abide', 'stave', 'blend', 'bless', 'heave', 'disprove', 'lean', 'chide'}
BASIC_ZIPF = 4.5      # verbes irréguliers au-delà : jugés basiques, formes non exigées


def _split0(s, sep):
    """Découpe au niveau 0 des parenthèses (comme splitDepth0 de l'appli)."""
    out, depth, cur, i = [], 0, '', 0
    while i < len(s):
        c = s[i]
        depth += (c == '(') - (c == ')')
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ''; i += len(sep); continue
        cur += c; i += 1
    return [x.strip() for x in out + [cur] if x.strip()]


def _norm(s):
    s = re.sub(r"\b(sb's|sb|sth|oneself|one's)\b", ' ', s.lower()).replace('/', ' ')
    s = re.sub(r'^to\s+', '', ' '.join(s.split()))
    s = re.sub(r'^(a|an|the)\s+', '', s)
    return ' '.join(re.sub(r"[.,!?;:'\"()]", '', s).split())


def _alts(s):
    """Clés de lien d'un Mot ou d'un synonyme (reprend linkKeys de l'appli)."""
    out = set()
    for alt in [y for x in _split0(s or '', ',') for y in _split0(x, ' / ')]:
        bare = alt
        while re.search(r'\([^()]*\)', bare):
            bare = re.sub(r'\([^()]*\)', '', bare)
        for v in (re.sub(r'[()]', '', alt), bare):
            vs = [v]
            for _ in range(6):
                nv = []
                for x in vs:
                    m = re.search(r'[^\s()/]+(?:/[^\s()/]+)+', x)
                    nv += [x[:m.start()] + p + x[m.end():] for p in m.group(0).split('/')] if m else [x]
                vs = nv
            out |= {_norm(x) for x in vs}
    out.discard('')
    return out


def _items(cell):
    return [x for x in _split0(cell or '', ',') if x != '-']


def _marker(r):
    """Marque de variété de la ligne ; aucune pour une ligne à variantes d'orthographe « x (GB) / y (US) »."""
    if '(GB)' in (r[M] or '') and '(US)' in (r[M] or ''):
        return None
    m = re.search(r'\((GB|US)\)', f'{r[M]} {r[T]}')
    return m.group(1) if m else None


def _alts_both(m):
    return '(GB)' in m and '(US)' in m


def lint(B):
    idx = {}
    for r in B.rows:
        for k in _alts(r[M]):
            idx.setdefault(k, []).append(r)
    warn = []
    for r in B.rows:  # comme l'appli : l'intitulé de la fiche sert aussi de clé
        for k in _alts(r[E]):
            if k not in idx:
                idx[k] = [x for x in B.rows if x[E] == r[E]]

    def w(cat, r, cible, msg):
        if (cat, r[M], cible) not in LINT_OK:
            warn.append((cat, f'{r[E]} | {r[M]} → {cible} : {msg}'))

    irr = None
    for r in B.rows:
        for col, lab in ((SYN, 'syn'), (ANT, 'ant')):
            for s in _items(r[col]):
                tg = [t for k in _alts(s) for t in idx.get(k, []) if t is not r]
                if not tg:
                    continue
                same = [t for t in tg if t[NAT] == r[NAT] or 'phrase' in (t[NAT], r[NAT]) or t[E] == r[E]]
                # 1. renvoi vers une ligne d'une autre nature (clear adj. → to clear)
                if not same:
                    w('nature', r, s, f'{lab} : aucune ligne cible de nature {r[NAT]}')
                    continue
                # 2. marque GB/US de la cible non recopiée
                mk = {_marker(t) for t in same}
                if len(mk) == 1 and None not in mk and f'({mk.pop()})' not in s and not _marker(r):
                    w('GB/US', r, s, f'{lab} : la cible porte une marque de variété')
                # 3. symétrie des synonymes
                nat = [t for t in same if t[NAT] == r[NAT] or 'phrase' in (t[NAT], r[NAT])]
                if col == SYN and nat and not any(_alts(r[M]) & {k for x in _items(t[SYN]) for k in _alts(x)} for t in nat):
                    w('symétrie', r, s, 'la cible ne renvoie pas')
        # 4 ter. espaces insécables (Traduction et traductions d'exemples)
        for txt in [r[T]] + [x[2] for x in getex(r)]:
            if txt and re.search(r' [:;?!»]|« |«(?=\S)(?!\u00a0)', txt):
                w('typo', r, '', f'espace insécable manquante : {txt[:60]}')
                break
        # 4 quinquies. variantes GB/US lexicales sur une même ligne (seules les variantes d'orthographe y restent)
        vs = [v for v in _split0(r[M] or '', ' / ') if re.search(r'\((GB|US)\)', v)]
        if len({re.search(r'\((GB|US)\)', v).group(1) for v in vs}) > 1:
            import difflib
            a, b = (re.sub(r'\s*\((GB|US)\)', '', v) for v in vs[:2])
            if difflib.SequenceMatcher(None, a, b).ratio() < 0.7:
                w('GB/US', r, '', 'variantes GB et US sur une même ligne : une ligne par variante')
        # 4 sexies. marque lexicale en fin de Traduction (le Mot ne porte que les variantes d'orthographe « x (GB) / y (US) »)
        if re.search(r'\((GB|US)\)$', r[M] or '') and not _alts_both(r[M]):
            w('GB/US', r, '', 'marque de variété dans le Mot : la placer en fin de Traduction')
        # 4 septies. variante d'orthographe entre parenthèses (behavio(u)r) : écrire « x (GB) / y (US) » ou « x/y »
        for col in (M, SYN, ANT):
            if re.search(r'o\(u\)r|[a-z]\(l\)(?:ing|ment|ed)?\b|enrol\(l\)|fulfil\(l\)', r[col] or ''):
                w('GB/US', r, '', f'variante d\'orthographe entre parenthèses : {r[col]}')
        # 4 quater. ligne marquée (GB)/(US) : la marque termine la traduction de chaque exemple
        mks = set(re.findall(r'\((GB|US)\)', f'{r[M]} {r[T]}'))
        if len(mks) == 1:
            mk = mks.pop()
            if any(not (fr or '').rstrip().endswith(f'({mk})') for _, _, fr in getex(r)):
                w('GB/US', r, '', f'traduction d\'exemple sans la marque ({mk}) finale')
        # 4 bis. mot à trouver à la casse exacte de la phrase
        for j, (en, mot, fr) in enumerate(getex(r), 1):
            if mot and en and mot not in en:
                w('casse', r, f'ex {j}', f'mot à trouver « {mot} » absent à la casse exacte')
        # 4. qn/qch dans la Traduction quand le Mot porte sb/sth
        mot, tr = r[M] or '', r[T] or ''
        mot = re.sub(r'\([^()]*\)', '', mot)
        if ' / ' in mot:
            mot = ''
        if re.search(r'\bsb\b', mot) and 'qn' not in tr and '(' not in tr:
            w('qn/qch', r, '', 'Mot en sb, Traduction sans qn ni complément entre parenthèses')
        if re.search(r'\bsth\b', mot) and 'qch' not in tr and '(' not in tr:
            w('qn/qch', r, '', 'Mot en sth, Traduction sans qch ni complément entre parenthèses')
    # 5. formes irrégulières manquantes (verbes non basiques, première ligne du verbe dans la fiche)
    try:
        from lemminflect import getAllInflections
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'lemminflect', '--break-system-packages'])
        from lemminflect import getAllInflections
    seen = set()
    for r in B.rows:
        m = re.match(r'to (\w+)', r[M] or '')
        if r[NAT] != 'verb' or not m or m.group(1) == 'be':
            continue
        v = m.group(1)
        if (r[E], v) in seen:
            continue
        seen.add((r[E], v))
        if v in IRREG_OK or re.search(r'\((?!sth|sb|on\b|up\b|out\b|for\b|with\b|to\b|doing|at\b|against|from|in\b|into|of\b|over\b|about\b)[a-z-]+[/, )]', r[M]):
            continue
        inf = getAllInflections(v, upos='VERB')
        forms = set(inf.get('VBD', ())) | set(inf.get('VBN', ()))
        regular = {v + 'ed', v + 'd', v[:-1] + 'ied', v + v[-1] + 'ed', v + 'ked'}
        if forms - regular and zipf(v) < BASIC_ZIPF:
            w('formes', r, '', f"verbe irrégulier sans formes ({', '.join(sorted(forms - regular))})")
    return warn


def show(rows):
    for r in rows:
        flags = ' [See also]' if r[TYPE] else ''
        print(f'{r[E]} | {r[M]} ({r[NAT]}) = {r[T]} | syn: {r[SYN] or "-"} | ant: {r[ANT] or "-"}'
              f' | FA: {r[FA] or "-"} | F{r[FREQ]} Z{r[ZIPF]}{flags}')
        for (a, m, t), adm in zip(getex(r), getadm(r)):
            print(f'    {a} [{m}{" | admis : " + adm if adm else ""}] → {t}')


if __name__ == '__main__':
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ('', [])
    B = Base()
    if cmd == 'show':
        for e in args:
            show(B.fiche(e))
    elif cmd == 'grep':
        rx = re.compile(args[0], re.I)
        show([r for r in B.rows if any(rx.search(str(r[c] or '')) for c in (M, T, SYN))])
    elif cmd == 'check':
        iss = B.check()
        print('\n'.join(iss) if iss else f'{len(B.rows)} lignes, contrôle OK')
    elif cmd == 'lint':
        ws = lint(B)
        cats = {}
        for c, msg in ws:
            cats.setdefault(c, []).append(msg)
        for c, l in cats.items():
            print(f'## {c} ({len(l)})')
            print('\n'.join('  ' + x for x in l))
        print(f'{len(ws)} avertissement(s)')
    else:
        print(__doc__)
