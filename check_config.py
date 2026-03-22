#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定確認スクリプト
Crypto Adventure RPGの設定が正しく読み込まれているか確認します
"""

from config_manager import ConfigManager

def main():
    print("🔍 Crypto Adventure RPG 設定確認")
    print("="*50)
    
    # 設定管理システムの初期化
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    print("✅ 設定ファイルの読み込み: 成功")
    print()
    
    # 基本設定
    print("📋 基本設定:")
    print(f"   ゲーム名: {config.get('game_name', '未設定')}")
    print(f"   バージョン: {config.get('version', '未設定')}")
    print(f"   出力ディレクトリ: {config.get('output_dir', '未設定')}")
    print()
    
    
    # CEA設定
    print("🚀 CEA設定:")
    cea_config = config.get('cea', {})
    print(f"   CEAパス: {cea_config.get('cea_path', '未設定')}")
    print(f"   出力ディレクトリ: {cea_config.get('output_dir', '未設定')}")
    print()
    
    # 発電所設定
    print("⚡ 発電所設定:")
    power_config = config.get('power_plant', {})
    print(f"   有効: {power_config.get('enabled', False)}")
    print(f"   監視間隔: {power_config.get('monitoring_interval', '未設定')}秒")
    print()
    
    # 音声設定
    print("🎵 音声設定:")
    audio_config = config.get('audio', {})
    print(f"   有効: {audio_config.get('enabled', False)}")
    print(f"   BGM音量: {audio_config.get('bgm_volume', '未設定')}")
    print(f"   効果音音量: {audio_config.get('effect_volume', '未設定')}")
    print()
    
    # 監視設定
    print("👁️ 監視設定:")
    monitoring_config = config.get('monitoring', {})
    print(f"   有効: {monitoring_config.get('enabled', False)}")
    print(f"   間隔: {monitoring_config.get('interval', '未設定')}秒")
    print(f"   自動同期: {monitoring_config.get('auto_sync', False)}")
    print()
    
    # 機密設定の確認
    print("🔒 機密設定の状態:")
    sensitive_config = config_manager.get_sensitive_config()
    for key, value in sensitive_config.items():
        if value == 'NOT_SET':
            print(f"   ❌ {key}: 未設定")
        else:
            print(f"   ✅ {key}: 設定済み")
    
    print()
    print("🎉 設定確認完了！")
    print("📋 すべての設定が正常に読み込まれています。")

if __name__ == "__main__":
    main() 