# SRBMiner自動ダウンロードスクリプト
Write-Host "⛏️ SRBMiner自動ダウンロード" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ダウンロードURL（最新版）
$downloadUrl = "https://github.com/doktor83/SRBMiner-Multi/releases/download/2.9.2/SRBMiner-Multi-2.9.2-Win64.zip"
$downloadPath = "C:\temp\SRBMiner-Multi-2.9.2-Win64.zip"
$extractPath = "C:\srbminer"

Write-Host "1. ダウンロード中..." -ForegroundColor Yellow
Write-Host "   URL: $downloadUrl" -ForegroundColor Gray

# 一時フォルダを作成
if (!(Test-Path "C:\temp")) {
    New-Item -ItemType Directory -Path "C:\temp" -Force
}

# ダウンロード
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "✅ ダウンロード完了" -ForegroundColor Green
} catch {
    Write-Host "❌ ダウンロード失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. 展開中..." -ForegroundColor Yellow

# 既存フォルダを削除
if (Test-Path $extractPath) {
    Remove-Item $extractPath -Recurse -Force
}

# 展開
try {
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    Write-Host "✅ 展開完了" -ForegroundColor Green
} catch {
    Write-Host "❌ 展開失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. 設定ファイルを作成中..." -ForegroundColor Yellow

# 設定ファイルを作成
$configContent = @"
# SRBMiner設定ファイル
# 自動生成: $(Get-Date)

# アルゴリズム
algorithm = randomx

# プール設定
pool = pool.supportxmr.com:3333

# ウォレットアドレス（後で設定）
wallet = YOUR_WALLET_ADDRESS_HERE

# ワーカー名
worker = CryptoAdventureRPG

# GPU無効化（CPUマイニング）
disable-gpu = true

# ログ設定
log-file = C:\srbminer\miner.log
"@

$configPath = "$extractPath\SRBMiner-Multi-2.9.2\config.txt"
$configContent | Out-File -FilePath $configPath -Encoding UTF8

Write-Host "✅ 設定ファイル作成完了" -ForegroundColor Green

Write-Host ""
Write-Host "4. クリーンアップ中..." -ForegroundColor Yellow

# 一時ファイルを削除
Remove-Item $downloadPath -Force

Write-Host "✅ クリーンアップ完了" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 SRBMinerインストール完了！" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ：" -ForegroundColor White
Write-Host "1. 設定ファイルを編集: $configPath" -ForegroundColor Gray
Write-Host "2. ウォレットアドレスを設定" -ForegroundColor Gray
Write-Host "3. ゲームを再起動" -ForegroundColor Gray
Write-Host ""
Write-Host "Enterキーを押して終了..."
Read-Host 