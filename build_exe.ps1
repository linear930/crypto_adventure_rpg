#requires -Version 5.1
param(
  [switch]$OneFile,
  [string]$Python = "python"
)

# venvがあれば優先
if (Test-Path "..\cea\Scripts\python.exe") {
  $Python = "..\cea\Scripts\python.exe"
}

# PyInstallerインストール
& $Python -m pip install --upgrade pip | Out-Host
& $Python -m pip install pyinstaller -r requirements.txt | Out-Host

# 出力設定
$distDir = "dist"
$buildDir = "build"
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }

# ベースの引数
$commonArgs = @(
  "--name", "CryptoAdventureRPG",
  "--clean",
  "--noupx",
  "--add-data", "assets;assets",
  "--add-data", "data;data",
  "--add-data", "save;save"
)

# onefile/onedir 切替
if ($OneFile) {
  $modeArgs = @("--onefile")
} else {
  $modeArgs = @("--onedir")
}

# 実行
& $Python -m PyInstaller @modeArgs @commonArgs "--console" "main.py" | Out-Host

Write-Host "\n✅ ビルド完了: $distDir" -ForegroundColor Green
if (-not $OneFile) {
  Write-Host "実行例: .\\dist\\CryptoAdventureRPG\\main.exe" -ForegroundColor Yellow
} else {
  Write-Host "実行例: .\\dist\\CryptoAdventureRPG.exe" -ForegroundColor Yellow
} 