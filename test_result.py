#!/usr/bin/env python3
"""
軽量シミュレーターの結果テスト
"""

from lightweight_miner import LightweightMiner

def test_miner_result():
    """マイナーの結果をテスト"""
    print("🧪 軽量シミュレーター結果テスト")
    print("=" * 50)
    
    # マイナーを作成
    miner = LightweightMiner("C:\\srbminer\\config.txt")
    
    # 短時間でテスト
    result = miner.start_mining(1)  # 1分間
    
    print("\n📊 結果の詳細:")
    for key, value in result.items():
        print(f"   {key}: {value}")
    
    # 必要なキーの存在確認
    required_keys = ['hash_rate', 'power_consumption', 'xmr_earned', 'success']
    print(f"\n🔍 必要なキーの確認:")
    for key in required_keys:
        if key in result:
            print(f"   ✅ {key}: {result[key]}")
        else:
            print(f"   ❌ {key}: 見つかりません")

if __name__ == "__main__":
    test_miner_result() 