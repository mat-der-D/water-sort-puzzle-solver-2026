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

    移動元の最上層から連続する同色セグメントをまとめて移動する（ブロック移動）。
    ブロックサイズが移動先の空き容量を超える場合は、空き容量分だけ移動する。
    """
    bottles = list(state)
    from_b = list(bottles[move.from_bottle])
    to_b = list(bottles[move.to_bottle])

    # 移動元の最上層の色
    top_color = from_b[-1]

    # 末尾から連続する同色セグメント数（ブロックサイズ）
    block_size = 0
    for seg in reversed(from_b):
        if seg == top_color:
            block_size += 1
        else:
            break

    # 移動先の空き容量
    available = BOTTLE_CAPACITY - len(to_b)

    # 実際に移動するセグメント数
    move_count = min(block_size, available)

    # セグメントをまとめて移動（末尾 = 最上層から順に）
    for _ in range(move_count):
        to_b.append(from_b.pop())

    bottles[move.from_bottle] = tuple(from_b)
    bottles[move.to_bottle] = tuple(to_b)
    return tuple(bottles)
