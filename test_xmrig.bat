@echo off
echo XMRig Test Simulator
echo ===================
echo.
echo Starting XMRig simulation...
echo.

REM ログファイルの作成
echo [%date% %time%] XMRig started > C:\xmrig\xmrig.log
echo [%date% %time%] Pool: pool.supportxmr.com:3333 >> C:\xmrig\xmrig.log
echo [%date% %time%] User: YOUR_WALLET_ADDRESS_HERE >> C:\xmrig\xmrig.log

REM マイニングのシミュレーション
for /l %%i in (1,1,60) do (
    echo [%date% %time%] Speed: 2500 H/s >> C:\xmrig\xmrig.log
    timeout /t 1 /nobreak >nul
)

echo [%date% %time%] XMRig stopped >> C:\xmrig\xmrig.log
echo.
echo XMRig simulation completed.
echo Log file: C:\xmrig\xmrig.log
pause 