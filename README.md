# Water Sort Puzzle Solver 2026

**English** | [日本語](#日本語)

A command-line tool that automatically solves Water Sort puzzle games. Provide your puzzle configuration as a YAML, JSON, or plain text file, and the solver finds a valid sequence of moves using BFS or DFS.

---

## Features

- **Multiple input formats**: YAML, JSON, and plain text
- **Two search strategies**: BFS (shortest solution, default) and DFS (faster search)
- **Multiple output formats**: text, JSON, and YAML
- **Validation mode**: check puzzle integrity without solving
- **Verbose mode**: display bottle states after each move
- **Configurable timeout**: prevent runaway searches
- **Debug mode**: trace search progress to stderr

---

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

---

## Installation

```bash
git clone https://github.com/smoothpudding/water-sort-puzzle-solver-2026.git
cd water-sort-puzzle-solver-2026
uv sync
```

---

## Quick Start

```bash
# Show help
uv run python main.py --help

# Show input format documentation
uv run python main.py --input-format-help

# Solve a puzzle
uv run python main.py --input puzzle.yaml

# Validate only (no solving)
uv run python main.py --input puzzle.yaml --validate
```

---

## Input Formats

### YAML (`.yaml` / `.yml`)

```yaml
bottles:
  - [red, blue, red, blue]
  - [green, green, yellow, yellow]
  - [blue, red, yellow, green]
  - [yellow, green, blue, red]
  - []        # empty bottle
  - null      # also empty
```

### JSON (`.json`)

```json
{
  "bottles": [
    ["red", "blue", "red", "blue"],
    ["green", "green", "yellow", "yellow"],
    ["blue", "red", "yellow", "green"],
    ["yellow", "green", "blue", "red"],
    []
  ]
}
```

### Plain Text (`.txt`)

Each line is one bottle. Colors are separated by spaces. An empty line or a line containing only `(empty)` represents an empty bottle.

```
red blue red blue
green green yellow yellow
blue red yellow green
yellow green blue red
(empty)
```

**Constraints:**
- 4–20 bottles total
- All non-empty bottles must have the same capacity (determined by the first non-empty bottle)
- Each color must appear a number of times that is a multiple of the bottle capacity
- Color names are arbitrary strings containing no spaces

---

## CLI Reference

```
uv run python main.py [OPTIONS]
```

| Option | Description |
|---|---|
| `--input-format-help` | Print input format documentation and exit |
| `--input FILE`, `-i FILE` | Path to puzzle input file (required to solve) |
| `--validate` | Validate the puzzle without solving |
| `--strategy {bfs,dfs}` | Search strategy: `bfs` (default, shortest path) or `dfs` (faster) |
| `--timeout SECONDS` | Search timeout in seconds (default: 30, `0` = unlimited) |
| `--format {text,json,yaml}` | Output format (default: `text`) |
| `--output FILE`, `-o FILE` | Write output to a file instead of stdout |
| `--verbose`, `-v` | Show bottle state after every move |
| `--debug` | Print search progress to stderr |
| `--version` | Show version number |
| `--help` | Show help message |

**Exit codes:** `0` = success, `1` = error, `2` = timeout

---

## Usage Examples

```bash
# Solve with DFS and a 10-second timeout
uv run python main.py --input puzzle.yaml --strategy dfs --timeout 10

# Output solution as JSON to a file
uv run python main.py --input puzzle.yaml --format json --output solution.json

# Verbose mode — show bottle states during the solution
uv run python main.py --input puzzle.yaml --verbose

# Debug mode — trace search progress
uv run python main.py --input puzzle.yaml --debug

# Unlimited timeout (complex puzzles)
uv run python main.py --input puzzle.yaml --timeout 0
```

---

## Development

### Run Tests

```bash
uv run pytest            # Run all tests
uv run pytest -v         # Verbose output
uv run pytest tests/test_solver.py  # Single file
```

### Project Structure

```
water-sort-puzzle-solver-2026/
├── main.py              # CLI entry point
├── src/
│   ├── models.py        # Data types and core logic (apply_move)
│   ├── parser.py        # Input file parsing (YAML/JSON/text)
│   ├── validator.py     # Puzzle validation (is_solved, validate)
│   ├── solver.py        # BFS and DFS solvers
│   ├── formatter.py     # Output formatting (text/JSON/YAML)
│   └── format_help.py   # --input-format-help content
├── tests/               # pytest test suite
├── pyproject.toml       # Project metadata and dependencies
└── .kiro/               # Spec-driven development artifacts
    ├── steering/        # Project-wide guidelines
    └── specs/           # Per-feature specifications
```

---

## License

MIT

---

---

# 日本語

[English](#water-sort-puzzle-solver-2026) | **日本語**

Water Sort パズルを自動で解くコマンドラインツールです。YAML・JSON・プレーンテキスト形式のファイルでパズル状態を入力すると、BFS または DFS を使って有効な手順を探索します。

---

## 機能

- **複数の入力形式に対応**: YAML、JSON、プレーンテキスト
- **2 種類の探索戦略**: BFS（最短手順、デフォルト）と DFS（高速探索）
- **複数の出力形式**: テキスト、JSON、YAML
- **バリデーションモード**: 解かずにパズルの整合性チェックのみ実行
- **詳細表示モード**: 各手順後のボトル状態を表示
- **タイムアウト設定**: 探索の暴走を防止
- **デバッグモード**: 探索の進捗を標準エラー出力に出力

---

## 動作要件

- Python 3.12 以上
- [uv](https://github.com/astral-sh/uv) パッケージマネージャー

---

## インストール

```bash
git clone https://github.com/smoothpudding/water-sort-puzzle-solver-2026.git
cd water-sort-puzzle-solver-2026
uv sync
```

---

## クイックスタート

```bash
# ヘルプを表示
uv run python main.py --help

# 入力形式のドキュメントを表示
uv run python main.py --input-format-help

# パズルを解く
uv run python main.py --input puzzle.yaml

# バリデーションのみ実行（解かない）
uv run python main.py --input puzzle.yaml --validate
```

---

## 入力形式

### YAML（`.yaml` / `.yml`）

```yaml
bottles:
  - [red, blue, red, blue]
  - [green, green, yellow, yellow]
  - [blue, red, yellow, green]
  - [yellow, green, blue, red]
  - []        # 空のボトル
  - null      # 空のボトル（別表記）
```

### JSON（`.json`）

```json
{
  "bottles": [
    ["red", "blue", "red", "blue"],
    ["green", "green", "yellow", "yellow"],
    ["blue", "red", "yellow", "green"],
    ["yellow", "green", "blue", "red"],
    []
  ]
}
```

### プレーンテキスト（`.txt`）

各行が 1 本のボトルを表します。色はスペース区切り。空行または `(empty)` のみの行は空のボトルです。

```
red blue red blue
green green yellow yellow
blue red yellow green
yellow green blue red
(empty)
```

**制約:**
- ボトルは 4〜20 本
- 空でないボトルはすべて同じ容量（最初の非空ボトルで決定）
- 各色のセグメント合計数はボトル容量の倍数
- 色名はスペースを含まない任意の文字列

---

## CLI リファレンス

```
uv run python main.py [オプション]
```

| オプション | 説明 |
|---|---|
| `--input-format-help` | 入力形式ドキュメントを表示して終了 |
| `--input FILE`, `-i FILE` | パズル入力ファイルのパス（解くには必須） |
| `--validate` | 解かずにバリデーションのみ実行 |
| `--strategy {bfs,dfs}` | 探索戦略: `bfs`（デフォルト、最短手順）または `dfs`（高速） |
| `--timeout 秒数` | 探索タイムアウト秒数（デフォルト: 30、`0` = 無制限） |
| `--format {text,json,yaml}` | 出力形式（デフォルト: `text`） |
| `--output FILE`, `-o FILE` | 結果をファイルに出力（デフォルト: 標準出力） |
| `--verbose`, `-v` | 各手順後のボトル状態を表示 |
| `--debug` | 探索の進捗を標準エラー出力に表示 |
| `--version` | バージョン番号を表示 |
| `--help` | ヘルプを表示 |

**終了コード:** `0` = 成功、`1` = エラー、`2` = タイムアウト

---

## 使用例

```bash
# DFS で 10 秒タイムアウトを設定して解く
uv run python main.py --input puzzle.yaml --strategy dfs --timeout 10

# 解法を JSON ファイルに出力
uv run python main.py --input puzzle.yaml --format json --output solution.json

# 詳細モード — 各手順のボトル状態を表示
uv run python main.py --input puzzle.yaml --verbose

# デバッグモード — 探索の進捗をトレース
uv run python main.py --input puzzle.yaml --debug

# タイムアウト無制限（難しいパズル向け）
uv run python main.py --input puzzle.yaml --timeout 0
```

---

## 開発

### テストの実行

```bash
uv run pytest            # 全テストを実行
uv run pytest -v         # 詳細出力
uv run pytest tests/test_solver.py  # 特定のファイルのみ
```

### プロジェクト構成

```
water-sort-puzzle-solver-2026/
├── main.py              # CLI エントリーポイント
├── src/
│   ├── models.py        # データ型とコアロジック（apply_move）
│   ├── parser.py        # 入力ファイルのパース（YAML/JSON/テキスト）
│   ├── validator.py     # パズルのバリデーション（is_solved、validate）
│   ├── solver.py        # BFS・DFS ソルバー
│   ├── formatter.py     # 出力フォーマット（テキスト/JSON/YAML）
│   └── format_help.py   # --input-format-help の内容
├── tests/               # pytest テストスイート
├── pyproject.toml       # プロジェクトのメタデータと依存関係
└── .kiro/               # スペック駆動開発の成果物
    ├── steering/        # プロジェクト全体のガイドライン
    └── specs/           # 機能ごとの仕様書
```

---

## ライセンス

MIT
