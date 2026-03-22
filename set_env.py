#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境変数設定スクリプト
Crypto Adventure RPG用の環境変数を設定します
"""

import os
import subprocess
import sys
from pathlib import Path

def set_environment_variables():
    """環境変数を設定"""
    print("🔧 環境変数の設定")
    print("="*40)
    
    # 環境変数の設定
    env_vars = {
        'CEA_PATH': 'C:\\CEA\\cea.exe',
        'BGM_VOLUME': '0.5',
        'EFFECT_VOLUME': '0.7',
        'MONITORING_INTERVAL': '30'
    }
    
    if os.name == 'nt':  # Windows
        print("Windows環境変数を設定中...")
        for key, value in env_vars.items():
            try:
                # 現在のセッションで環境変数を設定
                os.environ[key] = value
                print(f"✅ {key} = {value}")
            except Exception as e:
                print(f"❌ {key} の設定に失敗: {e}")
        
        print("setx CEA_PATH C:\\CEA\\cea.exe")
        print("setx BGM_VOLUME 0.5")
        print("setx EFFECT_VOLUME 0.7")
        print("setx MONITORING_INTERVAL 30")
        
    else:  # Unix/Linux/macOS
        print("Unix/Linux/macOS環境変数を設定中...")
        for key, value in env_vars.items():
            try:
                os.environ[key] = value
                print(f"✅ {key} = {value}")
            except Exception as e:
                print(f"❌ {key} の設定に失敗: {e}")
        
        print("echo 'export CEA_PATH=/path/to/cea' >> ~/.bashrc")
        print("echo 'export BGM_VOLUME=0.5' >> ~/.bashrc")
        print("echo 'export EFFECT_VOLUME=0.7' >> ~/.bashrc")
        print("echo 'export MONITORING_INTERVAL=30' >> ~/.bashrc")
        print("source ~/.bashrc")
    
    print("\n✅ 環境変数の設定が完了しました！")
    print("🎮 ゲームを実行する準備が整いました。")

def create_env_file():
    """環境変数ファイルを作成"""
    print("\n📄 .envファイルを作成中...")
    
    env_content = """# Crypto Adventure RPG 環境変数設定
# 機密情報をここに設定してください
CEA_PATH=C:\\CEA\\cea.exe
BGM_VOLUME=0.5
EFFECT_VOLUME=0.7
MONITORING_INTERVAL=30
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .envファイルを作成しました")
    except Exception as e:
        print(f"❌ .envファイルの作成に失敗: {e}")

def verify_configuration():
    """設定の確認"""
    print("\n🔍 設定の確認")
    print("="*40)
    
    from config_manager import ConfigManager
    
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    print("現在の設定:")
    print(f"  CEAパス: {config['cea']['cea_path']}")
    print(f"  BGM音量: {config['audio']['bgm_volume']}")
    print(f"  効果音音量: {config['audio']['effect_volume']}")
    
    # 機密設定の確認
    sensitive_config = config_manager.get_sensitive_config()
    print("\n機密設定の状態:")
    for key, value in sensitive_config.items():
        if value == 'NOT_SET':
            print(f"   ❌ {key}: 未設定")
        else:
            print(f"   ✅ {key}: 設定済み")

def main():
    """メイン関数"""
    print("🎮 Crypto Adventure RPG 環境変数設定")
    print("="*50)
    
    # 1. 環境変数の設定
    set_environment_variables()
    
    # 2. .envファイルの作成
    create_env_file()
    
    # 3. 設定の確認
    verify_configuration()
    
    print("\n🎉 設定が完了しました！")
    print("📋 次のステップ:")
    print("1. python main.py でゲームを実行")
    print("2. 必要に応じて設定を調整")
    print("3. 音声ファイルを data/sounds/ に配置")

if __name__ == "__main__":
    main() 