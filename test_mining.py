#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイニング機能テストスクリプト
実際のマイニング機能をテストするためのスクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from actions.mine import MoneroMiningLearningSystem
from config_manager import ConfigManager

def test_mining_system():
    """マイニングシステムのテスト"""
    print("🧪 マイニングシステムテスト")
    print("="*50)
    
    # 設定を読み込み
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # マイニングシステムを初期化
    miner = MoneroMiningLearningSystem(config)
    
    # システム互換性チェック
    print("\n1. システム互換性チェック")
    compatibility = miner.check_system_compatibility()
    print(f"   OS: {compatibility['os']}")
    print(f"   CPU: {compatibility['cpu_cores']}コア")
    print(f"   RAM: {compatibility['ram_gb']:.1f} GB")
    
    if compatibility['available_miners']:
        print(f"   ✅ 利用可能なマイニングソフト: {', '.join(compatibility['available_miners'])}")
    else:
        print(f"   ❌ 利用可能なマイニングソフト: なし")
        print(f"   📦 インストールが必要です")
    
    print(f"   🎯 マイニングサポート: {'✅ 可能' if compatibility['mining_supported'] else '❌ 不可能'}")
    
    # マイニング設定のテスト
    print("\n2. マイニング設定テスト")
    if compatibility['available_miners']:
        print("   設定テストを開始します...")
        # 実際の設定はユーザー入力が必要なので、設定ファイルから読み込みをテスト
        test_config = {
            'miner': compatibility['available_miners'][0],
            'pool_url': 'pool.supportxmr.com:3333',
            'wallet_address': 'test_wallet_address',
            'worker_name': 'test_worker',
            'threads': 2,
            'intensity': 5
        }
        miner.mining_config = test_config
        print(f"   ✅ テスト設定を適用: {test_config['miner']}")
    else:
        print("   ⚠️ マイニングソフトが未インストールのため、設定テストをスキップ")
    
    # マイニング状態のテスト
    print("\n3. マイニング状態テスト")
    status = miner.get_mining_status()
    print(f"   現在の状態: {status['status']}")
    
    # 学習目標のテスト
    print("\n4. 学習目標テスト")
    goals = miner.learning_goals
    total_goals = sum(len(category) for category in goals.values())
    print(f"   総学習目標数: {total_goals}")
    
    for category, goal_list in goals.items():
        print(f"   {category}: {len(goal_list)}個")
    
    # 統計機能のテスト
    print("\n5. 統計機能テスト")
    stats = miner.get_mining_statistics()
    print(f"   統計取得: {'✅ 成功' if stats['status'] == 'success' else '❌ 失敗'}")
    
    if stats['status'] == 'success':
        print(f"   総セッション数: {stats['total_sessions']}")
        print(f"   総シェア数: {stats['total_shares']}")
    
    print("\n✅ マイニングシステムテスト完了")
    print("\n💡 実際のマイニングをテストするには:")
    print("   1. cpuminer-optなどのマイニングソフトをインストール")
    print("   2. python main.py でゲームを起動")
    print("   3. マイニングメニューから設定と実行をテスト")

def test_mining_commands():
    """マイニングコマンドのテスト"""
    print("\n🔧 マイニングコマンドテスト")
    print("="*50)
    
    # 設定を読み込み
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # マイニングシステムを初期化
    miner = MoneroMiningLearningSystem(config)
    
    # テスト用設定
    test_config = {
        'miner': 'cpuminer-opt',
        'pool_url': 'pool.supportxmr.com:3333',
        'wallet_address': 'test_wallet_address',
        'worker_name': 'test_worker',
        'threads': 2,
        'intensity': 5
    }
    miner.mining_config = test_config
    
    # コマンド構築テスト
    print("1. コマンド構築テスト")
    try:
        cmd = miner._build_mining_command()
        print(f"   構築されたコマンド: {' '.join(cmd)}")
        print("   ✅ コマンド構築成功")
    except Exception as e:
        print(f"   ❌ コマンド構築エラー: {e}")
    
    # 出力解析テスト
    print("\n2. 出力解析テスト")
    test_outputs = [
        "accepted share",
        "rejected share",
        "hashrate: 1000 H/s",
        "error: connection failed"
    ]
    
    for output in test_outputs:
        print(f"   テスト出力: {output}")
        miner._parse_mining_output(output)
        print(f"   統計更新: ハッシュレート={miner.mining_stats['hashrate']}, "
              f"承認シェア={miner.mining_stats['accepted_shares']}, "
              f"拒否シェア={miner.mining_stats['rejected_shares']}")

if __name__ == "__main__":
    print("🚀 Crypto Adventure RPG - マイニング機能テスト")
    print("="*60)
    
    try:
        test_mining_system()
        test_mining_commands()
        
        print("\n🎉 すべてのテストが完了しました！")
        print("\n📋 次のステップ:")
        print("   1. マイニングソフトウェアのインストール")
        print("   2. ゲームの起動: python main.py")
        print("   3. マイニングメニューでの設定と実行")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc() 