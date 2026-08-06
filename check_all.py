#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全資料の整合を機械的に検査する。

使い方:
    python3 check_all.py

TSV・仕様書・ヘルプ・配布用エクセル・デスクトップの配布物を横断して、
数字の食い違いや参照切れを検出する。終了コード0で整合。

**資料を1つでも直したら、必ずこれを実行すること。**
件数や列数は複数の資料に複製されているため、1箇所直すと他が古くなる。
"""
import io, os, re, sys, collections

B = os.path.dirname(os.path.abspath(__file__))
DESK = os.path.expanduser('~/Desktop/タイムレコード_20260805')
NG = []


def ng(category, msg):
    NG.append((category, msg))


def load(name):
    p = os.path.join(B, name)
    rows = [r.split('\t') for r in io.open(p, encoding='utf-8').read().rstrip('\n').split('\n')]
    return rows[0], [r for r in rows[1:] if r[0] != '#']


def read(name, base=B):
    p = os.path.join(base, name)
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else ''


# ---------------------------------------------------------------- 1. 受け入れ条件
hd, D = load('20260804_受け入れ条件_定義表.tsv')
hc, C = load('20260804_受け入れ条件_確認表.tsv')
d = {r[1]: r for r in D}
c = {r[0]: r for r in C}

if set(d) != set(c):
    ng('受け入れ条件', f'定義表と確認表で条件IDが違う: {sorted(set(d) ^ set(c))}')
for k in sorted(set(d) & set(c)):
    for name, x, y in [('フロー', d[k][2], c[k][1]), ('MVP区分', d[k][5], c[k][2]),
                       ('マイルストーン', d[k][3], c[k][3]), ('満たすべきこと', d[k][4], c[k][4])]:
        if x.strip() != y.strip():
            ng('受け入れ条件', f'{k} の{name}が2表で違う（定義表「{x}」／確認表「{y}」）')

for label, rows, i in [('満たすべきこと', D, 4), ('合致していると言える状態', C, 6)]:
    g = collections.defaultdict(list)
    for r in rows:
        g[r[i].strip()].append(r[1] if rows is D else r[0])
    for text, ids in g.items():
        if len(ids) > 1:
            ng('受け入れ条件', f'{label}が同じ条件が複数: {" ".join(ids)} → {text[:40]}')

# 条件の本文が参照する条件IDが実在するか
for r in C:
    for m in re.findall(r'AC-\d+', r[6]):
        if m not in c:
            ng('受け入れ条件', f'{r[0]} の合致条件が存在しない {m} を参照している')

# ---------------------------------------------------------------- 2. 検証プラン
ho, OP = load('20260803_検証プラン_操作系.tsv')
ha, CA = load('20260803_検証プラン_計算系.tsv')
_, DS = load('20260803_検証用データセット.tsv')
vids = {r[1] for r in OP} | {r[0] for r in CA}
dids = {r[0] for r in DS}

used = collections.Counter()
for r in C:
    for m in re.findall(r'(?:OP|CA)-\d+', r[8]):
        used[m] += 1
        if m not in vids:
            ng('検証プラン', f'{r[0]} の根拠にある {m} が検証プランに無い')
for v in sorted(vids - set(used)):
    ng('検証プラン', f'{v} はどの受け入れ条件からも参照されていない')

for r in OP + CA:
    for m in re.findall(r'D\d+-\d+', ' '.join(r)):
        if m not in dids:
            ng('検証データ', f'検証プランが存在しない {m} を参照している')
for r in DS:
    for m in re.findall(r'(?:OP|CA)-\d+', r[5]):
        if m not in vids:
            ng('検証データ', f'{r[0]} の用途にある {m} が検証プランに無い')

# ---------------------------------------------------------------- 3. 実データの数
lv = collections.Counter(r[2] for r in C)
N = {
    '受け入れ条件': len(C),
    'MVP必須': lv['MVP必須'],
    'リリース必須': lv['リリース必須'],
    '改善': lv['改善'],
    '操作系': len(OP),
    '計算系': len(CA),
    '検証項目': len(OP) + len(CA),
    'データセット': len(DS),
    '操作系の列': len(ho),
    '計算系の列': len(ha),
}

# ---------------------------------------------------------------- 4. 資料に書かれた数と突き合わせ
spec = read('20260803_CSV一括登録機能_仕様書（PdM向け）.md')
CHECKS = [
    ('仕様書', r'\*\*何を守るか・なぜか\*\*（(\d+)件）', N['受け入れ条件']),
    ('仕様書', r'\*\*実装が条件に合致しているかの確認\*\*（(\d+)件）', N['受け入れ条件']),
    ('仕様書', r'エンジニアはMVP必須の(\d+)件を先に潰して', N['MVP必須']),
    ('仕様書', r'\| MVP必須(\d+)件がすべて合格 \|', N['MVP必須']),
    ('仕様書', r'操作手順と期待値(\d+)件', N['操作系']),
    ('仕様書', r'数値・件数・上限の確認(\d+)件', N['計算系']),
    ('仕様書', r'検証に使うデータ(\d+)件', N['データセット']),
    ('仕様書', r'検証項目は(\d+)件です', N['検証項目']),
    ('仕様書', r'操作系（(\d+)列）', N['操作系の列']),
    ('仕様書', r'計算系（(\d+)列）', N['計算系の列']),
]
for doc, pat, want in CHECKS:
    for got in re.findall(pat, spec):
        if int(got) != want:
            ng(doc, f'「{pat}」が {got} だが実データは {want}')

# 実装レベルの件数表
m = re.search(r'\| \*\*MVP必須\*\* \|[^|]+\| \*\*(\d+)件\*\* \|', spec)
if m and int(m.group(1)) != N['MVP必須']:
    ng('仕様書', f'MVP区分の表が {m.group(1)}件 だが実データは {N["MVP必須"]}件')

# フロー別の件数
for f in '1234':
    rows = [r for r in C if f in [x.strip() for x in r[1].split('/')]]
    mvp = sum(1 for r in rows if r[2] == 'MVP必須')
    pat = r'\| \*\*' + f + r'\*\* \| [^|]+ \| (\d+)件 \| \*\*(\d+)件\*\* \| (\d+)件 \|'
    mm = re.search(pat, spec)
    if mm:
        if int(mm.group(1)) != len(rows):
            ng('仕様書', f'フロー{f}の受け入れ条件が {mm.group(1)}件 だが実データは {len(rows)}件')
        if int(mm.group(2)) != mvp:
            ng('仕様書', f'フロー{f}のMVP必須が {mm.group(2)}件 だが実データは {mvp}件')

# ---------------------------------------------------------------- 5. ヘルプ（顧客に出す本文）
help_md = read('20260804_Notion掲載用_CSVで一括登録する.md')
draft = read('20260803_ヘルプページ_CSV一括登録_ドラフト.md')
for word, why in [('⚠️要確認', '実装未確定の内部メモ'), ('要確認：', '内部メモ'),
                  ('TODO', '作業メモ'), ('掲載しません', '作業用の節')]:
    if word in help_md:
        ng('ヘルプ', f'掲載本文に「{word}」が残っている（{why}）')
for ch in '①②③④⑤⑥⑦⑧⑨':
    if ch in help_md:
        ng('ヘルプ', f'掲載本文に丸数字「{ch}」が残っている（表示環境で潰れる）')
        break
if '業態・ブランド' in help_md:
    ng('ヘルプ', '掲載本文に旧表記「業態・ブランド」がある（2026-06-24 に業態へ統合）')
# 節番号の連番
nums = [int(m) for m in re.findall(r'^## (\d+)\. ', help_md, re.M)]
if nums != list(range(1, len(nums) + 1)):
    ng('ヘルプ', f'節番号が連番でない: {nums}')
# 本文が参照する節番号が実在するか
for m in set(re.findall(r'「(\d+)\. ', help_md)):
    if int(m) not in nums:
        ng('ヘルプ', f'本文が存在しない節「{m}番」を参照している')

# ---------------------------------------------------------------- 6. 配布用エクセルの数字
def xlsx_cells(name):
    """配布用エクセルの全セルを (シート名, 行, 列, 値) で返す。openpyxl が無ければ空。"""
    p = os.path.join(DESK, name)
    if not os.path.exists(p):
        return None
    try:
        from openpyxl import load_workbook
    except ImportError:
        return None
    wb = load_workbook(p)
    out = []
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    out.append((ws.title, c.row, c.column, c.value))
    return out


def xlsx_pair(name, label, want, col=2):
    """A列が label の行の col 列が want と一致するか。"""
    cells = xlsx_cells(name)
    if cells is None:
        return
    byrow = {}
    for _, r, cc, v in cells:
        byrow.setdefault(r, {})[cc] = v
    found = False
    for r, d in byrow.items():
        if str(d.get(1, '')).strip() == label:
            found = True
            got = d.get(col)
            if str(got).strip() != str(want):
                ng('配布エクセル', f'{name} の「{label}」が {got} だが実データは {want}')
    if not found:
        ng('配布エクセル', f'{name} に「{label}」の行が見つからない（検査が空振りしている）')


ms = collections.Counter(r[3] for r in C)
if os.path.isdir(DESK):
    for label, want in [('MVP必須', N['MVP必須']), ('リリース必須', N['リリース必須']),
                        ('改善', N['改善'])]:
        xlsx_pair('20260805_タイムレコード_00_定義表.xlsx', label, want)
    for f in '1234':
        rows = sum(1 for r in C if f in [x.strip() for x in r[1].split('/')])
        cells = xlsx_cells('20260805_タイムレコード_00_定義表.xlsx') or []
        hit = [v for _, r, cc, v in cells if cc == 1 and isinstance(v, str) and v.startswith(f'フロー{f} ')]
        if not hit:
            ng('配布エクセル', f'00_定義表.xlsx に「フロー{f}」の行が無い（検査が空振りしている）')
        else:
            byrow = {}
            for _, r, cc, v in cells:
                byrow.setdefault(r, {})[cc] = v
            for r, d in byrow.items():
                if isinstance(d.get(1), str) and d[1].startswith(f'フロー{f} '):
                    if str(d.get(2)).strip() != str(rows):
                        ng('配布エクセル', f'00_定義表.xlsx のフロー{f}が {d.get(2)} だが実データは {rows}')
    # 使い方
    use = xlsx_cells('20260805_タイムレコード_使い方.xlsx')
    if use is not None:
        text = '\n'.join(str(v) for _, _, _, v in use)
        m = re.search(r'MVP必須(\d+)件をエンジニアと合意', text)
        if not m:
            ng('配布エクセル', '使い方.xlsx に「MVP必須N件をエンジニアと合意」が無い（検査が空振りしている）')
        elif int(m.group(1)) != N['MVP必須']:
            ng('配布エクセル', f'使い方.xlsx のMVP必須が {m.group(1)}件 だが実データは {N["MVP必須"]}件')
        m = re.search(r'(\d+)〜(\d+)行 ?│? ?受入条件(\d+)件', text.replace(' ', ''))
        if f'受入条件{N["受け入れ条件"]}件' not in text.replace(' ', ''):
            ng('配布エクセル', f'使い方.xlsx の受入条件件数が {N["受け入れ条件"]}件 と書かれていない')

# ---------------------------------------------------------------- 7. 配布物の同期
PAIRS = [
    ('ヘルプページ/ヘルプページ_掲載用.md', '20260804_Notion掲載用_CSVで一括登録する.md'),
    ('Notion貼り付け用_md/02_ヘルプ_本文.md', '20260804_Notion掲載用_CSVで一括登録する.md'),
    ('ヘルプページ/ヘルプページ_作業用（チェックリスト付き）.md', '20260803_ヘルプページ_CSV一括登録_ドラフト.md'),
    ('仕様書/仕様書（PdM向け）.md', '20260803_CSV一括登録機能_仕様書（PdM向け）.md'),
]
if os.path.isdir(DESK):
    for desk, repo in PAIRS:
        a, b = read(desk, DESK), read(repo)
        if not a:
            ng('配布物', f'デスクトップに {desk} が無い')
        elif a != b:
            ng('配布物', f'{desk} がリポジトリの {repo} と違う')
else:
    print(f'（デスクトップ {DESK} が見つからないため配布物の確認は省略）\n')

# ---------------------------------------------------------------- 出力
print('=' * 72)
print('  実データ')
print('=' * 72)
for k, v in N.items():
    print(f'  {k:<16} {v}')
print()
print('=' * 72)
print('  検査結果')
print('=' * 72)
if not NG:
    print('  整合しています。')
    sys.exit(0)
g = collections.defaultdict(list)
for cat, msg in NG:
    g[cat].append(msg)
for cat, msgs in g.items():
    print(f'\n  ■ {cat}（{len(msgs)}件）')
    for m in msgs:
        print(f'    - {m}')
print(f'\n  合計 {len(NG)} 件')
sys.exit(1)
