#!/usr/bin/env python3
"""
GPTの条件テキストを自動的にミッション・称号データに変換
"""

import json
import re
from typing import Dict
from condition_parser import ConditionParser
from mission_system import MissionSystem

def parse_gpt_conditions(text: str) -> Dict:
    """GPTの条件テキストを解析"""
    missions = []
    titles = []
    
    # 行ごとに解析
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'):
            continue
            
        # ミッション番号と条件を抽出
        match = re.match(r'(\d+)\.\s*\*\*([^*]+)\*\*：(.+)', line)
        if match:
            mission_id, mission_name, condition_text = match.groups()
            
            # 条件を解析
            parser = ConditionParser()
            parsed_condition = parser.parse_condition_text(condition_text)
            
            # ミッションIDを生成
            mission_id_clean = f"mission_{int(mission_id):03d}"
            
            # ミッションデータを作成
            mission_data = {
                "id": mission_id_clean,
                "name": mission_name.strip(),
                "description": f"{mission_name.strip()}を達成する",
                "type": "main",  # メインミッションとして扱う
                "condition": parsed_condition,
                "reward": {
                    "xmr": 0.000001 * (100 - int(mission_id) + 1),  # 後半のミッションほど報酬が高い
                    "title": f"title_{mission_id_clean}"
                }
            }
            
            # 称号データを作成
            title_data = {
                "id": f"title_{mission_id_clean}",
                "name": mission_name.strip(),
                "description": f"{mission_name.strip()}を達成した",
                "condition": parsed_condition,
                "rarity": "common" if int(mission_id) <= 50 else "uncommon"
            }
            
            missions.append(mission_data)
            titles.append(title_data)
    
    return {
        "missions": missions,
        "titles": titles
    }

def convert_and_save_gpt_conditions():
    """GPTの条件を変換して保存"""
    print("🎯 GPTの条件テキストを変換中...")
    print("=" * 60)
    print()
    print("GPTから受け取った条件テキストを貼り付けてください:")
    print("（Ctrl+Z で終了）")
    print()
    
    try:
        # テキストを読み込み
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        
        text = '\n'.join(lines)
        
        # 条件を解析
        print("📋 条件を解析中...")
        data = parse_gpt_conditions(text)
        
        print(f"✅ {len(data['missions'])}個のミッションを解析")
        print(f"✅ {len(data['titles'])}個の称号を解析")
        
        # ミッションシステムに追加
        mission_system = MissionSystem()
        
        print("\n📋 ミッションデータを追加中...")
        for mission in data['missions']:
            mission_system.add_mission(mission, "main_missions")
            print(f"   ✅ {mission['name']} を追加")
        
        print("\n🏆 称号データを追加中...")
        for title in data['titles']:
            mission_system.add_title(title)
            print(f"   ✅ {title['name']} を追加")
        
        print()
        print("🎉 変換と追加が完了しました！")
        
        # 現在の状況を表示
        available = mission_system.get_available_missions()
        unlocked = mission_system.get_unlocked_titles()
        
        print(f"\n📊 現在の状況:")
        print(f"   利用可能なメインミッション: {len(available['main_missions'])}")
        print(f"   利用可能なサブミッション: {len(available['sub_missions'])}")
        print(f"   獲得済み称号: {len(unlocked)}")
        
        # サンプルデータをファイルに保存
        with open('data/gpt_converted_missions.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 変換結果を data/gpt_converted_missions.json に保存しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def test_condition_parser():
    """条件パーサーのテスト"""
    print("🧪 条件パーサーテスト")
    print("=" * 50)
    
    test_conditions = [
        "`design_plant` の `expected_output_kwh_per_day` ≥ 1.0",
        "`mine_log` 実行回数 ≥ 3",
        "累計 `cea_run` 実行回数 ≥ 10",
        "1日内の `mine_log` 回数 ≥ 1 かつ `power_usage_W` ≤ 0",
        "3日連続で `advance_day` を実行",
        "`mine_log` と `design_plant` を同日に両方実行 ≥ 1"
    ]
    
    parser = ConditionParser()
    
    for condition in test_conditions:
        result = parser.parse_condition_text(condition)
        print(f"条件: {condition}")
        print(f"解析結果: {result}")
        print()

def main():
    """メイン関数"""
    print("🎯 GPT条件変換ツール")
    print("=" * 60)
    print()
    print("1. 条件パーサーテスト")
    print("2. GPTの条件を変換・追加")
    print("3. 終了")
    print()
    
    choice = input("選択してください (1-3): ").strip()
    
    if choice == "1":
        test_condition_parser()
    elif choice == "2":
        convert_and_save_gpt_conditions()
    elif choice == "3":
        print("👋 終了します")
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    main() 