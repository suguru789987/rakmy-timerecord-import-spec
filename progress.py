#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""受け入れ条件表の「実装状況」「判定」を集計し、マイルストーンの達成度とリリース可否を出す。

使い方:
    python3 progress.py

受け入れ条件表の「実装状況」列に ○ / △ / ×、「判定」列に 合格 / 不合格 を記入してから実行する。
空欄は「未確認」として扱う。
"""
import io, os, sys, collections

B = os.path.dirname(os.path.abspath(__file__))
AC_PATH = os.path.join(B, '20260803_受け入れ条件表.tsv')
MS_PATH = os.path.join(B, '20260804_実装マイルストーン表.tsv')

def load(p):
    return [r.split('\t') for r in io.open(p, encoding='utf-8').read().rstrip('\n').split('\n')]

ac = [r for r in load(AC_PATH)[1:] if r[0] != '#']
ms = {r[0]: r[1] for r in load(MS_PATH)[1:] if r[0] not in ('#', '合計')}

MS_I, MVP_I, JUDGE_I, IMPL_I = 2, 4, 12, 11

def state(r):
    j = r[JUDGE_I].strip()
    if j.startswith('合格'): return '合格'
    if j.startswith('不合格'): return '不合格'
    return '未確認'

print('=' * 68)
print('  マイルストーン別の達成度')
print('=' * 68)
blockers = []
for k in ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']:
    rows = [r for r in ac if r[MS_I] == k and r[MVP_I] == 'MVP必須']
    c = collections.Counter(state(r) for r in rows)
    done = c['合格']
    total = len(rows)
    bar = '█' * done + '·' * (total - done)
    mark = '完了' if done == total and total else ('着手' if done else '未着手')
    print(f'  {k} {ms.get(k, ""):22} MVP必須 {done:>2}/{total:<2} {bar:<12} {mark}')
    blockers += [r[1] for r in rows if state(r) == '不合格']

print()
allmvp = [r for r in ac if r[MVP_I] == 'MVP必須']
c = collections.Counter(state(r) for r in allmvp)
print(f'  MVP必須 合計   合格 {c["合格"]} / 不合格 {c["不合格"]} / 未確認 {c["未確認"]}  （全 {len(allmvp)} 件）')
rel = [r for r in ac if r[MVP_I] == 'リリース必須']
cr = collections.Counter(state(r) for r in rel)
print(f'  リリース必須     合格 {cr["合格"]} / 不合格 {cr["不合格"]} / 未確認 {cr["未確認"]}  （全 {len(rel)} 件）')

print()
print('=' * 68)
print('  リリース判断')
print('=' * 68)
if c['未確認']:
    print(f'  判定できません。MVP必須に未確認が {c["未確認"]} 件あります')
elif c['不合格']:
    print(f'  リリース不可。MVP必須に不合格が {c["不合格"]} 件あります')
    print('    ' + ' '.join(blockers))
elif cr['不合格']:
    print(f'  条件付きでリリース可。リリース必須に不合格が {cr["不合格"]} 件あります')
    print('    影響を確認し、回避策を案内できるか判断してください')
    print('    ' + ' '.join(r[1] for r in rel if state(r) == '不合格'))
else:
    print('  リリース可。MVP必須とリリース必須がすべて合格しています')

if c['不合格'] or cr['不合格']:
    print()
    print('  不合格の内訳（崩れると起きること）')
    for r in ac:
        if state(r) == '不合格' and r[MVP_I] in ('MVP必須', 'リリース必須'):
            print(f'    {r[1]} [{r[MVP_I]}] {r[3][:34]}')
            print(f'      → {r[8][:76]}')
sys.exit(1 if (c['不合格'] or c['未確認']) else 0)
