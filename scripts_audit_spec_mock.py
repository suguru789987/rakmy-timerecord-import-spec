#!/usr/bin/env python3
"""仕様書(README §7〜§9)とモック(index.html)の整合を機械的に検査する。
仕様を変更したら必ずこれを実行すること。"""
import io,re,sys
B='/Users/sugurutsutsui/Projects/rakmy-timerecord-import-spec/'
r=io.open(B+'README.md',encoding='utf-8').read(); h=io.open(B+'index.html',encoding='utf-8').read()
sec=r[r.find('## 7. 仕様決定事項'):]; ng=[]
SKIP={'resolveAdminRegistrationType','go'}   # 画面に出さない社内用語 / 既存関数
for f in sorted(set(re.findall(r'`([a-zA-Z_][a-zA-Z0-9_]*)\(\)`',sec))):
    if f in SKIP: continue
    if ('function '+f) not in h: ng.append('関数が存在しない: '+f)
for i in sorted(set(re.findall(r'`(s-[a-z0-9-]+)`',sec))):
    if ('id="%s"'%i) not in h: ng.append('画面IDが存在しない: '+i)
for i in sorted(set(re.findall(r'`(#[a-z][a-z0-9-]*)`',sec))):
    if re.match(r'#[0-9a-f]{3,6}$',i[1:]): continue
    if ('id="%s"'%i[1:]) not in h: ng.append('要素IDが存在しない: '+i)
for name,ids in [('完了画面',['s-tpl3','s-saas4','s-tpl3-single','s-saas-done-single']),
                 ('プレビュー画面',['s-tpl2','s-tpl2-single','s-saas-preview','s-saas-preview-single'])]:
    for i in ids:
        if ('id="%s"'%i) not in h: ng.append(f'{name}が存在しない: {i}')
for cls,n in [('next-steps-box',4),('auto-code-note',4),('excluded-rows-box',4)]:
    if cls not in h: ng.append('クラス未定義: '+cls)
if h.count('最大500行・5MB）'): ng.append('種別を無視した500行表記が残存')
if '_失敗行_{YYYYMMDD}.csv' in r: ng.append('CSV拡張子が仕様とモックで不一致')
print('\n'.join('NG  '+x for x in ng) if ng else 'すべて整合')
sys.exit(1 if ng else 0)
