# プロジェクト構造

## 構成の考え方

フラットなレイヤー分割。`src/` に機能別モジュール、`tests/` に対応テスト、`main.py` がエントリポイント。

## ディレクトリパターン

### ソースモジュール
**Location**: `src/`
**Purpose**: ビジネスロジック（解析・検証・探索・整形）
**例**: `models.py`（共有型）、`parser.py`（入力解析）、`solver.py`（探索）、`formatter.py`（出力整形）

### テスト
**Location**: `tests/`
**Purpose**: 各ソースモジュールのユニットテスト
**例**: `test_solver.py` → `src/solver.py` に対応

### エントリポイント
**Location**: `main.py`（ルート直下）
**Purpose**: CLI 引数解析と処理フローのオーケストレーション

### 仕様管理
**Location**: `.kiro/specs/`
**Purpose**: フィーチャーごとの仕様（要件・設計・タスク）

## 命名規則

- **ファイル**: `snake_case.py`
- **クラス / NamedTuple**: `PascalCase`（例: `SolverResult`, `CLIArgs`）
- **関数**: `snake_case`（例: `parse_file`, `get_legal_moves`）
- **型エイリアス**: `PascalCase`（例: `PuzzleState`, `BottleState`）
- **定数**: `UPPER_SNAKE_CASE`（例: `BOTTLE_CAPACITY`）

## インポート規則

```python
# 標準ライブラリ → サードパーティ → src 内モジュール の順
from __future__ import annotations  # 全モジュール先頭

from src.models import Move, PuzzleState  # src パッケージからの絶対インポート
from src.validator import is_solved
```

**パスエイリアス**: なし（`src.` プレフィックスで絶対インポート）

## コード構成の原則

- `models.py` は他の `src/` モジュールに依存しない（依存ツリーのルート）
- `validator.py` は `models.py` のみに依存
- `solver.py` は `models.py` と `validator.py` に依存
- `formatter.py` は `models.py` のみに依存
- `main.py` がすべての `src/` モジュールをオーケストレート

---
_Document patterns, not file trees. New files following patterns shouldn't require updates_
