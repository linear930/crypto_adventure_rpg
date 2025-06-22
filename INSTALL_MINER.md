# cpuminer-opt インストールガイド

このガイドでは、Crypto Adventure RPGで実際のマイニングを行うために必要なcpuminer-optのインストール方法を説明します。

## 🪟 Windows用インストール手順

### 1. GitHubからダウンロード
- [cpuminer-opt リリースページ](https://github.com/JayDDee/cpuminer-opt/releases) にアクセス
- 最新版のWindows x64版をダウンロード（例：`cpuminer-opt-v3.21.0-windows.zip`）

### 2. ファイルを解凍
- ダウンロードしたZIPファイルを解凍
- 解凍したフォルダを `C:\cpuminer-opt` に移動

### 3. システム環境変数PATHに追加
1. Windowsキー + R を押して「sysdm.cpl」と入力
2. 「詳細設定」タブをクリック
3. 「環境変数」ボタンをクリック
4. 「システム環境変数」の「Path」を選択して「編集」をクリック
5. 「新規」をクリックして `C:\cpuminer-opt` を追加
6. すべてのダイアログで「OK」をクリック

### 4. 動作確認
コマンドプロンプトを開いて以下を実行：
```cmd
cpuminer-opt --help
```

## 🐧 Linux用インストール手順

### 1. 必要なパッケージをインストール
```bash
sudo apt-get update
sudo apt-get install build-essential git
```

### 2. ソースコードをクローン
```bash
git clone https://github.com/JayDDee/cpuminer-opt.git
```

### 3. ビルドディレクトリに移動
```bash
cd cpuminer-opt
```

### 4. ビルドスクリプトを実行
```bash
./build.sh
```

### 5. 実行ファイルをシステムパスにコピー
```bash
sudo cp cpuminer /usr/local/bin/cpuminer-opt
```

### 6. 動作確認
```bash
cpuminer-opt --help
```

## 🍎 macOS用インストール手順

### 1. Homebrewのインストール（未インストールの場合）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. cpuminer-optをインストール
```bash
brew install cpuminer-opt
```

### 3. 動作確認
```bash
cpuminer-opt --help
```

## 🔧 代替マイニングソフトウェア

cpuminer-optが利用できない場合、以下の代替ソフトウェアも使用できます：

### XMRig
- より現代的なマイニングソフトウェア
- 自動設定機能あり
- [XMRig公式サイト](https://xmrig.com/)

### cpuminer
- 基本的なCPUマイニングソフトウェア
- シンプルな設定

## ⚠️ 注意事項

1. **セキュリティ**: 信頼できるソースからのみダウンロードしてください
2. **電力消費**: マイニングは高電力消費を伴います
3. **システム温度**: CPU温度を監視してください
4. **ネットワーク**: 安定したインターネット接続が必要です
5. **セキュリティソフト**: ウイルス対策ソフトの設定を確認してください

## 🎯 次のステップ

インストール完了後、Crypto Adventure RPGを起動して：
1. メインメニューから「⛏️ Moneroマイニング」を選択
2. 「⚙️ マイニング設定」で設定を行う
3. 「🚀 マイニング開始」で実際のマイニングを開始

## 💡 トラブルシューティング

### コマンドが見つからない
- PATH設定を確認
- 再起動後に再試行

### 接続エラー
- プールURLを確認
- ファイアウォール設定を確認

### 低ハッシュレート
- スレッド数と強度を調整
- CPU使用率を確認

### 高CPU使用率
- 強度を下げる
- スレッド数を減らす

## 📞 サポート

問題が解決しない場合は、以下を確認してください：
- システム要件
- ネットワーク接続
- セキュリティソフトの設定
- プールの状態 