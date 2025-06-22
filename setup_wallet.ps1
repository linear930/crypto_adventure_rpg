# Moneroウォレットアドレス設定スクリプト
Write-Host "🔐 Moneroウォレットアドレス設定" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 設定ファイルのパス
$configPath = "data\reality_config.json"

if (Test-Path $configPath) {
    Write-Host "設定ファイルを開きます..." -ForegroundColor Yellow
    Write-Host "以下の手順で設定してください：" -ForegroundColor White
    Write-Host ""
    Write-Host "1. 'YOUR_NEW_MONERO_WALLET_ADDRESS' を" -ForegroundColor White
    Write-Host "   実際のMoneroウォレットアドレスに置き換える" -ForegroundColor White
    Write-Host "2. Ctrl+S で保存" -ForegroundColor White
    Write-Host "3. メモ帳を閉じる" -ForegroundColor White
    Write-Host ""
    
    # メモ帳で設定ファイルを開く
    Start-Process notepad $configPath -Wait
    
    Write-Host "✅ 設定完了！" -ForegroundColor Green
    Write-Host "ゲームを再起動してください。" -ForegroundColor White
} else {
    Write-Host "❌ 設定ファイルが見つかりません: $configPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "Enterキーを押して終了..."
Read-Host 