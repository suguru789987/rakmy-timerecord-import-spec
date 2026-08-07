# -*- coding: utf-8 -*-
"""TSV → 配布用エクセル（01・02）を同期する"""
import io,os,re
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.cell.rich_text import CellRichText,TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.utils import get_column_letter
os.chdir(os.path.expanduser('~/Projects/rakmy-timerecord-import-spec'))
D=os.path.expanduser('~/Desktop/タイムレコード_20260805')
def rich(s):
    if not isinstance(s,str) or '**' not in s: return s
    parts=re.split(r'\*\*(.+?)\*\*', s); out=[]
    for i,x in enumerate(parts):
        if x: out.append(TextBlock(InlineFont(b=True,sz=10) if i%2 else InlineFont(sz=10), x))
    return CellRichText(*out)
def load(p):
    r=[x.split('\t') for x in io.open(p,encoding='utf-8').read().rstrip('\n').split('\n')]
    return {n:i for i,n in enumerate(r[0])},[x for x in r[1:] if x[0]!='#']

# ---- 01 受入条件表（書式・集計式を保って上書き）----
hc,C=load('20260804_受け入れ条件_確認表.tsv'); hd,Dd=load('20260804_受け入れ条件_定義表.tsv')
c={r[0]:r for r in C}; d={r[hd['条件ID']]:r for r in Dd}
p1=os.path.join(D,'20260805_タイムレコード_01_受入条件表.xlsx')
wb=load_workbook(p1, rich_text=True); ws=wb.active
hx={str(ws.cell(28,i).value):i for i in range(1,ws.max_column+1)}
SRC={'設計ポイント':lambda k:d[k][hd['設計ポイント']],'実装レベル':lambda k:c[k][hc['MVP区分']],
 '何を実装するか':lambda k:c[k][hc['満たすべきこと']],
 '合格ライン（この数値を満たせば実装完了）':lambda k:c[k][hc['合致していると言える状態']],
 '実装できていないと起きること':lambda k:d[k][hd['崩れると起きること']],
 'フロー':lambda k:c[k][hc['フロー']],'確認する画面':lambda k:c[k][hc['実装箇所（画面・機能）']],
 '確認方法':lambda k:c[k][hc['確認方法']],'仕様書の根拠':lambda k:d[k][hd['仕様の該当箇所']],
 '対応検証ID':lambda k:c[k][hc['根拠（検証ID）']],'ヘルプ該当箇所':lambda k:c[k][hc['ヘルプ該当箇所']]}
n1=0
for r in range(29,ws.max_row+1):
    k=ws.cell(r,hx['条件ID']).value
    if k not in c: continue
    for col,fn in SRC.items():
        if col not in hx: continue
        want=fn(k)
        if str(ws.cell(r,hx[col]).value or '')!=want.replace('**',''):
            ws.cell(r,hx[col]).value=rich(want); n1+=1
wb.save(p1)

# ---- 02 検証プラン（作り直し）----
o,OP=load('20260803_検証プラン_操作系.tsv'); a,CA=load('20260803_検証プラン_計算系.tsv')
COLS=[('段階',15),('検証ID',10),('フロー',8),('検証内容',26),('先に実施する検証',24),
      ('初期設定（前提データ・データセット）',36),('操作・前提条件／入力値',46),('期待挙動（判定基準）',50),
      ('スクショファイル名',30),('証跡（撮る画面と状態）',42),('画面（どこを開いて操作するか）',46),
      ('確認ポイント',34),('対応する条件ID',16),('ヘルプ該当箇所',42),('実際の値',24),('判定',10),('計算根拠・備考',24)]
def row(ix,r):
    ope='操作・前提条件' if '操作・前提条件' in ix else '入力値'
    v=r[ix[ope]] if ope=='操作・前提条件' else '入力値: '+r[ix[ope]]
    last='根拠・備考' if '根拠・備考' in ix else '計算根拠'
    return [r[ix['段階']],r[ix['検証ID']],r[ix['フロー']],r[ix['検証内容']],r[ix['先に実施する検証']],
            r[ix['初期設定（前提データ）']],v,r[ix['期待挙動（判定基準）']],
            r[ix['スクショファイル名']],r[ix['証跡（撮る画面と状態）']],r[ix['画面（どこを開いて操作するか）']],
            r[ix['確認ポイント']],r[ix['対応する条件ID']],r[ix['ヘルプ該当箇所']],'','',r[ix[last]]]
rows=[row(o,r) for r in OP]+[row(a,r) for r in CA]
wb=Workbook(); ws=wb.active; ws.title='検証プラン'
HF=PatternFill('solid',fgColor='2F4858'); TH=Side(style='thin',color='CCCCCC')
BD=Border(left=TH,right=TH,top=TH,bottom=TH); YEL=PatternFill('solid',fgColor='FFF9C4')
KEY=PatternFill('solid',fgColor='EAF1F6'); LNK=PatternFill('solid',fgColor='F2F0E4'); SHT=PatternFill('solid',fgColor='FDEBD3')
ws.cell(1,1,'確かめる手順（85ケース）。「初期設定」のデータを用意し、「画面」を開いて「操作」を行い、「期待挙動」と一致するかを見る。'
            '期待挙動の【　】は判定する画面。「証跡」の状態を撮って「スクショファイル名」で保存する。'
            '結果は「対応する条件ID」で判定し、仕様が変われば「ヘルプ該当箇所」を直す。').font=Font(size=10)
for i,(nm,w) in enumerate(COLS,1):
    cc=ws.cell(2,i,nm); cc.fill=HF; cc.font=Font(color='FFFFFF',bold=True,size=10)
    cc.alignment=Alignment(vertical='center',wrap_text=True); ws.column_dimensions[get_column_letter(i)].width=w
ws.row_dimensions[2].height=36
for ri,r in enumerate(rows,3):
    for ci,v in enumerate(r,1):
        cc=ws.cell(ri,ci,rich(v)); cc.alignment=Alignment(vertical='top',wrap_text=True); cc.border=BD
    for ci in (6,7,8,11): ws.cell(ri,ci).fill=KEY
    for ci in (9,10): ws.cell(ri,ci).fill=SHT
    for ci in (13,14): ws.cell(ri,ci).fill=LNK
    for ci in (15,16,17): ws.cell(ri,ci).fill=YEL
nn=len(rows)+2
dv=DataValidation(type='list',formula1='"OK,NG,対象外"',allow_blank=True); ws.add_data_validation(dv); dv.add(f'P3:P{nn}')
ws.freeze_panes='D3'; ws.auto_filter.ref=f'A2:Q{nn}'
wb.save(os.path.join(D,'20260805_タイムレコード_02_検証プラン.xlsx'))
import shutil
for f in ['20260805_タイムレコード_01_受入条件表.xlsx','20260805_タイムレコード_02_検証プラン.xlsx',
          '20260805_タイムレコード_03_検証用データセット.xlsx','20260805_タイムレコード_00_定義表.xlsx',
          '20260805_タイムレコード_使い方.xlsx']:
    shutil.copy(os.path.join(D,f),'excel/')
print(f'01: {n1}セル同期 ／ 02: {len(rows)}件 再生成 ／ excel/ へコピー')
