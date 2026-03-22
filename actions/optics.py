#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天体観測記録・学習モジュール
実際の天体観測を記録し、写真と機材情報を管理するシステム
"""

import json
import time
import math
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class AstronomicalObservationSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.optics_dir = Path("data/optics_observations")
        self.optics_dir.mkdir(exist_ok=True)
        
        # 画像保存ディレクトリ
        self.images_dir = self.optics_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # 履歴ファイルの初期化
        self.history_file = self.optics_dir / "optics_observations.json"
        self.observation_history = self._load_observation_history()
        
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
                    'id': 'first_observation',
                    'name': '初めての天体観測',
                    'description': '初めて天体観測を記録した',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 100, 'crypto': 0.001},
                    'status': 'locked'
                },
                {
                    'id': 'multiple_targets',
                    'name': '多様な天体観測',
                    'description': '5種類以上の異なる天体を観測',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                }
            ],
            'planetary_goals': [
                {
                    'id': 'planets_observation',
                    'name': '惑星観測マスター',
                    'description': '太陽系の主要惑星を全て観測',
                    'type': 'collection',
                    'target': 8,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'moon_phases',
                    'name': '月相観測',
                    'description': '月の満ち欠けを10回以上観測',
                    'type': 'collection',
                    'target': 10,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'planetary_atmosphere_observer',
                    'name': '惑星の大気観測',
                    'description': '火星や木星の大気変化を3日連続観測',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'lunar_terrain_mapper',
                    'name': '月の地形マップ作成',
                    'description': '月のクレーターを5個以上詳細記録',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                },
                {
                    'id': 'sunspot_diary',
                    'name': '太陽黒点のダイアリー',
                    'description': '黒点観測を7回以上記録',
                    'type': 'collection',
                    'target': 7,
                    'current': 0,
                    'reward': {'experience': 220, 'crypto': 0.0022},
                    'status': 'active'
                },
                {
                    'id': 'earthshine_appreciator',
                    'name': '地球照の鑑賞者',
                    'description': '新月の地球照を1回観測',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 180, 'crypto': 0.0018},
                    'status': 'active'
                }
            ],
            'deep_sky_goals': [
                {
                    'id': 'messier_objects',
                    'name': 'メシエ天体観測',
                    'description': 'メシエ天体を10個以上観測',
                    'type': 'collection',
                    'target': 10,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'galaxy_observation',
                    'name': '銀河観測',
                    'description': '銀河を5個以上観測',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'planetary_nebula_trail',
                    'name': '惑星状星雲の光跡',
                    'description': '5つの惑星状星雲を確認',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 270, 'crypto': 0.0027},
                    'status': 'active'
                },
                {
                    'id': 'galaxy_waltz',
                    'name': '銀河の輪舞',
                    'description': '渦巻銀河を7個観測',
                    'type': 'collection',
                    'target': 7,
                    'current': 0,
                    'reward': {'experience': 320, 'crypto': 0.0032},
                    'status': 'active'
                },
                {
                    'id': 'supernova_flash',
                    'name': '超新星の閃光',
                    'description': '過去10年以内に観測された超新星を1つ追跡',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'galaxy_cluster_explorer',
                    'name': '銀河団の探索者',
                    'description': '3つの銀河団を観測',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 330, 'crypto': 0.0033},
                    'status': 'active'
                },
                {
                    'id': 'white_dwarf_mystery',
                    'name': '白色矮星の謎',
                    'description': '白色矮星を2つ観測・記録',
                    'type': 'collection',
                    'target': 2,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'dark_matter_researcher',
                    'name': '銀河の暗黒物質研究',
                    'description': '関連論文を調査・要約',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                }
            ],
            'stellar_goals': [
                {
                    'id': 'star_dust_poet',
                    'name': '星屑の詩人',
                    'description': '様々な恒星の光度変化を記録せよ',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 150, 'crypto': 0.0015},
                    'status': 'active'
                },
                {
                    'id': 'binary_star_dance',
                    'name': '双子星の舞踏',
                    'description': '二重星系を3種類観測',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 180, 'crypto': 0.0018},
                    'status': 'active'
                },
                {
                    'id': 'constellation_storyteller',
                    'name': '星座の物語紡ぎ',
                    'description': '12星座すべての主要星を観測',
                    'type': 'collection',
                    'target': 12,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'seasonal_constellation_observer',
                    'name': '季節の星座観察',
                    'description': '4季それぞれの代表星座を観測',
                    'type': 'collection',
                    'target': 4,
                    'current': 0,
                    'reward': {'experience': 260, 'crypto': 0.0026},
                    'status': 'active'
                },
                {
                    'id': 'stellar_life_tracker',
                    'name': '恒星の生涯を追う',
                    'description': '異なる進化段階の恒星を3種類観測',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                }
            ],
            'special_events_goals': [
                {
                    'id': 'comet_tracker',
                    'name': '彗星の追跡者',
                    'description': '1シーズンに彗星を2回以上観測',
                    'type': 'collection',
                    'target': 2,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                },
                {
                    'id': 'meteor_shower_witness',
                    'name': '流星雨の証人',
                    'description': '3回の流星群ピーク観測',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'dark_band_explorer',
                    'name': '暗黒帯の探求者',
                    'description': '天の川の暗黒帯を撮影・記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                },
                {
                    'id': 'interplanetary_dust_tracker',
                    'name': '惑星間塵の追跡者',
                    'description': '塵の帯を観測・記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 240, 'crypto': 0.0024},
                    'status': 'active'
                }
            ],
            'technical_goals': [
                {
                    'id': 'long_exposure',
                    'name': '長時間露光',
                    'description': '30分以上の長時間露光を実行',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                },
                {
                    'id': 'equipment_mastery',
                    'name': '機材マスター',
                    'description': '3種類以上の異なる機材を使用',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'lens_polisher',
                    'name': '夜空のレンズ磨き',
                    'description': '機材のレンズを10回クリーニング＆調整',
                    'type': 'collection',
                    'target': 10,
                    'current': 0,
                    'reward': {'experience': 100, 'crypto': 0.001},
                    'status': 'active'
                },
                {
                    'id': 'astrophotographer_dawn',
                    'name': '天体写真家の黎明',
                    'description': '露光時間5分以上の写真を3枚撮影',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 220, 'crypto': 0.0022},
                    'status': 'active'
                },
                {
                    'id': 'spectrum_magician',
                    'name': 'スペクトルの魔術師',
                    'description': '天体のスペクトル分析を3回行う',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                },
                {
                    'id': 'infrared_traveler',
                    'name': '赤外線の旅人',
                    'description': '赤外線望遠鏡で天体を2回観測',
                    'type': 'collection',
                    'target': 2,
                    'current': 0,
                    'reward': {'experience': 220, 'crypto': 0.0022},
                    'status': 'active'
                },
                {
                    'id': 'full_sky_camera_master',
                    'name': '全天周カメラマスター',
                    'description': '全天周写真を3枚撮影',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                }
            ],
            'research_goals': [
                {
                    'id': 'gravity_wave_whisper',
                    'name': '重力波のささやき',
                    'description': '関連ニュースを3回調査し記録',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 150, 'crypto': 0.0015},
                    'status': 'active'
                },
                {
                    'id': 'supermassive_black_hole_shadow',
                    'name': '超巨大ブラックホールの影',
                    'description': '研究論文を1つ読み解き感想を書く',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 180, 'crypto': 0.0018},
                    'status': 'active'
                },
                {
                    'id': 'planetary_exploration_simulator',
                    'name': '惑星探査ミッションシミュレーション',
                    'description': '自作プログラムで惑星探査を模擬実行',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                },
                {
                    'id': 'future_observer_letter',
                    'name': '未来の観測者への手紙',
                    'description': '観測成果をまとめ、未来の観測者に向けて記録を書く',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                }
            ],
            'location_goals': [
                {
                    'id': 'observation_poet',
                    'name': '観測地の詩人',
                    'description': '5箇所以上の異なる観測地で天体観測を行う',
                    'type': 'collection',
                    'target': 5,
                    'current': 0,
                    'reward': {'experience': 280, 'crypto': 0.0028},
                    'status': 'active'
                },
                {
                    'id': 'polar_night_challenger',
                    'name': '極夜の挑戦者',
                    'description': '極夜地域で最低1回観測成功',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                }
            ]
        }
    
    def record_astronomical_observation(self) -> Dict:
        """天体観測を記録"""
        print(f"\n🔭 天体観測記録")
        print("="*40)
        print("💡 入力中に「abort」と入力すると記録を中断できます")
        print("💡 入力中に「back」と入力すると一つ前の入力に戻れます")
        print("-" * 40)
        
        # 観測対象の選択
        print("🌌 観測対象を選択してください:")
        target_categories = {
            '1': 'planets',
            '2': 'moon', 
            '3': 'stars',
            '4': 'galaxies',
            '5': 'nebulae',
            '6': 'clusters',
            '7': 'comets',
            '8': 'other'
        }
        
        category_names = {
            'planets': '惑星',
            'moon': '月',
            'stars': '恒星',
            'galaxies': '銀河',
            'nebulae': '星雲',
            'clusters': '星団',
            'comets': '彗星',
            'other': 'その他'
        }
        
        for key, category in target_categories.items():
            print(f"   {key}. {category_names[category]}")
        
        try:
            choice = input(f"選択してください (1-{len(target_categories)}) [1]: ").strip()
            if choice.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if choice.lower() == "back":
                print("🔄 最初の入力なので戻る場所がありません。記録を中断します。")
                return None
            choice = choice or "1"
            if choice in target_categories:
                category = target_categories[choice]
            else:
                category = 'planets'
        except:
            category = 'planets'
        
        print(f"\n📊 {category_names[category]}の詳細を入力してください:")
        
        # 基本情報入力
        target_name = input("天体名 (例: 木星、M31、ベガ): ").strip()
        if target_name.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        observation_date = input("観測日時 (YYYY-MM-DD HH:MM): ").strip()
        if observation_date.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if observation_date.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            target_name = input("天体名 (例: 木星、M31、ベガ): ").strip()
            if target_name.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        observation_date = input("観測日時 (YYYY-MM-DD HH:MM): ").strip()
        if observation_date.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        location = input("観測場所: ").strip()
        if location.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if location.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            observation_date = input("観測日時 (YYYY-MM-DD HH:MM): ").strip()
            if observation_date.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        location = input("観測場所: ").strip()
        if location.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        weather = input("天候 (例: 晴れ、曇り、雨): ").strip()
        if weather.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if weather.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            location = input("観測場所: ").strip()
            if location.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        weather = input("天候 (例: 晴れ、曇り、雨): ").strip()
        if weather.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # 機材情報入力
        print(f"\n🛠️ 使用機材:")
        telescope = input("望遠鏡 (例: 8インチ反射、10cm屈折): ").strip()
        if telescope.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if telescope.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            weather = input("天候 (例: 晴れ、曇り、雨): ").strip()
            if weather.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        telescope = input("望遠鏡 (例: 8インチ反射、10cm屈折): ").strip()
        if telescope.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        eyepiece = input("アイピース (例: 25mm、10mm): ").strip()
        if eyepiece.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if eyepiece.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            telescope = input("望遠鏡 (例: 8インチ反射、10cm屈折): ").strip()
            if telescope.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        eyepiece = input("アイピース (例: 25mm、10mm): ").strip()
        if eyepiece.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        camera = input("カメラ (例: 一眼レフ、スマホ、なし): ").strip()
        if camera.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if camera.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            eyepiece = input("アイピース (例: 25mm、10mm): ").strip()
            if eyepiece.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        camera = input("カメラ (例: 一眼レフ、スマホ、なし): ").strip()
        if camera.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        mount = input("架台 (例: 経緯台、赤道儀): ").strip()
        if mount.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if mount.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            camera = input("カメラ (例: 一眼レフ、スマホ、なし): ").strip()
            if camera.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        mount = input("架台 (例: 経緯台、赤道儀): ").strip()
        if mount.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        filters = input("フィルター (例: 月面フィルター、光害カット): ").strip()
        if filters.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if filters.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            mount = input("架台 (例: 経緯台、赤道儀): ").strip()
            if mount.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        filters = input("フィルター (例: 月面フィルター、光害カット): ").strip()
        if filters.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # 観測条件入力
        print(f"\n🌡️ 観測条件:")
        try:
            temp_input = input("気温 (°C) [20]: ").strip()
            if temp_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if temp_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                filters = input("フィルター (例: 月面フィルター、光害カット): ").strip()
                if filters.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
            temp_input = input("気温 (°C) [20]: ").strip()
            if temp_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            temperature = float(temp_input or "20")
            
            humidity_input = input("湿度 (%) [60]: ").strip()
            if humidity_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if humidity_input.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                temp_input = input("気温 (°C) [20]: ").strip()
                if temp_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                temperature = float(temp_input or "20")
            humidity_input = input("湿度 (%) [60]: ").strip()
            if humidity_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            humidity = float(humidity_input or "60")
            
            seeing = input("シーイング (1-10) [5]: ").strip()
            if seeing.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if seeing.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                humidity_input = input("湿度 (%) [60]: ").strip()
                if humidity_input.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                humidity = float(humidity_input or "60")
            seeing = input("シーイング (1-10) [5]: ").strip()
            if seeing.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            seeing = seeing or "5"
            
            transparency = input("透明度 (1-10) [5]: ").strip()
            if transparency.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            if transparency.lower() == "back":
                print("🔄 一つ前の入力に戻ります")
                seeing = input("シーイング (1-10) [5]: ").strip()
                if seeing.lower() == "abort":
                    print("❌ 記録を中断しました")
                    return None
                seeing = seeing or "5"
            transparency = input("透明度 (1-10) [5]: ").strip()
            if transparency.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            transparency = transparency or "5"
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            temperature, humidity, seeing, transparency = 20, 60, 5, 5
        
        # 観測結果入力
        print(f"\n📈 観測結果:")
        magnification = input("倍率: ").strip()
        if magnification.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if magnification.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            transparency = input("透明度 (1-10) [5]: ").strip()
            if transparency.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            transparency = transparency or "5"
        magnification = input("倍率: ").strip()
        if magnification.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        exposure_time = input("露光時間 (秒): ").strip()
        if exposure_time.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if exposure_time.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            magnification = input("倍率: ").strip()
            if magnification.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        exposure_time = input("露光時間 (秒): ").strip()
        if exposure_time.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        notes = input("観測メモ (見え方、特徴など): ").strip()
        if notes.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        if notes.lower() == "back":
            print("🔄 一つ前の入力に戻ります")
            exposure_time = input("露光時間 (秒): ").strip()
            if exposure_time.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
        notes = input("観測メモ (見え方、特徴など): ").strip()
        if notes.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # 写真の処理
        photo_path = self._handle_photo_upload()
        if photo_path is None:  # abortが入力された場合
            print("❌ 記録を中断しました")
            return None
        
        # 結果をまとめる
        result = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'category_name': category_names[category],
            'target_name': target_name,
            'observation_date': observation_date,
            'location': location,
            'weather': weather,
            'equipment': {
                'telescope': telescope,
                'eyepiece': eyepiece,
                'camera': camera,
                'mount': mount,
                'filters': filters
            },
            'conditions': {
                'temperature': temperature,
                'humidity': humidity,
                'seeing': seeing,
                'transparency': transparency
            },
            'results': {
                'magnification': magnification,
                'exposure_time': exposure_time,
                'notes': notes
            },
            'photo_path': photo_path,
            'status': 'recorded'
        }
        
        # 履歴に追加
        self.observation_history.append(result)
        
        # 学習目標の進捗を更新
        self._update_learning_progress(result)
        
        # ファイルに保存
        self._save_observation_record(result)
        self._save_observation_history()
        
        print(f"\n✅ 天体観測を記録しました!")
        print(f"   🌌 対象: {target_name}")
        print(f"   📅 日時: {observation_date}")
        print(f"   📍 場所: {location}")
        print(f"   🔭 望遠鏡: {telescope}")
        if photo_path:
            print(f"   📸 写真: {photo_path}")
        
        return result
    
    def _handle_photo_upload(self) -> str:
        """写真のアップロード処理"""
        print(f"\n📸 写真の処理:")
        print("1. 写真ファイルをアップロード")
        print("2. 写真なしで記録")
        
        try:
            choice = input("選択してください (1-2) [2]: ").strip()
            if choice.lower() == "abort":
                return None
            choice = choice or "2"
            
            if choice == "1":
                photo_path = input("写真ファイルのパス: ").strip()
                if photo_path.lower() == "abort":
                    return None
                if photo_path and Path(photo_path).exists():
                    # 写真をコピー
                    timestamp = int(time.time())
                    filename = f"observation_{timestamp}.jpg"
                    dest_path = self.images_dir / filename
                    
                    try:
                        shutil.copy2(photo_path, dest_path)
                        print(f"✅ 写真をコピーしました: {dest_path}")
                        return str(dest_path)
                    except Exception as e:
                        print(f"❌ 写真コピーエラー: {e}")
                        return ""
                else:
                    print("❌ ファイルが見つかりません")
                    return ""
            else:
                return ""
                
        except Exception as e:
            print(f"❌ 写真処理エラー: {e}")
            return ""
    
    def _update_learning_progress(self, result: Dict):
        """学習目標の進捗を更新"""
        category = result['category']
        target_name = result['target_name']
        
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_observation':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'multiple_targets':
                # ユニークな天体をカウント
                unique_targets = set()
                for obs in self.observation_history:
                    unique_targets.add(obs['target_name'])
                goal['current'] = len(unique_targets)
        
        # 惑星観測目標の更新
        for goal in self.learning_goals['planetary_goals']:
            if goal['id'] == 'planets_observation' and category == 'planets':
                # 主要惑星のリスト
                planets = ['水星', '金星', '地球', '火星', '木星', '土星', '天王星', '海王星']
                if target_name in planets:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'moon_phases' and category == 'moon':
                goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 深宇宙目標の更新
        for goal in self.learning_goals['deep_sky_goals']:
            if goal['id'] == 'messier_objects' and target_name.startswith('M'):
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'galaxy_observation' and category == 'galaxies':
                goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 技術目標の更新
        for goal in self.learning_goals['technical_goals']:
            if goal['id'] == 'long_exposure':
                exposure_time = result['results']['exposure_time']
                try:
                    if exposure_time and float(exposure_time) >= 30:
                        goal['current'] = 1
                except:
                    pass
            elif goal['id'] == 'equipment_mastery':
                # ユニークな機材をカウント
                unique_equipment = set()
                for obs in self.observation_history:
                    if obs['equipment']['telescope']:
                        unique_equipment.add(obs['equipment']['telescope'])
                    if obs['equipment']['camera']:
                        unique_equipment.add(obs['equipment']['camera'])
                goal['current'] = len(unique_equipment)
            elif goal['id'] == 'lens_polisher' and 'レンズ' in result['results']['notes']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'astrophotographer_dawn':
                # 露光時間5分以上の写真
                exposure_time = result['results']['exposure_time']
                try:
                    if exposure_time and float(exposure_time) >= 300:  # 5分 = 300秒
                        goal['current'] = min(goal['current'] + 1, goal['target'])
                except:
                    pass
            elif goal['id'] == 'spectrum_magician' and 'スペクトル' in result['results']['notes']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'infrared_traveler' and '赤外線' in result['equipment']['filters']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'full_sky_camera_master' and result['photo_path']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 恒星観測目標の更新
        for goal in self.learning_goals['stellar_goals']:
            if goal['id'] == 'star_dust_poet' and category == 'stars':
                # 恒星の光度変化記録
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'binary_star_dance' and '二重星' in target_name:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'constellation_storyteller' and category == 'stars':
                # 星座の主要星をカウント
                zodiac_constellations = ['おひつじ座', 'おうし座', 'ふたご座', 'かに座', 'しし座', 'おとめ座', 
                                       'てんびん座', 'さそり座', 'いて座', 'やぎ座', 'みずがめ座', 'うお座']
                if any(const in target_name for const in zodiac_constellations):
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'seasonal_constellation_observer' and category == 'stars':
                # 季節の星座をカウント（簡易版）
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'stellar_life_tracker' and category == 'stars':
                goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 特殊事件目標の更新
        for goal in self.learning_goals['special_events_goals']:
            if goal['id'] == 'comet_tracker' and category == 'comets':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'meteor_shower_witness' and '流星' in target_name:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'dark_band_explorer' and '暗黒帯' in result['results']['notes']:
                goal['current'] = 1
            elif goal['id'] == 'interplanetary_dust_tracker' and '塵' in result['results']['notes']:
                goal['current'] = 1
        
        # 惑星観測目標の更新（新しく追加された目標）
        for goal in self.learning_goals['planetary_goals']:
            if goal['id'] == 'planetary_atmosphere_observer' and category == 'planets':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'lunar_terrain_mapper' and category == 'moon':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'sunspot_diary' and '黒点' in result['results']['notes']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'earthshine_appreciator' and '地球照' in result['results']['notes']:
                goal['current'] = 1
        
        # 深宇宙目標の更新（新しく追加された目標）
        for goal in self.learning_goals['deep_sky_goals']:
            if goal['id'] == 'planetary_nebula_trail' and category == 'nebulae':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'galaxy_waltz' and category == 'galaxies':
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'supernova_flash' and '超新星' in target_name:
                goal['current'] = 1
            elif goal['id'] == 'galaxy_cluster_explorer' and '銀河団' in target_name:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'white_dwarf_mystery' and '白色矮星' in target_name:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'dark_matter_researcher' and '暗黒物質' in result['results']['notes']:
                goal['current'] = 1
        
        # 研究目標の更新
        for goal in self.learning_goals['research_goals']:
            if goal['id'] == 'gravity_wave_whisper' and '重力波' in result['results']['notes']:
                goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'supermassive_black_hole_shadow' and '超巨大ブラックホール' in result['results']['notes']:
                goal['current'] = 1
            elif goal['id'] == 'planetary_exploration_simulator' and '自作プログラム' in result['results']['notes']:
                goal['current'] = 1
            elif goal['id'] == 'future_observer_letter' and '観測成果' in result['results']['notes']:
                goal['current'] = 1
        
        # 観測地目標の更新
        for goal in self.learning_goals['location_goals']:
            if goal['id'] == 'observation_poet':
                # ユニークな観測地をカウント
                unique_locations = set()
                for obs in self.observation_history:
                    unique_locations.add(obs['location'])
                goal['current'] = len(unique_locations)
            elif goal['id'] == 'polar_night_challenger' and '極夜' in result['results']['notes']:
                goal['current'] = 1
    
    def _load_observation_history(self) -> List[Dict]:
        """観測履歴を読み込み"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('observations', [])
            except Exception as e:
                print(f"⚠️ 観測履歴読み込みエラー: {e}")
        return []
    
    def _save_observation_history(self):
        """観測履歴をファイルに保存"""
        try:
            data = {'observations': self.observation_history}
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 観測履歴保存エラー: {e}")
    
    def _save_observation_record(self, result: Dict):
        """観測記録をファイルに保存"""
        timestamp = int(time.time())
        filename = f"observation_{timestamp}.json"
        filepath = self.optics_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 観測記録を保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
        
        # GameEngineのウォレットにも保存
        if self.game_engine:
            if 'optics_observations' not in self.game_engine.wallet:
                self.game_engine.wallet['optics_observations'] = []
            self.game_engine.wallet['optics_observations'].append(result)
            self.game_engine.save_wallet()
            print("💾 GameEngineウォレットに保存しました")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 天体観測学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'planetary': '🪐 惑星観測目標', 
            'deep_sky': '🌌 深宇宙目標',
            'technical': '🛠️ 技術目標',
            'stellar': '🌟 恒星観測目標',
            'special_events': '🎉 特殊事件目標',
            'research': '🔍 研究目標',
            'location': '📍 観測地目標',
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
        elif category == "planetary":
            goals = self.learning_goals['planetary_goals']
        elif category == "deep_sky":
            goals = self.learning_goals['deep_sky_goals']
        elif category == "technical":
            goals = self.learning_goals['technical_goals']
        elif category == "stellar":
            goals = self.learning_goals['stellar_goals']
        elif category == "special_events":
            goals = self.learning_goals['special_events_goals']
        elif category == "research":
            goals = self.learning_goals['research_goals']
        elif category == "location":
            goals = self.learning_goals['location_goals']
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
        
        for category in ['basic_goals', 'planetary_goals', 'deep_sky_goals', 'technical_goals', 'stellar_goals', 'special_events_goals', 'research_goals', 'location_goals']:
            for goal in self.learning_goals[category]:
                if goal['status'] == 'active' and goal['current'] >= goal['target']:
                    goal['status'] = 'completed'
                    goal['completion_time'] = datetime.now().isoformat()
                    completed_goals.append(goal)
        
        return completed_goals
    
    def get_observation_statistics(self) -> Dict:
        """観測統計を取得"""
        if not self.observation_history:
            return {'status': 'no_data'}
        
        # 統計計算
        total_observations = len(self.observation_history)
        unique_targets = set()
        unique_categories = set()
        equipment_usage = {}
        
        for obs in self.observation_history:
            unique_targets.add(obs['target_name'])
            unique_categories.add(obs['category'])
            
            # 機材使用統計
            telescope = obs['equipment']['telescope']
            if telescope:
                equipment_usage[telescope] = equipment_usage.get(telescope, 0) + 1
        
        return {
            'status': 'success',
            'total_observations': total_observations,
            'unique_targets': len(unique_targets),
            'unique_categories': len(unique_categories),
            'targets': list(unique_targets),
            'categories': list(unique_categories),
            'equipment_usage': equipment_usage
        }
    
    def show_observation_history(self):
        """観測履歴を表示"""
        print(f"\n📚 観測履歴")
        print("="*50)
        
        if not self.observation_history:
            print("📝 観測履歴がありません")
            return
        
        for i, obs in enumerate(self.observation_history[-5:], 1):  # 最新5件
            print(f"\n{i}. {obs['target_name']} ({obs['category_name']})")
            print(f"   📅 日時: {obs['observation_date']}")
            print(f"   📍 場所: {obs['location']}")
            print(f"   🔭 望遠鏡: {obs['equipment']['telescope']}")
            print(f"   📸 カメラ: {obs['equipment']['camera']}")
            if obs['photo_path']:
                print(f"   🖼️ 写真: あり")
            if obs['results']['notes']:
                print(f"   📝 メモ: {obs['results']['notes'][:50]}...")
    
    def show_equipment_guide(self):
        """機材ガイドを表示"""
        print(f"\n📖 天体観測機材ガイド")
        print("="*50)
        
        equipment_guide = {
            'telescopes': {
                'refractor': {
                    'name': '屈折望遠鏡',
                    'description': 'レンズを使用した望遠鏡',
                    'pros': ['色収差が少ない', 'メンテナンスが簡単', 'シャープな像'],
                    'cons': ['大口径が高価', '重い', '長い鏡筒'],
                    'suitable_for': '月・惑星観測、初心者'
                },
                'reflector': {
                    'name': '反射望遠鏡',
                    'description': 'ミラーを使用した望遠鏡',
                    'pros': ['大口径が安価', '色収差なし', 'コンパクト'],
                    'cons': ['コリメーション必要', '中央遮蔽', 'メンテナンス'],
                    'suitable_for': '深宇宙天体、大口径希望者'
                },
                'catadioptric': {
                    'name': 'カタディオプトリック',
                    'description': 'レンズとミラーの組み合わせ',
                    'pros': ['コンパクト', '万能', '高品質'],
                    'cons': ['高価', '複雑', '重い'],
                    'suitable_for': '写真撮影、中級者以上'
                }
            },
            'mounts': {
                'altazimuth': {
                    'name': '経緯台',
                    'description': '上下左右の動き',
                    'pros': ['簡単', '軽量', '安価'],
                    'cons': ['視野回転', '長時間露光困難'],
                    'suitable_for': '目視観測、初心者'
                },
                'equatorial': {
                    'name': '赤道儀',
                    'description': '地球の自転に追従',
                    'pros': ['視野回転なし', '長時間露光可能', '自動追尾'],
                    'cons': ['複雑', '重い', '高価'],
                    'suitable_for': '写真撮影、上級者'
                }
            }
        }
        
        for category, items in equipment_guide.items():
            print(f"\n🔧 {category.upper()}:")
            for item_id, info in items.items():
                print(f"\n   📡 {info['name']}")
                print(f"      📝 {info['description']}")
                print(f"      ✅ メリット: {', '.join(info['pros'])}")
                print(f"      ❌ デメリット: {', '.join(info['cons'])}")
                print(f"      🎯 適している人: {info['suitable_for']}")

    # ==========================================
    # 高度なシミュレーション・理論システム
    # ==========================================
    def show_theoretical_simulation_menu(self):
        """光学・天文学の理論計算およびシミュレーションメニュー"""
        while True:
            print("\n" + "="*40)
            print("🔬 光学・天文学 理論シミュレーション")
            print("="*40)
            print("1. 望遠鏡の静的性能限界を計算 (レイリー限界・集光力など)")
            print("2. 天体写真の動的 S/N 比シミュレーション (量子効率とノイズ)")
            print("3. ケプラーの第3法則を用いた惑星公転の計算")
            print("0. 戻る")
            
            choice = input("\n選択してください (1-3/0): ").strip()
            
            if choice == "1":
                self._simulate_static_optics()
            elif choice == "2":
                self._simulate_dynamic_snr()
            elif choice == "3":
                self._simulate_kepler()
            elif choice == "0":
                break
            else:
                print("❌ 無効な選択です。")

    def _simulate_static_optics(self):
        print("\n=== 望遠鏡の静的性能限界計算 ===")
        print("光の波動性と口径から、望遠鏡の持つ理論的な性能限界を計算します。")
        
        try:
            D = float(input("🔭 望遠鏡の有効口径 [mm]: "))
            lambda_nm = float(input("🌈 観測波長 [nm] (例: 可視光の緑は 550): ") or "550")
            d_eye = float(input("👁️ 人間の瞳孔径 [mm] (例: 暗順応時は約 7): ") or "7")
        except ValueError:
            print("❌ 無効な入力です。")
            return
            
        if D <= 0 or lambda_nm <= 0 or d_eye <= 0:
            print("❌ 正の値を入れてください。")
            return

        # 1. レイリーの解像限界 (分解能) θ = 1.22 * lambda / D (ラジアン -> 角度秒)
        # ラジアンを秒角に直すため 206265 を掛ける
        theta_rad = 1.22 * (lambda_nm * 1e-9) / (D * 1e-3)
        theta_arcsec = theta_rad * 206265.0
        
        # 2. 集光力 L = (D/d)^2
        light_gathering_power = (D / d_eye)**2
        
        # 3. 限界等級 (極限等級) m = 6.8 + 5 log10(D[cm])
        D_cm = D / 10.0
        limiting_mag = 6.8 + 5.0 * math.log10(D_cm)

        print("\n" + "="*40)
        print("📊 静的性能シミュレーション解析結果")
        print("="*40)
        print(f"📌 [使用方程式]: レイリーの解像限界 (θ = 1.22 * λ / D)")
        print(f"   => 理論分解能: {theta_arcsec:.2f} 秒角")
        print(f"   ※ 注: 光の回折(エアリーディスク)により点光源でも広がりを持つため、これ以上細かい構造は見えません。")
        
        print(f"\n📌 [使用方程式]: 集光力 (L = (D / d_eye)^2)")
        print(f"   => 人間の眼の {light_gathering_power:.1f} 倍の光を集めます")
        
        print(f"\n📌 [使用方程式]: 限界等級 (m = 6.8 + 5 * log10(D[cm]))")
        print(f"   => 肉眼で見える最も暗い星: 約 {limiting_mag:.1f} 等級")
        print("========================================")
        
        memo = input("\n📝 メモ・研究ノート (空白でスキップ): ").strip()
        self._save_simulation_record("理論光学計算", {"theta_arcsec": theta_arcsec, "light_gathering": light_gathering_power, "limiting_mag": limiting_mag}, memo)
        self._grant_rewards(15, "理論光学計算")

    def _simulate_dynamic_snr(self):
        print("\n=== 天体写真の動的 S/N比 シミュレーション ===")
        print("光電効果(光子->電子変換)から生じるシグナルと各種ノイズを用いた、露光時間による画質の時間発展を計算します。")
        
        try:
            S_rate = float(input("✨ 対象天体からの光子到達率 [光子/ピクセル/秒] (例: 5): ") or "5")
            B_rate = float(input("🌌 背景夜空からの光子到達率 [光子/ピクセル/秒] (例: 10): ") or "10")
            QE = float(input("📷 センサーの量子効率 (0.0〜1.0) [0.8]: ") or "0.8")
            dark_current = float(input("🔥 暗電流ノイズ [電子/ピクセル/秒] (例: 0.1): ") or "0.1")
            read_noise = float(input("⚡ 読み出しノイズ [電子/ピクセル] (例: 3.0): ") or "3.0")
            max_time_min = int(input("⏱️ 最大シミュレーション時間 [分] (例: 60): ") or "60")
        except ValueError:
            print("❌ 無効な入力です。")
            return
            
        print("\n⏳ 露光開始！ (10分ごとの S/N 比の推移を表示)")
        print("-" * 60)
        print(f"{'Time(m)':>8} | {'Signal(e-)':>12} | {'Noise(e-)':>12} | {'S/N Ratio':>12} | {'評価':>10}")
        print("-" * 60)

        dt = 60 # 1分 = 60秒
        t_sec = 0
        
        # 光電効果に基づく実際のシグナルと背景ノイズレート
        Signal_rate_e = S_rate * QE
        B_rate_e = B_rate * QE
        
        for m in range(0, max_time_min + 1, 10):
            if m == 0:
                continue
            
            t_sec = m * 60
            
            # シグナル総量: N*t
            Total_Signal = Signal_rate_e * t_sec
            
            # ノイズ分散の和 = ショットノイズ(シグナル+背景) + 暗電流 + リードノイズ^2
            variance = (Signal_rate_e * t_sec) + (B_rate_e * t_sec) + (dark_current * t_sec) + (read_noise**2)
            Total_Noise = math.sqrt(variance)
            
            SNR = Total_Signal / Total_Noise if Total_Noise > 0 else 0
            
            eval_str = "❌"
            if SNR > 100:
                eval_str = "🌟"
            elif SNR > 20:
                eval_str = "🟢"
            elif SNR > 5:
                eval_str = "🟡"
                
            print(f"{m:>8} | {Total_Signal:>12.1f} | {Total_Noise:>12.1f} | {SNR:>12.1f} | {eval_str:>10}")

        print("-" * 60)
        print(f"📌 [使用方程式]: S/N比モデル SNR = (N*·t*QE) / √(N*·t*QE + N_B·t*QE + N_D·t + N_r^2)")
        print(f"   => 時間の平方根に比例して画質が向上する様子が観測されました。")
        print("========================================")
        
        memo = input("\n📝 メモ・研究ノート (空白でスキップ): ").strip()
        self._save_simulation_record("動的S/Nシミュレーション", {"S_rate": S_rate, "QE": QE, "max_time_min": max_time_min}, memo)
        self._grant_rewards(25, "動的S/Nシミュレーション")

    def _simulate_kepler(self):
        print("\n=== ケプラーの第3法則 シミュレーション ===")
        try:
            M_sun = float(input("☀️ 中心星の質量 [太陽質量=1.0]: ") or "1.0")
            a_AU = float(input("🪐 惑星の軌道長半径 [AU=地球と太陽の距離]: ") or "1.0")
        except ValueError:
            print("❌ 無効な入力です。")
            return
            
        # ケプラーの第3法則: T^2 = a^3 / M (※単位系: T[年], a[AU], M[太陽質量])
        T_years = math.sqrt((a_AU**3) / M_sun)
        
        print("\n" + "="*40)
        print(f"📌 [使用方程式]: ケプラーの第3法則 (T^2 ∝ a^3 / M)")
        print(f"   => 惑星の公転周期: {T_years:.3f} 年")
        print("========================================")
        
        memo = input("\n📝 メモ・研究ノート (空白でスキップ): ").strip()
        self._save_simulation_record("ケプラー軌道計算", {"M_sun": M_sun, "a_AU": a_AU, "T_years": T_years}, memo)
        self._grant_rewards(10, "ケプラー軌道計算")

    def _save_simulation_record(self, sim_type, params, memo):
        """ シミュレーション結果をファイルに保存 """
        import time as _time
        from datetime import datetime as _dt
        record = {
            "timestamp": _dt.now().isoformat(),
            "type": sim_type,
            "params": params,
            "memo": memo
        }
        record_file = self.optics_dir / f"sim_{int(_time.time())}.json"
        try:
            import json as _json
            with open(record_file, 'w', encoding='utf-8') as f:
                _json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        # GameEngineにも保存
        if self.game_engine:
            if 'optics_simulations' not in self.game_engine.wallet:
                self.game_engine.wallet['optics_simulations'] = []
            self.game_engine.wallet['optics_simulations'].append(record)
            self.game_engine.save_wallet()

    def _grant_rewards(self, exp, exp_type):
        if self.game_engine:
            if not self.game_engine.use_action():
                print("⚠️ 行動回数が残っていませんが、シミュレーションは完了しました。")
                return
            print(f"\n🎁 【{exp_type}】により経験値を獲得しました: +{exp} EXP")
            self.game_engine.add_experience(exp) 