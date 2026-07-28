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
# 後続フェーズでの改名案など、まだ存在しない想定IDは検査対象から除く
PROPOSED={'s-saas-complete'}   # §3/§10: s-tpl-complete の改名案
for i in sorted(set(re.findall(r'`(s-[a-z0-9-]+)`',sec))):
    if i in PROPOSED: continue
    if ('id="%s"'%i) not in h: ng.append('画面IDが存在しない: '+i)
for i in sorted(set(re.findall(r'`(#[a-z][a-z0-9-]*)`',sec))):
    if re.fullmatch(r'[0-9a-fA-F]{3}|[0-9a-fA-F]{6}', i[1:]): continue   # カラーコードは除外
    if ('id="%s"'%i[1:]) not in h: ng.append('要素IDが存在しない: '+i)
for name,ids in [('完了画面',['s-tpl3','s-saas4','s-tpl3-single','s-saas-done-single']),
                 ('プレビュー画面',['s-tpl2','s-tpl2-single','s-saas-preview','s-saas-preview-single'])]:
    for i in ids:
        if ('id="%s"'%i) not in h: ng.append(f'{name}が存在しない: {i}')
for cls,n in [('next-steps-box',4),('auto-code-note',4),('excluded-rows-box',4)]:
    if cls not in h: ng.append('クラス未定義: '+cls)
if h.count('最大500行・5MB）'): ng.append('種別を無視した500行表記が残存')
if '_失敗行_{YYYYMMDD}.csv' in r: ng.append('CSV拡張子が仕様とモックで不一致')
# 適用範囲の網羅: §7.1〜§9.7 の全小節に「適用範囲」行があるか (テンプレ/外部の混同防止)
for m in re.finditer(r'^### ([789]\.\d+)\s[^\n]*\n(.{0,400})', r, re.M|re.S):
    if '適用範囲:' not in m.group(2): ng.append('適用範囲の記載がない: §'+m.group(1))
# 章レベルの適用範囲
for head in ['## 1. テンプレートインポート','## 3. マッピング不可項目の補完','## 5. UI配置']:
    i=r.find(head)
    if i<0 or '適用範囲:' not in r[i:i+700]: ng.append('章の適用範囲がない: '+head)
# 外部勤怠画面にフェーズバナーが配られる実装があるか
if 's-tpl-complete' not in h[h.find('function renderPhaseBanners'):h.find('function renderPhaseBanners')+700]:
    ng.append('補完画面がフェーズバナーの対象外')
print('\n'.join('NG  '+x for x in ng) if ng else 'すべて整合')
sys.exit(1 if ng else 0)
