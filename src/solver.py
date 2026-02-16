"""BFS / DFS によるウォーターソートパズル解法探索"""
from __future__ import annotations

import sys
import time
from collections import deque

from src.models import (
    BOTTLE_CAPACITY,
    Move,
    PuzzleState,
    PuzzleTimeoutError,
    SolverResult,
    Strategy,
    apply_move,
)
from src.validator import is_solved


def get_legal_moves(state: PuzzleState) -> list[Move]:
    """
    現在の状態から合法手の一覧を返す。
    合法手の条件:
    - 注ぎ元が空でない
    - 注ぎ先に空き容量がある（全ボトルの最大長 = ボトル容量 = max len で判定）
    - 注ぎ元の最上層色が注ぎ先の最上層色と一致するか、注ぎ先が空
    """
    n = len(state)
    # ボトル容量を推定（最大のボトル長か、デフォルト）
    capacity = max((len(b) for b in state), default=BOTTLE_CAPACITY)
    # capacity が 0 の場合は BOTTLE_CAPACITY を使う
    if capacity == 0:
        capacity = BOTTLE_CAPACITY

    moves: list[Move] = []
    for frm in range(n):
        src = state[frm]
        if not src:
            continue  # 空ボトルからは移動不可
        top_src = src[-1]

        for to in range(n):
            if frm == to:
                continue
            dst = state[to]
            # 注ぎ先が満杯なら不可
            if len(dst) >= capacity:
                continue
            # 注ぎ先が空（空ボトルへは移動可）か、最上層色が一致
            if not dst or dst[-1] == top_src:
                moves.append(Move(from_bottle=frm, to_bottle=to))

    return moves


def solve(
    initial_state: PuzzleState,
    strategy: Strategy = "bfs",
    timeout: float = 30.0,
    debug: bool = False,
) -> SolverResult:
    """
    初期状態から解法手順を探索して SolverResult を返す。
    Raises: PuzzleTimeoutError（timeout > 0 かつ制限時間超過時）
    """
    start_time = time.perf_counter()

    # 解決済み判定
    if is_solved(initial_state):
        return SolverResult(
            solved=True,
            moves=[],
            states_visited=0,
            elapsed_time=time.perf_counter() - start_time,
        )

    if strategy == "bfs":
        return _bfs(initial_state, timeout, debug, start_time)
    else:
        return _dfs(initial_state, timeout, debug, start_time)


def _bfs(
    initial_state: PuzzleState,
    timeout: float,
    debug: bool,
    start_time: float,
) -> SolverResult:
    """幅優先探索（最短手数保証）"""
    # parent: state → (parent_state, move)
    parent: dict[PuzzleState, tuple[PuzzleState, Move] | None] = {initial_state: None}
    queue: deque[PuzzleState] = deque([initial_state])
    iterations = 0

    while queue:
        # タイムアウトチェック
        if timeout > 0:
            elapsed = time.perf_counter() - start_time
            if elapsed >= timeout:
                raise PuzzleTimeoutError(
                    f"探索がタイムアウトしました（{elapsed:.1f}秒）"
                    f"、訪問済み状態数: {len(parent)}"
                )

        iterations += 1
        if debug and iterations % 1000 == 0:
            elapsed = time.perf_counter() - start_time
            print(
                f"[DEBUG] BFS: {len(parent)} states visited, {elapsed:.2f}s",
                file=sys.stderr,
            )

        current = queue.popleft()

        for move in get_legal_moves(current):
            next_state = apply_move(current, move)
            if next_state in parent:
                continue
            parent[next_state] = (current, move)

            if is_solved(next_state):
                moves = _reconstruct_path(parent, initial_state, next_state)
                return SolverResult(
                    solved=True,
                    moves=moves,
                    states_visited=len(parent),
                    elapsed_time=time.perf_counter() - start_time,
                )
            queue.append(next_state)

    return SolverResult(
        solved=False,
        moves=[],
        states_visited=len(parent),
        elapsed_time=time.perf_counter() - start_time,
    )


def _dfs(
    initial_state: PuzzleState,
    timeout: float,
    debug: bool,
    start_time: float,
) -> SolverResult:
    """深さ優先探索（高速探索、最適性保証なし）"""
    # parent: state → (parent_state, move) | None（初期状態）
    parent: dict[PuzzleState, tuple[PuzzleState, Move] | None] = {initial_state: None}
    stack: list[PuzzleState] = [initial_state]
    iterations = 0

    while stack:
        # タイムアウトチェック
        if timeout > 0:
            elapsed = time.perf_counter() - start_time
            if elapsed >= timeout:
                raise PuzzleTimeoutError(
                    f"探索がタイムアウトしました（{elapsed:.1f}秒）"
                    f"、訪問済み状態数: {len(parent)}"
                )

        iterations += 1
        if debug and iterations % 1000 == 0:
            elapsed = time.perf_counter() - start_time
            print(
                f"[DEBUG] DFS: {len(parent)} states visited, {elapsed:.2f}s",
                file=sys.stderr,
            )

        current = stack.pop()

        for move in get_legal_moves(current):
            next_state = apply_move(current, move)
            if next_state in parent:
                continue
            parent[next_state] = (current, move)

            if is_solved(next_state):
                moves = _reconstruct_path(parent, initial_state, next_state)
                return SolverResult(
                    solved=True,
                    moves=moves,
                    states_visited=len(parent),
                    elapsed_time=time.perf_counter() - start_time,
                )
            stack.append(next_state)

    return SolverResult(
        solved=False,
        moves=[],
        states_visited=len(parent),
        elapsed_time=time.perf_counter() - start_time,
    )


def _reconstruct_path(
    parent: dict[PuzzleState, tuple[PuzzleState, Move] | None],
    initial_state: PuzzleState,
    goal_state: PuzzleState,
) -> list[Move]:
    """解決状態から初期状態へ遡って手順を復元する"""
    moves: list[Move] = []
    current = goal_state
    while current != initial_state:
        entry = parent[current]
        assert entry is not None
        prev_state, move = entry
        moves.append(move)
        current = prev_state
    moves.reverse()
    return moves
