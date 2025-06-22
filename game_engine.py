#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ゲームエンジンモジュール
日付・行動・称号管理の中心的な処理を担当
"""

import json
import os
from pathlib import Path
import datetime
from typing import Dict, List, Optional
from audio_manager import AudioManager
from reality_connector import RealityConnector

class GameEngine:
    def __init__(self, data_dir: Path, assets_dir: Path, save_dir: Path):
        self.data_dir = data_dir
        self.assets_dir = assets_dir
        self.save_dir = save_dir
        
        # ゲーム状態ファイル
        self.state_file = Path("state.json")
        self.wallet_file = Path("wallet.json")
        
        # 経験値とCryptoの初期化
        self.experience = 0
        self.crypto = 0.0
        
        # 音声管理システムの初期化
        self.audio_manager = AudioManager(data_dir)
        
        # 現実連動システムの初期化
        self.reality_connector = RealityConnector(data_dir)
        
        # 初期化
        self.load_state()
        self.load_wallet()
        self.initialize_titles()
        
        # BGM開始（ファイルがある場合のみ）
        if self.audio_manager.bgm_files:
            self.audio_manager.play_bgm()
        
        # 現実連動監視の開始
        self.reality_connector.start_monitoring()
    
    def load_state(self):
        """ゲーム状態の読み込み"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                print(f"❌ ゲーム状態の読み込みに失敗: {e}")
                self.audio_manager.play_effect('error')
                self.create_default_state()
        else:
            self.create_default_state()
    
    def create_default_state(self):
        """デフォルトのゲーム状態を作成"""
        self.state = {
            "current_day": 1,
            "actions_remaining": 3,
            "total_actions": 0,
            "titles": [],
            "story_progress": 0,
            "last_action_date": datetime.datetime.now().isoformat(),
            "game_start_date": datetime.datetime.now().isoformat(),
            "achievements": [],
            "quests": [],
            "energy_balance": 0.0
        }
        self.save_state()
    
    def save_state(self):
        """ゲーム状態の保存"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ゲーム状態の保存に失敗: {e}")
            self.audio_manager.play_effect('error')
    
    def load_wallet(self):
        """ウォレット情報の読み込み"""
        if self.wallet_file.exists():
            try:
                with open(self.wallet_file, 'r', encoding='utf-8') as f:
                    self.wallet = json.load(f)
            except Exception as e:
                print(f"❌ ウォレット情報の読み込みに失敗: {e}")
                self.audio_manager.play_effect('error')
                self.create_default_wallet()
        else:
            self.create_default_wallet()
    
    def create_default_wallet(self):
        """デフォルトのウォレット情報を作成"""
        self.wallet = {
            "crypto_balance": 0.0,           # 日次Crypto残高
            "total_crypto_balance": 0.0,     # 累積Crypto残高
            "energy_consumed": 0.0,          # 日次消費電力
            "total_energy_consumed": 0.0,    # 累積消費電力
            "energy_generated": 0.0,         # 日次発電量
            "total_energy_generated": 0.0,   # 累積発電量
            "mining_history": [],
            "cea_calculations": [],
            "plant_designs": [],
            "optics_observations": [],
            "total_mining_time": 0,
            "total_cea_time": 0,
            "total_plant_time": 0,
            "total_optics_time": 0
        }
        self.save_wallet()
    
    def save_wallet(self):
        """ウォレット情報の保存"""
        try:
            with open(self.wallet_file, 'w', encoding='utf-8') as f:
                json.dump(self.wallet, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ウォレット情報の保存に失敗: {e}")
            self.audio_manager.play_effect('error')
    
    def initialize_titles(self):
        """称号システムの初期化"""
        titles_file = self.assets_dir / "titles.json"
        
        if not titles_file.exists():
            default_titles = {
                "titles": [
                    {
                        "id": "first_mining",
                        "name": "電力の芽生え",
                        "description": "初めてマイニングを実行した",
                        "condition": "mining_count >= 1",
                        "category": "mining"
                    },
                    {
                        "id": "crypto_master",
                        "name": "クリプト仙人",
                        "description": "1.0 XMRを獲得した",
                        "condition": "crypto_balance >= 1.0",
                        "category": "mining"
                    },
                    {
                        "id": "rocket_scientist",
                        "name": "重力を操る者",
                        "description": "CEA計算を10回実行した",
                        "condition": "cea_count >= 10",
                        "category": "cea"
                    },
                    {
                        "id": "energy_wizard",
                        "name": "エネルギー魔術師",
                        "description": "発電所を5基設計した",
                        "condition": "plant_count >= 5",
                        "category": "plant"
                    },
                    {
                        "id": "solar_master",
                        "name": "太陽の使い手",
                        "description": "太陽光発電所を3基設計した",
                        "condition": "solar_plant_count >= 3",
                        "category": "plant"
                    },
                    {
                        "id": "wind_master",
                        "name": "風の使い手",
                        "description": "風力発電所を2基設計した",
                        "condition": "wind_plant_count >= 2",
                        "category": "plant"
                    },
                    {
                        "id": "optics_observer",
                        "name": "星の観測者",
                        "description": "天体観測を5回実行した",
                        "condition": "optics_count >= 5",
                        "category": "optics"
                    },
                    {
                        "id": "energy_self_sufficient",
                        "name": "エネルギー自給自足",
                        "description": "発電量が消費量を上回った",
                        "condition": "energy_generated > energy_consumed",
                        "category": "energy"
                    },
                    {
                        "id": "persistent_miner",
                        "name": "不屈のマイナー",
                        "description": "マイニングを100時間実行した",
                        "condition": "total_mining_time >= 100",
                        "category": "mining"
                    },
                    {
                        "id": "master_engineer",
                        "name": "マスターエンジニア",
                        "description": "全ての分野で称号を獲得した",
                        "condition": "all_categories_master",
                        "category": "master"
                    }
                ]
            }
            
            try:
                with open(titles_file, 'w', encoding='utf-8') as f:
                    json.dump(default_titles, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ 称号ファイルの作成に失敗: {e}")
    
    def check_titles(self) -> List[Dict]:
        """称号のチェックと付与"""
        titles_file = self.assets_dir / "titles.json"
        
        if not titles_file.exists():
            return []
        
        try:
            with open(titles_file, 'r', encoding='utf-8') as f:
                titles_data = json.load(f)
        except Exception as e:
            print(f"❌ 称号ファイルの読み込みに失敗: {e}")
            self.audio_manager.play_effect('error')
            return []
        
        stats = self.calculate_stats()
        new_titles = []
        
        for title in titles_data.get('titles', []):
            title_id = title.get('id')
            
            # 既に獲得済みかチェック
            if title_id in self.state['titles']:
                continue
            
            # 条件をチェック
            if self.check_title_condition(title, stats):
                # 称号獲得時の詳細情報を追加
                title_info = {
                    'id': title_id,
                    'name': title['name'],
                    'description': title['description'],
                    'category': title.get('category', 'general'),
                    'earned_date': datetime.datetime.now().isoformat(),
                    'earned_day': self.state['current_day'],
                    'stats_at_earning': stats.copy()
                }
                
                # 称号履歴に追加
                if 'title_history' not in self.state:
                    self.state['title_history'] = []
                self.state['title_history'].append(title_info)
                
                # 称号リストに追加
                self.state['titles'].append(title_id)
                new_titles.append(title_info)
                
                # 称号獲得時の効果音と詳細通知
                self.audio_manager.play_effect('title_earned')
                self._show_title_notification(title_info)
        
        if new_titles:
            self.save_state()
            print(f"\n🏆 新しく獲得した称号: {len(new_titles)}個")
        
        return new_titles
    
    def _show_title_notification(self, title_info: Dict):
        """称号獲得通知の表示"""
        print(f"\n" + "="*60)
        print(f"🏆 新しい称号を獲得しました！")
        print(f"   📛 {title_info['name']}")
        print(f"   📝 {title_info['description']}")
        print(f"   🏷️ カテゴリ: {title_info['category']}")
        print(f"   📅 獲得日: {self.state['current_day']}日目")
        print(f"   ⏰ 獲得時刻: {title_info['earned_date'][:19]}")
        print("="*60)
    
    def get_title_history(self) -> List[Dict]:
        """称号獲得履歴を取得"""
        return self.state.get('title_history', [])
    
    def show_title_status(self):
        """称号状況の表示"""
        titles_file = self.assets_dir / "titles.json"
        
        if not titles_file.exists():
            print("❌ 称号ファイルが見つかりません")
            return
        
        try:
            with open(titles_file, 'r', encoding='utf-8') as f:
                titles_data = json.load(f)
        except Exception as e:
            print(f"❌ 称号ファイルの読み込みに失敗: {e}")
            return
        
        stats = self.calculate_stats()
        earned_titles = set(self.state['titles'])
        
        print(f"\n🏆 称号状況 ({self.state['current_day']}日目)")
        print("="*60)
        
        # カテゴリ別に表示
        categories = {}
        for title in titles_data.get('titles', []):
            category = title.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(title)
        
        for category, titles in categories.items():
            print(f"\n📂 {category.upper()} カテゴリ:")
            for title in titles:
                status = "✅" if title['id'] in earned_titles else "⏳"
                print(f"   {status} {title['name']}: {title['description']}")
                
                # 未獲得の場合、進捗状況を表示
                if title['id'] not in earned_titles:
                    progress = self._get_title_progress(title, stats)
                    if progress:
                        print(f"      📊 進捗: {progress}")
        
        # 称号履歴の表示
        history = self.get_title_history()
        if history:
            print(f"\n📜 最近獲得した称号:")
            for title in history[-5:]:  # 最新5個
                print(f"   🏆 {title['name']} ({title['earned_day']}日目)")
    
    def _get_title_progress(self, title: Dict, stats: Dict) -> str:
        """称号の進捗状況を取得"""
        condition = title.get('condition', '')
        
        if condition == "mining_count >= 1":
            current = stats['mining_count']
            return f"{current}/1 回"
        elif condition == "crypto_balance >= 1.0":
            current = stats['crypto_balance']
            return f"{current:.6f}/1.0 XMR"
        elif condition == "cea_count >= 10":
            current = stats['cea_count']
            return f"{current}/10 回"
        elif condition == "plant_count >= 5":
            current = stats['plant_count']
            return f"{current}/5 基"
        elif condition == "solar_plant_count >= 3":
            current = stats['solar_plant_count']
            return f"{current}/3 基"
        elif condition == "wind_plant_count >= 2":
            current = stats['wind_plant_count']
            return f"{current}/2 基"
        elif condition == "optics_count >= 5":
            current = stats['optics_count']
            return f"{current}/5 回"
        elif condition == "total_mining_time >= 100":
            current = stats['total_mining_time']
            return f"{current}/100 時間"
        
        return ""
    
    def calculate_stats(self) -> Dict:
        """現在の統計を計算"""
        mining_count = len(self.wallet['mining_history'])
        cea_count = len(self.wallet['cea_calculations'])
        plant_count = len(self.wallet['plant_designs'])
        optics_count = len(self.wallet['optics_observations'])
        
        # 発電所タイプ別カウント
        solar_plant_count = sum(1 for plant in self.wallet['plant_designs'] 
                              if plant.get('type') == 'solar')
        wind_plant_count = sum(1 for plant in self.wallet['plant_designs'] 
                             if plant.get('type') == 'wind')
        
        # 全カテゴリマスター判定
        all_categories_master = (
            mining_count >= 10 and
            cea_count >= 10 and
            plant_count >= 5 and
            optics_count >= 5
        )
        
        return {
            'mining_count': mining_count,
            'cea_count': cea_count,
            'plant_count': plant_count,
            'optics_count': optics_count,
            'solar_plant_count': solar_plant_count,
            'wind_plant_count': wind_plant_count,
            'crypto_balance': self.wallet['crypto_balance'],
            'energy_consumed': self.wallet['energy_consumed'],
            'energy_generated': self.wallet['energy_generated'],
            'total_mining_time': self.wallet['total_mining_time'],
            'all_categories_master': all_categories_master
        }
    
    def check_title_condition(self, title: Dict, stats: Dict) -> bool:
        """称号条件のチェック"""
        condition = title.get('condition', '')
        
        if condition == "mining_count >= 1":
            return stats['mining_count'] >= 1
        elif condition == "crypto_balance >= 1.0":
            return stats['crypto_balance'] >= 1.0
        elif condition == "cea_count >= 10":
            return stats['cea_count'] >= 10
        elif condition == "plant_count >= 5":
            return stats['plant_count'] >= 5
        elif condition == "solar_plant_count >= 3":
            return stats['solar_plant_count'] >= 3
        elif condition == "wind_plant_count >= 2":
            return stats['wind_plant_count'] >= 2
        elif condition == "optics_count >= 5":
            return stats['optics_count'] >= 5
        elif condition == "energy_generated > energy_consumed":
            return stats['energy_generated'] > stats['energy_consumed']
        elif condition == "total_mining_time >= 100":
            return stats['total_mining_time'] >= 100
        elif condition == "all_categories_master":
            return stats['all_categories_master']
        
        return False
    
    def use_action(self) -> bool:
        """行動回数を消費"""
        if self.state['actions_remaining'] > 0:
            self.state['actions_remaining'] -= 1
            self.state['total_actions'] += 1
            self.save_state()
            # 行動選択時の効果音
            self.audio_manager.play_effect('action_select')
            return True
        return False
    
    def advance_day(self) -> Dict:
        """次の日へ進む"""
        print(f"\n🌅 {self.state['current_day']}日目を終了")
        print("="*50)
        
        # 次の日へ進む時の効果音
        self.audio_manager.play_effect('next_day')
        
        # 今日の振り返り（リセット前）
        today_summary = self.get_today_summary()
        
        # 日付更新
        self.state['current_day'] += 1
        self.state['actions_remaining'] = 3
        self.state['story_progress'] += 1
        
        # 日次リセット
        self._reset_daily_values()
        
        # 称号チェック
        new_titles = self.check_titles()
        
        # ストーリー進行
        story_event = self.get_story_event()
        
        # 状態保存
        self.save_state()
        self.save_wallet()
        
        return {
            'new_day': self.state['current_day'],
            'today_summary': today_summary,
            'new_titles': new_titles,
            'story_event': story_event
        }
    
    def _reset_daily_values(self):
        """日次でリセットする値をクリア"""
        # 累積データを更新
        self.wallet['total_crypto_balance'] += self.wallet['crypto_balance']
        self.wallet['total_energy_consumed'] += self.wallet['energy_consumed']
        self.wallet['total_energy_generated'] += self.wallet['energy_generated']
        
        # 日次データをリセット
        self.wallet['crypto_balance'] = 0.0
        self.wallet['energy_consumed'] = 0.0
        self.wallet['energy_generated'] = 0.0
        
        print("🔄 日次リセット完了:")
        print(f"   💰 日次Crypto残高: 0.000000 XMR")
        print(f"   ⚡ 日次消費電力: 0.00 kWh")
        print(f"   🌞 日次発電量: 0.00 kWh")
        print(f"   📊 累積Crypto残高: {self.wallet['total_crypto_balance']:.6f} XMR")
        print(f"   📊 累積消費電力: {self.wallet['total_energy_consumed']:.2f} kWh")
        print(f"   📊 累積発電量: {self.wallet['total_energy_generated']:.2f} kWh")
    
    def get_today_summary(self) -> Dict:
        """今日の行動サマリー"""
        today = self.state['current_day']
        
        today_mining = [m for m in self.wallet['mining_history'] if m.get('day') == today]
        today_cea = [c for c in self.wallet['cea_calculations'] if c.get('day') == today]
        today_plant = [p for p in self.wallet['plant_designs'] if p.get('day') == today]
        today_optics = [o for o in self.wallet['optics_observations'] if o.get('day') == today]
        
        total_xmr_earned = sum(m.get('xmr_earned', 0) for m in today_mining)
        total_energy_consumed = sum(m.get('power_consumption', 0) for m in today_mining)
        total_energy_generated = sum(p.get('daily_generation', 0) for p in today_plant)
        
        return {
            'mining_count': len(today_mining),
            'cea_count': len(today_cea),
            'plant_count': len(today_plant),
            'optics_count': len(today_optics),
            'xmr_earned': total_xmr_earned,
            'energy_consumed': total_energy_consumed,
            'energy_generated': total_energy_generated
        }
    
    def get_story_event(self) -> Optional[Dict]:
        """ストーリーイベントの取得"""
        day = self.state['current_day']
        
        # 特定の日数でのイベント
        story_events = {
            1: {
                'title': '冒険の始まり',
                'description': 'あなたの技術者としての旅が始まりました。',
                'type': 'story'
            },
            7: {
                'title': '一週間の成果',
                'description': '一週間の活動を振り返り、新たな目標が見えてきました。',
                'type': 'milestone'
            },
            30: {
                'title': '一ヶ月の軌跡',
                'description': '一ヶ月の活動により、技術者として大きく成長しました。',
                'type': 'milestone'
            },
            100: {
                'title': '百日の挑戦',
                'description': '百日の継続により、真の技術者への道が開けました。',
                'type': 'milestone'
            }
        }
        
        return story_events.get(day)
    
    def get_game_status(self) -> Dict:
        """ゲーム状態の取得"""
        stats = self.calculate_stats()
        
        return {
            'current_day': self.state['current_day'],
            'actions_remaining': self.state['actions_remaining'],
            'total_actions': self.state['total_actions'],
            'story_progress': self.state['story_progress'],
            'titles': self.state['titles'],
            'stats': stats,
            'wallet': self.wallet
        }
    
    def add_mining_result(self, result: Dict):
        """マイニング結果を追加"""
        self.wallet['crypto_balance'] += result.get('xmr_earned', 0)
        self.wallet['energy_consumed'] += result.get('power_consumption', 0)
        self.wallet['mining_history'].append(result)
        self.wallet['total_mining_time'] += result.get('duration_minutes', 0)
        self.save_wallet()
        self.check_titles()
    
    def add_cea_result(self, result: Dict):
        """CEA計算結果を追加"""
        self.wallet['cea_calculations'].append(result)
        self.wallet['total_cea_time'] += 1  # 計算回数
        self.save_wallet()
        self.check_titles()
    
    def add_power_plant_result(self, result: Dict):
        """発電所設計結果を追加"""
        self.wallet['plant_designs'].append(result)
        self.wallet['energy_generated'] += result.get('annual_generation', 0) / 365  # 日間発電量
        self.wallet['total_plant_time'] += 1  # 設計回数
        self.save_wallet()
        self.check_titles()
    
    def add_plant_design(self, result: Dict):
        """発電所設計結果を追加（後方互換性）"""
        self.add_power_plant_result(result)
    
    def add_optics_observation(self, result: Dict):
        """天体観測結果を追加"""
        self.wallet['optics_observations'].append(result)
        self.wallet['total_optics_time'] += result.get('duration_minutes', 0)
        self.save_wallet()
        self.check_titles()
    
    def add_experience(self, experience: int):
        """経験値を追加"""
        # 現在の実装では経験値システムは簡易版
        # 将来的にはレベルシステムなどに拡張可能
        if not hasattr(self, 'experience'):
            self.experience = 0
        
        self.experience += experience
        print(f"💎 経験値 +{experience} 獲得! (総経験値: {self.experience})")
        
        # 経験値獲得時の効果音
        self.audio_manager.play_effect('action_select')
    
    def add_crypto(self, amount: float):
        """Cryptoを追加"""
        self.wallet['crypto_balance'] += amount
        self.crypto += amount
        self.save_wallet()
        print(f"💰 Crypto +{amount:.6f} XMR 獲得! (残高: {self.wallet['crypto_balance']:.6f} XMR)")
        
        # Crypto獲得時の効果音
        self.audio_manager.play_effect('action_select')
    
    def show_mission_status(self):
        """ミッション状況の表示"""
        print(f"📊 ミッション統計:")
        
        # 基本統計
        print(f"   📅 現在の日: {self.state['current_day']}日目")
        print(f"   ⚡ 残り行動回数: {self.state['actions_remaining']}/3")
        print(f"   💰 日次Crypto残高: {self.wallet['crypto_balance']:.6f} XMR")
        print(f"   ⚡ 日次消費電力: {self.wallet['energy_consumed']:.2f} kWh")
        print(f"   🌞 日次発電量: {self.wallet['energy_generated']:.2f} kWh")
        
        # 累積統計
        print(f"\n📊 累積統計:")
        print(f"   💰 累積Crypto残高: {self.wallet.get('total_crypto_balance', 0):.6f} XMR")
        print(f"   ⚡ 累積消費電力: {self.wallet.get('total_energy_consumed', 0):.2f} kWh")
        print(f"   🌞 累積発電量: {self.wallet.get('total_energy_generated', 0):.2f} kWh")
        
        # 活動統計
        stats = self.calculate_stats()
        print(f"\n📈 活動統計:")
        print(f"   ⛏️ マイニング回数: {stats['mining_count']}回")
        print(f"   🚀 CEA計算回数: {stats['cea_count']}回")
        print(f"   📊 発電監視回数: {stats['plant_count']}回")
        print(f"   🔭 天体観測回数: {stats['optics_count']}回")
        
        # 称号統計
        earned_titles = len(self.state.get('titles', []))
        print(f"\n🏆 称号統計:")
        print(f"   🏆 獲得称号: {earned_titles}個")
        
        # 経験値統計（存在する場合）
        if hasattr(self, 'experience'):
            print(f"   💎 総経験値: {self.experience}")
        
        print(f"\n💡 ヒント:")
        print(f"   • 発電監視・ミッションで発電データを記録するとミッションが進行します")
        print(f"   • ミッションを完了すると経験値とCryptoを獲得できます")
        print(f"   • 日次・週次・実績ミッションがあります") 