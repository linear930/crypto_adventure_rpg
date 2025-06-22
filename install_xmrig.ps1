#!/usr/bin/env pwsh
# XMRig インストールスクリプト

Write-Host "🚀 XMRig インストールスクリプト" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# インストールディレクトリの作成
$installDir = "C:\xmrig"
Write-Host "📁 インストールディレクトリを作成: $installDir" -ForegroundColor Yellow

if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "✅ ディレクトリを作成しました" -ForegroundColor Green
} else {
    Write-Host "ℹ️ ディレクトリは既に存在します" -ForegroundColor Blue
}

# ダウンロードURL（最新版）
$downloadUrl = "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-windows.zip"
$zipFile = "$installDir\xmrig-windows.zip"

Write-Host "📥 XMRigをダウンロード中..." -ForegroundColor Yellow
Write-Host "URL: $downloadUrl" -ForegroundColor Gray

try {
    # ダウンロード
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "✅ ダウンロード完了" -ForegroundColor Green
    
    # 展開
    Write-Host "📦 ファイルを展開中..." -ForegroundColor Yellow
    Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
    Write-Host "✅ 展開完了" -ForegroundColor Green
    
    # 設定ファイルをコピー
    $configFile = "xmrig_config.json"
    if (Test-Path $configFile) {
        Copy-Item -Path $configFile -Destination "$installDir\config.json" -Force
        Write-Host "✅ 設定ファイルをコピーしました" -ForegroundColor Green
    }
    
    # 一時ファイルを削除
    Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
    
    Write-Host "🎉 XMRigのインストールが完了しました！" -ForegroundColor Green
    Write-Host "📁 インストール場所: $installDir" -ForegroundColor Cyan
    Write-Host "⚙️ 設定ファイル: $installDir\config.json" -ForegroundColor Cyan
    
    # 設定の確認
    Write-Host "`n⚠️ 重要: 設定ファイルを編集してください" -ForegroundColor Red
    Write-Host "1. $installDir\config.json を開く" -ForegroundColor Yellow
    Write-Host "2. 'YOUR_WALLET_ADDRESS_HERE' を実際のウォレットアドレスに変更" -ForegroundColor Yellow
    Write-Host "3. 必要に応じてプールURLを変更" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ エラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "手動でダウンロードしてください: https://xmrig.com/download" -ForegroundColor Yellow
}

Write-Host "`n📋 次のステップ:" -ForegroundColor Cyan
Write-Host "1. ウォレットアドレスを設定" -ForegroundColor White
Write-Host "2. ゲームの現実連動設定でパスを更新" -ForegroundColor White
Write-Host "3. ゲームを再起動してマイニングをテスト" -ForegroundColor White

Read-Host "`nEnterキーを押して終了" 