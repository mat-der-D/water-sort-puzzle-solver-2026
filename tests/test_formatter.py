"""src/formatter.py の単体テスト"""
import json
import os
import tempfile

import pytest
import yaml

from src.formatter import format_output, write_output
from src.models import Move, PuzzleState, SolverResult


# --- テスト用データ ---

def make_result(moves: list[tuple[int, int]] | None = None) -> SolverResult:
    if moves is None:
        moves = [(0, 2), (1, 3)]
    return SolverResult(
        solved=True,
        moves=[Move(f, t) for f, t in moves],
        states_visited=42,
        elapsed_time=0.123,
    )


def make_initial_state() -> PuzzleState:
    return (
        ("red", "blue"),
        ("blue", "red"),
        (),
        (),
    )


# --- text 形式テスト ---

def test_format_text_basic():
    result = make_result([(0, 2), (1, 3)])
    state = make_initial_state()
    output = format_output(result, state, fmt="text")
    assert "ステップ 1" in output
    assert "ボトル 1" in output  # 1-indexed
    assert "ボトル 3" in output  # 1-indexed
    assert "ステップ 2" in output


def test_format_text_summary():
    result = make_result([(0, 2), (1, 3)])
    state = make_initial_state()
    output = format_output(result, state, fmt="text")
    assert "2" in output  # 手数
    assert "合計" in output or "解決" in output


def test_format_text_one_indexed():
    # Move(0, 2) は「ボトル 1 → ボトル 3」と表示される（1-indexed）
    result = make_result([(0, 2)])
    state = make_initial_state()
    output = format_output(result, state, fmt="text")
    assert "ボトル 1" in output
    assert "ボトル 3" in output


def test_format_text_no_moves():
    result = SolverResult(solved=True, moves=[], states_visited=0, elapsed_time=0.0)
    state = make_initial_state()
    output = format_output(result, state, fmt="text")
    assert "0" in output or "すでに解決" in output or "解決" in output


def test_format_text_verbose():
    result = make_result([(0, 2)])
    state = make_initial_state()
    output = format_output(result, state, fmt="text", verbose=True)
    # verbose モードでは各ステップ後のボトル状態が含まれる
    assert "ステップ 1" in output
    # 状態表示が含まれること（ボトルの内容）
    assert "ボトル" in output or "[" in output or "|" in output


# --- JSON 形式テスト ---

def test_format_json_basic():
    result = make_result([(0, 2), (1, 3)])
    state = make_initial_state()
    output = format_output(result, state, fmt="json")
    data = json.loads(output)
    assert data["solved"] is True
    assert data["total_moves"] == 2
    assert len(data["moves"]) == 2
    assert data["moves"][0]["from"] == 1  # 1-indexed
    assert data["moves"][0]["to"] == 3    # 1-indexed
    assert "stats" in data
    assert data["stats"]["states_visited"] == 42


def test_format_json_stats():
    result = make_result([(0, 2)])
    state = make_initial_state()
    output = format_output(result, state, fmt="json")
    data = json.loads(output)
    assert "elapsed_time" in data["stats"]
    assert data["stats"]["elapsed_time"] == pytest.approx(0.123)


def test_format_json_is_valid_json():
    result = make_result([(0, 2), (1, 3), (2, 1)])
    state = make_initial_state()
    output = format_output(result, state, fmt="json")
    # JSON として有効であること
    data = json.loads(output)
    assert isinstance(data, dict)


# --- YAML 形式テスト ---

def test_format_yaml_basic():
    result = make_result([(0, 2), (1, 3)])
    state = make_initial_state()
    output = format_output(result, state, fmt="yaml")
    data = yaml.safe_load(output)
    assert data["solved"] is True
    assert data["total_moves"] == 2
    assert len(data["moves"]) == 2


def test_format_yaml_is_valid_yaml():
    result = make_result([(0, 2)])
    state = make_initial_state()
    output = format_output(result, state, fmt="yaml")
    data = yaml.safe_load(output)
    assert isinstance(data, dict)


# --- 不正フォーマットテスト ---

def test_format_invalid_fmt():
    result = make_result()
    state = make_initial_state()
    with pytest.raises(ValueError):
        format_output(result, state, fmt="xml")  # type: ignore


# --- write_output テスト ---

def test_write_output_to_stdout(capsys):
    write_output("テスト出力")
    captured = capsys.readouterr()
    assert captured.out == "テスト出力"


def test_write_output_to_file():
    content = "ファイル出力テスト"
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    write_output(content, output_path=path)
    with open(path) as f:
        assert f.read() == content


def test_write_output_none_path_goes_to_stdout(capsys):
    write_output("stdout テスト", output_path=None)
    captured = capsys.readouterr()
    assert "stdout テスト" in captured.out
