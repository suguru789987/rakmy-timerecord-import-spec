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
# 方式の交差汚染検査 (テンプレ/外部勤怠が互いに混じっていないか)
# 「テンプレートのみ」の節が s-saas* を実装例として引用していたら検出する。
# 先行実装の仕様が後続実装の画面を根拠にすると、不要な工数が生まれるため。
_secs=[(m.start(), m.group(2)) for m in re.finditer(r'^(#{2,3})\s*(\d+(?:\.\d+)?)[.\s]', r, re.M)]+[(len(r),'END')]
for _i in range(len(_secs)-1):
    _b = r[_secs[_i][0]:_secs[_i+1][0]]
    _m = re.search(r'\*\*適用範囲:\s*([^*]+?)\*\*', _b)
    if not _m: continue
    _lab = _m.group(1).strip()
    _body = _b[_m.end():]          # 適用範囲の注記そのものは除外して本文だけ見る
    # 検出するのは「外部勤怠の画面を実装例・参考として引用している」場合のみ。
    # 現状説明やスコープ注記としての言及は正当なので対象外。
    # 先行実装の対象(テンプレートのみ / 両方式共通)は s-saas* を実装例にしてはならない。
    # 先行実装では s-saas* 系を作らないため(§0.2)。
    if _lab.startswith('テンプレートのみ') or _lab.startswith('両方式共通'):
        for _line in _body.split('\n'):
            _hit = re.search(r'(実装例|参考|と同じ形式|に倣[うい]|を踏襲)', _line)
            if not _hit: continue
            if not re.search(r'`s-saas[a-z0-9-]*`|単票プレビュー', _line): continue
            # 否定文・経緯の説明・スコープ注記は対象外(「誤って引用した」等)
            if re.search(r'誤って|してはならない|ではない|不要|後続フェーズ|参照用|対象外', _line): continue
            ng.append('§'+_secs[_i][1]+' が外部勤怠の画面を実装例として引用している')
            break
    if _lab.startswith('外部勤怠のみ') and re.search(r'実装例[^\n]*`s-tpl', _body):
        ng.append('§'+_secs[_i][1]+' は外部勤怠のみだがテンプレートの画面を実装例にしている')
if '行内3択アクション' in r and '先行実装では不要' not in r:
    ng.append('§7.2 に行内3択アクションが要件として残存している')

# §0 前提条件の存在と内容 (一般論での仕様作成を防ぐ土台)
if '## 0. 前提条件' not in r: ng.append('§0 前提条件が存在しない')
else:
    z = r[r.find('## 0. 前提条件'): r.find('## 1. テンプレートインポート')]
    for k in ['origin/feature/189','roleEnum','userStoreAssignments','employmentCategoryEnum','employee_code','neon-http']:
        if k not in z: ng.append('§0 に前提の記載がない: '+k)
    if '本節に書かれていない前提で判断してはならない' not in z:
        ng.append('§0 に運用ルール(一般論禁止)の記載がない')

# 仕様が主張する実体の検査 (文字列の有無だけでなく実装を見る)
if 'BOM付きUTF-8' in r:
    dl = h.count("new Blob(['\\ufeff'")
    if dl == 0: ng.append('§9.5 はBOM付きUTF-8と定めているが、モックのBlobにBOMが無い')
if 'EMP-{5桁のランダム数字}' in r or '5桁のランダム数字' in r:
    if 'EMP-{companyId' in r: ng.append('§8.1 に旧採番規則(companyIdプレフィックス)が残存')

# 適用範囲ラベルの語彙固定 (表記ゆれ防止)
VOCAB={'テンプレートのみ（先行実装）','外部勤怠のみ（後続実装）','両方式共通','方式別に定義済み'}
for l in {x.strip() for x in re.findall(r'\*\*適用範囲:\s*([^*]+?)\*\*', r)}:
    if l not in VOCAB: ng.append('適用範囲ラベルの表記ゆれ: '+l)

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
