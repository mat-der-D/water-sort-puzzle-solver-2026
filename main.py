"""Water Sort Puzzle Solver CLI エントリポイント"""
from __future__ import annotations

import argparse
import sys

from src.formatter import format_output, write_output
from src.models import CLIArgs, ParseError, PuzzleTimeoutError
from src.parser import parse_file
from src.solver import solve
from src.validator import validate

__version__ = "0.1.0"

_EXIT_OK = 0
_EXIT_ERROR = 1
_EXIT_TIMEOUT = 2


def build_parser() -> argparse.ArgumentParser:
    """引数パーサを構築して返す。"""
    parser = argparse.ArgumentParser(
        prog="water-sort-solver",
        description="ウォーターソートパズルの解法を自動生成するCLIツール",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="入力ファイルのパス（YAML / JSON / テキスト形式）",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="パズル状態の検証のみ行い、解法探索はしない",
    )
    parser.add_argument(
        "--strategy",
        choices=["bfs", "dfs"],
        default="bfs",
        help="探索アルゴリズム（デフォルト: bfs）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="タイムアウト秒数（0 でタイムアウトなし、デフォルト: 30.0）",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="出力フォーマット（デフォルト: text）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="出力ファイルのパス（未指定時は stdout）",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="各ステップ後のボトル状態を表示する（text フォーマット時のみ有効）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="探索進捗を stderr に出力する",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def run(args: CLIArgs) -> int:
    """CLIArgs を受け取り、処理を実行して終了コードを返す。"""
    # 1. 入力解析
    try:
        state, bottle_capacity = parse_file(args.input_path)
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません: {args.input_path}", file=sys.stderr)
        return _EXIT_ERROR
    except ParseError as e:
        print(f"エラー: 入力ファイルの解析に失敗しました。\n{e}", file=sys.stderr)
        return _EXIT_ERROR

    # 2. 検証
    validation = validate(state, bottle_capacity)
    if not validation.valid:
        print(f"エラー: パズル状態が不正です。\n{validation.error_message}", file=sys.stderr)
        return _EXIT_ERROR

    # 3. --validate のみの場合は検証結果を返して終了
    if args.validate_only:
        if validation.already_solved:
            print("パズルはすでに解決されています。（検証のみ実行）")
        else:
            print("パズル状態は有効です。")
        return _EXIT_OK

    # 4. 解決済み判定
    if validation.already_solved:
        print("パズルはすでに解決されています。")
        return _EXIT_OK

    # 5. 解法探索
    try:
        result = solve(
            initial_state=state,
            strategy=args.strategy,
            timeout=args.timeout,
            debug=args.debug,
        )
    except PuzzleTimeoutError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return _EXIT_TIMEOUT

    # 6. 解なし
    if not result.solved:
        print("このパズルは解決不可能です。", file=sys.stderr)
        return _EXIT_ERROR

    # 7. 出力フォーマット
    output = format_output(
        result=result,
        initial_state=state,
        fmt=args.output_format,
        verbose=args.verbose,
    )
    write_output(output, output_path=args.output_path)
    return _EXIT_OK


def main() -> None:
    """CLI エントリポイント。引数を解析して run() を呼び出す。"""
    parser = build_parser()
    # 不明なオプションを検出
    namespace, unknown = parser.parse_known_args()
    if unknown:
        print(
            f"エラー: 不明なオプション: {unknown}\n"
            f"使い方を確認するには --help を使用してください。",
            file=sys.stderr,
        )
        sys.exit(_EXIT_ERROR)

    args = CLIArgs(
        input_path=namespace.input,
        validate_only=namespace.validate,
        strategy=namespace.strategy,
        timeout=namespace.timeout,
        output_format=namespace.format,
        output_path=namespace.output,
        verbose=namespace.verbose,
        debug=namespace.debug,
    )
    sys.exit(run(args))


if __name__ == "__main__":
    main()
