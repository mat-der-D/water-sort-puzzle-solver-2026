# 要件定義書

## はじめに

Water Sort Puzzle ソルバ CLI は、ウォーターソートパズル（カラーウォーターソーティングゲーム）の初期状態をコマンドライン引数またはファイルで受け取り、最短または有効な手順を自動探索して解を出力する Python 製 CLI ツールである。ユーザーはパズルの盤面をテキストで記述し、ツールを実行するだけで解法ステップを取得できる。

## 要件

### 要件 1: パズル状態の入力

**目的:** パズルプレイヤーとして、ボトルの初期配色をCLIに入力できるようにしたい。手動でパズルを解く時間を節約するため。

#### 受け入れ基準

1. The Water Sort Solver CLI shall ボトル配列を標準入力またはファイル（`--input` オプション）から受け取ること
2. When `--input` オプションにファイルパスが指定された場合、the Water Sort Solver CLI shall 指定ファイルを読み込んでパズル状態を解析すること
3. The Water Sort Solver CLI shall ボトルをYAML・JSON・またはシンプルなテキスト形式で記述できること（各ボトルは色の配列で表現）
4. When パズル入力が与えられた場合、the Water Sort Solver CLI shall ボトル数と各ボトルの容量（色セグメント数）を認識すること
5. The Water Sort Solver CLI shall 標準的なパズルサイズ（ボトル数 4〜20本、容量 4 セグメント）に対応すること

### 要件 2: パズル状態の検証

**目的:** パズルプレイヤーとして、入力したパズル状態が有効かどうか確認できるようにしたい。不正な入力に気づいてやり直しできるため。

#### 受け入れ基準

1. When パズル状態が入力された場合、the Water Sort Solver CLI shall 各色の合計セグメント数がボトル容量の倍数であることを検証すること
2. If 同じ色のセグメント総数がボトル容量と一致しない場合、the Water Sort Solver CLI shall エラーメッセージとともに終了すること
3. If ボトルが0本または容量が0のボトルが存在する場合、the Water Sort Solver CLI shall 「無効なパズル状態」としてエラーを報告すること
4. When パズル状態が既に解決済みの場合、the Water Sort Solver CLI shall 「パズルはすでに解決されています」と通知して終了すること
5. The Water Sort Solver CLI shall `--validate` フラグのみを指定した場合、解を探索せずに入力の検証結果のみを返すこと

### 要件 3: パズルの自動解法（ソルバ）

**目的:** パズルプレイヤーとして、有効な解法手順を自動的に取得したい。自力では解けない難しいパズルを突破するため。

#### 受け入れ基準

1. When 有効なパズル状態が入力された場合、the Water Sort Solver CLI shall BFS（幅優先探索）またはA\*アルゴリズムで解を探索すること
2. The Water Sort Solver CLI shall 解が存在する場合に有効な移動手順（ボトル番号のペア列）を返すこと
3. The Water Sort Solver CLI shall `--strategy` オプションで `bfs`（最短手数）または `dfs`（高速探索）を選択できること
4. While 解探索が実行中の場合、the Water Sort Solver CLI shall `--timeout` オプションで指定された秒数（デフォルト 30 秒）以内に探索を完了すること
5. If 解が存在しない場合、the Water Sort Solver CLI shall 「このパズルは解決不可能です」と報告すること
6. If タイムアウトが発生した場合、the Water Sort Solver CLI shall タイムアウトを通知してプロセスを終了すること

### 要件 4: 解法の表示

**目的:** パズルプレイヤーとして、解法の手順を分かりやすい形式で確認したい。実際のゲーム画面で手順を再現できるため。

#### 受け入れ基準

1. When 解が見つかった場合、the Water Sort Solver CLI shall 各ステップを「ボトル X → ボトル Y」の形式で標準出力に表示すること
2. The Water Sort Solver CLI shall 解法の総手数をサマリーとして表示すること
3. Where `--verbose` フラグが指定された場合、the Water Sort Solver CLI shall 各ステップ後のボトル状態をビジュアル表示（テキストアート）すること
4. Where `--output` オプションが指定された場合、the Water Sort Solver CLI shall 解法をファイルに書き出すこと
5. The Water Sort Solver CLI shall `--format` オプションで `text`（デフォルト）・`json`・`yaml` の出力形式を選択できること

### 要件 5: CLI インターフェース

**目的:** パズルプレイヤーとして、直感的なコマンドラインインターフェースを通じてツールを操作したい。学習コストを最小化するため。

#### 受け入れ基準

1. The Water Sort Solver CLI shall `--help` オプションで使用方法・オプション一覧・使用例を表示すること
2. The Water Sort Solver CLI shall `--version` オプションでバージョン番号を表示すること
3. When 不明なオプションが指定された場合、the Water Sort Solver CLI shall エラーメッセージとともにヘルプの参照方法を表示すること
4. The Water Sort Solver CLI shall 正常終了時に終了コード 0 を返し、エラー時に非ゼロの終了コードを返すこと
5. The Water Sort Solver CLI shall `uv run python main.py [オプション]` の形式で実行できること

### 要件 6: エラーハンドリングとユーザビリティ

**目的:** パズルプレイヤーとして、エラーが発生した場合に原因を把握して対処できるようにしたい。トラブルシューティングを迅速に行うため。

#### 受け入れ基準

1. If 入力ファイルが存在しない場合、the Water Sort Solver CLI shall 「ファイルが見つかりません: {パス}」というエラーメッセージを表示すること
2. If 入力ファイルの形式が不正な場合、the Water Sort Solver CLI shall 解析エラーの行番号と内容を含むエラーメッセージを表示すること
3. The Water Sort Solver CLI shall すべてのエラーメッセージを stderr に出力すること
4. When `--debug` フラグが指定された場合、the Water Sort Solver CLI shall 探索の進捗（訪問済み状態数、経過時間）を stderr に出力すること
