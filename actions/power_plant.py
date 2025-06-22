#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
発電方法記録・学習モジュール
実際の発電方法を記録し、学習効果を促進するシステム
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class PowerGenerationLearningSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.power_dir = Path(config.get('output_dir', 'data/power_generation'))
        self.power_dir.mkdir(exist_ok=True)
        
        # 発電方法履歴
        self.generation_history = []
        
        # 学習目標
        self.learning_goals = self._initialize_learning_goals()
        
    def _initialize_learning_goals(self) -> Dict:
        """学習目標の初期化"""
        return {
            'basic_goals': [
                {
                    'id': 'first_power',
                    'name': '初めての発電',
                    'description': '初めて発電方法を記録した',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 100, 'crypto': 0.001},
                    'status': 'locked'
                },
                {
                    'id': 'multiple_methods',
                    'name': '多様な発電方法',
                    'description': '3種類以上の異なる発電方法を記録',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                }
            ],
            'renewable_goals': [
                {
                    'id': 'solar_power',
                    'name': '太陽光発電マスター',
                    'description': '太陽光発電の詳細記録を5回以上',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'wind_power',
                    'name': '風力発電マスター',
                    'description': '風力発電の詳細記録を3回以上',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'hydro_power',
                    'name': '水力発電マスター',
                    'description': '水力発電の詳細記録を2回以上',
                    'type': 'collection',
                    'target': 2,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                }
            ],
            'advanced_goals': [
                {
                    'id': 'hybrid_system',
                    'name': 'ハイブリッドシステム',
                    'description': '複数の発電方法を組み合わせたシステムを記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'efficiency_improvement',
                    'name': '効率改善',
                    'description': '発電効率を10%以上改善した記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                }
            ]
        }
    
    def record_power_generation(self) -> Dict:
        """発電方法を記録"""
        print(f"\n⚡ 発電方法記録")
        print("="*40)
        
        # 発電方法の選択
        print("🔌 発電方法を選択してください:")
        power_methods = {
            '1': 'solar',
            '2': 'wind', 
            '3': 'hydro',
            '4': 'thermal',
            '5': 'nuclear',
            '6': 'biomass',
            '7': 'geothermal',
            '8': 'tidal',
            '9': 'other'
        }
        
        method_names = {
            'solar': '太陽光発電',
            'wind': '風力発電',
            'hydro': '水力発電', 
            'thermal': '火力発電',
            'nuclear': '原子力発電',
            'biomass': 'バイオマス発電',
            'geothermal': '地熱発電',
            'tidal': '潮力発電',
            'other': 'その他'
        }
        
        for key, method in power_methods.items():
            print(f"   {key}. {method_names[method]}")
        
        try:
            choice = input(f"選択してください (1-{len(power_methods)}) [1]: ").strip() or "1"
            if choice in power_methods:
                method = power_methods[choice]
            else:
                method = 'solar'
        except:
            method = 'solar'
        
        print(f"\n📊 {method_names[method]}の詳細を入力してください:")
        
        # 基本パラメータ入力
        try:
            capacity = float(input("発電容量 (kW) [1.0]: ").strip() or "1.0")
            efficiency = float(input("発電効率 (%) [15.0]: ").strip() or "15.0")
            location = input("設置場所/地域: ").strip()
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            capacity, efficiency, location = 1.0, 15.0, "自宅"
        
        # 詳細情報入力
        print(f"\n📝 詳細情報:")
        equipment = input("使用機器/設備 (例: 太陽光パネル、風力タービン): ").strip()
        manufacturer = input("メーカー/ブランド: ").strip()
        installation_date = input("設置日 (YYYY-MM-DD): ").strip()
        
        # 実績データ入力
        print(f"\n📈 実績データ:")
        try:
            daily_generation = float(input("1日あたりの発電量 (kWh) [5.0]: ").strip() or "5.0")
            monthly_generation = float(input("1ヶ月あたりの発電量 (kWh) [150.0]: ").strip() or "150.0")
            cost_per_kwh = float(input("発電コスト (円/kWh) [25.0]: ").strip() or "25.0")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            daily_generation, monthly_generation, cost_per_kwh = 5.0, 150.0, 25.0
        
        # 学習メモ入力
        print(f"\n📚 学習メモ:")
        challenges = input("課題や問題点: ").strip()
        improvements = input("改善点や工夫: ").strip()
        learnings = input("学んだこと: ").strip()
        
        # 結果をまとめる
        result = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'method_name': method_names[method],
            'capacity': capacity,
            'efficiency': efficiency,
            'location': location,
            'equipment': equipment,
            'manufacturer': manufacturer,
            'installation_date': installation_date,
            'daily_generation': daily_generation,
            'monthly_generation': monthly_generation,
            'cost_per_kwh': cost_per_kwh,
            'challenges': challenges,
            'improvements': improvements,
            'learnings': learnings,
            'status': 'recorded'
        }
        
        # 履歴に追加
        self.generation_history.append(result)
        
        # 学習目標の進捗を更新
        self._update_learning_progress(result)
        
        # ファイルに保存
        self._save_generation_record(result)
        
        print(f"\n✅ 発電方法を記録しました!")
        print(f"   ⚡ 方法: {method_names[method]}")
        print(f"   📊 容量: {capacity} kW")
        print(f"   📈 効率: {efficiency}%")
        print(f"   📍 場所: {location}")
        print(f"   💰 1日あたり: {daily_generation} kWh")
        
        return result
    
    def _update_learning_progress(self, result: Dict):
        """学習目標の進捗を更新"""
        method = result['method']
        
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_power':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'multiple_methods':
                # ユニークな発電方法をカウント
                unique_methods = set()
                for gen in self.generation_history:
                    unique_methods.add(gen['method'])
                goal['current'] = len(unique_methods)
        
        # 再生可能エネルギー目標の更新
        for goal in self.learning_goals['renewable_goals']:
            if goal['id'] == 'solar_power' and method == 'solar':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'wind_power' and method == 'wind':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'hydro_power' and method == 'hydro':
                goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 高度目標の更新
        for goal in self.learning_goals['advanced_goals']:
            if goal['id'] == 'hybrid_system':
                # 複数方法の組み合わせをチェック
                methods_in_session = set()
                for gen in self.generation_history[-3:]:  # 最近3件
                    methods_in_session.add(gen['method'])
                if len(methods_in_session) >= 2:
                    goal['current'] = 1
    
    def _save_generation_record(self, result: Dict):
        """発電記録をファイルに保存"""
        timestamp = int(time.time())
        filename = f"power_generation_{timestamp}.json"
        filepath = self.power_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 発電記録を保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 発電学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'renewable': '🌱 再生可能エネルギー目標', 
            'advanced': '🚀 高度目標',
            'all': '📋 全ての目標'
        }
        
        # カテゴリ選択
        if selected_category == "all":
            print(f"📑 カテゴリ選択:")
            for i, (cat_id, cat_name) in enumerate(categories.items(), 1):
                print(f"   {i}. {cat_name}")
            
            try:
                choice = input(f"カテゴリを選択してください (1-{len(categories)}) [1]: ").strip()
                if not choice:
                    choice = "1"
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(categories):
                    selected_category = list(categories.keys())[choice_idx]
                else:
                    selected_category = "basic"
            except ValueError:
                selected_category = "basic"
        
        # 選択されたカテゴリの目標を表示
        if selected_category == "all":
            for cat_id, cat_name in categories.items():
                if cat_id != "all":
                    self._show_category_goals(cat_id, cat_name)
        else:
            cat_name = categories.get(selected_category, "目標")
            self._show_category_goals(selected_category, cat_name)
    
    def _show_category_goals(self, category: str, category_name: str):
        """カテゴリ別の目標を表示"""
        print(f"\n{category_name}:")
        
        if category == "basic":
            goals = self.learning_goals['basic_goals']
        elif category == "renewable":
            goals = self.learning_goals['renewable_goals']
        elif category == "advanced":
            goals = self.learning_goals['advanced_goals']
        else:
            return
        
        for goal in goals:
            if goal['status'] == 'locked':
                status_icon = "🔒"
                progress = "ロック中"
            elif goal['status'] == 'completed':
                status_icon = "✅"
                progress = f"{goal['current']}/{goal['target']} (完了)"
            else:
                status_icon = "⏳"
                progress = f"{goal['current']}/{goal['target']}"
            
            print(f"   {status_icon} {goal['name']}: {progress}")
            print(f"      📝 {goal['description']}")
            
            reward = goal.get('reward', {})
            if reward.get('experience', 0) > 0 or reward.get('crypto', 0) > 0:
                rewards = []
                if reward.get('experience', 0) > 0:
                    rewards.append(f"💎 経験値 +{reward['experience']}")
                if reward.get('crypto', 0) > 0:
                    rewards.append(f"💰 Crypto +{reward['crypto']:.6f} XMR")
                print(f"      🎁 報酬: {', '.join(rewards)}")
    
    def check_goal_completion(self) -> List[Dict]:
        """学習目標の完了をチェック"""
        completed_goals = []
        
        for category in ['basic_goals', 'renewable_goals', 'advanced_goals']:
            for goal in self.learning_goals[category]:
                if goal['status'] == 'active' and goal['current'] >= goal['target']:
                    goal['status'] = 'completed'
                    goal['completion_time'] = datetime.now().isoformat()
                    completed_goals.append(goal)
        
        return completed_goals
    
    def get_generation_statistics(self) -> Dict:
        """発電統計を取得"""
        if not self.generation_history:
            return {'status': 'no_data'}
        
        # 統計計算
        total_records = len(self.generation_history)
        unique_methods = set()
        total_capacity = 0
        total_daily_generation = 0
        
        method_counts = {}
        
        for gen in self.generation_history:
            unique_methods.add(gen['method'])
            total_capacity += gen['capacity']
            total_daily_generation += gen['daily_generation']
            
            method = gen['method']
            method_counts[method] = method_counts.get(method, 0) + 1
        
        return {
            'status': 'success',
            'total_records': total_records,
            'unique_methods': len(unique_methods),
            'total_capacity': total_capacity,
            'total_daily_generation': total_daily_generation,
            'method_counts': method_counts,
            'methods': list(unique_methods)
        }
    
    def show_generation_history(self):
        """発電履歴を表示"""
        print(f"\n📚 発電履歴")
        print("="*50)
        
        if not self.generation_history:
            print("📝 発電履歴がありません")
            return
        
        for i, gen in enumerate(self.generation_history[-5:], 1):  # 最新5件
            print(f"\n{i}. {gen['method_name']} ({gen['capacity']}kW)")
            print(f"   📍 場所: {gen['location']}")
            print(f"   ⚡ 効率: {gen['efficiency']}%")
            print(f"   💰 1日あたり: {gen['daily_generation']} kWh")
            print(f"   🛠️ 機器: {gen['equipment']}")
            if gen['learnings']:
                print(f"   📝 学んだこと: {gen['learnings'][:50]}...")
    
    def show_power_methods_guide(self):
        """発電方法ガイドを表示"""
        print(f"\n📖 発電方法ガイド")
        print("="*50)
        
        methods_guide = {
            'solar': {
                'name': '太陽光発電',
                'description': '太陽光を電気に変換',
                'pros': ['無尽蔵のエネルギー', 'メンテナンスが少ない', '静音'],
                'cons': ['天候に依存', '夜間発電不可', '初期コストが高い'],
                'suitable_for': '個人住宅、商業施設',
                'efficiency_range': '15-25%'
            },
            'wind': {
                'name': '風力発電',
                'description': '風の運動エネルギーを電気に変換',
                'pros': ['クリーンエネルギー', '高効率', '24時間発電可能'],
                'cons': ['風況に依存', '騒音問題', '鳥への影響'],
                'suitable_for': '風況の良い地域、大規模施設',
                'efficiency_range': '30-50%'
            },
            'hydro': {
                'name': '水力発電',
                'description': '水の位置エネルギーを電気に変換',
                'pros': ['安定した発電', '高効率', '調整可能'],
                'cons': ['地形に制限', '環境影響', '初期コストが高い'],
                'suitable_for': '河川沿い、山間部',
                'efficiency_range': '80-90%'
            },
            'thermal': {
                'name': '火力発電',
                'description': '化石燃料の燃焼で発電',
                'pros': ['安定した発電', '技術が成熟', '調整可能'],
                'cons': ['CO2排出', '燃料コスト', '環境負荷'],
                'suitable_for': '大規模発電所',
                'efficiency_range': '35-45%'
            }
        }
        
        for method_id, info in methods_guide.items():
            print(f"\n🔌 {info['name']}")
            print(f"   📝 {info['description']}")
            print(f"   ✅ メリット: {', '.join(info['pros'])}")
            print(f"   ❌ デメリット: {', '.join(info['cons'])}")
            print(f"   🎯 適している場所: {info['suitable_for']}")
            print(f"   📊 効率範囲: {info['efficiency_range']}")


