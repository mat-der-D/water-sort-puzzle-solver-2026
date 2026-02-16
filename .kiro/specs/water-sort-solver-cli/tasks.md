# 実装計画

- [ ] 1. 共有データモデルと基盤整備
- [ ] 1.1 プロジェクト基盤のセットアップ
  - `src/` ディレクトリと `src/__init__.py` を作成し、パッケージ構造を整備する
  - `tests/` ディレクトリを作成し、テスト用の基本構造を用意する
  - `pyproject.toml` に pyyaml 依存と Python 3.12+ 設定が揃っていることを確認し、不足があれば追記する
  - _Requirements: 5.5_

- [ ] 1.2 パズル状態・移動手順・解法結果の型定義
  - `BottleState`（色文字列タプル、下から上の順）と `PuzzleState`（ボトルタプルのイミュータブルなタプル）を定義する
  - `Move`（from_bottle / to_bottle の 0-indexed ペア）と `SolverResult`（solved フラグ・moves リスト・states_visited・elapsed_time）を定義する
  - `BOTTLE_CAPACITY` 定数（デフォルト 4）を定義する
  - _Requirements: 1.4, 3.2_

- [ ] 1.3 CLIArgs・ValidationResult・エラー型の定義
  - `ValidationResult`（valid フラグ・already_solved フラグ・error_message）を定義する
  - `CLIArgs`（input_path・validate_only・strategy・timeout・output_format・output_path・verbose・debug）を定義する
  - `ParseError`（入力ファイル解析エラー）と `PuzzleTimeoutError`（タイムアウトエラー）のカスタム例外クラスを定義する
  - `Strategy` と `OutputFormat` の型エイリアスを定義する
  - _Requirements: 2.2, 2.4, 3.3, 3.4, 4.5, 5.4, 6.1, 6.2_

- [ ] 1.4 ムーブ適用の純粋変換関数の実装
  - `apply_move()` を副作用のない純粋関数として実装し、元の PuzzleState を変更せずムーブ適用後の新しい PuzzleState を返す
  - ソルバ（探索中の状態生成）とフォーマッター（verbose モードの中間状態再生成）の両方から共有できる場所に配置する
  - _Requirements: 3.2_

- [ ] 2. 入力解析機能の実装
- [ ] 2.1 YAML・JSON・テキスト形式のファイル解析
  - `parse_file()` を実装し、ファイル拡張子（`.yaml`/`.yml`・`.json`・その他）または明示的なフォーマット引数に基づいて解析形式を自動選択する
  - YAML 形式は pyyaml の `safe_load()` を使用し、`bottles` キー配下のリストを解析する
  - JSON 形式は標準ライブラリ `json` で `bottles` キーのリストを解析する
  - テキスト形式は各行をスペース区切りで色名として解析し、`(empty)` を空ボトルとして扱う
  - 解析結果として `PuzzleState` と `bottle_capacity`（全ボトルの最大セグメント数）のタプルを返す
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 2.2 入力エラーハンドリング
  - ファイルが存在しない場合は `FileNotFoundError` を raise する
  - フォーマットが不正な場合は `ParseError` を raise し、エラーの種別（「色名が不正」「ボトルの容量が一致しない」等）と期待するフォーマット例をメッセージに含める
  - ボトル間でセグメント数が不一致の場合も `ParseError` として処理する
  - ボトル数が標準範囲（4〜20 本）を超える場合も `ParseError` とする
  - _Requirements: 1.5, 6.1, 6.2_

- [ ] 3. パズル検証機能の実装
- [ ] 3.1 パズル状態の妥当性検証
  - `validate()` を実装し、ボトル数が 0 でないこと・容量が 0 のボトルが存在しないことを検証する
  - `collections.Counter` で色ごとの合計セグメント数を集計し、`bottle_capacity` の倍数であることを検証する
  - 検証結果を `ValidationResult`（valid フラグ・error_message）として返す
  - _Requirements: 1.4, 1.5, 2.1, 2.2, 2.3_

- [ ] 3.2 解決済みパズルの判定
  - `is_solved()` を実装し、全ボトルが単色（同色のみ）または空の場合に `True` を返す
  - `validate()` 内で `is_solved()` を呼び出し、`ValidationResult.already_solved` フラグをセットする
  - _Requirements: 2.4, 2.5_

- [ ] 4. ソルバの実装
- [ ] 4.1 合法手の生成ロジック実装
  - `get_legal_moves()` を実装し、現在のパズル状態から全ての合法手を列挙して返す
  - 合法手の条件：注ぎ元が空でない、注ぎ先に空き容量がある、注ぎ元の最上層色が注ぎ先の最上層色と一致するか注ぎ先が空
  - 結果は `Move` オブジェクト（0-indexed ボトルペア）のリストとして返す
  - _Requirements: 3.1, 3.2_

- [ ] 4.2 BFS アルゴリズムの実装
  - `collections.deque` を使ったキューで幅優先探索を実装し、最短手数の解法を保証する
  - 訪問済み状態を `dict[PuzzleState, tuple[PuzzleState, Move]]`（親状態とムーブ）で管理し、解決状態から遡って手順を復元する
  - `SolverResult`（solved=True・moves リスト・states_visited・elapsed_time）を返す
  - 解が存在しない場合は `SolverResult(solved=False, moves=[], ...)` を返す
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [ ] 4.3 DFS アルゴリズムの実装
  - `list` スタックで深さ優先探索を実装し、高速探索（最適性保証なし）を提供する
  - 訪問済み状態管理により無限ループを防ぐ
  - BFS と同じ `SolverResult` インターフェースを返す
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [ ] 4.4 タイムアウト制御とデバッグ出力の実装
  - `time.perf_counter()` によるループ内ポーリングで BFS/DFS 両方のタイムアウトを実装する（各イテレーション先頭でチェック）
  - `timeout > 0` かつ制限時間超過時は `PuzzleTimeoutError` を raise する
  - `timeout=0` の場合はタイムアウトなしで探索を継続する
  - `debug=True` の場合は 1000 イテレーションごとに訪問済み状態数と経過時間を `sys.stderr` に出力する
  - _Requirements: 3.4, 3.5, 3.7, 6.4_

