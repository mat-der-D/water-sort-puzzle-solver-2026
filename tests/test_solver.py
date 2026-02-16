"""src/solver.py の単体テスト"""
import pytest
from src.models import Move, PuzzleState, PuzzleTimeoutError, SolverResult, apply_move
from src.solver import get_legal_moves, solve
from src.validator import is_solved


# --- テスト用パズル定義 ---

def make_simple_solvable() -> PuzzleState:
    """
    簡単な解決可能パズル（BFS/DFS が素早く解ける）
    ボトル0: (red, blue)  ボトル1: (blue, red)  ボトル2: () ボトル3: ()
    Move(0,2) → red を取り出し 2へ → 残りをまとめれば解決
    """
    return (
        ("red", "blue"),
        ("blue", "red"),
        (),
        (),
    )


def make_already_solved() -> PuzzleState:
    """解決済みパズル"""
    return (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )


def make_unsolvable() -> PuzzleState:
    """
    解けないパズル（色の制約を満たしているが移動できない状態）
    容量4、各色4セグメント。しかし移動不可能な状態に閉じ込められている。
    より確実に解けないパズル: 全ボトルが満杯かつ移動不可
    ボトル0: (red, blue, red, blue) ボトル1: (blue, red, blue, red)
    ボトル2: (red, blue, red, blue) ボトル3: (blue, red, blue, red)
    → 最上層が交互 red/blue なのでどのボトルも合法手がない
    → ただしこの状態は実は探索で確認するのでシンプルな不解パズルは難しい
    代わりにタイムアウトテスト用に大きなパズルを使う
    """
    # シンプルに: redが5セグメント（4の倍数でない）は検証で弾かれるので
    # 実際に探索して解なしになるパズル
    # 各ボトルが満杯で全ボトルの最上層色が全て異なる→ しかし本当に解なしは難しい
    # ここでは移動不可能な単純ケース: 全ボトル満杯かつ最上層色が全部違う
    return (
        ("red", "blue", "green", "yellow"),   # top: yellow
        ("yellow", "green", "blue", "red"),   # top: red
        ("red", "blue", "green", "yellow"),   # top: yellow (満杯)
        ("yellow", "green", "blue", "red"),   # top: red (満杯)
    )


# --- get_legal_moves テスト ---

def test_get_legal_moves_basic():
    # ボトル0: (red, blue) → top: blue
    # ボトル1: (blue,) → top: blue
    # ボトル2: () → 空
    # ボトル3: () → 空
    # 合法手: blue を 0→1（同色）、0→2（空）、0→3（空）
    state: PuzzleState = (
        ("red", "blue"),
        ("blue",),
        (),
        (),
    )
    moves = get_legal_moves(state)
    # from=0 の手がある
    from_0_moves = [m for m in moves if m.from_bottle == 0]
    assert len(from_0_moves) >= 1


def test_get_legal_moves_empty_source_not_included():
    # 空ボトルからは移動できない
    state: PuzzleState = (
        (),
        ("red", "blue"),
        ("red",),
        (),
    )
    moves = get_legal_moves(state)
    assert all(m.from_bottle != 0 for m in moves)


def test_get_legal_moves_full_dest_not_included():
    # 満杯ボトルへは移動できない
    state: PuzzleState = (
        ("red", "blue", "green", "yellow"),   # 満杯
        ("blue", "red", "green", "yellow"),   # 満杯
        ("green",),
        (),
    )
    moves = get_legal_moves(state)
    # to_bottle が 0 または 1（満杯）の手はない
    assert all(m.to_bottle not in (0, 1) for m in moves)


def test_get_legal_moves_color_match():
    # to_bottle の最上層色と from_bottle の最上層色が一致する場合のみ合法
    state: PuzzleState = (
        ("red", "blue"),    # top: blue
        ("green", "red"),   # top: red → blue でないので blue を受け取れない
        ("green",),         # top: green → blue を受け取れない
        (),                 # 空 → 受け取れる
    )
    moves = get_legal_moves(state)
    # from=0(blue) → to=3(空) は合法のはず
    assert Move(0, 3) in moves
    # from=0(blue) → to=1(top:red) は不合法
    assert Move(0, 1) not in moves


