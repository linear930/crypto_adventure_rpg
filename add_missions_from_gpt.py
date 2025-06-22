#!/usr/bin/env python3
"""
GPTからのミッション・称号データを受け取って追加するスクリプト
"""

import json
from mission_system import MissionSystem

def add_missions_from_gpt():
    """GPTからのミッションデータを追加"""
    print("🎯 GPTからのミッション・称号データ追加")
    print("=" * 60)
    print()
    print("GPTから受け取ったJSONデータを貼り付けてください:")
    print("（Ctrl+Z で終了）")
    print()
    
    try:
        # 複数行のJSONデータを読み込み
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        
        json_data = '\n'.join(lines)
        data = json.loads(json_data)
        
        # ミッションシステムを初期化
        mission_system = MissionSystem()
        
        # データの種類を判定して追加
        if "missions" in data:
            print("📋 ミッションデータを追加中...")
            for mission in data["missions"]:
                mission_type = mission.get("type", "sub_missions")
                if mission_type == "main":
                    mission_system.add_mission(mission, "main_missions")
                else:
                    mission_system.add_mission(mission, "sub_missions")
                print(f"   ✅ {mission['name']} を追加")
        
        if "titles" in data:
            print("🏆 称号データを追加中...")
            for title in data["titles"]:
                mission_system.add_title(title)
                print(f"   ✅ {title['name']} を追加")
        
        print()
        print("🎉 データの追加が完了しました！")
        
        # 現在の状況を表示
        available = mission_system.get_available_missions()
        unlocked = mission_system.get_unlocked_titles()
        
        print(f"📊 現在の状況:")
        print(f"   利用可能なメインミッション: {len(available['main_missions'])}")
        print(f"   利用可能なサブミッション: {len(available['sub_missions'])}")
        print(f"   獲得済み称号: {len(unlocked)}")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON形式エラー: {e}")
        print("正しいJSON形式で入力してください")
    except Exception as e:
        print(f"❌ エラー: {e}")

def show_format_example():
    """フォーマット例を表示"""
    print("📝 入力フォーマット例:")
    print("=" * 60)
    print()
    
    example = {
        "missions": [
            {
                "id": "example_mission",
                "name": "サンプルミッション",
                "description": "これはサンプルミッションです",
                "type": "main",  # "main" または "sub"
                "condition": {
                    "type": "total_action_count",
                    "action": "mining",
                    "count": 10
                },
                "reward": {
                    "xmr": 0.000005,
                    "title": "サンプル称号"
                }
            }
        ],
        "titles": [
            {
                "id": "example_title",
                "name": "サンプル称号",
                "description": "これはサンプル称号です",
                "condition": {
                    "type": "total_action_count",
                    "action": "mining",
                    "count": 10
                },
                "rarity": "rare"
            }
        ]
    }
    
    print(json.dumps(example, indent=2, ensure_ascii=False))

def main():
    """メイン関数"""
    print("🎯 GPTからのミッション・称号データ追加ツール")
    print("=" * 60)
    print()
    print("1. フォーマット例を表示")
    print("2. データを追加")
    print("3. 終了")
    print()
    
    choice = input("選択してください (1-3): ").strip()
    
    if choice == "1":
        show_format_example()
    elif choice == "2":
        add_missions_from_gpt()
    elif choice == "3":
        print("👋 終了します")
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    main() 