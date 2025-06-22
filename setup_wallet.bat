@echo off
chcp 65001 >nul
echo 🔐 Moneroウォレットアドレス設定
echo ================================================
echo.
echo 以下の手順でウォレットアドレスを設定してください：
echo.
echo 1. 新しいMoneroウォレットを作成
echo 2. 受信アドレスをコピー
echo 3. 下記のファイルをメモ帳で開く：
echo    data\reality_config.json
echo 4. "YOUR_NEW_MONERO_WALLET_ADDRESS" を
echo    実際のアドレスに置き換える
echo.
echo 設定ファイルを開きますか？ (Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    notepad data\reality_config.json
)
echo.
echo ✅ 設定完了後、ゲームを再起動してください
pause 