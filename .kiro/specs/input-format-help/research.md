# リサーチ & 設計判断ログ

---
**目的**: 技術設計を裏付ける調査結果・アーキテクチャ検討・設計判断の根拠を記録する。

---

## サマリー
- **フィーチャー**: `input-format-help`
- **調査スコープ**: Extension（既存 CLI への引数追加）
- **主な調査結果**:
  - `--input` が `required=True` に設定されているため、`--input-format-help` と共存させるには `required=False` への変更と手動バリデーションが必要
  - 新モジュール `src/format_help.py` を追加するのみで外部依存は不要
  - `CLIArgs` dataclass に `format_help: bool` フィールドを追加する最小変更で対応可能

---

## リサーチログ

### トピック: argparse と `--input` の必須制約

- **背景**: 要件 1.2 により `--input-format-help` 指定時は `--input` が未指定でも動作する必要がある
- **参照**: `main.py` の `build_parser()` — `parser.add_argument("--input", required=True, ...)`
- **調査結果**:
  - 現状 `--input` は `required=True` であり、`argparse` は `--input` が無い場合にエラーで終了する
  - `--input-format-help` を `action="store_true"` で追加し、`--input` を `required=False` に変更することで解決できる
  - `main()` 内で `namespace.input_format_help` が False の場合に `--input` の存在を手動チェックし、未指定なら `parser.error()` を呼ぶ
- **影響**: `build_parser()` と `main()` の両方を修正する必要がある

### トピック: 早期終了パターンの実装場所

- **背景**: 要件 1.2・1.4 により解析・探索処理を実行せずにヘルプ出力して終了する必要がある
- **調査結果**:
  - `main()` 関数内で `CLIArgs` を生成した直後に `args.format_help` を確認し、早期 `sys.exit(0)` する
  - `run()` 関数への委譲前に処理を打ち切ることで、既存の `parse_file` / `validate` / `solve` パイプラインに影響を与えない
- **影響**: `run()` 関数の変更は不要。`main()` のみ変更。

### トピック: フォーマットヘルプテキストの実装場所

- **背景**: ヘルプテキストを `main.py` に直書きすると責務が混在する
- **調査結果**:
  - steering `structure.md` のモジュール分割原則に従い `src/format_help.py` として独立モジュール化する
  - `build_format_help_text() -> str` を公開関数として定義し、`main()` から呼び出す
  - このモジュールは `src/models.py` に依存しない（依存ツリーの最末端）
- **影響**: `main.py` からのインポート追加のみ。既存モジュールへの影響なし。

---

## アーキテクチャパターン評価

| オプション | 説明 | 利点 | リスク / 制限 | 備考 |
|-----------|------|------|-------------|------|
| A: `main.py` に直書き | ヘルプテキストを `build_parser()` または `main()` 内に埋め込む | 変更ファイルを1つに絞れる | 責務混在・テスト困難 | steering の構造原則に反する |
| B: `src/format_help.py` として分離（採用） | 専用モジュールで文字列生成 | 単一責任・単体テスト可能 | ファイル追加が1つ増える | steering の構造原則と整合 |

---

## 設計判断

### 判断: `--input` の必須制御方法

- **背景**: `--input-format-help` は `--input` なしで動作しなければならない
- **検討した代替案**:
  1. `parse_known_args` + 事後バリデーション — 現在の `main()` と同じ構造
  2. `required=False` + `main()` 内手動チェック — シンプルで argparse の標準的な拡張パターン
- **採用アプローチ**: オプション 2。`--input` を `required=False` にし、`namespace.input_format_help` が False の場合のみ `--input` の存在を確認する
- **根拠**: argparse の `parse_known_args` を使うと不明なオプションのエラーハンドリングと衝突するリスクがある。シンプルな手動チェックが既存コードと整合する
- **トレードオフ**: `--help` の表示において `--input` が必須と見えなくなるが、ヘルプ文言で補足可能
- **フォローアップ**: `--help` の `--input` 説明文に「（`--input-format-help` なし時は必須）」と追記することで解消

### 判断: `CLIArgs` の拡張方法

- **背景**: `main()` から `run()` へのフロー制御に `format_help` フラグが必要
- **採用アプローチ**: `CLIArgs` dataclass に `format_help: bool = False` を追加
- **根拠**: 既存の型付きラッパーパターンに一致。`run()` は変更不要
- **トレードオフ**: `format_help=True` 時は `input_path` が空文字列または None になるが、`run()` は呼ばれないため問題なし

---

## リスクと緩和策

- `--input` 必須制約変更による既存テストの破損 — `test_main.py` が存在すれば更新が必要（現在 `tests/` に存在しない）
- `--input-format-help` と他オプションの同時指定での挙動 — 要件 1.4 に従い最優先でヘルプ出力 + 終了することで対応済み

---

## 参照

- `main.py` — 既存 CLI エントリポイント・argparse 設定
- `src/models.py` — `CLIArgs` dataclass 定義
- `.kiro/steering/structure.md` — モジュール分割・命名規則
- `.kiro/steering/tech.md` — Python 型アノテーション・テスト規約
