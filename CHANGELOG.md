# CHANGELOG — タイムレコード import-spec

タイムレコード CSV 取込フロー（テンプレート／外部勤怠サービス連携）モックと仕様の変更履歴。
判断経緯＝`JUDGMENT_LOG.md`。全体の入口・正本は owner-mock（`rakmy-owner-registration-mock`）。

---

## 2026-06-24

### Changed（owner-mock 決定 #13/#17 に追従）
- **業態・ブランド → 業態に統合**：ブランド／ブランドコード廃止。
  - ①テンプレを 3列（業態/ブランド名/ブランドコード）→ **1列（業態名）**、ファイル名も `①業態.tsv` に。
  - ②店舗の `所属ブランドコード` → `所属業態`。
  - 取込プレビュー・マッピング（`brand_code` 削除）・入力ガイド・README・物理TSV から コード列を除去。
- **業態名の入力形式**：入力ガイドで「選択」→「テキスト」に修正（名前付けの自由入力マスタ）。
- **`brand` → `businesstype` に一括改称**：画面ID・関数・データキー（`s-tpl-single-businesstype` / `downloadBusinesstypeTemplate` / `map-kot-businesstype` ほか）、下書きスペックTSVの参照IDも追従。

---

## 〜2026-06-04（ベースライン）

- 旧「2テンプレート方式」→ **5テンプレート方式（エンティティ別）** に統一（README・実ファイル・モック画面）。
- native alert を `showFloatToast`（トースト）に全置換。
- 到達不能の孤立画面 `s-saas3`（旧プレビュー）撤去。
- 一括取込プレビュー/完了画面の旧ラベルを5テンプレ体系に統一。
- README に owner-mock を入口とする導線を追加。
