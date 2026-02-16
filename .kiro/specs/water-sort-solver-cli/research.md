# リサーチ & 設計決定ログ

---
**目的**: 技術設計に影響を与えた調査結果・アーキテクチャ検討・意思決定の根拠を記録する。

---

## Summary

- **Feature**: `water-sort-solver-cli`
- **Discovery Scope**: New Feature（グリーンフィールド）
- **Key Findings**:
  - BFS が最短手数を保証、DFS が高速探索向き。既存の OSS 実装（[GitHub: tanjuntao/water-sort-puzzle](https://github.com/tanjuntao/water-sort-puzzle)）を参考に、状態をイミュータブルなタプルで表現することで `visited` 集合への O(1) 参照が可能。
  - Python 3.12 + 依存ゼロスタート。CLI ライブラリは `argparse`（標準ライブラリ）を採用し、追加依存は YAML パース用 `pyyaml` のみに抑える。
  - タイムアウト機構は `signal.alarm`（Unix 専用）ではなく、探索ループ内で `time.perf_counter()` を参照するポーリング方式とし、クロスプラットフォーム互換を確保する。

---

## Research Log

### BFS / DFS によるウォーターソートパズル探索

- **Context**: 要件 3.1〜3.7 で BFS/DFS の両方をサポートし、タイムアウトも求められる。
- **Sources Consulted**:
  - [GitHub: tanjuntao/water-sort-puzzle](https://github.com/tanjuntao/water-sort-puzzle)
  - [A* Application for Water Sort Puzzle (2025)](https://informatika.stei.itb.ac.id/~rinaldi.munir/Stmik/2024-2025/Makalah2025/Makalah-IF2211-Strategi-Algoritma-2025%20(39).pdf)
  - [Medium: Color Water Sort Genetic Algorithm](https://medium.com/@pathsko/solving-the-color-water-sort-game-using-a-genetic-algorithm-30355443c66c)
- **Findings**:
  - ウォーターソートパズルの合法手：注ぎ元ボトルの最上層色が、注ぎ先ボトルの最上層色と一致 **かつ** 注ぎ先に空きがある場合に移動可能。
  - 状態表現：`tuple[tuple[str, ...], ...]`（ボトルのリストを immutable タプルに変換）で `set` への追加が O(1)。
  - BFS は最短手数保証、メモリ消費大。DFS はメモリ効率良いが最適性なし。A* はヒューリスティック（color breaks 数）で高効率だが要件外のため対象外。
  - 20 ボトル × 4 セグメントの状態空間は理論上膨大だが、実際のゲームは解が数十手以内に収まることが多い。
- **Implications**:
  - BFS デフォルトが要件 3.3 を満たす。訪問済み集合のメモリ増大リスクに対し、タイムアウト（要件 3.4）でフェイルセーフを確保する。

### CLI ライブラリ選定

- **Context**: 要件 5.1〜5.5 でヘルプ・バージョン・終了コード・オプション多数が必要。
- **Sources Consulted**:
  - [CodeCut: argparse vs Click vs Typer](https://codecut.ai/comparing-python-command-line-interface-tools-argparse-click-and-typer/)
  - [Python CLI Tools Guide 2026](https://devtoolbox.dedyn.io/blog/python-click-typer-cli-guide)
- **Findings**:
  - `argparse`: 標準ライブラリ、追加依存なし、設定が冗長。
  - `click`: デコレータ API で簡潔、テスト用 `CliRunner` 付き、`click` 依存が必要。
  - `typer`: 型ヒント活用、click ベース、開発が最も速い。ただし click + typer の 2 依存が必要。
- **Implications**:
  - 本プロジェクトは `pyproject.toml` の `dependencies = []` から出発する小規模ツール。`argparse` でも要件はすべて満たせる。`click` の `CliRunner` はテストに便利。本設計では **`argparse`（標準ライブラリ）を採用** し、依存を `pyyaml` のみに抑える。

### タイムアウト実装方式

- **Context**: 要件 3.4 で探索のタイムアウトが必要。クロスプラットフォーム動作が望ましい。
- **Findings**:
  - `signal.alarm`：POSIX 専用、Windows 非対応、メインスレッドのみ有効。
  - `threading.Timer`：クロスプラットフォーム、スレッドセーフだが探索ループとの協調が必要。
  - ループ内ポーリング（`time.perf_counter()`）：最もシンプル、追加依存なし、GIL の影響なし。
- **Implications**: ループ内ポーリング方式を採用。探索ループの各イテレーションで経過時間を確認し、タイムアウト超過で `TimeoutError` を発生させる。

---

## Architecture Pattern Evaluation

| オプション | 説明 | 強み | リスク / 制限 | 採用判断 |
|-----------|------|------|--------------|--------|
| 単一モジュール（main.py） | 全機能を 1 ファイルに実装 | シンプル | テスト困難、拡張不可 | ❌ 却下 |
| レイヤードアーキテクチャ | CLI → Parser → Validator → Solver → Formatter のレイヤー分離 | 単体テスト容易、責務明確 | 若干のボイラープレート | ✅ **採用** |
| ヘキサゴナル（Ports & Adapters） | ドメインコアを入出力から分離 | 柔軟性高 | 小規模ツールには過剰設計 | ❌ 却下 |

---

## Design Decisions

### Decision: レイヤードアーキテクチャの採用

- **Context**: 単一ファイルでは単体テストが困難で要件のカバレッジが難しい。
- **Alternatives Considered**:
  1. 単一 `main.py` — 最小実装だがテスト不可
  2. レイヤードアーキテクチャ — 各レイヤーを独立モジュールに分離
- **Selected Approach**: `src/` パッケージ配下に `models.py`, `parser.py`, `validator.py`, `solver.py`, `formatter.py` を配置。`main.py` はエントリポイントのみ。
- **Rationale**: 要件の単体テスト（特に solver、validator）が独立して実施可能。将来的なアルゴリズム追加（A* 等）も solver モジュール内で吸収できる。
- **Trade-offs**: ファイル数は増えるが、各モジュールの責務が明確で並列実装が可能。
- **Follow-up**: `src/` パッケージ配下のインポートを `pyproject.toml` で適切に設定する。

### Decision: 状態表現に immutable タプルを使用

- **Context**: BFS/DFS の `visited` 集合に状態を格納するには hashable な型が必要。
- **Alternatives Considered**:
  1. `list[list[str]]` — 可変、hashable でない
  2. `tuple[tuple[str, ...], ...]` — immutable、hashable、O(1) 検索
- **Selected Approach**: `PuzzleState = tuple[tuple[str, ...], ...]` を型エイリアスとして定義し、全ての状態操作でこの型を使用する。
- **Rationale**: set への格納・検索が O(1)、Python の組み込み型のみ使用でパフォーマンスが安定。
- **Trade-offs**: 移動操作のたびに新しいタプルを生成するコスト（メモリ割り当て）があるが、探索における集合参照の高速化が上回る。

### Decision: argparse の採用

- **Context**: `dependencies = []` から出発し、依存最小化が望ましい。
- **Selected Approach**: 標準ライブラリ `argparse` を使用。外部依存は入力ファイル形式対応の `pyyaml` のみ。
- **Rationale**: `click` や `typer` は追加依存が必要なうえ、本ツールのオプション数は `argparse` で十分に管理できる。
- **Trade-offs**: `argparse` のテストは `sys.argv` のモック、または `parse_args()` への引数リスト渡しで対応。

---

## Risks & Mitigations

- **状態空間爆発リスク** — デフォルト 30 秒タイムアウトでフェイルセーフ。`--debug` フラグで訪問済み状態数を観察可能。
- **YAML/JSON パースエラー** — 要件 6.2 に従い、エラー種別と期待フォーマットを stderr に出力。
- **クロスプラットフォーム非互換** — `signal.alarm` は使用せず、ポーリング方式でタイムアウトを実装。
- **大量のボトル（20 本）での BFS メモリ超過** — タイムアウトが先に発動する想定。将来的には A* やメモリ制限オプションの追加を検討。

---

## References

- [GitHub: tanjuntao/water-sort-puzzle](https://github.com/tanjuntao/water-sort-puzzle) — BFS/DFS 実装の参考
- [A* for Water Sort Puzzle (2025, ITB)](https://informatika.stei.itb.ac.id/~rinaldi.munir/Stmik/2024-2025/Makalah2025/Makalah-IF2211-Strategi-Algoritma-2025%20(39).pdf) — A* ヒューリスティック評価の参考
- [CodeCut: argparse vs Click vs Typer](https://codecut.ai/comparing-python-command-line-interface-tools-argparse-click-and-typer/) — CLI ライブラリ比較
- [Python CLI Tools Guide 2026](https://devtoolbox.dedyn.io/blog/python-click-typer-cli-guide) — 最新 CLI ベストプラクティス
