# 実装計画

- [x] 1. (P) `CLIArgs` に `format_help` フィールドを追加する
  - `src/models.py` の `CLIArgs` dataclass に `format_help: bool = False` フィールドを追加する
  - `format_help=True` の場合は `input_path` が使用されないことをコメントで明示する
  - _Requirements: 1.2, 1.4_

- [x] 2. フォーマットヘルプ文字列生成モジュールを実装する
- [x] 2.1 YAML・JSON・テキスト各フォーマットのセクションを実装する
  - `src/format_help.py` を新規作成し、`build_format_help_text() -> str` 関数を定義する
  - YAML セクション: `bottles` キーがリスト型であることを明示し、空ボトルを `null` または `[]` で表現する記法と、ボトル 4 本以上の最小構成サンプルを含める
  - JSON セクション: `{"bottles": [...]}` のトップレベル構造、空ボトルを空配列 `[]` で表現する記法と、ボトル 4 本以上の最小構成サンプルを含める
  - テキストセクション: 1 行 = 1 ボトル（スペース区切り）のルール、`(empty)` キーワード、ボトル 4 本以上のサンプル、空行無視の記載を含める
  - 各セクションにファイル拡張子の対応（YAML: `.yaml`/`.yml`、JSON: `.json`、テキスト: その他）を記載する
  - 関数は副作用なし（`sys.stdout` への書き込みを行わない）
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4_

- [x] 2.2 共通制約セクションを実装する
  - ボトル本数の範囲（最小 4 本・最大 20 本）を明示する
  - 非空ボトルはすべて同一の容量（セグメント数）でなければならないルールを記載する
  - 色名が任意の文字列であることを記載する
  - ファイル拡張子によるフォーマット自動検出のルールを説明する（`.yaml`/`.yml` → YAML、`.json` → JSON、その他 → テキスト）
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 3. CLIエントリポイントを修正して `--input-format-help` に対応させる
- [x] 3.1 `build_parser()` に `--input-format-help` オプションを追加する
  - `--input-format-help` 引数を `action="store_true"` で追加する
  - `--help` の説明文に「入力ファイルのフォーマット仕様を表示する」と記載する
  - `--input` を `required=False` に変更する
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 3.2 `main()` に早期終了ガードを追加する
  - `namespace.input_format_help` が真の場合、`build_format_help_text()` を呼び出して `print` し、`sys.exit(0)` する
  - `--input-format-help` が偽かつ `--input` が未指定の場合は `parser.error()` でエラーを出力する
  - `src.format_help` モジュールをインポートする
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 4. (P) フォーマットヘルプのユニットテストを実装する
  - `tests/test_format_help.py` を新規作成する
  - `build_format_help_text()` が非空文字列を返すことを確認するテストを追加する
  - YAML セクションに `bottles`・`null` または `[]`・`.yaml`/`.yml` が含まれることを検証する
  - JSON セクションに `{"bottles"`・`[]`・`.json` が含まれることを検証する
  - テキストセクションに `(empty)`・空行無視の記載が含まれることを検証する
  - 共通制約セクションにボトル本数範囲・統一容量ルール・色名任意・拡張子自動検出の記載が含まれることを検証する
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [x] 5. CLIエントリポイントの統合テストを実装する
  - `tests/test_main.py` を新規作成する
  - `--input-format-help` 単独指定で終了コード 0・stdout に出力があることを確認する
  - `--input-format-help --input puzzle.yaml` 同時指定でヘルプのみ出力・終了コード 0 を確認する
  - `--input-format-help --strategy dfs` 同時指定でヘルプのみ出力・終了コード 0 を確認する
  - `--input` 未指定（`--input-format-help` なし）でエラー終了（終了コード 2）することを確認する
  - _Requirements: 1.1, 1.2, 1.3, 1.4_
