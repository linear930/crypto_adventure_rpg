#!/usr/bin/env python3
"""
ウォレットアドレス安全設定スクリプト
"""

import json
import os
from pathlib import Path

def setup_wallet_address():
    """ウォレットアドレスを安全に設定"""
    print("🔐 Moneroウォレットアドレス設定")
    print("=" * 50)
    print("⚠️  注意: ウォレットアドレスは絶対に他人に教えないでください！")
    print()
    
    # 設定ファイルのパス
    config_path = Path("data/reality_config.json")
    
    if not config_path.exists():
        print("❌ 設定ファイルが見つかりません")
        return
    
    # 現在の設定を読み込み
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 現在のアドレスを表示（マスク済み）
    current_addr = config.get('mining', {}).get('wallet_address', '')
    if current_addr and not current_addr.startswith('YOUR_'):
        masked_addr = current_addr[:8] + "..." + current_addr[-8:]
        print(f"現在のアドレス: {masked_addr}")
    else:
        print("現在のアドレス: 未設定")
    
    print()
    print("新しいMoneroウォレットアドレスを入力してください:")
    print("（Enterキーでスキップ）")
    
    new_address = input("アドレス: ").strip()
    
    if not new_address:
        print("設定をキャンセルしました")
        return
    
    # アドレスの形式チェック（簡易）
    if not new_address.startswith('4') or len(new_address) < 90:
        print("❌ 無効なMoneroアドレスです")
        print("   正しいMoneroアドレスを入力してください")
        return
    
    # 設定を更新
    config['mining']['wallet_address'] = new_address
    
    # 設定ファイルを保存
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print()
    print("✅ ウォレットアドレスを設定しました")
    print(f"   アドレス: {new_address[:8]}...{new_address[-8:]}")
    print()
    print("🔒 セキュリティのヒント:")
    print("   - このアドレスを他人に教えないでください")
    print("   - シードフレーズを安全に保管してください")
    print("   - 定期的にウォレットを更新してください")

if __name__ == "__main__":
    setup_wallet_address() 