class PowerMissionSystem:
    """発電所ミッション管理システム"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.missions_dir = Path(config.get('output_dir', 'data/power_missions'))
        self.missions_dir.mkdir(exist_ok=True)
        
        # ミッションの初期化
        self.missions = self._initialize_missions()
        
        # 現在のタブ
        self.current_tab = 'daily'
        
    def _initialize_missions(self) -> Dict:
        """ミッションの初期化"""
        return {
            'daily': [
                {
                    'id': 'daily_solar_1',
                    'name': '太陽光発電の日次監視',
                    'description': '太陽光発電の1日あたりの発電量を記録',
                    'type': 'daily',
                    'target': 5.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 50, 'crypto': 0.0005},
                    'status': 'active',
                    'category': 'solar'
                },
                {
                    'id': 'daily_wind_1',
                    'name': '風力発電の日次監視',
                    'description': '風力発電の1日あたりの発電量を記録',
                    'type': 'daily',
                    'target': 3.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 60, 'crypto': 0.0006},
                    'status': 'active',
                    'category': 'wind'
                },
                {
                    'id': 'daily_efficiency_1',
                    'name': '発電効率の改善',
                    'description': '発電効率を前日比で5%以上改善',
                    'type': 'daily',
                    'target': 5.0,  # %
                    'current': 0.0,
                    'unit': '%',
                    'reward': {'experience': 80, 'crypto': 0.0008},
                    'status': 'active',
                    'category': 'efficiency'
                }
            ],
            'weekly': [
                {
                    'id': 'weekly_solar_1',
                    'name': '太陽光発電の週次目標',
                    'description': '1週間で30kWh以上の太陽光発電を達成',
                    'type': 'weekly',
                    'target': 30.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active',
                    'category': 'solar'
                },
                {
                    'id': 'weekly_wind_1',
                    'name': '風力発電の週次目標',
                    'description': '1週間で20kWh以上の風力発電を達成',
                    'type': 'weekly',
                    'target': 20.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 180, 'crypto': 0.0018},
                    'status': 'active',
                    'category': 'wind'
                },
                {
                    'id': 'weekly_hybrid_1',
                    'name': 'ハイブリッド発電の週次目標',
                    'description': '複数の発電方法を組み合わせて50kWh以上を達成',
                    'type': 'weekly',
                    'target': 50.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active',
                    'category': 'hybrid'
                }
            ],
            'achievement': [
                {
                    'id': 'achievement_first_100',
                    'name': '初めての100kWh',
                    'description': '累計で100kWhの発電を達成',
                    'type': 'achievement',
                    'target': 100.0,  # kWh
                    'current': 0.0,
                    'unit': 'kWh',
                    'reward': {'experience': 500, 'crypto': 0.005},
                    'status': 'active',
                    'category': 'total'
                },
                {
                    'id': 'achievement_efficiency_master',
                    'name': '効率マスター',
                    'description': '平均発電効率20%以上を1週間維持',
                    'type': 'achievement',
                    'target': 20.0,  # %
                    'current': 0.0,
                    'unit': '%',
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active',
                    'category': 'efficiency'
                },
                {
                    'id': 'achievement_sustainability',
                    'name': '持続可能性の追求',
                    'description': '再生可能エネルギーで1ヶ月間発電を継続',
                    'type': 'achievement',
                    'target': 30,  # 日数
                    'current': 0,
                    'unit': '日',
                    'reward': {'experience': 1000, 'crypto': 0.01},
                    'status': 'active',
                    'category': 'sustainability'
                }
            ],
            'completed': [],
            'in_progress': []
        }
    
    def show_missions(self):
        """ミッション一覧を表示"""
        print(f"\n🏭 発電所ミッション")
        print("="*50)
        
        # タブ選択
        tabs = {
            'daily': '📅 日次ミッション',
            'weekly': '📊 週次ミッション',
            'achievement': '🏆 実績ミッション',
            'completed': '✅ 完了済み',
            'in_progress': '⏳ 進行中'
        }
        
        print("📑 タブ選択:")
        for i, (tab_id, tab_name) in enumerate(tabs.items(), 1):
            current_indicator = " ←" if tab_id == self.current_tab else ""
            print(f"   {i}. {tab_name}{current_indicator}")
        
        try:
            choice = input(f"タブを選択してください (1-{len(tabs)}) [{list(tabs.keys()).index(self.current_tab) + 1}]: ").strip()
            if choice:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(tabs):
                    self.current_tab = list(tabs.keys())[choice_idx]
        except ValueError:
            pass
        
        # 選択されたタブのミッションを表示
        self._show_tab_missions(self.current_tab, tabs[self.current_tab])
    
    def _show_tab_missions(self, tab: str, tab_name: str):
        """タブ別のミッションを表示"""
        print(f"\n{tab_name}:")
        print("="*40)
        
        missions = self.missions.get(tab, [])
        
        if not missions:
            print("📝 ミッションがありません")
            return
        
        for i, mission in enumerate(missions, 1):
            if mission['status'] == 'completed':
                status_icon = "✅"
                progress = f"{mission['current']}/{mission['target']} {mission['unit']} (完了)"
            else:
                status_icon = "⏳"
                progress = f"{mission['current']}/{mission['target']} {mission['unit']}"
            
            print(f"\n{i}. {status_icon} {mission['name']}")
            print(f"   📝 {mission['description']}")
            print(f"   📊 進捗: {progress}")
            
            reward = mission.get('reward', {})
            if reward.get('experience', 0) > 0 or reward.get('crypto', 0) > 0:
                rewards = []
                if reward.get('experience', 0) > 0:
                    rewards.append(f"💎 経験値 +{reward['experience']}")
                if reward.get('crypto', 0) > 0:
                    rewards.append(f"💰 Crypto +{reward['crypto']:.6f} XMR")
                print(f"   🎁 報酬: {', '.join(rewards)}")
    
    def update_mission_progress(self):
        """ミッション進捗を更新"""
        print(f"\n📊 ミッション進捗更新")
        print("="*40)
        
        # 更新可能なミッションを表示
        updateable_missions = []
        for tab in ['daily', 'weekly', 'achievement']:
            for mission in self.missions[tab]:
                if mission['status'] == 'active':
                    updateable_missions.append(mission)
        
        if not updateable_missions:
            print("📝 更新可能なミッションがありません")
            return
        
        print("更新可能なミッション:")
        for i, mission in enumerate(updateable_missions, 1):
            print(f"   {i}. {mission['name']} ({mission['current']}/{mission['target']} {mission['unit']})")
        
        try:
            choice = input(f"更新するミッションを選択してください (1-{len(updateable_missions)}): ").strip()
            if not choice:
                return
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(updateable_missions):
                mission = updateable_missions[choice_idx]
                self._update_single_mission(mission)
            else:
                print("❌ 無効な選択です")
                
        except ValueError:
            print("❌ 無効な入力です")
    
    def _update_single_mission(self, mission: Dict):
        """単一ミッションの進捗を更新"""
        print(f"\n📈 {mission['name']}の進捗を更新")
        print(f"現在の進捗: {mission['current']}/{mission['target']} {mission['unit']}")
        
        try:
            new_value = float(input(f"新しい値を入力してください ({mission['unit']}): ").strip())
            
            # 進捗を更新
            mission['current'] = new_value
            
            # 完了チェック
            if mission['current'] >= mission['target']:
                mission['status'] = 'completed'
                mission['completion_time'] = datetime.now().isoformat()
                
                # 完了済みリストに移動
                self.missions['completed'].append(mission)
                
                print(f"🎉 ミッション完了: {mission['name']}!")
                print(f"   💎 経験値 +{mission['reward']['experience']}")
                print(f"   💰 Crypto +{mission['reward']['crypto']:.6f} XMR")
            else:
                print(f"✅ 進捗を更新しました: {mission['current']}/{mission['target']} {mission['unit']}")
                
        except ValueError:
            print("❌ 無効な値です")
    
    def show_mission_statistics(self):
        """ミッション統計を表示"""
        print(f"\n📊 ミッション統計")
        print("="*40)
        
        total_missions = 0
        completed_missions = 0
        total_rewards = {'experience': 0, 'crypto': 0}
        
        for tab in ['daily', 'weekly', 'achievement']:
            for mission in self.missions[tab]:
                total_missions += 1
                if mission['status'] == 'completed':
                    completed_missions += 1
                    total_rewards['experience'] += mission['reward']['experience']
                    total_rewards['crypto'] += mission['reward']['crypto']
        
        completion_rate = (completed_missions / total_missions * 100) if total_missions > 0 else 0
        
        print(f"📋 総ミッション数: {total_missions}")
        print(f"✅ 完了ミッション数: {completed_missions}")
        print(f"📈 完了率: {completion_rate:.1f}%")
        print(f"💎 獲得経験値: {total_rewards['experience']}")
        print(f"💰 獲得Crypto: {total_rewards['crypto']:.6f} XMR")
        
        # カテゴリ別統計
        print(f"\n📑 カテゴリ別統計:")
        categories = {}
        for tab in ['daily', 'weekly', 'achievement']:
            for mission in self.missions[tab]:
                category = mission['category']
                if category not in categories:
                    categories[category] = {'total': 0, 'completed': 0}
                categories[category]['total'] += 1
                if mission['status'] == 'completed':
                    categories[category]['completed'] += 1
        
        for category, stats in categories.items():
            rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {category}: {stats['completed']}/{stats['total']} ({rate:.1f}%)")
    
    def show_mission_hints(self):
        """ミッションヒントを表示"""
        print(f"\n💡 ミッションヒント")
        print("="*40)
        
        hints = {
            'daily': [
                "📅 日次ミッションは毎日リセットされます",
                "☀️ 太陽光発電は天候に大きく影響されます",
                "💨 風力発電は風速3m/s以上で効果的です",
                "📊 発電量は定期的に記録しましょう"
            ],
            'weekly': [
                "📊 週次ミッションは週末に完了を目指しましょう",
                "🔋 バッテリーを活用して安定発電を実現",
                "🌱 複数の発電方法を組み合わせて効率化",
                "📈 週間の傾向を分析して改善点を見つけましょう"
            ],
            'achievement': [
                "🏆 実績ミッションは長期的な目標です",
                "📚 発電技術の学習を継続しましょう",
                "🛠️ 設備のメンテナンスを定期的に行いましょう",
                "🌍 環境への配慮を忘れずに"
            ],
            'general': [
                "⚡ 電力効率を重視した運用を心がけましょう",
                "📱 スマートフォンアプリで発電量を監視",
                "🔧 定期的な設備点検で故障を予防",
                "📖 発電技術の最新情報をチェック"
            ]
        }
        
        for category, category_hints in hints.items():
            print(f"\n{category.upper()}:")
            for hint in category_hints:
                print(f"   • {hint}")
    
    def reset_daily_missions(self):
        """日次ミッションをリセット"""
        for mission in self.missions['daily']:
            if mission['status'] == 'active':
                mission['current'] = 0.0
        print("✅ 日次ミッションをリセットしました")
    
    def reset_weekly_missions(self):
        """週次ミッションをリセット"""
        for mission in self.missions['weekly']:
            if mission['status'] == 'active':
                mission['current'] = 0.0
        print("✅ 週次ミッションをリセットしました") 