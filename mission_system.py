#!/usr/bin/env python3
"""
ミッション・称号管理システム
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from condition_parser import ConditionParser

class MissionSystem:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.missions_file = self.data_dir / "missions.json"
        self.titles_file = self.data_dir / "titles.json"
        self.progress_file = self.data_dir / "mission_progress.json"
        self.action_logs_file = self.data_dir / "action_logs.json"
        
        # データを読み込み
        self.missions = self.load_missions()
        self.titles = self.load_titles()
        self.progress = self.load_progress()
        self.action_logs = self.load_action_logs()
        
        # 条件パーサー
        self.condition_parser = ConditionParser()
        
    def load_missions(self) -> Dict:
        """ミッションデータを読み込み"""
        if self.missions_file.exists():
            with open(self.missions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"main_missions": [], "sub_missions": []}
    
    def load_titles(self) -> Dict:
        """称号データを読み込み"""
        if self.titles_file.exists():
            with open(self.titles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"titles": []}
    
    def load_progress(self) -> Dict:
        """進行状況を読み込み"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "completed_missions": [],
            "unlocked_titles": [],
            "action_counts": {
                "mining": 0,
                "cea": 0,
                "power_plant": 0,
                "astronomy": 0,
                "build": 0,
                "advance_day": 0,
                "learning": 0,
                "review_day": 0
            },
            "daily_actions": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mining": 0,
                "cea": 0,
                "power_plant": 0,
                "astronomy": 0,
                "build": 0,
                "advance_day": 0,
                "learning": 0,
                "review_day": 0
            },
            "consecutive_days": {
                "advance_day": 0,
                "last_date": None
            },
            "daily_metrics": {
                "power_usage_W": 0,
                "mined_amount_XMR": 0,
                "expected_output_kwh_per_day": 0
            }
        }
    
    def load_action_logs(self) -> List[Dict]:
        """アクションログを読み込み"""
        if self.action_logs_file.exists():
            with open(self.action_logs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_progress(self):
        """進行状況を保存"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def save_action_logs(self):
        """アクションログを保存"""
        with open(self.action_logs_file, 'w', encoding='utf-8') as f:
            json.dump(self.action_logs, f, indent=2, ensure_ascii=False)
    
    def log_action(self, action_type: str, action_data: Dict = None):
        """アクションをログに記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "action_type": action_type,
            "data": action_data or {}
        }
        
        self.action_logs.append(log_entry)
        self.save_action_logs()
        
        # 進行状況を更新
        self.update_action_count(action_type)
        
        # 日次メトリクスを更新
        if action_data:
            self.update_daily_metrics(action_data)
    
    def update_action_count(self, action_type: str):
        """アクション回数を更新"""
        # 日付が変わったらリセット
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.progress["daily_actions"]["date"] != current_date:
            self.progress["daily_actions"] = {
                "date": current_date,
                "mining": 0,
                "cea": 0,
                "power_plant": 0,
                "astronomy": 0,
                "build": 0,
                "advance_day": 0,
                "learning": 0,
                "review_day": 0
            }
            
            # 日次メトリクスもリセット
            self.progress["daily_metrics"] = {
                "power_usage_W": 0,
                "mined_amount_XMR": 0,
                "expected_output_kwh_per_day": 0
            }
        
        # カウント更新
        if action_type in self.progress["action_counts"]:
            self.progress["action_counts"][action_type] += 1
        if action_type in self.progress["daily_actions"]:
            self.progress["daily_actions"][action_type] += 1
        
        # 連続日数を更新
        if action_type == "advance_day":
            self.update_consecutive_days()
        
        self.save_progress()
    
    def update_consecutive_days(self):
        """連続日数を更新"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        last_date = self.progress["consecutive_days"]["last_date"]
        
        if last_date:
            last_dt = datetime.strptime(last_date, "%Y-%m-%d")
            current_dt = datetime.strptime(current_date, "%Y-%m-%d")
            
            if (current_dt - last_dt).days == 1:
                # 連続
                self.progress["consecutive_days"]["advance_day"] += 1
            else:
                # 連続が途切れた
                self.progress["consecutive_days"]["advance_day"] = 1
        else:
            # 初回
            self.progress["consecutive_days"]["advance_day"] = 1
        
        self.progress["consecutive_days"]["last_date"] = current_date
    
    def update_daily_metrics(self, action_data: Dict):
        """日次メトリクスを更新"""
        metrics = self.progress["daily_metrics"]
        
        # マイニング関連
        if "power_usage_W" in action_data:
            metrics["power_usage_W"] += action_data["power_usage_W"]
        if "mined_amount_XMR" in action_data:
            metrics["mined_amount_XMR"] += action_data["mined_amount_XMR"]
        
        # 発電所関連
        if "expected_output_kwh_per_day" in action_data:
            metrics["expected_output_kwh_per_day"] += action_data["expected_output_kwh_per_day"]
    
    def check_missions(self, action_type: str, action_data: Dict = None) -> List[Dict]:
        """ミッション達成をチェック"""
        completed_missions = []
        
        # メインミッションをチェック
        for mission in self.missions["main_missions"]:
            if mission["id"] not in self.progress["completed_missions"]:
                if self.check_mission_condition(mission, action_type, action_data):
                    completed_missions.append(mission)
                    self.progress["completed_missions"].append(mission["id"])
        
        # サブミッションをチェック
        for mission in self.missions["sub_missions"]:
            if mission["id"] not in self.progress["completed_missions"]:
                if self.check_mission_condition(mission, action_type, action_data):
                    completed_missions.append(mission)
                    self.progress["completed_missions"].append(mission["id"])
        
        self.save_progress()
        return completed_missions
    
    def check_mission_condition(self, mission: Dict, action_type: str, action_data: Dict = None) -> bool:
        """ミッション条件をチェック（拡張版）"""
        condition = mission["condition"]
        
        # 基本的な条件タイプ
        if condition["type"] == "simple":
            return self.check_simple_condition(condition, action_type, action_data)
        
        elif condition["type"] == "total_action_count":
            return self.check_total_action_count(condition, action_type)
        
        elif condition["type"] == "daily_action_count":
            return self.check_daily_action_count(condition, action_type)
        
        elif condition["type"] == "completion":
            return self.check_completion_condition(condition, action_type, action_data)
        
        elif condition["type"] == "compound_and":
            return self.check_compound_and_condition(condition, action_type, action_data)
        
        elif condition["type"] == "consecutive_days":
            return self.check_consecutive_days_condition(condition, action_type)
        
        elif condition["type"] == "incremental_increase":
            return self.check_incremental_increase_condition(condition)
        
        elif condition["type"] == "same_day_both":
            return self.check_same_day_both_condition(condition, action_type)
        
        elif condition["type"] == "over_period":
            return self.check_over_period_condition(condition, action_type, action_data)
        
        elif condition["type"] == "percentage":
            return self.check_percentage_condition(condition, action_type, action_data)
        
        elif condition["type"] == "range_check":
            return self.check_range_condition(condition, action_type, action_data)
        
        # 従来の条件タイプ（後方互換性）
        elif condition["type"] == "first_action":
            return (condition["action"] == action_type and 
                   self.progress["action_counts"][action_type] == 1)
        
        return False
    
    def check_simple_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """シンプルな条件をチェック"""
        if condition["action"] != action_type or not action_data:
            return False
        
        metric = condition["metric"]
        operator = condition["operator"]
        target_value = condition["value"]
        
        if metric not in action_data:
            return False
        
        actual_value = action_data[metric]
        
        # 演算子による比較
        if operator == ">=":
            return actual_value >= target_value
        elif operator == "<=":
            return actual_value <= target_value
        elif operator == "==":
            return actual_value == target_value
        elif operator == "!=":
            return actual_value != target_value
        elif operator == ">":
            return actual_value > target_value
        elif operator == "<":
            return actual_value < target_value
        
        return False
    
    def check_total_action_count(self, condition: Dict, action_type: str) -> bool:
        """累計実行回数条件をチェック"""
        if condition["action"] != action_type:
            return False
        
        current_count = self.progress["action_counts"].get(action_type, 0)
        operator = condition["operator"]
        target_count = condition["count"]
        
        if operator == ">=":
            return current_count >= target_count
        elif operator == "<=":
            return current_count <= target_count
        elif operator == "==":
            return current_count == target_count
        
        return False
    
    def check_daily_action_count(self, condition: Dict, action_type: str) -> bool:
        """日次実行回数条件をチェック"""
        if condition["action"] != action_type:
            return False
        
        current_count = self.progress["daily_actions"].get(action_type, 0)
        operator = condition["operator"]
        target_count = condition["count"]
        
        if operator == ">=":
            return current_count >= target_count
        elif operator == "<=":
            return current_count <= target_count
        elif operator == "==":
            return current_count == target_count
        
        return False
    
    def check_completion_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """完了条件をチェック"""
        if condition["action"] != action_type or not action_data:
            return False
        
        # 条件文字列を解析してチェック
        condition_text = condition["condition"]
        # ここでより詳細な条件チェックを実装
        return True  # 簡易実装
    
    def check_compound_and_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """複合AND条件をチェック"""
        for sub_condition in condition["conditions"]:
            if not self.check_simple_condition(sub_condition, action_type, action_data):
                return False
        return True
    
    def check_consecutive_days_condition(self, condition: Dict, action_type: str) -> bool:
        """連続日数条件をチェック"""
        if condition["action"] != action_type:
            return False
        
        current_consecutive = self.progress["consecutive_days"].get(action_type, 0)
        target_days = condition["days"]
        
        return current_consecutive >= target_days
    
    def check_incremental_increase_condition(self, condition: Dict) -> bool:
        """増分条件をチェック"""
        metric = condition["metric"]
        target_days = condition["days"]
        
        # 過去N日間のデータを取得
        recent_logs = [log for log in self.action_logs[-target_days:] if metric in log.get("data", {})]
        
        if len(recent_logs) < target_days:
            return False
        
        # 増加しているかチェック
        values = [log["data"][metric] for log in recent_logs]
        for i in range(1, len(values)):
            if values[i] <= values[i-1]:
                return False
        
        return True
    
    def check_same_day_both_condition(self, condition: Dict, action_type: str) -> bool:
        """同日実行条件をチェック"""
        actions = condition["actions"]
        operator = condition["operator"]
        target_count = condition["count"]
        
        # 今日のアクションをチェック
        today = datetime.now().strftime("%Y-%m-%d")
        today_actions = [log["action_type"] for log in self.action_logs 
                        if log["date"] == today]
        
        # 両方のアクションが今日実行されているかチェック
        both_executed = all(action in today_actions for action in actions)
        
        if operator == ">=":
            return both_executed and target_count >= 1
        elif operator == "==":
            return both_executed and target_count == 1
        
        return False
    
    def check_over_period_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """期間条件をチェック"""
        if condition["action"] != action_type or not action_data:
            return False
        
        metric = condition["metric"]
        operator = condition["operator"]
        target_value = condition["value"]
        days = condition["days"]
        
        # 過去N日間のデータを取得
        recent_logs = [log for log in self.action_logs[-days:] 
                      if log["action_type"] == action_type and metric in log.get("data", {})]
        
        if not recent_logs:
            return False
        
        # 条件をチェック
        for log in recent_logs:
            actual_value = log["data"][metric]
            if operator == ">=" and actual_value < target_value:
                return False
            elif operator == "<=" and actual_value > target_value:
                return False
        
        return True
    
    def check_percentage_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """パーセンテージ条件をチェック"""
        if condition["action"] != action_type or not action_data:
            return False
        
        metric = condition["metric"]
        operator = condition["operator"]
        target_percentage = condition["percentage"]
        
        if metric not in action_data:
            return False
        
        actual_value = action_data[metric]
        
        # パーセンテージ計算（簡易実装）
        # 実際の実装では、より詳細な計算が必要
        return True
    
    def check_range_condition(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """範囲条件をチェック"""
        if condition["action"] != action_type or not action_data:
            return False
        
        metric = condition["metric"]
        target_values = condition["values"]
        
        if metric not in action_data:
            return False
        
        actual_value = action_data[metric]
        return actual_value in target_values
    
    def check_titles(self, action_type: str, action_data: Dict = None) -> List[Dict]:
        """称号獲得をチェック"""
        unlocked_titles = []
        
        for title in self.titles["titles"]:
            if title["id"] not in self.progress["unlocked_titles"]:
                if self.check_mission_condition(title, action_type, action_data):
                    unlocked_titles.append(title)
                    self.progress["unlocked_titles"].append(title["id"])
        
        self.save_progress()
        return unlocked_titles
    
    def get_available_missions(self) -> Dict:
        """利用可能なミッションを取得"""
        available = {
            "main_missions": [],
            "sub_missions": []
        }
        
        for mission in self.missions["main_missions"]:
            if mission["id"] not in self.progress["completed_missions"]:
                available["main_missions"].append(mission)
        
        for mission in self.missions["sub_missions"]:
            if mission["id"] not in self.progress["completed_missions"]:
                available["sub_missions"].append(mission)
        
        return available
    
    def get_unlocked_titles(self) -> List[Dict]:
        """獲得済み称号を取得"""
        unlocked = []
        for title in self.titles["titles"]:
            if title["id"] in self.progress["unlocked_titles"]:
                unlocked.append(title)
        return unlocked
    
    def add_mission(self, mission_data: Dict, mission_type: str = "sub_missions"):
        """ミッションを追加"""
        if mission_type not in self.missions:
            self.missions[mission_type] = []
        
        self.missions[mission_type].append(mission_data)
        
        with open(self.missions_file, 'w', encoding='utf-8') as f:
            json.dump(self.missions, f, indent=2, ensure_ascii=False)
    
    def add_title(self, title_data: Dict):
        """称号を追加"""
        self.titles["titles"].append(title_data)
        
        with open(self.titles_file, 'w', encoding='utf-8') as f:
            json.dump(self.titles, f, indent=2, ensure_ascii=False)

def main():
    """テスト用"""
    mission_system = MissionSystem()
    
    print("🎯 ミッションシステムテスト")
    print("=" * 50)
    
    # テストアクション
    test_action_data = {
        "power_usage_W": 15,
        "mined_amount_XMR": 0.00002,
        "expected_output_kwh_per_day": 2.5
    }
    
    # アクションをログに記録
    mission_system.log_action("mining", test_action_data)
    
    # ミッションをチェック
    completed = mission_system.check_missions("mining", test_action_data)
    unlocked = mission_system.check_titles("mining", test_action_data)
    
    print(f"✅ 完了したミッション: {len(completed)}")
    print(f"🏆 獲得した称号: {len(unlocked)}")
    
    # 利用可能なミッションを表示
    available = mission_system.get_available_missions()
    print(f"📋 利用可能なメインミッション: {len(available['main_missions'])}")
    print(f"📋 利用可能なサブミッション: {len(available['sub_missions'])}")

if __name__ == "__main__":
    main() 