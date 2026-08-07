#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""仕様書に書かれた件数・列数を、TSVの実データから書き直す。

使い方:
    python3 sync_docs.py          # 書き直す
    python3 sync_docs.py --check  # 書き直さずに、古い箇所があるかだけ見る

**仕様書に数字を手で書かないこと。** ここに登録した箇所は実データから生成される。
数字を書く場所を増やしたら、下の RULES に1行足す（置換できなければ異常として止まる）。
"""
import io, os, re, sys

B = os.path.dirname(os.path.abspath(__file__))
SPEC = '20260803_CSV一括登録機能_仕様書（PdM向け）.md'


def load(name):
    p = os.path.join(B, name)
    rows = [r.split('\t') for r in io.open(p, encoding='utf-8').read().rstrip('\n').split('\n')]
    return rows[0], [r for r in rows[1:] if r[0] != '#']


def counts():
    hd, D = load('20260804_受け入れ条件_定義表.tsv')
    hc, C = load('20260804_受け入れ条件_確認表.tsv')
    ho, OP = load('20260803_検証プラン_操作系.tsv')
    ha, CA = load('20260803_検証プラン_計算系.tsv')
    _, DS = load('20260803_検証用データセット.tsv')
    lvl = hc.index('MVP区分')
    flow = hc.index('フロー')
    import collections
    lv = collections.Counter(r[lvl] for r in C)
    n = {
        '受け入れ条件': len(C), 'MVP必須': lv['MVP必須'], 'リリース必須': lv['リリース必須'],
        '改善': lv['改善'], '対象外': lv['—'],
        '操作系': len(OP), '計算系': len(CA), '検証項目': len(OP) + len(CA),
        'データセット': len(DS), '操作系の列': len(ho), '計算系の列': len(ha),
        'マイルストーン数': len({r[hc.index('マイルストーン')] for r in C}),
    }
    for f in '1234':
        rows = [r for r in C if f in [x.strip() for x in r[flow].split('/')]]
        n[f'フロー{f}条件'] = len(rows)
        n[f'フロー{f}MVP'] = sum(1 for r in rows if r[lvl] == 'MVP必須')
    # フロー別の検証項目数
    fo, fa = ho.index('フロー'), ha.index('フロー')
    for f in '1234':
        n[f'フロー{f}検証'] = (sum(1 for r in OP if f in [x.strip() for x in r[fo].split('/')])
                              + sum(1 for r in CA if f in [x.strip() for x in r[fa].split('/')]))
    return n


# (説明, 正規表現, 置き換える値のキー)
# 正規表現は「前 / 数字 / 後」の3グループ。数字だけを差し替え、前後はそのまま残す。
RULES = [
    ('定義表の件数',        r'(\*\*何を守るか・なぜか\*\*（)(\d+)(件）)', '受け入れ条件'),
    ('確認表の件数',        r'(\*\*実装が条件に合致しているかの確認\*\*（)(\d+)(件）)', '受け入れ条件'),
    ('図中の受け入れ条件',  r'(受け入れ条件（)(\d+)(件）)', '受け入れ条件'),
    ('図中の検証項目',      r'(検証項目（)(\d+)(件）)', '検証項目'),
    ('操作系の件数',        r'(操作手順と期待挙動)(\d+)(件)', '操作系'),
    ('計算系の件数',        r'(数値・件数・上限の確認)(\d+)(件)', '計算系'),
    ('データセットの件数',  r'(検証に使うデータ)(\d+)(件)', 'データセット'),
    ('検証項目の合計',      r'(検証項目は)(\d+)(件です)', '検証項目'),
    ('内訳（操作系）',      r'(（操作系)(\d+)(・計算系)', '操作系'),
    ('内訳（計算系）',      r'(・計算系)(\d+)(）)', '計算系'),
    ('操作系の列数',        r'(操作系（)(\d+)(列）)', '操作系の列'),
    ('計算系の列数',        r'(計算系（)(\d+)(列）)', '計算系の列'),
    ('MVP必須（区分表）',   r'(導入が完了しない \| \*\*)(\d+)(件\*\* \|)', 'MVP必須'),
    ('リリース必須（区分表）', r'(無いと問い合わせや誤解が起きる \| )(\d+)(件 \|)', 'リリース必須'),
    ('改善（区分表）',      r'(無くても運用は回る。余力があれば \| )(\d+)(件 \|)', '改善'),
    ('対象外（区分表）',    r'(対象外・検証の前提（実装対象ではない） \| )(\d+)(件 \|)', '対象外'),
    ('MVP必須を先に潰す',   r'(エンジニアはMVP必須の)(\d+)(件を先に潰して)', 'MVP必須'),
    ('リリース可の条件',    r'(\| MVP必須)(\d+)(件がすべて合格 \|)', 'MVP必須'),
]
# フロー別の表（1行に 条件数・MVP必須・検証項目 の3つ）
for _f in '1234':
    _head = r'(\| \*\*' + _f + r'\*\* \| [^|]+ \| )'
    RULES.append((f'フロー{_f}の条件数',
                  _head + r'(\d+)(件 \| \*\*\d+件\*\* \| \d+件 \|)', f'フロー{_f}条件'))
    RULES.append((f'フロー{_f}のMVP必須',
                  r'(\| \*\*' + _f + r'\*\* \| [^|]+ \| \d+件 \| \*\*)(\d+)(件\*\* \| \d+件 \|)', f'フロー{_f}MVP'))
    RULES.append((f'フロー{_f}の検証項目',
                  r'(\| \*\*' + _f + r'\*\* \| [^|]+ \| \d+件 \| \*\*\d+件\*\* \| )(\d+)(件 \|)', f'フロー{_f}検証'))


def render(text, n):
    """仕様書の数字を実データに合わせる。置換できないルールがあれば例外にする。"""
    miss = []
    for name, pat, key in RULES:
        want = str(n[key])
        new, cnt = re.subn(pat, lambda m, w=want: m.group(1) + w + m.group(3), text)
        if cnt == 0:
            miss.append(name)
        text = new
    if miss:
        raise SystemExit('数字を書く場所が見つかりません: ' + ' / '.join(miss)
                         + '\n仕様書の文言を変えたら sync_docs.py の RULES も直してください。')
    return text


def main():
    n = counts()
    p = os.path.join(B, SPEC)
    cur = io.open(p, encoding='utf-8').read()
    new = render(cur, n)
    if '--check' in sys.argv:
        if cur != new:
            print('仕様書の数字が実データと違います。python3 sync_docs.py を実行してください。')
            sys.exit(1)
        print('仕様書の数字は実データと一致しています。')
        sys.exit(0)
    if cur == new:
        print(f'仕様書の数字は最新です（{len(RULES)}箇所を確認）')
    else:
        io.open(p, 'w', encoding='utf-8').write(new)
        print(f'仕様書の数字を書き直しました（{len(RULES)}箇所）')
    for k in ['受け入れ条件', 'MVP必須', '検証項目', 'データセット', '操作系の列']:
        print(f'  {k:<12} {n[k]}')


if __name__ == '__main__':
    main()
