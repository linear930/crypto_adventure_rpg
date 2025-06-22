# Crypto Adventure RPG

現実連動型CLIゲーム - マイニング、CEA計算、発電所設計などの実際の活動を仮想世界の物語として展開するRPGツール

## 🎮 概要

このプロジェクトは、現実世界での技術活動（マイニング、ロケットエンジン計算、発電所設計など）をゲーム内の冒険として記録し、学習効果を促進するCLI型RPGです。

## 🚀 主な機能

- **仮想時間進行**: 1日最大3回の行動制限
- **現実データ連動**: 実際のマイニングログ、CEA計算結果、発電所設計データを読み込み
- **称号システム**: 条件達成に応じて称号を付与
- **学習促進システム**: 各活動の記録と学習目標管理
- **進捗管理**: ウォレット情報とゲーム状態の永続化
- **BGMシステム**: ゲーム内音楽の再生と変更

## 🔒 セキュリティ

このプロジェクトはGitHub公開を前提として設計されており、機密情報の安全な管理を重視しています：

- **環境変数による機密情報管理**: APIキーやウォレットアドレスは環境変数で管理
- **設定ファイルのテンプレート化**: 機密情報を含まない設定テンプレートを提供
- **.gitignoreによる除外**: 機密ファイルや個人データを自動除外
- **設定検証機能**: 機密情報の漏洩を防ぐ設定チェック機能

## 📁 プロジェクト構造

```
crypto_adventure_rpg/
├── main.py                    # メインゲームファイル
├── setup.py                   # セットアップスクリプト
├── config_manager.py          # 設定管理システム
├── config_template.json       # 設定テンプレート
├── .gitignore                 # Git除外設定
├── requirements.txt           # 依存ライブラリ
├── README.md                 # このファイル
├── data/                     # ゲームデータ（自動生成）
│   ├── mining_results/
│   ├── cea_results/
│   ├── power_plant_designs/
│   ├── astronomical_observations/
│   ├── logs/
│   └── sounds/               # 音声ファイル
├── assets/                   # ゲームアセット（自動生成）
│   └── titles.json
└── save/                     # セーブデータ（自動生成）
    └── ending_*.txt
```

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/crypto-adventure-rpg.git
cd crypto-adventure-rpg
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. セットアップスクリプトの実行

```bash
python setup.py
```

このスクリプトは以下を自動実行します：
- 設定ファイルの作成
- 必要なディレクトリの作成
- .envファイルの作成
- セキュリティチェック

### 4. 機密情報の設定

#### 環境変数による設定（推奨）

**Windows:**
```cmd
set MINING_WALLET_ADDRESS=your_wallet_address_here
set MINING_POOL_URL=pool.supportxmr.com:3333
set MINING_WORKER_NAME=your_worker_name
set CEA_PATH=C:\CEA\cea.exe
```

**Unix/Linux/macOS:**
```bash
export MINING_WALLET_ADDRESS=your_wallet_address_here
export MINING_POOL_URL=pool.supportxmr.com:3333
export MINING_WORKER_NAME=your_worker_name
export CEA_PATH=/path/to/cea
```

#### .envファイルによる設定

`.env`ファイルを編集して機密情報を設定：

```env
MINING_WALLET_ADDRESS=your_wallet_address_here
MINING_POOL_URL=pool.supportxmr.com:3333
MINING_WORKER_NAME=your_worker_name
CEA_PATH=C:\CEA\cea.exe
BGM_VOLUME=0.5
EFFECT_VOLUME=0.7
MONITORING_INTERVAL=30
```

### 5. 音声ファイルの配置

`data/sounds/`ディレクトリに以下の音声ファイルを配置：

- `action_select.mp3` - メニュー選択音
- `next_day.mp3` - 日付変更音
- `title_earned.mp3` - 称号獲得音
- `error.mp3` - エラー音
- `bgm_*.mp3` - BGMファイル（複数可）
- `ending_bgm.mp3` - エンディングBGM

### 6. ゲームの実行

```bash
python main.py
```

## 🎯 ゲームプレイ

### 基本ルール

1. **1日3回の行動制限**: 毎日最大3回まで行動可能
2. **現実データ連動**: 実際の技術活動の結果をゲーム内に反映
3. **称号獲得**: 条件を満たすと称号を獲得
4. **学習促進**: 各活動の記録と学習目標管理

### 利用可能な行動

1. **CEA計算記録・学習**: ロケットエンジン計算結果の記録と学習
2. **発電方法記録・学習**: 発電システムの記録と学習
3. **天体観測記録・学習**: 天体観測の記録と学習
4. **Moneroマイニング**: 実際のマイニング活動の記録
5. **発電所ミッション**: 発電所設計と監視ミッション
6. **統計・履歴表示**: ゲーム進行状況の確認
7. **学習目標確認**: 学習目標の進捗確認
8. **BGM変更**: ゲーム内音楽の変更
9. **ゲーム保存**: 進行状況の保存

