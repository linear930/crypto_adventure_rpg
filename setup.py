#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crypto Adventure RPG セットアップスクリプト
GitHub公開用の安全な設定を行います
"""

import os
import sys
from pathlib import Path
from config_manager import ConfigManager

def main():
    print("🎮 Crypto Adventure RPG セットアップ")
    print("="*50)
    print("GitHub公開用の安全な設定を行います")
    print()
    
    # 設定管理システムの初期化
    config_manager = ConfigManager()
    
    # 1. 設定ファイルの作成
    print("1️⃣ 設定ファイルの作成")
    if not config_manager.config_file.exists():
        if config_manager.create_config_from_template():
            print("✅ 設定ファイルを作成しました")
        else:
            print("❌ 設定ファイルの作成に失敗しました")
            return
    else:
        print("ℹ️ 設定ファイルは既に存在します")
    
    print()
    
    # 2. 環境変数の設定方法を説明
    print("2️⃣ 環境変数の設定（推奨）")
    print("機密情報を環境変数で設定することを推奨します：")
    print()
    
    if os.name == 'nt':  # Windows
        print("Windowsの場合:")
        print("set MINING_WALLET_ADDRESS=your_wallet_address_here")
        print("set MINING_POOL_URL=pool.supportxmr.com:3333")
        print("set MINING_WORKER_NAME=your_worker_name")
        print("set CEA_PATH=C:\\CEA\\cea.exe")
        print()
        print("または、.envファイルを作成:")
    else:  # Unix/Linux/macOS
        print("Unix/Linux/macOSの場合:")
        print("export MINING_WALLET_ADDRESS=your_wallet_address_here")
        print("export MINING_POOL_URL=pool.supportxmr.com:3333")
        print("export MINING_WORKER_NAME=your_worker_name")
        print("export CEA_PATH=/path/to/cea")
        print()
        print("または、.envファイルを作成:")
    
    print()
    print(".envファイルの例:")
    print("MINING_WALLET_ADDRESS=your_wallet_address_here")
    print("MINING_POOL_URL=pool.supportxmr.com:3333")
    print("MINING_WORKER_NAME=your_worker_name")
    print("CEA_PATH=C:\\CEA\\cea.exe")
    print("BGM_VOLUME=0.5")
    print("EFFECT_VOLUME=0.7")
    print()
    
    # 3. .envファイルの作成
    print("3️⃣ .envファイルの作成")
    env_file = Path(".env")
    if not env_file.exists():
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# Crypto Adventure RPG 環境変数設定\n")
                f.write("# 機密情報をここに設定してください\n")
                f.write("\n")
                f.write("MINING_WALLET_ADDRESS=your_wallet_address_here\n")
                f.write("MINING_POOL_URL=pool.supportxmr.com:3333\n")
                f.write("MINING_WORKER_NAME=your_worker_name\n")
                f.write("CEA_PATH=C:\\CEA\\cea.exe\n")
                f.write("BGM_VOLUME=0.5\n")
                f.write("EFFECT_VOLUME=0.7\n")
                f.write("MONITORING_INTERVAL=30\n")
            
            print("✅ .envファイルを作成しました")
            print("📝 .envファイルを編集して、実際の値を設定してください")
        except Exception as e:
            print(f"❌ .envファイルの作成に失敗: {e}")
    else:
        print("ℹ️ .envファイルは既に存在します")
    
    print()
    
    # 4. 必要なディレクトリの作成
    print("4️⃣ 必要なディレクトリの作成")
    directories = [
        "data",
        "assets", 
        "save",
        "data/mining_results",
        "data/cea_results",
        "data/power_plant_designs",
        "data/astronomical_observations",
        "data/logs",
        "data/sounds"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    print()
    
    # 5. サンプルファイルの作成
    print("5️⃣ サンプルファイルの作成")
    
    # サンプル音声ファイルの説明
    sounds_dir = Path("data/sounds")
    if sounds_dir.exists():
        print("📁 音声ファイルを data/sounds/ に配置してください:")
        print("   - action_select.mp3")
        print("   - next_day.mp3")
        print("   - title_earned.mp3")
        print("   - error.mp3")
        print("   - bgm_*.mp3 (BGMファイル)")
        print("   - ending_bgm.mp3")
    
    print()
    
    # 6. セキュリティチェック
    print("6️⃣ セキュリティチェック")
    config = config_manager.load_config()
    
    # 機密設定の確認
    sensitive_config = config_manager.get_sensitive_config()
    print("現在の機密設定:")
    for key, value in sensitive_config.items():
        if value == 'NOT_SET':
            print(f"   ❌ {key}: 未設定")
        else:
            print(f"   ✅ {key}: 設定済み")
    
    print()
    
    # 7. 最終確認
    print("7️⃣ セットアップ完了")
    print("✅ セットアップが完了しました！")
    print()
    print("📋 次のステップ:")
    print("1. .envファイルを編集して機密情報を設定")
    print("2. data/sounds/に音声ファイルを配置")
    print("3. python main.py でゲームを実行")
    print()
    print("🔒 セキュリティに関する注意:")
    print("- .envファイルは.gitignoreに含まれています")
    print("- 機密情報は環境変数で管理してください")
    print("- 設定ファイルに直接APIキーを書かないでください")
    print()
    print("🎮 ゲームを楽しんでください！")

if __name__ == "__main__":
    main() 