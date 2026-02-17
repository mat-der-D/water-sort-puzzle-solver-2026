"""共有データモデルと型定義"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, NamedTuple

# ボトル内のセグメントを下から上の順に格納する immutable タプル
BottleState = tuple[str, ...]
# パズル全体の状態（hashable で set に格納可能）
PuzzleState = tuple[BottleState, ...]

# 標準ボトル容量（要件 1.5: 容量 4 セグメント）
BOTTLE_CAPACITY: int = 4

Strategy = Literal["bfs", "dfs"]
OutputFormat = Literal["text", "json", "yaml"]


class Move(NamedTuple):
    from_bottle: int  # 0-indexed
    to_bottle: int    # 0-indexed


class SolverResult(NamedTuple):
    solved: bool
    moves: list[Move]
    states_visited: int
    elapsed_time: float  # seconds


class ValidationResult(NamedTuple):
    valid: bool
    already_solved: bool
    error_message: str | None  # None if valid


@dataclass
class CLIArgs:
    """argparse.Namespace の型付きラッパー"""
    input_path: str
    validate_only: bool = False
    strategy: Strategy = "bfs"
    timeout: float = 30.0
    output_format: OutputFormat = "text"
    output_path: str | None = None
    verbose: bool = False
    debug: bool = False
    format_help: bool = False  # True の場合、input_path は使用されない


class ParseError(ValueError):
    """入力ファイルの解析エラー"""


class PuzzleTimeoutError(Exception):
    """解探索のタイムアウト"""


def apply_move(state: PuzzleState, move: Move) -> PuzzleState:
    """
    ムーブを適用した新しい PuzzleState を返す。元の state は変更しない。
    Preconditions: move は get_legal_moves() で得た合法手であること
    Postconditions: 戻り値は move 適用後の immutable PuzzleState
    """
    bottles = list(state)
    from_b = list(bottles[move.from_bottle])
    to_b = list(bottles[move.to_bottle])

    # 最上層（末尾）のセグメントを移動元から取り出す
    segment = from_b.pop()
    to_b.append(segment)

    bottles[move.from_bottle] = tuple(from_b)
    bottles[move.to_bottle] = tuple(to_b)
    return tuple(bottles)
