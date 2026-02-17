"""入力ファイルフォーマットヘルプ文字列の生成モジュール"""
from __future__ import annotations


def build_format_help_text() -> str:
    """
    全フォーマット（YAML・JSON・テキスト）の仕様説明・サンプル・共通制約を含む文字列を返す。
    副作用なし（sys.stdout への書き込みは行わない）。
    """
    sections = [
        _yaml_section(),
        _json_section(),
        _text_section(),
        _common_constraints_section(),
    ]
    return "\n\n".join(sections)


def _yaml_section() -> str:
    return """\
=== YAML フォーマット ===
拡張子: .yaml / .yml

構造:
  - トップレベルキー `bottles` がボトルのリスト（list型）
  - 各ボトルは色名（文字列）のリスト、または空ボトルを表す null / []

サンプル（最小構成: 4本以上）:
  bottles:
    - [赤, 青, 赤, 青]
    - [緑, 緑, 黄, 黄]
    - [青, 赤, 黄, 緑]
    - [黄, 緑, 青, 赤]
    - null
    - []"""


def _json_section() -> str:
    return """\
=== JSON フォーマット ===
拡張子: .json

構造:
  - トップレベルは {"bottles": [...]} のオブジェクト
  - 各ボトルは色名（文字列）の配列、または空ボトルを表す空配列 []

サンプル（最小構成: 4本以上）:
  {
    "bottles": [
      ["赤", "青", "赤", "青"],
      ["緑", "緑", "黄", "黄"],
      ["青", "赤", "黄", "緑"],
      ["黄", "緑", "青", "赤"],
      []
    ]
  }"""


def _text_section() -> str:
    return """\
=== テキストフォーマット ===
拡張子: その他（.txt など）

構造:
  - 1行 = 1ボトル（色名をスペース区切りで列挙）
  - 空ボトルは (empty) キーワードで表現
  - 空行は無視される

サンプル（最小構成: 4本以上）:
  赤 青 赤 青
  緑 緑 黄 黄
  青 赤 黄 緑
  黄 緑 青 赤
  (empty)"""


def _common_constraints_section() -> str:
    return """\
=== 共通制約 ===
ボトル本数: 最小 4 本・最大 20 本
容量（セグメント数）: 非空ボトルはすべて同一の容量でなければならない
色名: 任意の文字列（スペースを含まない）
フォーマット自動検出: 拡張子に基づいて自動的に判定する
  .yaml / .yml → YAML フォーマット
  .json        → JSON フォーマット
  その他        → テキストフォーマット"""
