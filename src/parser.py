"""入力ファイルの解析（YAML / JSON / テキスト形式）"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml

from src.models import BOTTLE_CAPACITY, ParseError, PuzzleState

_MIN_BOTTLES = 4
_MAX_BOTTLES = 20


def parse_file(
    path: str,
    fmt: Literal["yaml", "json", "text", "auto"] = "auto",
) -> tuple[PuzzleState, int]:
    """
    指定パスのファイルを読み込み (PuzzleState, bottle_capacity) を返す。
    Raises: FileNotFoundError, ParseError
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

    # フォーマット判定
    resolved_fmt = fmt
    if fmt == "auto":
        suffix = p.suffix.lower()
        if suffix in (".yaml", ".yml"):
            resolved_fmt = "yaml"
        elif suffix == ".json":
            resolved_fmt = "json"
        else:
            resolved_fmt = "text"

    text = p.read_text(encoding="utf-8")

    if resolved_fmt == "yaml":
        bottles_raw = _parse_yaml(text, path)
    elif resolved_fmt == "json":
        bottles_raw = _parse_json(text, path)
    else:
        bottles_raw = _parse_text(text, path)

    return _build_state(bottles_raw, path)


def _parse_yaml(text: str, path: str) -> list[list[str]]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ParseError(
            f"YAML 解析エラー: {e}\n"
            f"期待フォーマット:\n  bottles:\n    - [color1, color2, ...]\n    - []"
        ) from e
    if not isinstance(data, dict) or "bottles" not in data:
        raise ParseError(
            f"'bottles' キーが見つかりません: {path}\n"
            f"期待フォーマット:\n  bottles:\n    - [color1, color2, ...]\n    - []"
        )
    bottles = data["bottles"]
    if not isinstance(bottles, list):
        raise ParseError(f"'bottles' はリストである必要があります: {path}")
    return [b if b is not None else [] for b in bottles]


def _parse_json(text: str, path: str) -> list[list[str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(
            f"JSON 解析エラー: {e}\n"
            f'期待フォーマット: {{"bottles": [["color1", "color2"], []]}}'
        ) from e
    if not isinstance(data, dict) or "bottles" not in data:
        raise ParseError(
            f"'bottles' キーが見つかりません: {path}\n"
            f'期待フォーマット: {{"bottles": [["color1", "color2"], []]}}'
        )
    bottles = data["bottles"]
    if not isinstance(bottles, list):
        raise ParseError(f"'bottles' はリストである必要があります: {path}")
    return [b if b is not None else [] for b in bottles]


def _parse_text(text: str, path: str) -> list[list[str]]:
    bottles: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "(empty)":
            bottles.append([])
        else:
            bottles.append(line.split())
    return bottles


def _build_state(bottles_raw: list[list[str]], path: str) -> tuple[PuzzleState, int]:
    """raw リストを検証して (PuzzleState, bottle_capacity) に変換する"""
    n = len(bottles_raw)
    if n < _MIN_BOTTLES:
        raise ParseError(
            f"ボトル数が少なすぎます: {n} 本（最小 {_MIN_BOTTLES} 本）: {path}"
        )
    if n > _MAX_BOTTLES:
        raise ParseError(
            f"ボトル数が多すぎます: {n} 本（最大 {_MAX_BOTTLES} 本）: {path}"
        )

    # 容量（空でないボトルの最大セグメント数）を決定
    non_empty_lengths = [len(b) for b in bottles_raw if len(b) > 0]
    if non_empty_lengths:
        capacity = max(non_empty_lengths)
        # 全ボトルのセグメント数が統一されているか確認（空ボトルは除外）
        if any(len(b) != capacity for b in bottles_raw if len(b) > 0):
            raise ParseError(
                f"ボトル間でセグメント数（容量）が一致しません: {path}\n"
                f"全ボトルは同じ容量（または空）である必要があります。"
            )
    else:
        capacity = BOTTLE_CAPACITY  # 全ボトル空の場合はデフォルト

    state: PuzzleState = tuple(tuple(b) for b in bottles_raw)
    return state, capacity
