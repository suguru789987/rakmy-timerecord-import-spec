# エンジニア共有ノート（タイムレコード import-spec）

> 2026-07-13 更新。本リポは **CSV 取込フローの仕様／モック**。全体の入口・正本は owner-mock 側。

## 0. まず読む順番
1. **owner-mock / HANDOFF.md**（全体の入口）… タイムレコード全体の最新状態
   https://github.com/suguru789987/rakmy-owner-registration-mock/blob/main/HANDOFF.md
2. **本リポ README.md** … 5テンプレート構成・列定義・外部勤怠サービス マッピング
3. **本リポ CHANGELOG.md / JUDGMENT_LOG.md** … 変更履歴／PdM判断
4. コード（index.html）／ライブモック

> 矛盾時の優先：UI/挙動は **コード(index.html) を正**、データ項目（CSV列・型・必須）は **本リポのテンプレTSV を正**。

## 1. 直近の主要変更（2026-06-24）
- **業態・ブランド → 業態に統合**（owner-mock 決定に追従）：①テンプレは **業態名1列**、②店舗は **所属業態**。ブランドコード等は廃止。
- **`brand` → `businesstype` に一括改称**：画面ID・関数・データキーを統一（owner-mock ルート `/settings/business-types` と整合）。
- 詳細は `CHANGELOG.md` / `JUDGMENT_LOG.md`。

## 2. ライブモック（main 反映済み・要ハードリフレッシュ）
- import-spec: https://suguru789987.github.io/rakmy-timerecord-import-spec/
- 主要ディープリンク：
  - テンプレート取込: `.../#tpl-setup`
  - 外部勤怠サービス（KoT/Jobcan）取込: `.../#saas-setup`
- owner-mock（全体）: https://suguru789987.github.io/rakmy-owner-registration-mock/

## 3. 5テンプレート（現行）
① 業態（1列：業態名）／② 店舗（6列）／③ 雇用区分（6列）／④ 従業員（8列）／⑤ 管理者（4列）。
依存：②は①（所属業態）、④は②③（店舗名/雇用区分名）、⑤は②（担当店舗）を参照。

## 4. 残オープン項目
- 外部勤怠サービスのマッピング不可項目（電話/メール/交通費 等）の補完フロー（完了画面の補完テンプレDL→再取込）。
- 業態改称に伴う既存 `brand` 系実装の置換。

---
🤖 全体の入口は owner-mock / HANDOFF.md。最新は常に main の各成果物を参照。
