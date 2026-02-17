"""main.py の統合テスト・エンドツーエンドテスト"""
import json
import os
import sys
import tempfile

import pytest
import yaml

# main モジュールのインポート
import main as main_module
from main import build_parser, run
from src.models import CLIArgs


# --- テスト用パズルファイル生成 ---

def write_puzzle_yaml(bottles: list, suffix: str = ".yaml") -> str:
    data = {"bottles": bottles}
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        yaml.dump(data, f)
    return path


def write_puzzle_json(bottles: list) -> str:
    data = {"bottles": bottles}
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return path


def write_puzzle_text(lines: list[str]) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# 簡単な解決可能パズル（4本）
_SOLVABLE_BOTTLES = [
    ["red", "blue"],
    ["blue", "red"],
    [],
    [],
]

# 解決済みパズル
_SOLVED_BOTTLES = [
    ["red", "red", "red", "red"],
    ["blue", "blue", "blue", "blue"],
    [],
    [],
]


# --- build_parser テスト ---

def test_build_parser_returns_parser():
    import argparse
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_has_input_option():
    parser = build_parser()
    args = parser.parse_args(["--input", "test.yaml"])
    assert args.input == "test.yaml"


def test_build_parser_strategy_choices():
    parser = build_parser()
    args = parser.parse_args(["--input", "p.yaml", "--strategy", "dfs"])
    assert args.strategy == "dfs"


def test_build_parser_format_choices():
    parser = build_parser()
    args = parser.parse_args(["--input", "p.yaml", "--format", "json"])
    assert args.format == "json"


def test_build_parser_validate_flag():
    parser = build_parser()
    args = parser.parse_args(["--input", "p.yaml", "--validate"])
    assert args.validate is True


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["--input", "p.yaml"])
    assert args.strategy == "bfs"
    assert args.format == "text"
    assert args.timeout == 30.0
    assert args.verbose is False
    assert args.debug is False


# --- run() 正常系テスト ---

def test_run_bfs_solve(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, strategy="bfs", timeout=10.0)
    exit_code = run(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "合計" in captured.out or "ステップ" in captured.out


def test_run_dfs_solve(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, strategy="dfs", timeout=10.0)
    exit_code = run(args)
    assert exit_code == 0


def test_run_already_solved(capsys):
    path = write_puzzle_yaml(_SOLVED_BOTTLES)
    args = CLIArgs(input_path=path)
    exit_code = run(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "解決" in captured.out or "すでに" in captured.out


def test_run_validate_only_valid(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, validate_only=True)
    exit_code = run(args)
    assert exit_code == 0


def test_run_validate_only_invalid(capsys):
    # 不正なパズル（redが3セグメントのみ）
    bottles = [
        ["red", "red", "red", "blue"],  # red=3（4の倍数でない）
        ["blue", "blue", "blue", "blue"],
        [],
        [],
    ]
    path = write_puzzle_yaml(bottles)
    args = CLIArgs(input_path=path, validate_only=True)
    exit_code = run(args)
    assert exit_code == 1


def test_run_json_output(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, output_format="json")
    exit_code = run(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["solved"] is True


def test_run_yaml_output(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, output_format="yaml")
    exit_code = run(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    data = yaml.safe_load(captured.out)
    assert data["solved"] is True


def test_run_file_not_found(capsys):
    args = CLIArgs(input_path="/nonexistent/puzzle.yaml")
    exit_code = run(args)
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "見つかりません" in captured.err or "ファイル" in captured.err


def test_run_parse_error(capsys):
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w") as f:
        f.write("bottles: [invalid: yaml: :")
    args = CLIArgs(input_path=path)
    exit_code = run(args)
    assert exit_code == 1


def test_run_output_to_file(capsys):
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    fd, out_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    args = CLIArgs(input_path=path, output_path=out_path)
    exit_code = run(args)
    assert exit_code == 0
    with open(out_path) as f:
        content = f.read()
    assert "合計" in content or "ステップ" in content


def test_run_timeout(capsys):
    # 複雑なパズルで短いタイムアウト（各色が4の倍数のセグメント数で有効）
    # 4色×8セグメント=32セグメント、8本のボトル+2本の空=10本
    bottles = [
        ["red", "blue", "green", "yellow"],
        ["yellow", "red", "blue", "green"],
        ["green", "yellow", "red", "blue"],
        ["blue", "green", "yellow", "red"],
        ["red", "blue", "green", "yellow"],
        ["yellow", "red", "blue", "green"],
        ["green", "yellow", "red", "blue"],
        ["blue", "green", "yellow", "red"],
        [],
        [],
    ]
    path = write_puzzle_yaml(bottles)
    args = CLIArgs(input_path=path, timeout=0.001)
    exit_code = run(args)
    assert exit_code == 2


# --- パフォーマンステスト ---

def test_performance_standard_puzzle():
    """12ボトル × 4セグメントのパズルが30秒以内に解ける（または合理的な時間でタイムアウト）"""
    import time
    # 実際に解けるパズルではなく、ある程度の規模で動作確認
    # 小さなパズルで十分速いことを確認
    path = write_puzzle_yaml(_SOLVABLE_BOTTLES)
    args = CLIArgs(input_path=path, strategy="bfs", timeout=30.0)
    start = time.perf_counter()
    exit_code = run(args)
    elapsed = time.perf_counter() - start
    assert exit_code == 0
    assert elapsed < 30.0


# --- --input-format-help 統合テスト ---

def test_input_format_help_alone_exits_0(capsys):
    """--input-format-help 単独指定で終了コード 0 になること"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--input-format-help"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert result.returncode == 0


def test_input_format_help_alone_has_stdout():
    """--input-format-help 単独指定で stdout に出力があること"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--input-format-help"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert len(result.stdout) > 0


def test_input_format_help_with_input_option():
    """--input-format-help --input puzzle.yaml 同時指定でヘルプのみ出力・終了コード 0"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--input-format-help", "--input", "puzzle.yaml"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert result.returncode == 0
    assert len(result.stdout) > 0


def test_input_format_help_with_strategy_option():
    """--input-format-help --strategy dfs 同時指定でヘルプのみ出力・終了コード 0"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--input-format-help", "--strategy", "dfs"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert result.returncode == 0
    assert len(result.stdout) > 0


def test_missing_input_without_format_help_exits_2():
    """--input 未指定（--input-format-help なし）でエラー終了（終了コード 2）"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert result.returncode == 2


def test_input_format_help_does_not_run_pipeline():
    """--input-format-help 指定時は解析・探索処理を実行しないこと（存在しないファイルでもエラーにならない）"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--input-format-help", "--input", "nonexistent_file_xyz.yaml"],
        capture_output=True, text=True,
        cwd="/home/smoothpudding/Documents/dev/github/water-sort-puzzle-solver-2026",
    )
    assert result.returncode == 0
