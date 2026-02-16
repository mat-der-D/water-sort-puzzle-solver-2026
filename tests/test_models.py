"""src/models.py の単体テスト"""
import pytest
from src.models import (
    BOTTLE_CAPACITY,
    CLIArgs,
    Move,
    ParseError,
    PuzzleState,
    PuzzleTimeoutError,
    SolverResult,
    ValidationResult,
    apply_move,
)


# --- 定数テスト ---

def test_bottle_capacity_default():
    assert BOTTLE_CAPACITY == 4


# --- Move テスト ---

def test_move_named_tuple():
    m = Move(from_bottle=0, to_bottle=2)
    assert m.from_bottle == 0
    assert m.to_bottle == 2


def test_move_immutable():
    m = Move(0, 1)
    with pytest.raises(AttributeError):
        m.from_bottle = 5  # type: ignore


# --- SolverResult テスト ---

def test_solver_result_fields():
    r = SolverResult(solved=True, moves=[Move(0, 1)], states_visited=10, elapsed_time=0.5)
    assert r.solved is True
    assert r.moves == [Move(0, 1)]
    assert r.states_visited == 10
    assert r.elapsed_time == 0.5


# --- ValidationResult テスト ---

def test_validation_result_valid():
    v = ValidationResult(valid=True, already_solved=False, error_message=None)
    assert v.valid is True
    assert v.error_message is None


def test_validation_result_invalid():
    v = ValidationResult(valid=False, already_solved=False, error_message="色の合計が不正")
    assert v.valid is False
    assert v.error_message == "色の合計が不正"


# --- CLIArgs テスト ---

def test_cli_args_defaults():
    args = CLIArgs(input_path="puzzle.yaml")
    assert args.input_path == "puzzle.yaml"
    assert args.validate_only is False
    assert args.strategy == "bfs"
    assert args.timeout == 30.0
    assert args.output_format == "text"
    assert args.output_path is None
    assert args.verbose is False
    assert args.debug is False


def test_cli_args_custom():
    args = CLIArgs(
        input_path="p.json",
        validate_only=True,
        strategy="dfs",
        timeout=10.0,
        output_format="json",
        output_path="out.json",
        verbose=True,
        debug=True,
    )
    assert args.strategy == "dfs"
    assert args.timeout == 10.0


# --- カスタム例外テスト ---

def test_parse_error_is_value_error():
    err = ParseError("フォーマット不正")
    assert isinstance(err, ValueError)
    assert str(err) == "フォーマット不正"


def test_puzzle_timeout_error():
    err = PuzzleTimeoutError("タイムアウト")
    assert isinstance(err, Exception)


# --- apply_move テスト ---

def test_apply_move_basic():
    # ボトル0: (red, blue) ボトル1: (red,)  →  Move(0, 1) で red を 0→1 へ
    # ボトル0の最上層は blue (インデックス1)、ボトル1の最上層は red (インデックス0)
    # 合法手ではないが apply_move は合法性チェックなし（pure function）
    state: PuzzleState = (("red", "blue"), ("red",))
    move = Move(from_bottle=0, to_bottle=1)
    new_state = apply_move(state, move)
    # from_bottle(0) から最上層 "blue" を取り出す
    assert new_state[0] == ("red",)
    # to_bottle(1) に "blue" が積まれる
    assert new_state[1] == ("red", "blue")


def test_apply_move_does_not_mutate_original():
    state: PuzzleState = (("red", "blue"), ("green",))
    original_state = state
    new_state = apply_move(state, Move(0, 1))
    assert state is original_state
    assert state == (("red", "blue"), ("green",))


def test_apply_move_empty_source_after():
    # ボトル0に1セグメントだけ → 移動後は空タプル
    state: PuzzleState = (("red",), ("red",))
    new_state = apply_move(state, Move(0, 1))
    assert new_state[0] == ()
    assert new_state[1] == ("red", "red")


def test_apply_move_returns_immutable():
    state: PuzzleState = (("red",), ())
    new_state = apply_move(state, Move(0, 1))
    # タプルであること（hashable）
    assert isinstance(new_state, tuple)
    for bottle in new_state:
        assert isinstance(bottle, tuple)


def test_apply_move_result_is_hashable():
    state: PuzzleState = (("red", "blue"), ("green",))
    new_state = apply_move(state, Move(0, 1))
    # set に格納できる（hashable）
    visited = {state, new_state}
    assert len(visited) == 2
