# 音声会話チャットソフト 説明書

このソフトは、マイク入力した音声を文字起こしし、AI に送って返答を生成し、その返答を音声で読み上げるコンソールアプリです。
GUI は使わず、会話内容はコンソールとログファイルに記録されます。

---

## 第1部: 利用者向け説明書

### 1. できること

- マイクから話した内容を認識して AI に送信
- AI の返答をコンソールに表示
- AI の返答を音声合成で読み上げ
- 音声合成エンジンを設定で切替（VOICEVOX / pyttsx3 / PowerShell）
- 会話ログをファイル保存
- 終了ワードを話すと会話を終了

### 2. 必要なもの

- Windows
- Python 3.13 系を推奨
- マイク入力デバイス
- LM Studio 互換の Chat Completions API
  - 既定の接続先: `http://127.0.0.1:1234/v1/chat/completions`

### 3. セットアップ

1. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

2. AI サーバー（例: LM Studio）を起動し、チャット API が受け付け可能な状態にする

3. 必要に応じて設定ファイルを編集

- 既定の設定ファイル: `chat_config.yaml`

### 4. 起動方法

通常起動:

```bash
python speark_chat.py
```

設定ファイルを指定して起動:

```bash
python speark_chat.py --config chat_config.yaml
```

### 5. 使い方

1. 起動後、周囲ノイズの調整が実行されます
2. `Listening...` が表示されたら話しかけます
3. 認識結果が `You: ...` として表示されます
4. AI 返答が `Assistant: ...` として表示され、同時に音声再生されます
5. `終了` や `stop` などの終了ワードを話すと停止します

### 5.1 VOICEVOX の使い方

1. VOICEVOX Engine を起動
2. `chat_config.yaml` の `tts.provider` を `voicevox` に変更
3. `tts.voicevox.speaker` を話者IDに合わせる
4. 通常どおり `python speark_chat.py` で起動

切り替えしやすい設定例:

```yaml
tts:
  # provider: pyttsx3
  provider: voicevox
  voicevox:
    # speaker: 3  # ずんだもん
    speaker: 8    # 春日部つむぎ
```

主要話者ID（この環境で確認済み）:

- ずんだもん（ノーマル）: `3`
- 春日部つむぎ（ノーマル）: `8`
- 四国めたん: `2`（ノーマル）, `0`（あまあま）, `6`（ツンツン）, `4`（セクシー）, `36`（ささやき）, `37`（ヒソヒソ）

VOICEVOX 単体テスト:

```bash
python voicevox_speak_test.py --speaker 8 --text "VOICEVOXテストです"
```

補足:

- VOICEVOX が失敗した場合は `fallback_providers` の順で `pyttsx3` / `powershell` にフォールバックします
- `voicevox_speak_test.py` はテスト専用で、VOICEVOX を強制利用します

### 6. 設定項目（chat_config.yaml）

```yaml
log_file: speech_log.txt
history:
  max_messages: 12
speech_recognition:
  language: ja-JP
  ambient_duration: 1.0
  listen_timeout: 8.0
  phrase_time_limit: 10.0
  exit_phrases:
    - stop
    - 終了
ai:
  api_url: http://127.0.0.1:1234/v1/chat/completions
  model_name: local-model
  temperature: 0.3
  timeout_seconds: 30
  system_prompt: あなたは簡潔に短く会話するアシスタントです。返答は1文で短くしてください。
tts:
  provider: pyttsx3
  fallback_providers:
    - powershell
  voicevox:
    base_url: http://127.0.0.1:50021
    speaker: 3
    timeout_seconds: 15
  pyttsx3:
    rate: null
    volume: null
    voice_name: null
  powershell:
    rate: 0
    volume: 100
```

主な調整ポイント:

- `speech_recognition.language`
  - 音声認識の言語。日本語は `ja-JP`
- `speech_recognition.listen_timeout`
  - 話し始め待ちのタイムアウト秒
- `speech_recognition.phrase_time_limit`
  - 1 発話の最大秒数
- `speech_recognition.exit_phrases`
  - 終了とみなす語句（小文字化して照合）
- `history.max_messages`
  - AI に渡す会話履歴の最大メッセージ数
- `ai.*`
  - API 接続先、モデル、温度、システムプロンプト
