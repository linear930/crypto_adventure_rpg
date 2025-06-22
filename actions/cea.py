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
            'propellant_goals': [
                {
                    'id': 'propellant_alchemist',
                    'name': '推進剤の錬金術師',
                    'description': '未体験の推進剤組み合わせを1つ発見し計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 150, 'crypto': 0.0015},
                    'status': 'active'
                },
                {
                    'id': 'propellant_polyhedron',
                    'name': '推進剤の多面体',
                    'description': '10種類以上の推進剤組み合わせを試行',
                    'type': 'collection',
                    'target': 10,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'oxidizer_alchemy',
                    'name': '酸化剤の錬金術',
                    'description': '新規酸化剤を組み合わせて実験計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'fuel_symphony',
                    'name': '燃料の交響曲',
                    'description': '多様な燃料で燃焼特性を比較',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'propellant_composition_alchemy',
                    'name': '推進剤組成の錬金術',
                    'description': '新規組成比率で実験計算成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'propellant_stability_evaluator',
                    'name': '推進剤安定性評価',
                    'description': '推進剤の安定性試験を計算で模擬',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                }
            ],
            'performance_goals': [
                {
                    'id': 'specific_impulse_heights',
                    'name': '比推力の高みへ',
                    'description': '比推力350秒以上の計算結果達成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'high_specific_impulse_legend',
                    'name': '高比推力伝説',
                    'description': '400秒以上の比推力を目指せ',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'exhaust_velocity_traveler',
                    'name': '排気速度の旅人',
                    'description': '理論排気速度4000m/s超を達成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                },
                {
                    'id': 'combustion_efficiency_conductor',
                    'name': '燃焼効率の調律者',
                    'description': '燃焼効率95%以上の計算に成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'energy_density_explorer',
                    'name': 'エネルギー密度の探求',
                    'description': '高エネルギー密度燃料の評価計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                }
            ],
            'pressure_goals': [
                {
                    'id': 'combustion_chamber_abyss',
                    'name': '燃焼室の深淵',
                    'description': '200bar以上の燃焼室圧力で計算成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'combustion_pressure_master',
                    'name': '燃焼室圧力マスター',
                    'description': '圧力変動を考慮した複数計算成功',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'mixture_ratio_magician',
                    'name': '混合比の魔術師',
                    'description': '最適混合比を見つけて計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                },
                {
                    'id': 'mixture_ratio_variation_explorer',
                    'name': '混合比変動の探査',
                    'description': '連続的に混合比を変えた計算実施',
                    'type': 'collection',
                    'target': 10,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                }
            ],
            'temperature_goals': [
                {
                    'id': 'combustion_temperature_explorer',
                    'name': '燃焼温度の探求者',
                    'description': '3000K以上の燃焼温度を計算で確認',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                },
                {
                    'id': 'propellant_cooling_researcher',
                    'name': '推進剤冷却技術研究',
                    'description': '燃焼温度低減技術を理論計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                },
                {
                    'id': 'heat_exchange_efficiency_explorer',
                    'name': '熱交換効率の探査',
                    'description': '冷却系統の熱交換効率計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                }
            ],
            'design_goals': [
                {
                    'id': 'expansion_ratio_poet',
                    'name': '膨張比の詩人',
                    'description': '膨張比15以上のノズル計算を実施',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 220, 'crypto': 0.0022},
                    'status': 'active'
                },
                {
                    'id': 'nozzle_design_master',
                    'name': 'ノズル設計の匠',
                    'description': '拡大膨張ノズル設計と計算成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'combustion_chamber_shape_revolution',
                    'name': '燃焼室形状の革命',
                    'description': '複雑な燃焼室設計で性能向上計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                }
            ],
            'advanced_analysis_goals': [
                {
                    'id': 'calculation_accuracy_explorer',
                    'name': '計算精度の探求者',
                    'description': '誤差1%以下の再現性ある計算を実施',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'multi_stage_propulsion_simulator',
                    'name': '多段階推進シミュレータ',
                    'description': '多段式ロケットの燃焼計算を模擬',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 380, 'crypto': 0.0038},
                    'status': 'active'
                },
                {
                    'id': 'combustion_stability_guardian',
                    'name': '燃焼安定性の守護者',
                    'description': '不安定燃焼を解析し回避計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'reaction_rate_analyzer',
                    'name': '反応速度の解析者',
                    'description': '燃焼反応速度の最適化計算',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'combustion_gas_dynamics',
                    'name': '燃焼ガスの動力学',
                    'description': '燃焼ガスの流体力学計算を実施',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'extreme_combustion_challenger',
                    'name': '極限燃焼条件への挑戦',
                    'description': '極高圧・高温条件での計算成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                }
            ],
            'documentation_goals': [
                {
                    'id': 'engineering_document_master',
                    'name': 'エンジニアリング文書の達人',
                    'description': 'CEA計算結果を技術報告書にまとめる',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'propulsion_research_conference_participant',
                    'name': '燃焼推進研究会議参加',
                    'description': '専門家とのオンライン討論に参加（報告提出）',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'future_rocket_bridge',
                    'name': '未来ロケットへの架け橋',
                    'description': '新技術を取り入れたCEA計算成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                }
            ]
        }
    
    def record_cea_calculation(self) -> Dict:
        """CEA計算結果を記録"""
        print(f"\n🚀 CEA計算結果記録")
        print("="*40)
        print("💡 入力中に「abort」と入力すると記録を中断できます")
        print("-" * 40)
        
        # 基本パラメータ入力
        print("📊 計算パラメータを入力してください:")
        
        try:
            fuel = input("燃料 (例: LH2, RP-1, CH4, C2H6) [LH2]: ").strip()
            if fuel.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            fuel = fuel or "LH2"
            
            oxidizer = input("酸化剤 (例: LOX, N2O4, H2O2) [LOX]: ").strip()
            if oxidizer.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            oxidizer = oxidizer or "LOX"
            
            Pc_input = input("燃焼室圧力 (bar) [50]: ").strip()
            if Pc_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            Pc = float(Pc_input or "50")
            
            MR_input = input("混合比 [6.0]: ").strip()
            if MR_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            MR = float(MR_input or "6.0")
            
            Pe_input = input("排気圧力 (bar) [1.0]: ").strip()
            if Pe_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            Pe = float(Pe_input or "1.0")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            fuel, oxidizer, Pc, MR, Pe = "LH2", "LOX", 50.0, 6.0, 1.0
        
        # 計算結果入力
        print(f"\n📈 計算結果を入力してください:")
        
        try:
            isp_vac_input = input("真空中比推力 (s) [400]: ").strip()
            if isp_vac_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            isp_vacuum = float(isp_vac_input or "400")
            
            isp_sl_input = input("海面比推力 (s) [350]: ").strip()
            if isp_sl_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            isp_sea_level = float(isp_sl_input or "350")
            
            Tc_input = input("燃焼室温度 (K) [3500]: ").strip()
            if Tc_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            Tc = float(Tc_input or "3500")
            
            gamma_input = input("比熱比 [1.2]: ").strip()
            if gamma_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            gamma = float(gamma_input or "1.2")
            
            Cf_input = input("推力係数 [1.8]: ").strip()
            if Cf_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            Cf = float(Cf_input or "1.8")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            isp_vacuum, isp_sea_level, Tc, gamma, Cf = 400, 350, 3500, 1.2, 1.8
        
        # 学習メモ入力
        print(f"\n📝 学習メモを入力してください:")
        notes = input("計算の目的、発見、学んだこと: ").strip()
        if notes.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # 使用ツール入力
        print(f"\n🛠️ 使用ツール:")
        tools = input("使用したソフトウェア/ツール (例: CEA, RPA, 自作プログラム): ").strip()
        if tools.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
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
        basic_combinations = ['LH2/LOX', 'RP-1/LOX', 'UDMH/N2O4']
        
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_cea':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'basic_propellants':
                # 基本推進剤の組み合わせをチェック
                if fuel_oxidizer in basic_combinations:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 推進剤目標の更新
        for goal in self.learning_goals['propellant_goals']:
            if goal['id'] == 'propellant_alchemist' and fuel_oxidizer not in basic_combinations:
                goal['current'] = 1
            elif goal['id'] == 'propellant_polyhedron':
                # ユニークな推進剤組み合わせをカウント
                unique_combinations = set()
                for calc in self.calculation_history:
                    unique_combinations.add(f"{calc['fuel']}/{calc['oxidizer']}")
                goal['current'] = len(unique_combinations)
            elif goal['id'] == 'oxidizer_alchemy' and result['oxidizer'] not in ['LOX', 'N2O4', 'H2O2']:
                goal['current'] = 1
            elif goal['id'] == 'fuel_symphony':
                # ユニークな燃料をカウント
                unique_fuels = set()
                for calc in self.calculation_history:
                    unique_fuels.add(calc['fuel'])
                goal['current'] = len(unique_fuels)
            elif goal['id'] == 'propellant_composition_alchemy' and '新規組成' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'propellant_stability_evaluator' and '安定性' in result['notes']:
                goal['current'] = 1
        
        # 性能目標の更新
        for goal in self.learning_goals['performance_goals']:
            if goal['id'] == 'specific_impulse_heights' and result['isp_vacuum'] >= 350:
                goal['current'] = 1
            elif goal['id'] == 'high_specific_impulse_legend' and result['isp_vacuum'] >= 400:
                goal['current'] = 1
            elif goal['id'] == 'exhaust_velocity_traveler':
                # 理論排気速度 = 比推力 × 重力加速度
                exhaust_velocity = result['isp_vacuum'] * 9.81
                if exhaust_velocity >= 4000:
                    goal['current'] = 1
            elif goal['id'] == 'combustion_efficiency_conductor' and '効率95%' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'energy_density_explorer' and 'エネルギー密度' in result['notes']:
                goal['current'] = 1
        
        # 圧力目標の更新
        for goal in self.learning_goals['pressure_goals']:
            if goal['id'] == 'combustion_chamber_abyss' and result['Pc'] >= 200:
                goal['current'] = 1
            elif goal['id'] == 'combustion_pressure_master':
                # 圧力変動を考慮した計算をカウント
                pressure_variations = 0
                for calc in self.calculation_history:
                    if calc['Pc'] != result['Pc']:
                        pressure_variations += 1
                goal['current'] = min(pressure_variations, goal['target'])
            elif goal['id'] == 'mixture_ratio_magician' and '最適混合比' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'mixture_ratio_variation_explorer':
                # 混合比変動の計算をカウント
                mr_variations = 0
                for calc in self.calculation_history:
                    if calc['MR'] != result['MR']:
                        mr_variations += 1
                goal['current'] = min(mr_variations, goal['target'])
        
        # 温度目標の更新
        for goal in self.learning_goals['temperature_goals']:
            if goal['id'] == 'combustion_temperature_explorer' and result['Tc'] >= 3000:
                goal['current'] = 1
            elif goal['id'] == 'propellant_cooling_researcher' and '冷却技術' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'heat_exchange_efficiency_explorer' and '熱交換' in result['notes']:
                goal['current'] = 1
        
        # 設計目標の更新
        for goal in self.learning_goals['design_goals']:
            # 膨張比 = 燃焼室圧力 / 排気圧力
            expansion_ratio = result['Pc'] / result['Pe']
            if goal['id'] == 'expansion_ratio_poet' and expansion_ratio >= 15:
                goal['current'] = 1
            elif goal['id'] == 'nozzle_design_master' and 'ノズル設計' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_chamber_shape_revolution' and '燃焼室形状' in result['notes']:
                goal['current'] = 1
        
        # 高度解析目標の更新
        for goal in self.learning_goals['advanced_analysis_goals']:
            if goal['id'] == 'calculation_accuracy_explorer' and '精度1%' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'multi_stage_propulsion_simulator' and '多段式' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_stability_guardian' and '燃焼安定性' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'reaction_rate_analyzer' and '反応速度' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_gas_dynamics' and '流体力学' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'extreme_combustion_challenger' and (result['Pc'] >= 300 or result['Tc'] >= 4000):
                goal['current'] = 1
        
        # ドキュメント目標の更新
        for goal in self.learning_goals['documentation_goals']:
            if goal['id'] == 'engineering_document_master' and '技術報告書' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'propulsion_research_conference_participant' and '研究会議' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'future_rocket_bridge' and '新技術' in result['notes']:
                goal['current'] = 1
    
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
            'propellant': '🚀 推進剤目標',
            'performance': '🔬 性能目標',
            'pressure': '🌡️ 圧力目標',
            'temperature': '🌡️ 温度目標',
            'design': '🛠️ 設計目標',
            'advanced': '🚀 高度目標',
            'documentation': '📋 ドキュメント目標',
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
        elif category == "propellant":
            goals = self.learning_goals['propellant_goals']
        elif category == "performance":
            goals = self.learning_goals['performance_goals']
        elif category == "pressure":
            goals = self.learning_goals['pressure_goals']
        elif category == "temperature":
            goals = self.learning_goals['temperature_goals']
        elif category == "design":
            goals = self.learning_goals['design_goals']
        elif category == "advanced":
            goals = self.learning_goals['advanced_analysis_goals']
        elif category == "documentation":
            goals = self.learning_goals['documentation_goals']
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
        
        for category in ['basic_goals', 'propellant_goals', 'performance_goals', 'pressure_goals', 'temperature_goals', 'design_goals', 'advanced_analysis_goals', 'documentation_goals']:
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