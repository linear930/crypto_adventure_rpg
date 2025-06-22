#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEA計算記録・学習モジュール
実際のCEA計算結果を記録し、学習効果を促進するシステム
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class CEALearningSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.cea_dir = Path(config.get('output_dir', 'data/cea_learning'))
        self.cea_dir.mkdir(exist_ok=True)
        
        # CEA計算履歴
        self.calculation_history = []
        
        # 学習目標
        self.learning_goals = self._initialize_learning_goals()
        
    def _initialize_learning_goals(self) -> Dict:
        """学習目標の初期化"""
        return {
            'basic_goals': [
                {
                    'id': 'first_cea',
                    'name': '初めてのCEA計算',
                    'description': '初めてCEA計算を実行した',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 100, 'crypto': 0.001},
                    'status': 'locked'
                },
                {
                    'id': 'basic_propellants',
                    'name': '基本推進剤マスター',
                    'description': 'LOX/LH2、LOX/RP-1、N2O4/UDMHの計算を実行',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                }
            ],
            'advanced_goals': [
                {
                    'id': 'high_pressure',
                    'name': '高圧燃焼室',
                    'description': '100bar以上の燃焼室圧力で計算を実行',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 150, 'crypto': 0.0015},
                    'status': 'active'
                },
                {
                    'id': 'efficiency_optimization',
                    'name': '効率最適化',
                    'description': '比推力300秒以上の結果を達成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                }
            ],
            'research_goals': [
                {
                    'id': 'propellant_research',
                    'name': '推進剤研究',
                    'description': '5種類以上の異なる推進剤組み合わせを試行',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'parameter_study',
                    'name': 'パラメータ研究',
                    'description': '混合比、燃焼室圧力、膨張比の系統的研究を実行',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 500, 'crypto': 0.005},
                    'status': 'active'
                }
            ]
        }
    
    def record_cea_calculation(self) -> Dict:
        """CEA計算結果を記録"""
        print(f"\n🚀 CEA計算結果記録")
        print("="*40)
        
        # 基本パラメータ入力
        print("📊 計算パラメータを入力してください:")
        
        try:
            fuel = input("燃料 (例: LH2, RP-1, CH4, C2H6) [LH2]: ").strip() or "LH2"
            oxidizer = input("酸化剤 (例: LOX, N2O4, H2O2) [LOX]: ").strip() or "LOX"
            Pc = float(input("燃焼室圧力 (bar) [50]: ").strip() or "50")
            MR = float(input("混合比 [6.0]: ").strip() or "6.0")
            Pe = float(input("排気圧力 (bar) [1.0]: ").strip() or "1.0")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            fuel, oxidizer, Pc, MR, Pe = "LH2", "LOX", 50.0, 6.0, 1.0
        
        # 計算結果入力
        print(f"\n📈 計算結果を入力してください:")
        
        try:
            isp_vacuum = float(input("真空中比推力 (s) [400]: ").strip() or "400")
            isp_sea_level = float(input("海面比推力 (s) [350]: ").strip() or "350")
            Tc = float(input("燃焼室温度 (K) [3500]: ").strip() or "3500")
            gamma = float(input("比熱比 [1.2]: ").strip() or "1.2")
            Cf = float(input("推力係数 [1.8]: ").strip() or "1.8")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            isp_vacuum, isp_sea_level, Tc, gamma, Cf = 400, 350, 3500, 1.2, 1.8
        
        # 学習メモ入力
        print(f"\n📝 学習メモを入力してください:")
        notes = input("計算の目的、発見、学んだこと: ").strip()
        
        # 使用ツール入力
        print(f"\n🛠️ 使用ツール:")
        tools = input("使用したソフトウェア/ツール (例: CEA, RPA, 自作プログラム): ").strip()
        
        # 結果をまとめる
        result = {
            'timestamp': datetime.now().isoformat(),
            'fuel': fuel,
            'oxidizer': oxidizer,
            'Pc': Pc,
            'MR': MR,
            'Pe': Pe,
            'isp_vacuum': isp_vacuum,
            'isp_sea_level': isp_sea_level,
            'Tc': Tc,
            'gamma': gamma,
            'Cf': Cf,
            'notes': notes,
            'tools': tools,
            'status': 'recorded'
        }
        
        # 履歴に追加
        self.calculation_history.append(result)
        
        # 学習目標の進捗を更新
        self._update_learning_progress(result)
        
        # ファイルに保存
        self._save_calculation(result)
        
        print(f"\n✅ CEA計算結果を記録しました!")
        print(f"   🔥 燃料: {fuel}")
        print(f"   💨 酸化剤: {oxidizer}")
        print(f"   📊 燃焼室圧力: {Pc} bar")
        print(f"   ⚖️ 混合比: {MR}")
        print(f"   ⚡ 真空中比推力: {isp_vacuum} s")
        print(f"   🌡️ 燃焼室温度: {Tc} K")
        
        return result
    
    def _update_learning_progress(self, result: Dict):
        """学習目標の進捗を更新"""
        fuel_oxidizer = f"{result['fuel']}/{result['oxidizer']}"
        
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_cea':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'basic_propellants':
                # 基本推進剤の組み合わせをチェック
                basic_combinations = ['LH2/LOX', 'RP-1/LOX', 'UDMH/N2O4']
                if fuel_oxidizer in basic_combinations:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 高度目標の更新
        for goal in self.learning_goals['advanced_goals']:
            if goal['id'] == 'high_pressure' and result['Pc'] >= 100:
                goal['current'] = 1
            elif goal['id'] == 'efficiency_optimization' and result['isp_vacuum'] >= 300:
                goal['current'] = 1
        
        # 研究目標の更新
        for goal in self.learning_goals['research_goals']:
            if goal['id'] == 'propellant_research':
                # ユニークな推進剤組み合わせをカウント
                unique_combinations = set()
                for calc in self.calculation_history:
                    unique_combinations.add(f"{calc['fuel']}/{calc['oxidizer']}")
                goal['current'] = len(unique_combinations)
    
    def _save_calculation(self, result: Dict):
        """計算結果をファイルに保存"""
        timestamp = int(time.time())
        filename = f"cea_calculation_{timestamp}.json"
        filepath = self.cea_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 計算結果を保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 CEA学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'advanced': '🚀 高度目標', 
            'research': '🔬 研究目標',
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
        elif category == "advanced":
            goals = self.learning_goals['advanced_goals']
        elif category == "research":
            goals = self.learning_goals['research_goals']
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
        
        for category in ['basic_goals', 'advanced_goals', 'research_goals']:
            for goal in self.learning_goals[category]:
                if goal['status'] == 'active' and goal['current'] >= goal['target']:
                    goal['status'] = 'completed'
                    goal['completion_time'] = datetime.now().isoformat()
                    completed_goals.append(goal)
        
        return completed_goals
    
    def get_calculation_statistics(self) -> Dict:
        """計算統計を取得"""
        if not self.calculation_history:
            return {'status': 'no_data'}
        
        # 統計計算
        total_calculations = len(self.calculation_history)
        unique_propellants = set()
        max_isp = 0
        max_pressure = 0
        
        for calc in self.calculation_history:
            unique_propellants.add(f"{calc['fuel']}/{calc['oxidizer']}")
            max_isp = max(max_isp, calc['isp_vacuum'])
            max_pressure = max(max_pressure, calc['Pc'])
        
        return {
            'status': 'success',
            'total_calculations': total_calculations,
            'unique_propellants': len(unique_propellants),
            'max_isp': max_isp,
            'max_pressure': max_pressure,
            'propellant_combinations': list(unique_propellants)
        }
    
    def show_calculation_history(self):
        """計算履歴を表示"""
        print(f"\n📚 CEA計算履歴")
        print("="*50)
        
        if not self.calculation_history:
            print("📝 計算履歴がありません")
            return
        
        for i, calc in enumerate(self.calculation_history[-5:], 1):  # 最新5件
            print(f"\n{i}. {calc['fuel']}/{calc['oxidizer']} (Pc={calc['Pc']}bar, MR={calc['MR']})")
            print(f"   ⚡ 比推力: {calc['isp_vacuum']}s (真空), {calc['isp_sea_level']}s (海面)")
            print(f"   🌡️ 燃焼室温度: {calc['Tc']}K")
            print(f"   🛠️ ツール: {calc['tools']}")
            if calc['notes']:
                print(f"   📝 メモ: {calc['notes'][:50]}...") 