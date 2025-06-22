@echo off
chcp 65001 >nul
echo 🔧 SRBMinerバッチファイル修正
echo ================================================
echo.

set "bat_file=C:\srbminer\SRBMiner-Multi-2-9-2\start-mining-monero.bat"
set "config_file=C:\srbminer\config.txt"

echo 1. バッチファイルを修正中...
echo.

REM 新しいバッチファイルの内容を作成
(
echo @echo off
echo cd %%~dp0
echo cls
echo.
echo echo ⛏️ SRBMiner-Multi マイニング開始
echo echo ================================================
echo echo.
echo echo 設定ファイル: %config_file%
echo echo.
echo.
echo REM 設定ファイルが存在するかチェック
echo if not exist "%config_file%" ^(
echo     echo ❌ 設定ファイルが見つかりません: %config_file%
echo     echo 設定ファイルを作成してください
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM SRBMinerを実行
echo echo マイニングを開始します...
echo echo.
echo SRBMiner-MULTI.exe --config "%config_file%"
echo.
echo if errorlevel 1 ^(
echo     echo ❌ SRBMinerの実行に失敗しました
echo     echo SRBMiner-MULTI.exeが存在するか確認してください
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ マイニング完了
echo pause
) > "%bat_file%"

echo ✅ バッチファイルを修正しました
echo.

echo 2. 設定ファイルを作成中...
echo.

REM 設定ファイルの内容を作成
(
echo # SRBMiner設定ファイル
echo # 自動生成: %date% %time%
echo.
echo # アルゴリズム
echo algorithm = randomx
echo.
echo # プール設定
echo pool = pool.supportxmr.com:3333
echo.
echo # ウォレットアドレス
echo wallet = 4BGrZRkV7jgetvovXr67st34LM8qf1rFpPfC8vymNWFwDvHnDumYBABVyuJYM2PZGjJxS7nVFSK7JRrx6QMJU48B4DhvfUk
echo.
echo # ワーカー名
echo worker = CryptoAdventureRPG
echo.
echo # GPU無効化（CPUマイニング）
echo disable-gpu = true
echo.
echo # ログ設定
echo log-file = C:\srbminer\miner.log
) > "%config_file%"

echo ✅ 設定ファイルを作成しました
echo.

echo 3. ファイルの存在確認...
echo.

if exist "%bat_file%" (
    echo ✅ バッチファイル: %bat_file%
) else (
    echo ❌ バッチファイルが見つかりません
)

if exist "%config_file%" (
    echo ✅ 設定ファイル: %config_file%
) else (
    echo ❌ 設定ファイルが見つかりません
)

echo.
echo 🎉 修正完了！
echo.
echo 次のステップ：
echo 1. SRBMiner-MULTI.exeが存在するか確認
echo 2. ゲームを再起動
echo 3. マイニングを実行
echo.
pause 