#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
発電所設計モジュール
再生可能エネルギー発電所の設計とシミュレーション
"""

import json
import os
from pathlib import Path
import math
import random

class PlantAction:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        
    def read_plant_design(self, design_file: str = "sample_plant_design.json"):
        """発電所設計データを読み込む"""
        design_path = self.data_dir / design_file
        
        if not design_path.exists():
            return None
            
        try:
            with open(design_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 発電所設計データの読み込みに失敗: {e}")
            return None
    
    def design_solar_plant(self, capacity_kw: float = 2.5, location: str = "Tokyo"):
        """太陽光発電所の設計"""
        print(f"🌞 太陽光発電所設計中...")
        print(f"   📍 設置場所: {location}")
        print(f"   ⚡ 容量: {capacity_kw} kW")
        
        # 場所に応じた日射量データ（簡易版）
        solar_data = {
            "Tokyo": {"annual_sunshine": 1900, "efficiency_factor": 0.75},
            "Osaka": {"annual_sunshine": 1800, "efficiency_factor": 0.73},
            "Fukuoka": {"annual_sunshine": 2000, "efficiency_factor": 0.77},
            "Sapporo": {"annual_sunshine": 1600, "efficiency_factor": 0.70}
        }
        
        location_data = solar_data.get(location, solar_data["Tokyo"])
        
        # パネル枚数計算（1枚あたり300W想定）
        panel_wattage = 300  # W
        panel_count = int(capacity_kw * 1000 / panel_wattage)
        
        # 設置面積計算（1枚あたり1.6m²想定）
        panel_area = 1.6  # m²
        total_area = panel_count * panel_area
        
        # 年間発電量計算
        annual_generation = (capacity_kw * location_data["annual_sunshine"] * 
                           location_data["efficiency_factor"] * 0.8)  # 損失率20%
        
        # 日間発電量
        daily_generation = annual_generation / 365
        
        # コスト計算（1kWあたり30万円想定）
        cost_per_kw = 300000  # 円
        total_cost = capacity_kw * cost_per_kw
        
        # 投資回収期間計算（電気代1kWhあたり25円想定）
        electricity_price = 25  # 円/kWh
        annual_savings = annual_generation * electricity_price
        payback_years = total_cost / annual_savings if annual_savings > 0 else float('inf')
        
        # CO2削減効果（1kWhあたり0.5kg-CO2削減想定）
        co2_reduction = annual_generation * 0.5
        
        result = {
            "type": "solar",
            "location": location,
            "capacity": capacity_kw,
            "panel_count": panel_count,
            "installation_area": total_area,
            "annual_generation": annual_generation,
            "daily_generation": daily_generation,
            "cost": total_cost,
            "payback_years": payback_years,
            "co2_reduction": co2_reduction,
            "efficiency": location_data["efficiency_factor"],
            "design_date": "2024-01-15"
        }
        
        return result
    
    def design_wind_plant(self, capacity_kw: float = 5.0, location: str = "Coastal"):
        """風力発電所の設計"""
        print(f"💨 風力発電所設計中...")
        print(f"   📍 設置場所: {location}")
        print(f"   ⚡ 容量: {capacity_kw} kW")
        
        # 場所に応じた風況データ（簡易版）
        wind_data = {
            "Coastal": {"average_wind_speed": 6.5, "capacity_factor": 0.25},
            "Mountain": {"average_wind_speed": 5.0, "capacity_factor": 0.20},
            "Urban": {"average_wind_speed": 3.0, "capacity_factor": 0.10}
        }
        
        location_data = wind_data.get(location, wind_data["Coastal"])
        
        # 年間発電量計算
        annual_generation = (capacity_kw * 8760 * location_data["capacity_factor"])
        daily_generation = annual_generation / 365
        
        # コスト計算（1kWあたり50万円想定）
        cost_per_kw = 500000  # 円
        total_cost = capacity_kw * cost_per_kw
        
        # 投資回収期間計算
        electricity_price = 25  # 円/kWh
        annual_savings = annual_generation * electricity_price
        payback_years = total_cost / annual_savings if annual_savings > 0 else float('inf')
        
        # CO2削減効果
        co2_reduction = annual_generation * 0.5
        
        result = {
            "type": "wind",
            "location": location,
            "capacity": capacity_kw,
            "turbine_count": 1,  # 簡易版では1基
            "annual_generation": annual_generation,
            "daily_generation": daily_generation,
            "cost": total_cost,
            "payback_years": payback_years,
            "co2_reduction": co2_reduction,
            "capacity_factor": location_data["capacity_factor"],
            "design_date": "2024-01-15"
        }
        
        return result
    
    def design_hybrid_plant(self, solar_capacity: float = 2.0, wind_capacity: float = 3.0):
        """ハイブリッド発電所の設計"""
        print(f"🔋 ハイブリッド発電所設計中...")
        print(f"   ☀️ 太陽光容量: {solar_capacity} kW")
        print(f"   💨 風力容量: {wind_capacity} kW")
        
        # 各発電所の設計
        solar_result = self.design_solar_plant(solar_capacity, "Tokyo")
        wind_result = self.design_wind_plant(wind_capacity, "Coastal")
        
        if not solar_result or not wind_result:
            return None
        
        # ハイブリッド効果（補完効果）
        hybrid_factor = 1.1  # 10%の効率向上
        
        total_capacity = solar_capacity + wind_capacity
        total_annual_generation = (solar_result["annual_generation"] + 
                                 wind_result["annual_generation"]) * hybrid_factor
        total_daily_generation = total_annual_generation / 365
        total_cost = solar_result["cost"] + wind_result["cost"]
        total_co2_reduction = solar_result["co2_reduction"] + wind_result["co2_reduction"]
        
        # 投資回収期間計算
        electricity_price = 25  # 円/kWh
        annual_savings = total_annual_generation * electricity_price
        payback_years = total_cost / annual_savings if annual_savings > 0 else float('inf')
        
        result = {
            "type": "hybrid",
            "solar_capacity": solar_capacity,
            "wind_capacity": wind_capacity,
            "total_capacity": total_capacity,
            "annual_generation": total_annual_generation,
            "daily_generation": total_daily_generation,
            "cost": total_cost,
            "payback_years": payback_years,
            "co2_reduction": total_co2_reduction,
            "hybrid_factor": hybrid_factor,
            "design_date": "2024-01-15"
        }
        
        return result
    
    def display_plant_results(self, result: dict):
        """発電所設計結果を表示"""
        if not result:
            print("❌ 設計結果がありません")
            return
        
        plant_type = result.get("type", "unknown")
        
        print(f"✅ {plant_type}発電所設計完了!")
        print(f"   🏭 発電所タイプ: {plant_type}")
        
        if plant_type == "solar":
            print(f"   📍 設置場所: {result.get('location', 'N/A')}")
            print(f"   ⚡ 容量: {result.get('capacity', 0):.1f} kW")
            print(f"   🧩 パネル枚数: {result.get('panel_count', 0)}枚")
            print(f"   📐 設置面積: {result.get('installation_area', 0):.1f} m²")
        elif plant_type == "wind":
            print(f"   📍 設置場所: {result.get('location', 'N/A')}")
            print(f"   ⚡ 容量: {result.get('capacity', 0):.1f} kW")
            print(f"   🌀 タービン数: {result.get('turbine_count', 0)}基")
        elif plant_type == "hybrid":
            print(f"   ☀️ 太陽光容量: {result.get('solar_capacity', 0):.1f} kW")
            print(f"   💨 風力容量: {result.get('wind_capacity', 0):.1f} kW")
            print(f"   ⚡ 総容量: {result.get('total_capacity', 0):.1f} kW")
        
        print(f"   🌞 年間発電量: {result.get('annual_generation', 0):.1f} kWh")
        print(f"   📅 日間発電量: {result.get('daily_generation', 0):.1f} kWh")
        print(f"   💰 建設コスト: {result.get('cost', 0):,} 円")
        print(f"   ⏰ 投資回収期間: {result.get('payback_years', 0):.1f} 年")
        print(f"   🌱 CO2削減: {result.get('co2_reduction', 0):.1f} kg-CO2/年")
    
    def save_plant_design(self, result: dict, filename: str = "plant_design_result.json"):
        """発電所設計結果を保存"""
        result_path = self.data_dir / filename
        
        try:
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 発電所設計結果を保存: {result_path}")
        except Exception as e:
            print(f"❌ 発電所設計結果の保存に失敗: {e}")
    
    def get_plant_analysis(self, result: dict):
        """発電所設計の分析と評価"""
        if not result:
            return None
        
        analysis = {
            'efficiency_score': 0,
            'economic_score': 0,
            'environmental_score': 0,
            'comments': [],
            'recommendations': []
        }
        
        # 効率性評価
        plant_type = result.get("type", "")
        if plant_type == "solar":
            efficiency = result.get("efficiency", 0)
            if efficiency > 0.8:
                analysis['efficiency_score'] = 5
                analysis['comments'].append("高効率な太陽光発電所です")
            elif efficiency > 0.7:
                analysis['efficiency_score'] = 4
                analysis['comments'].append("良好な効率の太陽光発電所です")
        elif plant_type == "wind":
            capacity_factor = result.get("capacity_factor", 0)
            if capacity_factor > 0.3:
                analysis['efficiency_score'] = 5
                analysis['comments'].append("優秀な風況の風力発電所です")
            elif capacity_factor > 0.2:
                analysis['efficiency_score'] = 4
                analysis['comments'].append("良好な風況の風力発電所です")
        
        # 経済性評価
        payback_years = result.get("payback_years", float('inf'))
        if payback_years < 5:
            analysis['economic_score'] = 5
            analysis['comments'].append("非常に経済的な発電所です")
        elif payback_years < 10:
            analysis['economic_score'] = 4
            analysis['comments'].append("経済的な発電所です")
        elif payback_years < 15:
            analysis['economic_score'] = 3
            analysis['comments'].append("標準的な経済性です")
        
        # 環境性評価
        co2_reduction = result.get("co2_reduction", 0)
        if co2_reduction > 1000:
            analysis['environmental_score'] = 5
            analysis['comments'].append("大きな環境貢献を果たします")
        elif co2_reduction > 500:
            analysis['environmental_score'] = 4
            analysis['comments'].append("良好な環境貢献を果たします")
        
        # 推奨事項
        if analysis['efficiency_score'] < 3:
            analysis['recommendations'].append("効率向上のための設備改善を検討してください")
        if analysis['economic_score'] < 3:
            analysis['recommendations'].append("経済性向上のための補助金活用を検討してください")
        
        return analysis 