### 称号システム

- **電力の芽生え**: 初めてマイニングを実行
- **クリプト仙人**: 1.0 XMRを獲得
- **重力を操る者**: CEA計算を10回実行
- **エネルギー魔術師**: 発電所を5基設計
- **天体観測者**: 天体観測を実行
- その他多数の称号

## 📊 データ形式

### マイニング記録

```json
{
  "start_time": "2024-01-15 10:30:00",
  "end_time": "2024-01-15 11:30:00",
  "results": {
    "hashrate": 2500,
    "power_consumption": 0.15,
    "accepted_shares": 5,
    "rejected_shares": 0,
    "estimated_xmr": 0.00000123
  },
  "mining_config": {
    "pool_url": "pool.supportxmr.com:3333",
    "wallet_address": "your_wallet_address",
    "worker_name": "worker1"
  },
  "hardware": {
    "cpu_model": "Intel Core i7",
    "gpu_model": "NVIDIA RTX 3080",
    "ram_gb": 16
  }
}
```

### CEA計算記録

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "fuel": "CH4",
  "oxidizer": "LOX",
  "mixture_ratio": 3.5,
  "chamber_pressure_bar": 100,
  "expansion_ratio": 50,
  "results": {
    "isp_sec": 350.5,
    "thrust_n": 1250.0,
    "c_star": 1800.0
  },
  "notes": "メタン/LOXエンジンの基本計算"
}
```

### 発電所設計記録

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "plant_type": "solar",
  "capacity_kw": 2.5,
  "daily_generation_kwh": 10.0,
  "cost_usd": 150000,
  "location": "自宅屋根",
  "notes": "家庭用太陽光発電システム"
}
```

## 🔧 カスタマイズ

### 新しい称号の追加

`assets/titles.json`ファイルを編集して新しい称号を追加できます：

```json
{
  "id": "new_title",
  "name": "新しい称号",
  "description": "称号の説明",
  "condition": {
    "action": "mining",
    "metric": "hashrate",
    "operator": ">=",
    "value": 10000
  }
}
```

### 学習目標のカスタマイズ

各モジュールの`_initialize_learning_goals`メソッドを編集して学習目標をカスタマイズできます。

## 🚧 将来の拡張予定

- [ ] Web UI版の開発
- [ ] マルチプレイヤー機能
- [ ] より詳細な電力監視機能
- [ ] 複数のCrypto対応
- [ ] モバイルアプリ版

## 🤝 貢献

バグ報告や機能提案は歓迎します。プルリクエストも受け付けています。

### 貢献のガイドライン

1. フォークしてブランチを作成
2. 変更をコミット
3. プルリクエストを作成
4. セキュリティに関する変更は事前に議論

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🔒 セキュリティに関する注意

- 機密情報（APIキー、ウォレットアドレスなど）は環境変数で管理してください
- 設定ファイルに直接機密情報を書かないでください
- .envファイルは.gitignoreに含まれていますが、手動で確認してください
- 新しい機密情報を追加する場合は、.gitignoreを更新してください

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。

## 🎵 音声ファイルについて

### ⚠️ 著作権に関する重要事項
このゲームで使用されている音声ファイル（BGM・効果音）は、著作権保護された素材です。

**音声ファイルは含まれていません：**
- ゲームのソースコードには音声ファイルは含まれていません
- ユーザーは自身で適切な音声ファイルを用意する必要があります
- 著作権を尊重し、適切なライセンスの音声ファイルを使用してください

### 📁 必要な音声ファイル
以下のファイルを`data/sounds/`フォルダに配置してください：

**効果音：**
- `action_select.mp3` - 行動選択時
- `next_day.mp3` - 次の日へ進む時
- `title_earned.mp3` - 称号獲得時
- `error.mp3` - エラー時

**BGM：**
- `bgm_1.mp3` - メインBGM
- `bgm_2.mp3` - サブBGM
- `bgm_3.mp3` - 追加BGM
- `ending_bgm.mp3` - エンディングBGM

### 🎵 推奨音声素材サイト
- **魔王魂**: ゲーム用BGM・効果音（商用利用可）
- **甘茶の音楽工房**: 8bit音楽素材
- **効果音ラボ**: 無料効果音素材
- **DOVA-SYNDROME**: 商用利用可能な音楽素材

### 📋 注意事項
- 全てのファイルは`.mp3`形式である必要があります
- ファイルが見つからない場合は、エラーメッセージが表示されます
- BGMはランダムに選択され、ループ再生されます
- 音量はゲーム内の音声設定で調整可能です

---

**Crypto Adventure RPG** - 現実と仮想を繋ぐ技術者向けRPG 