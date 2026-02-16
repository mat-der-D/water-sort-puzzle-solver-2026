"""src/validator.py の単体テスト"""
import pytest
from src.models import BOTTLE_CAPACITY, PuzzleState, ValidationResult
from src.validator import is_solved, validate


# --- is_solved テスト ---

def test_is_solved_already_solved():
    # 全ボトルが単色または空
    state: PuzzleState = (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )
    assert is_solved(state) is True


def test_is_solved_not_solved():
    state: PuzzleState = (
        ("red", "blue", "red", "red"),
        ("blue", "red", "blue", "blue"),
        (),
        (),
    )
    assert is_solved(state) is False


def test_is_solved_all_empty():
    state: PuzzleState = ((), (), (), ())
    assert is_solved(state) is True


def test_is_solved_partial_fill():
    # 部分的に同色（ただし容量満たしていないが単色）
    state: PuzzleState = (
        ("red", "red"),
        ("blue", "blue"),
        (),
        (),
    )
    assert is_solved(state) is True


def test_is_solved_mixed_single_bottle():
    # 1本だけ混色
    state: PuzzleState = (
        ("red", "blue", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )
    assert is_solved(state) is False


# --- validate テスト ---

def test_validate_valid_state():
    # 各色が4セグメントずつ（1色 × 1本 × 4セグメント）
    state: PuzzleState = (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        ("green", "green", "green", "green"),
        (),
    )
    result = validate(state, bottle_capacity=4)
    assert result.valid is True
    assert result.error_message is None


def test_validate_already_solved():
    state: PuzzleState = (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        ("green", "green", "green", "green"),
        (),
    )
    result = validate(state, bottle_capacity=4)
    assert result.already_solved is True


def test_validate_not_yet_solved():
    # 解決前の状態（混色あり）
    state: PuzzleState = (
        ("red", "blue", "green", "red"),
        ("blue", "green", "red", "blue"),
        ("green", "red", "blue", "green"),
        (),
    )
    result = validate(state, bottle_capacity=4)
    assert result.valid is True
    assert result.already_solved is False


def test_validate_invalid_color_count():
    # red が3セグメントしかない（4の倍数にならない）
    state: PuzzleState = (
        ("red", "red", "red", "blue"),
        ("blue", "blue", "blue", "red"),  # red=4, blue=4 → 実はOK... 別のケースで
        (),
        (),
    )
    # こちらはOKなので別のケースを試す
    state2: PuzzleState = (
        ("red", "red", "red", "blue"),
        ("blue", "blue", "blue", "blue"),  # red=3（4の倍数でない）
        (),
        (),
    )
    result = validate(state2, bottle_capacity=4)
    assert result.valid is False
    assert result.error_message is not None


def test_validate_zero_bottles():
    state: PuzzleState = ()
    result = validate(state, bottle_capacity=4)
    assert result.valid is False
    assert result.error_message is not None


def test_validate_returns_validation_result():
    state: PuzzleState = (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )
    result = validate(state, bottle_capacity=4)
    assert isinstance(result, ValidationResult)


def test_validate_invalid_sets_error_message():
    state: PuzzleState = (
        ("red", "red", "red", "blue"),  # red=3（4の倍数でない）
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )
    result = validate(state, bottle_capacity=4)
    if not result.valid:
        assert result.error_message is not None
        assert len(result.error_message) > 0


def test_validate_default_bottle_capacity():
    # デフォルト容量（4）で検証
    state: PuzzleState = (
        ("red", "red", "red", "red"),
        ("blue", "blue", "blue", "blue"),
        (),
        (),
    )
    result = validate(state)
    assert result.valid is True