def test_get_legal_moves_returns_list():
    state = make_simple_solvable()
    moves = get_legal_moves(state)
    assert isinstance(moves, list)
    for m in moves:
        assert isinstance(m, Move)


def test_get_legal_moves_all_full_no_empty():
    # 全ボトル満杯で最上層色が全て異なる → 合法手なし
    state: PuzzleState = (
        ("red", "blue", "green", "yellow"),
        ("yellow", "green", "blue", "red"),
        ("blue", "red", "yellow", "green"),
        ("green", "yellow", "red", "blue"),
    )
    moves = get_legal_moves(state)
    # 各ボトル満杯なので to_bottle が満杯のものは除かれる
    # → 実際に合法手があるか確認（空ボトルなし + 最上層色不一致なら0手）
    # この状態は全ボトル満杯なので移動先がない
    assert moves == []


# --- solve (BFS) テスト ---

def test_solve_bfs_simple():
    state = make_simple_solvable()
    result = solve(state, strategy="bfs", timeout=10.0)
    assert isinstance(result, SolverResult)
    assert result.solved is True
    assert len(result.moves) > 0
    # 解の適用後に解決状態になることを確認
    current = state
    for move in result.moves:
        current = apply_move(current, move)
    assert is_solved(current)


def test_solve_bfs_already_solved():
    state = make_already_solved()
    result = solve(state, strategy="bfs", timeout=10.0)
    # 解決済みなのでステップ0で解決
    assert result.solved is True
    assert len(result.moves) == 0


def test_solve_bfs_returns_solver_result():
    state = make_simple_solvable()
    result = solve(state, strategy="bfs", timeout=10.0)
    assert isinstance(result.solved, bool)
    assert isinstance(result.moves, list)
    assert isinstance(result.states_visited, int)
    assert isinstance(result.elapsed_time, float)
    assert result.elapsed_time >= 0.0


# --- solve (DFS) テスト ---

def test_solve_dfs_simple():
    state = make_simple_solvable()
    result = solve(state, strategy="dfs", timeout=10.0)
    assert result.solved is True
    assert len(result.moves) > 0
    # 解の適用後に解決状態になることを確認
    current = state
    for move in result.moves:
        current = apply_move(current, move)
    assert is_solved(current)


def test_solve_dfs_already_solved():
    state = make_already_solved()
    result = solve(state, strategy="dfs", timeout=10.0)
    assert result.solved is True
    assert len(result.moves) == 0


# --- タイムアウトテスト ---

def test_solve_timeout():
    # 非常に短いタイムアウト（0.001秒）で複雑なパズルを実行
    state: PuzzleState = (
        ("red", "blue", "green", "yellow"),
        ("yellow", "red", "blue", "green"),
        ("green", "yellow", "red", "blue"),
        ("blue", "green", "yellow", "red"),
        ("red", "blue", "green", "yellow"),
        ("yellow", "red", "blue", "green"),
        (),
        (),
    )
    with pytest.raises(PuzzleTimeoutError):
        solve(state, strategy="bfs", timeout=0.001)


def test_solve_no_timeout_when_zero():
    # タイムアウト 0 の場合は制限なし（簡単なパズルで確認）
    state = make_simple_solvable()
    result = solve(state, strategy="bfs", timeout=0)
    assert result.solved is True


# --- 解なしテスト ---

def test_solve_unsolvable_returns_false():
    # 解なしパズル：全ボトル満杯で最上層色が全て異なる（合法手なし）
    state: PuzzleState = (
        ("red", "blue", "green", "yellow"),
        ("yellow", "green", "blue", "red"),
        ("blue", "red", "yellow", "green"),
        ("green", "yellow", "red", "blue"),
    )
    result = solve(state, strategy="bfs", timeout=5.0)
    assert result.solved is False
    assert result.moves == []
