# スキル標準化変更履歴

## 2026-04-24 レポート作成スキル清書

### 変更内容

- `report-format-kri` を 10 セクション固定の標準レポート清書スキルとして再整理
- `research-report` を「レポート + A4 要約」の両出力ワークフローとして再整理
- `report-format-a4` を新規情報生成禁止の 5 セクション要約スキルとして再整理
- `report-fact-check` を構造、事実、数値、リンク、課題 ID の検証スキルとして再整理
- `report-format` を旧 6 セクション形式から `report-format-kri` への互換委譲スキルとして縮退

### 標準化方針

- 新規レポート作成は `research-report` または `report-format-kri` を使う
- A4 要約は `report-format-a4` を使う
- 検証は `report-fact-check` を使う
- 旧 `report-format` は新規作成に使わない

## 2026-04-24 qwen3.5:9b 向け制御文見直し

### 変更内容

- `description` と制御手順を英語中心に変更
- 出力テンプレート、固定見出し、固定ラベルは日本語のまま維持
- `MUST` / `Do not` / `Workflow` / `Completion Checks` 形式へ寄せ、弱い LLM でも制約を追いやすく整理
- `report-format-a4` の YAML frontmatter を検証し、description をクォートして valid 化

### 検証結果

- `skills/report-format-kri`: valid
- `skills/research-report`: valid
- `skills/report-format-a4`: valid
- `skills/report-fact-check`: valid

## 2026-04-24 スキル設計 README 追加

### 変更内容

- `skills/README.md` を追加
- 今後のスキル追加・改修時に使う設計原則、`SKILL.md` テンプレート、AI への依頼プロンプトを整理
- qwen3.5:9b など小型モデル向けに、英語制御文と日本語出力テンプレートを分離する方針を明文化
- frontmatter、description、固定テンプレート、検証チェックリスト、失敗パターンを記載

## 2026-04-24 workflow 英語制御文対応

### 変更内容

- `workflows/research-report-kri.md` を英語制御文中心に再整理
- 出力ファイル名、日本語見出し、固定ラベルは日本語のまま維持
- 旧ルールの `参照 ID` 付与と、不要なユーザー確認で停止する分岐を削除
- `format-only` 時の外部検索禁止、レポート/A4 両出力、検証完了条件を明確化
- `workflows/README.md` を追加し、今後の workflow 設計手順、テンプレート、AI 依頼プロンプト、changelog 方針を整理

## 2026-04-24 標準化ルール見直し（weak LLM 対策）

### 変更内容

#### スキル削除

| 削除対象 | 理由 | 代替手段 |
|---------|------|---------|
| skills/report-format/ | report-format-kri の旧バージョンとして不要 | report-format-kri に統合 |
| workflows/research-report.md | 旧ワークフロー、report-format-kri 準拠がない | workflows/research-report-kri.md に統合 |

#### スキル更新

1. **skills/report-format-a4/SKILL.md**
   - A4 1 枚相当の要約レポートテンプレート
   - 新規情報の生成禁止
   - 文字数制限の明確化
   - 定量表現の必須化
   - レポート＋A4 両出力対応

2. **skills/research-report/SKILL.md**
   - レポート＋A4 両出力ワークフロー定義
   - report-format-kri（10 セクション）のレポート出力
   - report-format-a4（5 セクション）の A4 出力
   - 両方の出力を別ファイルとして保存

3. **skills/report-fact-check/SKILL.md**
   - 事実検証チェックリスト
   - 数値・日付・主張・参照整合性の検証
   - ソース品質評価

4. **skills/report-format-kri/SKILL.md**
   - 10 セクション固定テンプレート
   - 「現状 → 課題 → AI 解決 → 価値」の流れ
   - 本文リンク必須

#### ワークフロー更新

1. **workflows/research-report-kri.md**
   - レポート＋A4 両出力ワークフロー定義
   - 新規作成と既存レポート更新の分岐
   - 調査プロセス（検索 → 評価 → ファクトチェック）
   - レポート生成（10 セクション＋A4 5 セクション）
   - 構造検証（レポート・A4 両方）
   - 更新処理（ドキュメント解析 → 更新判定 → 更新実行）

### 標準化ルール（最終版）

#### 必須項目

- report-format-kri: 10 セクションの構造維持
- report-format-a4: 5 セクションの構造維持（文字数制限遵守）
- 「現状 → 課題 → AI 解決 → 価値」の流れ
- 本文リンク必須
- 課題 ID（C1, C2...）付与
- 価値の定量性（数値・比較）

#### 禁止事項

- 構造の変更
- 注釈・脚注の使用
- 推測（「不明」と書く）

#### レポート＋A4 両出力ワークフロー

```
research-report (調査ワークフロー)
  ↓
  ├─── report-format-kri → レポート（10 セクション）
  └─── report-format-a4 → A4 要約（5 セクション）
```

### 維持するスキル・ワークフロー

1. **skills/report-format-kri/** - 標準フォーマット（10 セクション）
2. **skills/research-report/** - 調査ワークフロー（レポート＋A4 両出力）
3. **skills/report-fact-check/** - 品質検証
4. **skills/report-format-a4/** - A4 要約用（5 セクション）
5. **workflows/research-report-kri.md** - レポート＋A4 両出力ワークフロー

### 出力形式

- レポート：`{topic}_レポート.md`（10 セクション）
- A4 要約：`{topic}_A4_要約.md`（5 セクション）

---

## 2026-04-23 計画書作成

### 初期分析

#### レポート一覧化

- A4 フォーマットレポート：17 ファイル確認
- 非 A4 フォーマットレポート：33 ファイル確認
- 最新フォーマットレポート（2026-04-xx）：テンプレート適用
- 旧フォーマットレポート（2026-03-xx）：テンプレート未適用

#### スキル分析

- report-format: 6 セクション固定、柔軟性不足
- report-format-kri: 10 セクション、複雑で弱い LLM で制御困難
- report-format-a4: 5 セクション固定、文字数制限厳守困難
- report-fact-check: 指示のみ、実装なし
- research-report: 旧ワークフロー、report-format-kri との連携不足

### 標準化方針

- report-format-kri を標準フォーマットとして固定
- research-report でワークフローを定義
- weak LLM 制御強化を目標

### 次のステップ

- report-format-kri の標準化ルール策定
- research-report の統合方針策定
- report-format の統合方針策定
- report-format-a4 の維持
- report-fact-check の実装
- 既存レポートのテンプレート適用
