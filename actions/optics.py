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
        self.optics_dir = Path(config.get('output_dir', 'data/astronomical_observations'))
        self.optics_dir.mkdir(exist_ok=True)
        
        # 画像保存ディレクトリ
        self.images_dir = self.optics_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # 観測履歴
        self.observation_history = []
        
        # 学習目標
        self.learning_goals = self._initialize_learning_goals()
        
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
                }
            ]
        }
    
    def record_astronomical_observation(self) -> Dict:
        """天体観測を記録"""
        print(f"\n🔭 天体観測記録")
        print("="*40)
        
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
            choice = input(f"選択してください (1-{len(target_categories)}) [1]: ").strip() or "1"
            if choice in target_categories:
                category = target_categories[choice]
            else:
                category = 'planets'
        except:
            category = 'planets'
        
        print(f"\n📊 {category_names[category]}の詳細を入力してください:")
        
        # 基本情報入力
        target_name = input("天体名 (例: 木星、M31、ベガ): ").strip()
        observation_date = input("観測日時 (YYYY-MM-DD HH:MM): ").strip()
        location = input("観測場所: ").strip()
        weather = input("天候 (例: 晴れ、曇り、雨): ").strip()
        
        # 機材情報入力
        print(f"\n🛠️ 使用機材:")
        telescope = input("望遠鏡 (例: 8インチ反射、10cm屈折): ").strip()
        eyepiece = input("アイピース (例: 25mm、10mm): ").strip()
        camera = input("カメラ (例: 一眼レフ、スマホ、なし): ").strip()
        mount = input("架台 (例: 経緯台、赤道儀): ").strip()
        filters = input("フィルター (例: 月面フィルター、光害カット): ").strip()
        
        # 観測条件入力
        print(f"\n🌡️ 観測条件:")
        try:
            temperature = float(input("気温 (°C) [20]: ").strip() or "20")
            humidity = float(input("湿度 (%) [60]: ").strip() or "60")
            seeing = input("シーイング (1-10) [5]: ").strip() or "5"
            transparency = input("透明度 (1-10) [5]: ").strip() or "5"
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            temperature, humidity, seeing, transparency = 20, 60, 5, 5
        
        # 観測結果入力
        print(f"\n📈 観測結果:")
        magnification = input("倍率: ").strip()
        exposure_time = input("露光時間 (秒): ").strip()
        notes = input("観測メモ (見え方、特徴など): ").strip()
        
        # 写真の処理
        photo_path = self._handle_photo_upload()
        
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
            choice = input("選択してください (1-2) [2]: ").strip() or "2"
            
            if choice == "1":
                photo_path = input("写真ファイルのパス: ").strip()
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
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 天体観測学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'planetary': '🪐 惑星観測目標', 
            'deep_sky': '🌌 深宇宙目標',
            'technical': '🛠️ 技術目標',
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
        
        for category in ['basic_goals', 'planetary_goals', 'deep_sky_goals', 'technical_goals']:
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