- [ ] 5. 出力フォーマッターの実装
- [ ] 5.1 text 形式の出力と verbose モード
  - `format_output()` で「ステップ N: ボトル X → ボトル Y」（1-indexed）形式の出力文字列を生成する
  - 解法の総手数「合計 N 手で解決しました。」をサマリとして末尾に出力する
  - `verbose=True` の場合、`apply_move()` を順次適用して各ステップ後のボトル状態をテキストアートで表示する
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 5.2 JSON・YAML 形式の出力
  - `json` 形式：`solved`・`total_moves`・`moves`（from/to ペア）・`stats`（states_visited・elapsed_time）の構造化出力を生成する
  - `yaml` 形式：同等の構造を pyyaml で出力する
  - `format_output()` の `fmt` 引数で形式を切り替え、`text|json|yaml` 以外の場合は `ValueError` を raise する
  - _Requirements: 4.5_

- [ ] 5.3 ファイル書き出し機能
  - `write_output()` を実装し、`output_path` が指定された場合はファイルに書き出し、`None` の場合は `sys.stdout` に出力する
  - ファイル書き込み失敗時は `OSError` を捕捉して `sys.stderr` に出力する
  - _Requirements: 4.4_

- [ ] 6. CLI エントリポイントの実装
- [ ] 6.1 引数パーサの構築
  - `build_parser()` で `argparse.ArgumentParser` を構築し、全オプション（`--input`・`--validate`・`--strategy`・`--timeout`・`--format`・`--output`・`--verbose`・`--debug`）を定義する
  - `--help` は argparse 自動生成、`--version` は `action="version"` で実装する
  - `--strategy` を `choices=["bfs", "dfs"]`、`--format` を `choices=["text", "json", "yaml"]` で制約する
  - `parse_known_args()` で不明なオプションを検出し、エラーメッセージとともにヘルプ参照先を表示する
  - _Requirements: 1.1, 3.3, 3.4, 4.4, 4.5, 5.1, 5.2, 5.3_

- [ ] 6.2 コンポーネントのオーケストレーション
  - `run()` で InputParser → PuzzleValidator → Solver → OutputFormatter の順にコンポーネントを呼び出す
  - `--validate` のみの場合は入力解析・検証のみ実行して終了する
  - 解決済みパズルの場合は「パズルはすでに解決されています」と通知して終了する
  - `--debug` フラグを Solver に渡し、`--output` および `--format` を OutputFormatter に渡す
  - _Requirements: 2.5, 3.5_

- [ ] 6.3 終了コードとエラーハンドリング
  - 全エラーを `sys.stderr` に出力し、`sys.exit()` で適切な終了コードを設定する（正常終了: 0、エラー: 1、タイムアウト: 2）
  - `FileNotFoundError` → 「ファイルが見つかりません: {パス}」、`ParseError` → エラー種別+期待フォーマット、`PuzzleTimeoutError` → タイムアウト通知を出力する
  - `SolverResult(solved=False)` の場合「このパズルは解決不可能です」と出力して終了コード 1 で終了する
  - `if __name__ == "__main__":` ブロックで `main()` を呼び出し、`uv run python main.py` 形式での実行を可能にする
  - _Requirements: 5.4, 5.5, 6.1, 6.2, 6.3_

- [ ] 7. テストの実装
- [ ] 7.1 (P) models.py と parser.py の単体テスト
  - `apply_move()` のムーブ適用後の状態の正確性と、元状態が変更されていないことを検証する
  - `parse_file()` の YAML・JSON・テキスト各フォーマット正常パースを検証する
  - `FileNotFoundError` と `ParseError`（フォーマット不正・容量不一致）の各エラーケースを検証する
  - _Requirements: 1.2, 1.3, 6.1, 6.2_

- [ ] 7.2 (P) validator.py と formatter.py の単体テスト
  - `validate()` の有効状態・無効状態（色不整合・ボトル 0 本・容量 0）・解決済み判定の各ケースを検証する
  - `format_output()` の text・json・yaml 各フォーマットの出力文字列を検証する
  - verbose モードでの各ステップ後状態表示を検証する
  - _Requirements: 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 4.5_

- [ ] 7.3 (P) solver.py の単体テスト
  - `get_legal_moves()` の合法手の正確な列挙を複数パターンで検証する
  - 小規模パズル（4 ボトル）での BFS・DFS 解法の正確性と手順適用後の解決状態を検証する
  - タイムアウト発生ケース（timeout=0.001 秒で不解パズルを実行）を検証する
  - 解なしパズルで `SolverResult(solved=False)` が返ることを検証する
  - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 3.7_

- [ ] 7.4 エンドツーエンド統合テスト
  - 4 ボトルの小規模パズルで `main.run()` を直接呼び出し、BFS・DFS それぞれの解法エンドツーエンドを検証する
  - `--validate` のみのフロー（解探索なし）を検証する
  - text・json・yaml 各出力フォーマットでの正常終了（終了コード 0）を確認する
  - パフォーマンステスト：12 ボトル × 4 セグメントの標準サイズパズルが 30 秒以内に解法を返すことを確認する
  - _Requirements: 2.5, 3.3, 4.4, 5.4, 5.5_
