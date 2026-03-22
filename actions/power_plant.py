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
        self.power_dir = Path("data/power_generation")
        self.power_dir.mkdir(exist_ok=True)
        
        # 履歴ファイルの初期化
        self.history_file = self.power_dir / "power_generations.json"
        self.generation_history = self._load_generation_history()
        
        # 学習目標
        self.learning_goals = self._initialize_learning_goals()
        
        # GameEngineへの参照を追加
        self.game_engine = None
        
    def set_game_engine(self, game_engine):
        """GameEngineへの参照を設定"""
        self.game_engine = game_engine
    
    def _initialize_learning_goals(self) -> Dict:
        """学習目標の初期化"""
        return {
            'basic_goals': [
                {
                    'id': 'first_power_sparkle',
                    'name': '初電の煌めき',
                    'description': '初めての電力生成を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 120, 'crypto': 0.0012},
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
            'renewable_energy_goals': [
                {
                    'id': 'wind_conductor',
                    'name': '風の調律者',
                    'description': '風速10m/s以上での風力発電を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 220, 'crypto': 0.0022},
                    'status': 'active'
                },
                {
                    'id': 'solar_poet',
                    'name': '太陽光の詩人',
                    'description': '異なる5地点で太陽光発電を記録',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'water_flow_melody',
                    'name': '水流の旋律',
                    'description': '河川での水力発電を複数回記録',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 240, 'crypto': 0.0024},
                    'status': 'active'
                },
                {
                    'id': 'biomass_breath',
                    'name': 'バイオマスの息吹',
                    'description': 'バイオマス発電を成功させる',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 230, 'crypto': 0.0023},
                    'status': 'active'
                },
                {
                    'id': 'tidal_explorer',
                    'name': '潮流の探求者',
                    'description': '潮流発電のデータを取得',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'geothermal_heartbeat',
                    'name': '地熱の鼓動',
                    'description': '地熱発電システムの記録を作成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                },
                {
                    'id': 'wave_energy_explorer',
                    'name': '波動エネルギーの探検家',
                    'description': '波力発電のデータを初めて記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                }
            ],
            'efficiency_goals': [
                {
                    'id': 'thermoelectric_alchemy',
                    'name': '熱電の錬金術',
                    'description': '廃熱回収発電を試し記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 260, 'crypto': 0.0026},
                    'status': 'active'
                },
                {
                    'id': 'efficiency_explorer',
                    'name': '効率の探求者',
                    'description': '総合発電効率を15%以上向上',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'power_conversion_magician',
                    'name': '電力変換の魔術師',
                    'description': 'インバータ効率90%以上を達成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 310, 'crypto': 0.0031},
                    'status': 'active'
                },
                {
                    'id': 'cooling_efficiency_alchemist',
                    'name': '冷却効率の錬金術師',
                    'description': '発電機冷却効率を10%以上向上',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'energy_saving_missionary',
                    'name': '省エネ発電の伝道師',
                    'description': '発電にかかるエネルギーロスを削減',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                },
                {
                    'id': 'solar_panel_cleaning_master',
                    'name': 'ソーラーパネル洗浄マスター',
                    'description': 'パネル汚れ低減による発電効率向上',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'inverter_optimization_artisan',
                    'name': 'インバータ最適化の職人',
                    'description': 'インバータ出力波形の歪み10%以下に改善',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 310, 'crypto': 0.0031},
                    'status': 'active'
                }
            ],
            'storage_goals': [
                {
                    'id': 'storage_guardian',
                    'name': '蓄電の守護者',
                    'description': '蓄電池システムの効率を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'night_power_pioneer',
                    'name': '夜間発電の開拓者',
                    'description': '蓄電を利用した夜間電力供給成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                }
            ],
            'grid_goals': [
                {
                    'id': 'smart_grid_dream',
                    'name': 'スマートグリッドの夢',
                    'description': '電力ネットワークの負荷制御を成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                },
                {
                    'id': 'renewable_mix_master',
                    'name': '再生可能ミックスマスター',
                    'description': '3種以上の発電方法を同時に運用',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 340, 'crypto': 0.0034},
                    'status': 'active'
                },
                {
                    'id': 'voltage_stability_guardian',
                    'name': '電圧安定の守護者',
                    'description': '電圧変動を±1%以内に制御成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 310, 'crypto': 0.0031},
                    'status': 'active'
                },
                {
                    'id': 'grid_cooperation_strategist',
                    'name': 'グリッド連携の策士',
                    'description': '電力グリッドとの連携運転を実施',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                }
            ],
            'environmental_goals': [
                {
                    'id': 'low_environmental_impact_knight',
                    'name': '低環境負荷の騎士',
                    'description': 'CO2排出を大幅削減した発電を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 330, 'crypto': 0.0033},
                    'status': 'active'
                },
                {
                    'id': 'local_energy_pioneer',
                    'name': '地産地消エネルギーの開拓者',
                    'description': '地域密着型発電システムを成功させる',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                }
            ],
            'system_goals': [
                {
                    'id': 'self_generation_architect',
                    'name': '自家発電アーキテクト',
                    'description': '小規模自家発電システムを構築・記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 290, 'crypto': 0.0029},
                    'status': 'active'
                },
                {
                    'id': 'environmental_adaptation_engineer',
                    'name': '環境適応エンジニア',
                    'description': '厳寒・高温環境下での発電記録作成',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 310, 'crypto': 0.0031},
                    'status': 'active'
                },
                {
                    'id': 'wind_direction_tracking_poet',
                    'name': '風向追尾の詩人',
                    'description': '風向に最適追尾するタービン設計',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 310, 'crypto': 0.0031},
                    'status': 'active'
                },
                {
                    'id': 'emergency_backup_planner',
                    'name': '緊急電力バックアップ計画',
                    'description': '停電時のバックアップ運用を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                }
            ],
            'advanced_analysis_goals': [
                {
                    'id': 'demand_prediction_magician',
                    'name': '電力需要予測の魔術師',
                    'description': '需要予測モデルを活用し最適運用',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 340, 'crypto': 0.0034},
                    'status': 'active'
                },
                {
                    'id': 'anomaly_detection_guardian',
                    'name': '異常検知の守護神',
                    'description': '故障予知・異常検知システムを構築',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 330, 'crypto': 0.0033},
                    'status': 'active'
                },
                {
                    'id': 'future_energy_visionary',
                    'name': '未来エネルギービジョナリー',
                    'description': '革新的発電技術のシミュレーション成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                }
            ]
        }
    
    def record_power_generation(self) -> Dict:
        """発電方法を記録"""
        print(f"\n⚡ 発電方法記録")
        print("="*40)
        print("💡 入力中に「abort」と入力すると記録を中断できます")
        print("💡 入力中に「back」と入力すると一つ前の入力に戻れます")
        print("-" * 40)
        
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
            choice = input(f"選択してください (1-{len(power_methods)}) [1]: ").strip()
            if choice.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if choice.lower() == "back":
                print("🔄 最初の入力なので戻る場所がありません。記録を中断します。")
                return None
            choice = choice or "1"
            if choice in power_methods:
                method = power_methods[choice]
            else:
                method = 'solar'
        except:
            method = 'solar'
        
        print(f"\n📊 {method_names[method]}の詳細を入力してください:")
        
        # 基本パラメータ入力
        try:
            capacity_input = input("発電容量 (kW) [1.0]: ").strip()
            if capacity_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if capacity_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                choice = input(f"選択してください (1-{len(power_methods)}) [1]: ").strip()
                if choice.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                choice = choice or "1"
                if choice in power_methods:
                    method = power_methods[choice]
                else:
                    method = 'solar'
                print(f"\n📊 {method_names[method]}の詳細を入力してください:")
                capacity_input = input("発電容量 (kW) [1.0]: ").strip()
                if capacity_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            capacity = float(capacity_input or "1.0")
            
            efficiency_input = input("発電効率 (%) [15.0]: ").strip()
            if efficiency_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if efficiency_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                capacity_input = input("発電容量 (kW) [1.0]: ").strip()
                if capacity_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                capacity = float(capacity_input or "1.0")
                efficiency_input = input("発電効率 (%) [15.0]: ").strip()
                if efficiency_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            efficiency = float(efficiency_input or "15.0")
            
            location = input("設置場所/地域: ").strip()
            if location.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if location.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                efficiency_input = input("発電効率 (%) [15.0]: ").strip()
                if efficiency_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                efficiency = float(efficiency_input or "15.0")
                location = input("設置場所/地域: ").strip()
                if location.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            capacity, efficiency, location = 1.0, 15.0, "自宅"
        
        # 詳細情報入力
        print(f"\n📝 詳細情報:")
        equipment = input("使用機器/設備 (例: 太陽光パネル、風力タービン): ").strip()
        if equipment.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if equipment.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            location = input("設置場所/地域: ").strip()
            if location.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            equipment = input("使用機器/設備 (例: 太陽光パネル、風力タービン): ").strip()
            if equipment.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
        manufacturer = input("メーカー/ブランド: ").strip()
        if manufacturer.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if manufacturer.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            equipment = input("使用機器/設備 (例: 太陽光パネル、風力タービン): ").strip()
            if equipment.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            manufacturer = input("メーカー/ブランド: ").strip()
            if manufacturer.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
        installation_date = input("設置日 (YYYY-MM-DD): ").strip()
        if installation_date.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if installation_date.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            manufacturer = input("メーカー/ブランド: ").strip()
            if manufacturer.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            installation_date = input("設置日 (YYYY-MM-DD): ").strip()
            if installation_date.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
        # 実績データ入力
        print(f"\n📈 実績データ:")
        try:
            daily_gen_input = input("1日あたりの発電量 (kWh) [5.0]: ").strip()
            if daily_gen_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if daily_gen_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                installation_date = input("設置日 (YYYY-MM-DD): ").strip()
                if installation_date.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                daily_gen_input = input("1日あたりの発電量 (kWh) [5.0]: ").strip()
                if daily_gen_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            daily_generation = float(daily_gen_input or "5.0")
            
            monthly_gen_input = input("1ヶ月あたりの発電量 (kWh) [150.0]: ").strip()
            if monthly_gen_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if monthly_gen_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                daily_gen_input = input("1日あたりの発電量 (kWh) [5.0]: ").strip()
                if daily_gen_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                daily_generation = float(daily_gen_input or "5.0")
                monthly_gen_input = input("1ヶ月あたりの発電量 (kWh) [150.0]: ").strip()
                if monthly_gen_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            monthly_generation = float(monthly_gen_input or "150.0")
            
            cost_input = input("発電コスト (円/kWh) [25.0]: ").strip()
            if cost_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if cost_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                monthly_gen_input = input("1ヶ月あたりの発電量 (kWh) [150.0]: ").strip()
                if monthly_gen_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                monthly_generation = float(monthly_gen_input or "150.0")
                cost_input = input("発電コスト (円/kWh) [25.0]: ").strip()
                if cost_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            cost_per_kwh = float(cost_input or "25.0")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            daily_generation, monthly_generation, cost_per_kwh = 5.0, 150.0, 25.0
        
        # 学習メモ入力
        print(f"\n📚 学習メモ:")
        challenges = input("課題や問題点: ").strip()
        if challenges.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if challenges.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            cost_input = input("発電コスト (円/kWh) [25.0]: ").strip()
            if cost_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            cost_per_kwh = float(cost_input or "25.0")
            challenges = input("課題や問題点: ").strip()
            if challenges.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
        improvements = input("改善点や工夫: ").strip()
        if improvements.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if improvements.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            challenges = input("課題や問題点: ").strip()
            if challenges.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            improvements = input("改善点や工夫: ").strip()
            if improvements.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
        learnings = input("学んだこと: ").strip()
        if learnings.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if learnings.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            improvements = input("改善点や工夫: ").strip()
            if improvements.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            learnings = input("学んだこと: ").strip()
            if learnings.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        
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
        self._save_generation_history()
        
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
            if goal['id'] == 'first_power_sparkle':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'multiple_methods':
                # ユニークな発電方法をカウント
                unique_methods = set()
                for gen in self.generation_history:
                    unique_methods.add(gen['method'])
                goal['current'] = len(unique_methods)
        
        # 再生可能エネルギー目標の更新
        for goal in self.learning_goals['renewable_energy_goals']:
            if goal['id'] == 'wind_conductor' and method == 'wind' and '風速10m/s' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'solar_poet' and method == 'solar':
                # 異なる地点での太陽光発電をカウント
                unique_locations = set()
                for gen in self.generation_history:
                    if gen['method'] == 'solar':
                        unique_locations.add(gen['location'])
                goal['current'] = len(unique_locations)
            elif goal['id'] == 'water_flow_melody' and method == 'hydro':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'biomass_breath' and method == 'biomass':
                goal['current'] = 1
            elif goal['id'] == 'tidal_explorer' and method == 'tidal':
                goal['current'] = 1
            elif goal['id'] == 'geothermal_heartbeat' and method == 'geothermal':
                goal['current'] = 1
            elif goal['id'] == 'wave_energy_explorer' and method == 'other' and '波力' in result.get('notes', ''):
                goal['current'] = 1
        
        # 効率目標の更新
        for goal in self.learning_goals['efficiency_goals']:
            if goal['id'] == 'thermoelectric_alchemy' and '廃熱回収' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'efficiency_explorer':
                # 総合発電効率を向上
                if len(self.generation_history) > 0:
                    total_efficiency = 0
                    for gen in self.generation_history:
                        total_efficiency += gen['efficiency']
                    average_efficiency = total_efficiency / len(self.generation_history)
                    if average_efficiency >= 15.0:
                        goal['current'] = 1
            elif goal['id'] == 'power_conversion_magician' and result['efficiency'] >= 90.0:
                goal['current'] = 1
            elif goal['id'] == 'cooling_efficiency_alchemist' and '冷却効率' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'energy_saving_missionary' and 'エネルギーロス削減' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'solar_panel_cleaning_master' and method == 'solar' and 'パネル洗浄' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'inverter_optimization_artisan' and 'インバータ最適化' in result.get('notes', ''):
                goal['current'] = 1
        
        # 蓄電目標の更新
        for goal in self.learning_goals['storage_goals']:
            if goal['id'] == 'storage_guardian' and '蓄電池' in result.get('equipment', ''):
                goal['current'] = 1
            elif goal['id'] == 'night_power_pioneer' and '夜間電力供給' in result.get('notes', ''):
                goal['current'] = 1
        
        # グリッド目標の更新
        for goal in self.learning_goals['grid_goals']:
            if goal['id'] == 'smart_grid_dream' and '負荷制御' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'renewable_mix_master':
                # 3種以上の発電方法を同時運用
                recent_methods = set()
                for gen in self.generation_history[-5:]:  # 最近5件
                    recent_methods.add(gen['method'])
                if len(recent_methods) >= 3:
                    goal['current'] = 1
            elif goal['id'] == 'voltage_stability_guardian' and '電圧制御' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'grid_cooperation_strategist' and 'グリッド連携' in result.get('notes', ''):
                goal['current'] = 1
        
        # 環境目標の更新
        for goal in self.learning_goals['environmental_goals']:
            if goal['id'] == 'low_environmental_impact_knight' and 'CO2削減' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'local_energy_pioneer' and '地域密着' in result.get('notes', ''):
                goal['current'] = 1
        
        # システム目標の更新
        for goal in self.learning_goals['system_goals']:
            if goal['id'] == 'self_generation_architect' and '自家発電' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'environmental_adaptation_engineer' and ('厳寒' in result.get('notes', '') or '高温' in result.get('notes', '')):
                goal['current'] = 1
            elif goal['id'] == 'wind_direction_tracking_poet' and method == 'wind' and '風向追尾' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'emergency_backup_planner' and 'バックアップ' in result.get('notes', ''):
                goal['current'] = 1
        
        # 高度解析目標の更新
        for goal in self.learning_goals['advanced_analysis_goals']:
            if goal['id'] == 'demand_prediction_magician' and '需要予測' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'anomaly_detection_guardian' and '異常検知' in result.get('notes', ''):
                goal['current'] = 1
            elif goal['id'] == 'future_energy_visionary' and '革新的技術' in result.get('notes', ''):
                goal['current'] = 1
    
    def _load_generation_history(self) -> List[Dict]:
        """発電履歴を読み込み"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('generations', [])
            except Exception as e:
                print(f"⚠️ 発電履歴読み込みエラー: {e}")
        return []
    
    def _save_generation_history(self):
        """発電履歴をファイルに保存"""
        try:
            data = {'generations': self.generation_history}
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 発電履歴保存エラー: {e}")
    
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
        
        # GameEngineのウォレットにも保存
        if self.game_engine:
            if 'plant_designs' not in self.game_engine.wallet:
                self.game_engine.wallet['plant_designs'] = []
            self.game_engine.wallet['plant_designs'].append(result)
            self.game_engine.save_wallet()
            print("💾 GameEngineウォレットに保存しました")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 発電学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'renewable': '🌱 再生可能エネルギー目標', 
            'efficiency': '🚀 効率改善',
            'storage': '🛠️ 蓄電',
            'grid': '📡 グリッド',
            'environmental': '🌍 環境',
            'system': '🛠️ システム',
            'advanced': '🚀 高度',
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
            goals = self.learning_goals['renewable_energy_goals']
        elif category == "efficiency":
            goals = self.learning_goals['efficiency_goals']
        elif category == "storage":
            goals = self.learning_goals['storage_goals']
        elif category == "grid":
            goals = self.learning_goals['grid_goals']
        elif category == "environmental":
            goals = self.learning_goals['environmental_goals']
        elif category == "system":
            goals = self.learning_goals['system_goals']
        elif category == "advanced":
            goals = self.learning_goals['advanced_analysis_goals']
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
        
        for category in ['basic_goals', 'renewable_energy_goals', 'efficiency_goals', 'storage_goals', 'grid_goals', 'environmental_goals', 'system_goals', 'advanced_analysis_goals']:
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
        
        self.game_engine = None
        
    def set_game_engine(self, engine):
        self.game_engine = engine
        
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
                
                # 世界エネルギーによる報酬ボーナス
                multiplier = 1.0
                if self.game_engine:
                    world_energy = self.game_engine.state.get('world_energy', 100)
                    if world_energy > 500:
                        multiplier = 1.5
                    elif world_energy > 200:
                        multiplier = 1.2
                        
                final_exp = int(mission['reward']['experience'] * multiplier)
                final_crypto = mission['reward']['crypto'] * multiplier
                
                # 完了済みリストに移動
                self.missions['completed'].append(mission)
                
                print(f"🎉 ミッション完了: {mission['name']}!")
                if multiplier > 1.0:
                    print(f"   🌪️ 世界が騒がしいため、報酬が {multiplier}倍 になりました！")
                print(f"   💎 経験値 +{final_exp}")
                print(f"   💰 Crypto +{final_crypto:.6f} XMR")
                
                if self.game_engine:
                    self.game_engine.add_experience(final_exp)
                    # self.game_engine.add_crypto(final_crypto) # If wallet handles it
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