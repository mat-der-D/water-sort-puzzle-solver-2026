# 技術スタック

## アーキテクチャ

パイプライン型 CLI: `parse → validate → solve → format → output` の直線フロー。
各ステージは独立したモジュールとして実装され、`main.py` がオーケストレートする。

## コア技術

- **言語**: Python 3.12+（`from __future__ import annotations` を全モジュールで使用）
- **ランタイム**: CPython 3.12、uv による仮想環境管理（`.venv/`）
- **主要ライブラリ**: `pyyaml>=6.0`（YAML 入出力）、`argparse`（CLI 引数）

## 開発標準

### 型安全性
- 全モジュールに型アノテーションを付与
- `NamedTuple` / `dataclass` で構造化データを定義
- `Literal` 型で列挙値を制約（例: `Strategy = Literal["bfs", "dfs"]`）

### テスト
- pytest 9.x、モジュールごとに `tests/test_<module>.py` を用意
- テストはモジュール境界（公開 API）を単位とする

### エラーハンドリング
- エラーはすべて `stderr` に出力
- 終了コード: 0（正常）、1（エラー）、2（タイムアウト）
- 独自例外: `ParseError`（入力解析失敗）、`PuzzleTimeoutError`（探索タイムアウト）

## 開発環境

### 必須ツール
- Python 3.12+
- uv（パッケージ管理・仮想環境）

### 主要コマンド
```bash
# 実行: uv run python main.py --input puzzle.yaml
# テスト: uv run pytest
# 依存追加: uv add <package>
```

## 重要な技術的決定

- **イミュータブル状態**: `PuzzleState = tuple[BottleState, ...]` により状態を hashable に保ち、訪問済みセットで循環を防止
- **BFS デフォルト**: 最短手数保証のため BFS をデフォルト戦略とし、DFS はオプション

---
_Document standards and patterns, not every dependency_
