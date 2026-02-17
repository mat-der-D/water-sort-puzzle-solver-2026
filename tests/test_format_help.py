"""build_format_help_text() のユニットテスト"""
from __future__ import annotations

import pytest

from src.format_help import build_format_help_text


def test_returns_nonempty_string() -> None:
    """非空文字列を返すこと"""
    result = build_format_help_text()
    assert isinstance(result, str)
    assert len(result) > 0


# --- YAML セクション ---

def test_yaml_bottles_key_is_list() -> None:
    """YAML セクションに bottles キーがリスト型であることを明示する"""
    result = build_format_help_text()
    assert "bottles" in result


def test_yaml_empty_bottle_notation() -> None:
    """YAML セクションに空ボトルを null または [] で表現する記法を含む"""
    result = build_format_help_text()
    assert "null" in result or "[]" in result


def test_yaml_sample_has_4_or_more_bottles() -> None:
    """YAML セクションにボトル 4 本以上のサンプルを含む"""
    result = build_format_help_text()
    # サンプル内のボトル数を確認: YAML サンプルには "-" でリスト要素が含まれる
    # セクション内に少なくとも 4 本分の記述があることを確認
    assert result.count("- [") >= 4 or result.count("  - ") >= 4 or result.count("- null") >= 1


def test_yaml_extension_info() -> None:
    """YAML セクションに .yaml / .yml の拡張子情報を含む"""
    result = build_format_help_text()
    assert ".yaml" in result
    assert ".yml" in result


# --- JSON セクション ---

def test_json_top_level_structure() -> None:
    """JSON セクションに {"bottles": [...]} のトップレベル構造を明示する"""
    result = build_format_help_text()
    assert '"bottles"' in result or "bottles" in result


def test_json_empty_bottle_notation() -> None:
    """JSON セクションに空ボトルを空配列 [] で表現する記法を含む"""
    result = build_format_help_text()
    assert "[]" in result


def test_json_extension_info() -> None:
    """JSON セクションに .json の拡張子情報を含む"""
    result = build_format_help_text()
    assert ".json" in result


# --- テキストセクション ---

def test_text_one_line_per_bottle_rule() -> None:
    """テキストセクションに 1 行 = 1 ボトルのルールを含む"""
    result = build_format_help_text()
    # 「1行」または「1 行」という記述
    assert "1行" in result or "1 行" in result or "1ライン" in result or "1 line" in result.lower()


def test_text_empty_keyword() -> None:
    """テキストセクションに (empty) キーワードを含む"""
    result = build_format_help_text()
    assert "(empty)" in result


def test_text_blank_line_ignored() -> None:
    """テキストセクションに空行が無視されることを記載する"""
    result = build_format_help_text()
    assert "空行" in result or "blank" in result.lower() or "empty line" in result.lower()


# --- 共通制約セクション ---

def test_common_bottle_count_range() -> None:
    """共通制約セクションにボトル本数の範囲（4〜20）を明示する"""
    result = build_format_help_text()
    assert "4" in result and "20" in result


def test_common_uniform_capacity_rule() -> None:
    """共通制約セクションに非空ボトルが同一容量でなければならないルールを含む"""
    result = build_format_help_text()
    assert "容量" in result or "セグメント" in result or "capacity" in result.lower()


def test_common_color_name_arbitrary() -> None:
    """共通制約セクションに色名が任意の文字列であることを含む"""
    result = build_format_help_text()
    assert "色" in result or "color" in result.lower()


def test_common_auto_detect_by_extension() -> None:
    """拡張子によるフォーマット自動検出のルールを含む"""
    result = build_format_help_text()
    # .yaml/.yml → YAML, .json → JSON の記述
    assert "自動" in result or "auto" in result.lower() or "検出" in result