- `tts.provider`
  - 利用する音声合成エンジン。`voicevox` / `pyttsx3` / `powershell`
- `tts.fallback_providers`
  - 失敗時に切り替える順序
- `tts.voicevox.speaker`
  - VOICEVOX の話者 ID（ずんだもん標準は `3`）
- `ai.voicevox_character_prompts`
  - VOICEVOX 利用時、`speaker` に対応する口調プロンプトを `system_prompt` の後ろに自動で追加
- `tts.pyttsx3.*` と `tts.powershell.*`
  - それぞれの読み上げパラメータ

### 7. ログ

- 保存先は `log_file` で指定
- 形式: `[YYYY-MM-DD HH:MM:SS] Speaker: text`
- `Speaker` は `User` または `Assistant`

### 8. よくあるトラブル

- マイクが開けない
  - 他アプリがマイクを占有していないか確認
  - OS のマイク許可設定を確認
- 音声認識 API エラー
  - ネットワーク状態を確認
  - `language` 設定が意図通りか確認
- AI 応答が取れない
  - `ai.api_url` が正しいか確認
  - AI サーバー起動状態を確認
- 読み上げに失敗する
  - `tts.provider` と `tts.fallback_providers` の組み合わせを確認
  - VOICEVOX を使う場合は Engine を起動し、`tts.voicevox.base_url` を確認
  - VOICEVOX の話者IDが正しいか確認（IDは style ごとに異なる）
  - `pyttsx3` または PowerShell に切り替えて切り分け

---

## 第2部: 技術解説

### 1. 構成方針

- エントリポイントは薄く保つ
- 機能をライブラリとして分離
- 設定値は YAML に集約

### 2. ディレクトリ構成

```text
.
├─ speark_chat.py
├─ chat_config.yaml
├─ requirements.txt
├─ voice_chat_lib
│  ├─ __init__.py
│  ├─ config.py
│  ├─ mic_in.py
│  ├─ ai_agent.py
│  ├─ speaker_out.py
│  └─ chat_session.py
```

### 3. 主要モジュール

- `voice_chat_lib.config`
  - YAML 設定の読み込み
  - `AppConfig` / `AIConfig` など dataclass で型化
  - 設定ファイル基準で相対パスを解決
- `voice_chat_lib.mic_in`
  - マイク調整、音声キャプチャ、ログ整形
- `voice_chat_lib.ai_agent`
  - Chat Completions API 呼び出し
  - `history` と `system_prompt` を送信
  - VOICEVOX 利用時は話者別口調プロンプトを連結した `system_prompt` を受け取る
- `voice_chat_lib.speaker_out`
  - 設定に応じて `voicevox` / `pyttsx3` / `powershell` を切り替え
  - `fallback_providers` 順にフォールバック
- `voice_chat_lib.chat_session`
  - 会話のオーケストレーション（入力→推論→出力→履歴更新）

### 4. 実行フロー

1. `speark_chat.py` が設定パスを解決
2. `run_voice_chat(config_path)` を実行
3. 設定読込後にマイクを初期化
4. ループで発話を取得
5. 終了ワード判定
6. `tts.provider == voicevox` の場合、`speaker` 対応の口調プロンプトを合成
7. AI へ問い合わせ
8. 応答を表示・ログ出力・音声再生
9. 履歴を `max_messages` に収めて継続

### 5. 設計上のポイント

- 会話履歴の上限管理でプロンプト肥大化を抑制
- 設定外だしにより本体コードの変更なしで運用調整可能
- 音声出力にフォールバックを持たせ、環境差異に対応
- 例外処理を I/O 境界に寄せ、ループ継続可能な設計

### 6. 拡張アイデア

- ストリーミング応答への対応
- VAD（Voice Activity Detection）導入で無音検知を改善
- 会話ログのローテーション、JSONL 出力
- 話者分離や wake word の導入
- 単体テスト用に I/O インターフェースを抽象化

### 7. 開発時メモ

- 設定は `.yaml` / `.yml` を受理
- 既定設定は `chat_config.yaml`
- Python 3.13 環境では `SpeechRecognition==3.16.1` を使用
- ずんだもん音声は VOICEVOX Engine + `tts.provider: voicevox` + `tts.voicevox.speaker: 3`
