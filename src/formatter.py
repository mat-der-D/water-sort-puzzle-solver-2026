"""解法の text / json / yaml フォーマット出力"""
from __future__ import annotations

import json
import sys

import yaml

from src.models import OutputFormat, PuzzleState, SolverResult, apply_move


def format_output(
    result: SolverResult,
    initial_state: PuzzleState,
    fmt: OutputFormat = "text",
    verbose: bool = False,
) -> str:
    """
    SolverResult を指定フォーマットの文字列に変換して返す。
    Raises: ValueError（fmt が text|json|yaml 以外の場合）
    """
    match fmt:
        case "text":
            return _format_text(result, initial_state, verbose)
        case "json":
            return _format_json(result)
        case "yaml":
            return _format_yaml(result)
        case _:
            raise ValueError(f"未対応の出力フォーマット: {fmt!r}。text / json / yaml のいずれかを指定してください。")


def write_output(content: str, output_path: str | None = None) -> None:
    """
    content を output_path（指定時）または stdout に書き出す。
    Raises: OSError（ファイル書き込み失敗時）
    """
    if output_path is None:
        sys.stdout.write(content)
    else:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            print(f"ファイル書き込みエラー: {e}", file=sys.stderr)
            raise


def _format_text(
    result: SolverResult,
    initial_state: PuzzleState,
    verbose: bool,
) -> str:
    lines: list[str] = []
    current_state = initial_state

    for i, move in enumerate(result.moves, start=1):
        lines.append(
            f"ステップ {i}: ボトル {move.from_bottle + 1} → ボトル {move.to_bottle + 1}"
        )
        current_state = apply_move(current_state, move)
        if verbose:
            lines.append(_render_state(current_state))

    total = len(result.moves)
    lines.append(f"合計 {total} 手で解決しました。")
    return "\n".join(lines)


def _render_state(state: PuzzleState) -> str:
    """ボトル状態をテキストアートで表示"""
    parts = []
    for i, bottle in enumerate(state):
        contents = ", ".join(bottle) if bottle else "(空)"
        parts.append(f"  ボトル {i + 1}: [{contents}]")
    return "\n".join(parts)


def _build_dict(result: SolverResult) -> dict:
    return {
        "solved": result.solved,
        "total_moves": len(result.moves),
        "moves": [
            {"from": m.from_bottle + 1, "to": m.to_bottle + 1}
            for m in result.moves
        ],
        "stats": {
            "states_visited": result.states_visited,
            "elapsed_time": result.elapsed_time,
        },
    }


def _format_json(result: SolverResult) -> str:
    return json.dumps(_build_dict(result), ensure_ascii=False, indent=2)


def _format_yaml(result: SolverResult) -> str:
    return yaml.dump(
        _build_dict(result),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
