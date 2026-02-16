"""src/parser.py の単体テスト"""
import json
import os
import tempfile

import pytest
import yaml

from src.models import BOTTLE_CAPACITY, ParseError
from src.parser import parse_file


# --- テスト用ヘルパー ---

def write_temp(content: str, suffix: str) -> str:
    """一時ファイルを作成してパスを返す"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


# 最小4本を満たす標準的なテスト用パズル
_STANDARD_BOTTLES = [
    ["red", "blue", "green", "red"],
    ["blue", "green", "red", "blue"],
    ["green", "red", "blue", "green"],
    [],
]


# --- YAML 形式 ---

def test_parse_yaml_basic():
    data = {"bottles": _STANDARD_BOTTLES}
    path = write_temp(yaml.dump(data), ".yaml")
    state, capacity = parse_file(path)
    assert capacity == 4
    assert state[0] == ("red", "blue", "green", "red")
    assert state[1] == ("blue", "green", "red", "blue")
    assert state[3] == ()


def test_parse_yaml_yml_extension():
    data = {"bottles": [["a", "b"], ["b", "a"], ["a", "b"], ["b", "a"]]}
    path = write_temp(yaml.dump(data), ".yml")
    state, capacity = parse_file(path)
    assert capacity == 2
    assert state[0] == ("a", "b")


def test_parse_yaml_auto_detect():
    data = {"bottles": [["red"], ["blue"], ["green"], ["red"]]}
    path = write_temp(yaml.dump(data), ".yaml")
    state, capacity = parse_file(path, fmt="auto")
    assert len(state) == 4


def test_parse_yaml_explicit_fmt():
    data = {"bottles": [["x", "y"], ["y", "x"], ["x", "y"], ["y", "x"]]}
    path = write_temp(yaml.dump(data), ".txt")  # 拡張子はtxtだが明示的にyamlを指定
    state, capacity = parse_file(path, fmt="yaml")
    assert state[0] == ("x", "y")


# --- JSON 形式 ---

def test_parse_json_basic():
    data = {"bottles": [["red", "blue"], ["green", "red"], ["blue", "green"], []]}
    path = write_temp(json.dumps(data), ".json")
    state, capacity = parse_file(path)
    assert capacity == 2
    assert state[0] == ("red", "blue")
    assert state[3] == ()


def test_parse_json_explicit_fmt():
    data = {"bottles": [["a", "b", "c"], ["c", "b", "a"], ["a", "b", "c"], ["c", "b", "a"]]}
    path = write_temp(json.dumps(data), ".data")
    state, capacity = parse_file(path, fmt="json")
    assert capacity == 3


# --- テキスト形式 ---

def test_parse_text_basic():
    content = "red blue green\nblue green red\ngreen red blue\n(empty)\n"
    path = write_temp(content, ".txt")
    state, capacity = parse_file(path)
    assert capacity == 3
    assert state[0] == ("red", "blue", "green")
    assert state[1] == ("blue", "green", "red")


def test_parse_text_empty_bottle():
    content = "red blue\ngreen red\nblue green\n(empty)\n"
    path = write_temp(content, ".txt")
    state, capacity = parse_file(path)
    assert state[3] == ()


def test_parse_text_explicit_fmt():
    content = "a b\nb a\na b\nb a\n"
    path = write_temp(content, ".yaml")  # 拡張子はyamlだが明示的にtextを指定
    state, capacity = parse_file(path, fmt="text")
    assert state[0] == ("a", "b")


# --- エラーケース ---

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_file("/nonexistent/path/puzzle.yaml")


def test_parse_error_invalid_yaml():
    path = write_temp("bottles: [invalid: yaml: :", ".yaml")
    with pytest.raises(ParseError):
        parse_file(path)


def test_parse_error_missing_bottles_key_yaml():
    data = {"wrong_key": [["red"]]}
    path = write_temp(yaml.dump(data), ".yaml")
    with pytest.raises(ParseError) as exc_info:
        parse_file(path)
    assert "bottles" in str(exc_info.value).lower() or "キー" in str(exc_info.value)


def test_parse_error_missing_bottles_key_json():
    data = {"data": [["red"]]}
    path = write_temp(json.dumps(data), ".json")
    with pytest.raises(ParseError):
        parse_file(path)


def test_parse_error_too_few_bottles():
    data = {"bottles": [["red", "blue", "green", "red"]]}  # 1本のみ
    path = write_temp(yaml.dump(data), ".yaml")
    with pytest.raises(ParseError) as exc_info:
        parse_file(path)
    assert "4" in str(exc_info.value) or "本" in str(exc_info.value)


def test_parse_error_too_many_bottles():
    # 21本（上限超え）
    data = {"bottles": [["red"] for _ in range(21)]}
    path = write_temp(yaml.dump(data), ".yaml")
    with pytest.raises(ParseError) as exc_info:
        parse_file(path)
    assert "20" in str(exc_info.value) or "本" in str(exc_info.value)


def test_parse_error_mismatched_capacity():
    # ボトルのセグメント数が不一致（4本以上で不一致）
    data = {"bottles": [["red", "blue"], ["red", "blue", "green"], ["red"], ["blue", "green"]]}
    path = write_temp(yaml.dump(data), ".yaml")
    with pytest.raises(ParseError) as exc_info:
        parse_file(path)
    assert "容量" in str(exc_info.value) or "セグメント" in str(exc_info.value) or "一致" in str(exc_info.value)


def test_parse_returns_tuple_of_tuples():
    data = {"bottles": [["red", "blue"], ["blue", "red"], ["red", "blue"], ["blue", "red"]]}
    path = write_temp(yaml.dump(data), ".yaml")
    state, capacity = parse_file(path)
    assert isinstance(state, tuple)
    for b in state:
        assert isinstance(b, tuple)
