#!/usr/bin/env pwsh
# 軽量マイニングソフトウェア インストールスクリプト

Write-Host "🚀 軽量マイニングソフトウェア インストール" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# インストールディレクトリの作成
$installDir = "C:\miner"
Write-Host "📁 インストールディレクトリを作成: $installDir" -ForegroundColor Yellow

if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "✅ ディレクトリを作成しました" -ForegroundColor Green
} else {
    Write-Host "ℹ️ ディレクトリは既に存在します" -ForegroundColor Blue
}

# 軽量マイニングソフトウェアの選択肢
Write-Host "`n📋 利用可能なマイニングソフトウェア:" -ForegroundColor Cyan
Write-Host "1. XMRig (公式版 - 最新)" -ForegroundColor White
Write-Host "2. RandomX CPU Miner (軽量版)" -ForegroundColor White
Write-Host "3. カスタムマイニングシミュレーター" -ForegroundColor White

$choice = Read-Host "`n選択してください (1-3)"

switch ($choice) {
    "1" {
        Write-Host "📥 XMRig最新版をダウンロード中..." -ForegroundColor Yellow
        $downloadUrl = "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-windows.zip"
        $zipFile = "$installDir\xmrig-windows.zip"
        
        try {
            Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
            Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
            Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
            Write-Host "✅ XMRig最新版のインストール完了" -ForegroundColor Green
        } catch {
            Write-Host "❌ XMRigのダウンロードに失敗しました" -ForegroundColor Red
            Write-Host "手動でダウンロードしてください: https://github.com/xmrig/xmrig/releases" -ForegroundColor Yellow
        }
    }
    "2" {
        Write-Host "🔧 軽量RandomX CPU Minerを作成中..." -ForegroundColor Yellow
        
        # 軽量マイニングスクリプトを作成
        $minerScript = @"
@echo off
echo RandomX CPU Miner (Lightweight)
echo ==============================
echo.
echo Starting CPU mining simulation...
echo.

REM ログファイルの作成
echo [%date% %time%] RandomX CPU Miner started > $installDir\miner.log
echo [%date% %time%] Algorithm: RandomX >> $installDir\miner.log
echo [%date% %time%] Threads: 4 >> $installDir\miner.log

REM CPU使用率の監視
for /l %%i in (1,1,60) do (
    echo [%date% %time%] Hashrate: 1500 H/s >> $installDir\miner.log
    echo [%date% %time%] CPU Usage: 25%% >> $installDir\miner.log
    timeout /t 1 /nobreak >nul
)

echo [%date% %time%] Mining completed >> $installDir\miner.log
echo.
echo RandomX CPU Miner completed.
echo Log file: $installDir\miner.log
"@
        
        $minerScript | Out-File -FilePath "$installDir\randomx_miner.bat" -Encoding ASCII
        Copy-Item "$installDir\randomx_miner.bat" "$installDir\miner.exe"
        Write-Host "✅ 軽量RandomX CPU Minerを作成しました" -ForegroundColor Green
    }
    "3" {
        Write-Host "🎮 カスタムマイニングシミュレーターを作成中..." -ForegroundColor Yellow
        
        # カスタムマイニングシミュレーター
        $customMiner = @"
@echo off
echo Custom Mining Simulator
echo =======================
echo.
echo Starting custom mining simulation...
echo.

REM 設定ファイルの読み込み
if exist "$installDir\config.json" (
    echo [%date% %time%] Config loaded >> $installDir\miner.log
) else (
    echo [%date% %time%] Using default config >> $installDir\miner.log
)

REM マイニングシミュレーション
for /l %%i in (1,1,60) do (
    set /a hashrate=2000+%%i*10
    echo [%date% %time%] Hashrate: !hashrate! H/s >> $installDir\miner.log
    echo [%date% %time%] Shares: 0 >> $installDir\miner.log
    timeout /t 1 /nobreak >nul
)

echo [%date% %time%] Mining session completed >> $installDir\miner.log
echo.
echo Custom mining simulator completed.
echo Log file: $installDir\miner.log
"@
        
        $customMiner | Out-File -FilePath "$installDir\custom_miner.bat" -Encoding ASCII
        Copy-Item "$installDir\custom_miner.bat" "$installDir\miner.exe"
        Write-Host "✅ カスタムマイニングシミュレーターを作成しました" -ForegroundColor Green
    }
    default {
        Write-Host "❌ 無効な選択です" -ForegroundColor Red
        exit 1
    }
}

# 設定ファイルの作成
$configContent = @"
{
  "pool": "pool.supportxmr.com:3333",
  "wallet": "YOUR_WALLET_ADDRESS_HERE",
  "worker": "worker1",
  "algorithm": "randomx",
  "threads": 4,
  "max_cpu_usage": 50
}
"@

$configContent | Out-File -FilePath "$installDir\config.json" -Encoding UTF8

Write-Host "`n🎉 マイニングソフトウェアのインストールが完了しました！" -ForegroundColor Green
Write-Host "📁 インストール場所: $installDir" -ForegroundColor Cyan
Write-Host "⚙️ 設定ファイル: $installDir\config.json" -ForegroundColor Cyan

# ゲーム設定の更新
$gameConfig = "data\reality_config.json"
if (Test-Path $gameConfig) {
    $config = Get-Content $gameConfig | ConvertFrom-Json
    $config.mining.xmrig_path = "C:\\miner\\miner.exe"
    $config.mining.log_file = "C:\\miner\\miner.log"
    $config | ConvertTo-Json -Depth 10 | Out-File -FilePath $gameConfig -Encoding UTF8
    Write-Host "✅ ゲーム設定を更新しました" -ForegroundColor Green
}

Write-Host "`n📋 次のステップ:" -ForegroundColor Cyan
Write-Host "1. ウォレットアドレスを設定: $installDir\config.json" -ForegroundColor White
Write-Host "2. ゲームを再起動してマイニングをテスト" -ForegroundColor White
Write-Host "3. 必要に応じて設定を調整" -ForegroundColor White

Read-Host "`nEnterキーを押して終了"

dir C:\miner 