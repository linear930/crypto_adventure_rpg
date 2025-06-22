#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crypto Adventure RPG - メインファイル
現実連動型CLIゲーム
"""

import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from game_engine import GameEngine
from actions.cea import CEALearningSystem
from actions.power_plant import PowerGenerationLearningSystem
from actions.optics import AstronomicalObservationSystem
from actions.mine import MoneroMiningLearningSystem
from actions.power_plant import PowerMissionSystem
from config_manager import ConfigManager

class CryptoAdventureRPG:
    def __init__(self):
        # 設定管理システムの初期化
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # ディレクトリの設定
        self.data_dir = Path("data")
        self.assets_dir = Path("assets")
        self.save_dir = Path("save")
        
        # ディレクトリの作成
        self.data_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.save_dir.mkdir(exist_ok=True)
        
        self.game_engine = GameEngine(self.data_dir, self.assets_dir, self.save_dir)
        
        # 各システムの初期化
        self.cea_system = CEALearningSystem(self.config)
        self.power_system = PowerGenerationLearningSystem(self.config)
        self.optics_system = AstronomicalObservationSystem(self.config)
        self.miner = MoneroMiningLearningSystem(self.config)
        self.power_missions = PowerMissionSystem(self.config)
        
        # ゲーム状態
        self.current_day = 1
        self.actions_remaining = 3
        self.last_action_time = None
        
    def _load_config(self) -> Dict:
        """設定ファイルを読み込み（非推奨 - ConfigManagerを使用）"""
        return self.config_manager.load_config()
    
    def start_game(self):
        """ゲーム開始"""
        game_name = self.config.get('game_name', 'Crypto Adventure RPG')
        version = self.config.get('version', '2.0.0')
        
        print(f"\n🎮 {game_name} v{version}")
        print("="*60)
        print("🌍 現実連動型暗号通貨アドベンチャーゲーム")
        print("💎 実際の暗号通貨マイニング、CEA計算、発電所設計、天体観測で冒険しよう！")
        print("="*60)
        
        # ゲーム状態の読み込み
        self._load_game_state()
        
        # メインメニュー
        self._show_main_menu()
    
    def _load_game_state(self):
        """ゲーム状態を読み込み"""
        # GameEngineの状態を読み込み（これがメインのセーブデータ）
        self.game_engine.load_state()
        self.game_engine.load_wallet()
        
        # main.pyの状態をGameEngineと同期
        self.current_day = self.game_engine.state.get('current_day', 1)
        self.actions_remaining = self.game_engine.state.get('actions_remaining', 3)
        
        # 日付チェック（最終行動日から経過日数を計算）
        last_action_date = self.game_engine.state.get('last_action_date')
        if last_action_date:
            try:
                last_time = datetime.fromisoformat(last_action_date)
                now = datetime.now()
                days_diff = (now - last_time).days
                
                if days_diff >= 1:
                    print(f"📅 {days_diff}日経過しました。新しい日の始まりです！")
                    # 新しい日の処理はGameEngineで行われるため、ここでは表示のみ
            except Exception as e:
                print(f"⚠️ 日付チェックエラー: {e}")
        
        # 旧式のセーブファイル（data/game_state.json）も確認
        save_file = Path("data/game_state.json")
        if save_file.exists():
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    old_state = json.load(f)
                    # 旧式データがあれば、GameEngineの状態を優先
                    print("📂 セーブデータを読み込みました")
            except Exception as e:
                print(f"⚠️ 旧式セーブデータ読み込みエラー: {e}")
        else:
            print("🆕 新しいゲームを開始します")
    
    def _save_game_state(self):
        """ゲーム状態を保存"""
        save_file = Path("data/game_state.json")
        save_file.parent.mkdir(exist_ok=True)
        
        state = {
            'current_day': self.current_day,
            'actions_remaining': self.actions_remaining,
            'last_action_time': datetime.now().isoformat(),
            'save_time': datetime.now().isoformat()
        }
        
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ゲーム状態保存エラー: {e}")
    
    def _show_main_menu(self):
        """メインメニューを表示"""
        while True:
            print(f"\n🏠 メインメニュー (Day {self.current_day})")
            print("="*50)
            print(f"💎 経験値: {self.game_engine.experience}")
            print(f"💰 Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
            print(f"⚡ 残り行動: {self.actions_remaining}/3")
            print()
            
            print("📋 アクション選択:")
            print("   1. 🚀 CEA計算記録・学習")
            print("   2. ⚡ 発電方法記録・学習")
            print("   3. 🔭 天体観測記録・学習")
            print("   4. ⛏️  Moneroマイニング")
            print("   5. 🏭 発電所ミッション")
            print("   6. 📊 統計・履歴表示")
            print("   7. 🎯 学習目標確認")
            print("   8. 🎵 BGM変更")
            print("   9. 💾 ゲーム保存")
            print("   10. 📂 セーブデータ読み込み")
            print("   11. ❌ 終了")
            
            try:
                choice = input(f"\n選択してください (1-11): ").strip()
                
                if choice == "1":
                    self._cea_menu()
                elif choice == "2":
                    self._power_menu()
                elif choice == "3":
                    self._optics_menu()
                elif choice == "4":
                    self._mining_menu()
                elif choice == "5":
                    self._power_missions_menu()
                elif choice == "6":
                    self._statistics_menu()
                elif choice == "7":
                    self._learning_goals_menu()
                elif choice == "8":
                    self._bgm_menu()
                elif choice == "9":
                    self._save_game_state()
                    print("✅ ゲームを保存しました")
                elif choice == "10":
                    self._load_game_menu()
                elif choice == "11":
                    print("👋 ゲームを終了します。お疲れ様でした！")
                    break
                else:
                    print("❌ 無効な選択です")
                    
            except KeyboardInterrupt:
                print("\n👋 ゲームを終了します")
                break
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
    
    def _cea_menu(self):
        """CEA計算メニュー"""
        if self.actions_remaining <= 0:
            print("❌ 今日の行動回数が終了しました")
            return
        
        print(f"\n🚀 CEA計算記録・学習システム")
        print("="*40)
        print("1. 📝 計算結果を記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 計算履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-5): ").strip()
            
            if choice == "1":
                result = self.cea_system.record_cea_calculation()
                if result:
                    self._consume_action()
                    # 学習目標の完了チェック
                    completed_goals = self.cea_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        
            elif choice == "2":
                self.cea_system.show_learning_goals()
            elif choice == "3":
                self.cea_system.show_calculation_history()
            elif choice == "4":
                stats = self.cea_system.get_calculation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 CEA計算統計:")
                    print(f"   総計算回数: {stats['total_calculations']}")
                    print(f"   ユニーク推進剤: {stats['unique_propellants']}")
                    print(f"   最高比推力: {stats['max_isp']} s")
                    print(f"   最高圧力: {stats['max_pressure']} bar")
                else:
                    print("📝 計算データがありません")
            elif choice == "5":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _power_menu(self):
        """発電方法メニュー"""
        if self.actions_remaining <= 0:
            print("❌ 今日の行動回数が終了しました")
            return
        
        print(f"\n⚡ 発電方法記録・学習システム")
        print("="*40)
        print("1. 📝 発電方法を記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 発電履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 📖 発電方法ガイド")
        print("6. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-6): ").strip()
            
            if choice == "1":
                result = self.power_system.record_power_generation()
                if result:
                    self._consume_action()
                    # 学習目標の完了チェック
                    completed_goals = self.power_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        
            elif choice == "2":
                self.power_system.show_learning_goals()
            elif choice == "3":
                self.power_system.show_generation_history()
            elif choice == "4":
                stats = self.power_system.get_generation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 発電統計:")
                    print(f"   総記録数: {stats['total_records']}")
                    print(f"   ユニーク方法: {stats['unique_methods']}")
                    print(f"   総容量: {stats['total_capacity']} kW")
                    print(f"   1日あたり発電量: {stats['total_daily_generation']} kWh")
                else:
                    print("📝 発電データがありません")
            elif choice == "5":
                self.power_system.show_power_methods_guide()
            elif choice == "6":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _optics_menu(self):
        """天体観測メニュー"""
        if self.actions_remaining <= 0:
            print("❌ 今日の行動回数が終了しました")
            return
        
        print(f"\n🔭 天体観測記録・学習システム")
        print("="*40)
        print("1. 📝 観測を記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 観測履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 📖 機材ガイド")
        print("6. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-6): ").strip()
            
            if choice == "1":
                result = self.optics_system.record_astronomical_observation()
                if result:
                    self._consume_action()
                    # 学習目標の完了チェック
                    completed_goals = self.optics_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        
            elif choice == "2":
                self.optics_system.show_learning_goals()
            elif choice == "3":
                self.optics_system.show_observation_history()
            elif choice == "4":
                stats = self.optics_system.get_observation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 観測統計:")
                    print(f"   総観測回数: {stats['total_observations']}")
                    print(f"   ユニーク天体: {stats['unique_targets']}")
                    print(f"   カテゴリ数: {stats['unique_categories']}")
                    print(f"   使用機材: {len(stats['equipment_usage'])}種類")
                else:
                    print("📝 観測データがありません")
            elif choice == "5":
                self.optics_system.show_equipment_guide()
            elif choice == "6":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _mining_menu(self):
        """マイニングメニュー"""
        if self.actions_remaining <= 0:
            print("❌ 今日の行動回数が終了しました")
            return
        
        print(f"\n⛏️  Moneroマイニング記録・学習システム")
        print("="*40)
        print("1. 📝 マイニングセッションを記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 マイニング履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 📖 マイニングガイド")
        print("6. 🔍 システム互換性チェック")
        print("7. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-7): ").strip()
            
            if choice == "1":
                result = self.miner.record_mining_session()
                if result:
                    self._consume_action()
                    # 学習目標の完了チェック
                    completed_goals = self.miner.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        
            elif choice == "2":
                self.miner.show_learning_goals()
            elif choice == "3":
                self.miner.show_mining_history()
            elif choice == "4":
                stats = self.miner.get_mining_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 マイニング統計:")
                    print(f"   総セッション数: {stats['total_sessions']}")
                    print(f"   総シェア数: {stats['total_shares']}")
                    print(f"   平均ハッシュレート: {stats['avg_hashrate']:.0f} H/s")
                    print(f"   平均効率: {stats['avg_efficiency']:.2f} H/s/W")
                    print(f"   使用プール数: {stats['unique_pools']}")
                    print(f"   使用ハードウェア数: {stats['unique_hardware']}")
                else:
                    print("📝 マイニングデータがありません")
            elif choice == "5":
                self.miner.show_mining_guide()
            elif choice == "6":
                self.miner.check_system_compatibility()
            elif choice == "7":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _power_missions_menu(self):
        """発電所ミッションメニュー"""
        print(f"\n🏭 発電所ミッションシステム")
        print("="*40)
        print("1. 📋 ミッション一覧")
        print("2. 📊 ミッション統計")
        print("3. 💡 ミッションヒント")
        print("4. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-4): ").strip()
            
            if choice == "1":
                self.power_missions.show_missions()
            elif choice == "2":
                self.power_missions.show_mission_statistics()
            elif choice == "3":
                self.power_missions.show_mission_hints()
            elif choice == "4":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _statistics_menu(self):
        """統計メニュー"""
        print(f"\n📊 統計・履歴表示")
        print("="*40)
        print("1. 🎮 ゲーム統計")
        print("2. 🚀 CEA統計")
        print("3. ⚡ 発電統計")
        print("4. 🔭 観測統計")
        print("5. ⛏️  マイニング統計")
        print("6. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-6): ").strip()
            
            if choice == "1":
                self._show_game_statistics()
            elif choice == "2":
                stats = self.cea_system.get_calculation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 CEA計算統計:")
                    print(f"   総計算回数: {stats['total_calculations']}")
                    print(f"   ユニーク推進剤: {stats['unique_propellants']}")
                    print(f"   最高比推力: {stats['max_isp']} s")
                    print(f"   最高圧力: {stats['max_pressure']} bar")
                else:
                    print("📝 計算データがありません")
            elif choice == "3":
                stats = self.power_system.get_generation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 発電統計:")
                    print(f"   総記録数: {stats['total_records']}")
                    print(f"   ユニーク方法: {stats['unique_methods']}")
                    print(f"   総容量: {stats['total_capacity']} kW")
                    print(f"   1日あたり発電量: {stats['total_daily_generation']} kWh")
                else:
                    print("📝 発電データがありません")
            elif choice == "4":
                stats = self.optics_system.get_observation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 観測統計:")
                    print(f"   総観測回数: {stats['total_observations']}")
                    print(f"   ユニーク天体: {stats['unique_targets']}")
                    print(f"   カテゴリ数: {stats['unique_categories']}")
                    print(f"   使用機材: {len(stats['equipment_usage'])}種類")
                else:
                    print("📝 観測データがありません")
            elif choice == "5":
                self.miner.show_mining_stats()
            elif choice == "6":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _learning_goals_menu(self):
        """学習目標メニュー"""
        print(f"\n🎯 学習目標確認")
        print("="*40)
        print("1. 🚀 CEA学習目標")
        print("2. ⚡ 発電学習目標")
        print("3. 🔭 観測学習目標")
        print("4. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-4): ").strip()
            
            if choice == "1":
                self.cea_system.show_learning_goals()
            elif choice == "2":
                self.power_system.show_learning_goals()
            elif choice == "3":
                self.optics_system.show_learning_goals()
            elif choice == "4":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _show_game_statistics(self):
        """ゲーム統計を表示"""
        print(f"\n🎮 ゲーム統計")
        print("="*40)
        print(f"📅 現在の日: {self.current_day}")
        print(f"💎 経験値: {self.game_engine.experience}")
        print(f"💰 Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        print(f"⚡ 残り行動: {self.actions_remaining}/3")
        
        # 各システムの統計
        cea_stats = self.cea_system.get_calculation_statistics()
        power_stats = self.power_system.get_generation_statistics()
        optics_stats = self.optics_system.get_observation_statistics()
        
        print(f"\n📊 アクティビティ統計:")
        print(f"   🚀 CEA計算: {cea_stats.get('total_calculations', 0)}回")
        print(f"   ⚡ 発電記録: {power_stats.get('total_records', 0)}回")
        print(f"   🔭 観測記録: {optics_stats.get('total_observations', 0)}回")
    
    def _consume_action(self):
        """行動回数を消費"""
        if self.actions_remaining > 0:
            self.actions_remaining -= 1
            
            # GameEngineの行動回数も更新
            if self.game_engine.use_action():
                # GameEngineの状態と同期
                self.current_day = self.game_engine.state.get('current_day', 1)
                self.actions_remaining = self.game_engine.state.get('actions_remaining', 3)
                print(f"⚡ 行動を実行しました (残り: {self.actions_remaining}/3)")
            else:
                print("❌ 行動回数が不足しています")
        else:
            print("❌ 今日の行動回数が終了しました")
    
    def _bgm_menu(self):
        """BGM変更メニュー"""
        print(f"\n🎵 BGM変更")
        print("="*40)
        
        # 利用可能なBGMファイルを取得
        bgm_files = self.game_engine.audio_manager.bgm_files
        
        if not bgm_files:
            print("📝 BGMファイルが見つかりません")
            return
        
        print("🎼 利用可能なBGM:")
        for i, bgm_file in enumerate(bgm_files, 1):
            # ファイル名から拡張子を除去して表示
            bgm_name = Path(bgm_file).stem
            current_indicator = " ← 現在再生中" if bgm_file == self.game_engine.audio_manager.current_bgm else ""
            print(f"   {i}. {bgm_name}{current_indicator}")
        
        print(f"   {len(bgm_files) + 1}. 🔇 BGM停止")
        print(f"   {len(bgm_files) + 2}. 🔙 戻る")
        
        try:
            choice = input(f"選択してください (1-{len(bgm_files) + 2}): ").strip()
            
            if not choice:
                return
            
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(bgm_files):
                # BGM変更
                selected_bgm = bgm_files[choice_idx]
                self.game_engine.audio_manager.change_bgm(selected_bgm)
                bgm_name = Path(selected_bgm).stem
                print(f"🎵 BGMを変更しました: {bgm_name}")
                
            elif choice_idx == len(bgm_files):
                # BGM停止
                self.game_engine.audio_manager.stop_bgm()
                print("🔇 BGMを停止しました")
                
            elif choice_idx == len(bgm_files) + 1:
                # 戻る
                return
            else:
                print("❌ 無効な選択です")
                
        except ValueError:
            print("❌ 無効な入力です")
        except Exception as e:
            print(f"❌ BGM変更エラー: {e}")
    
    def _load_game_menu(self):
        """セーブデータ読み込みメニュー"""
        print(f"\n📂 セーブデータ読み込み")
        print("="*40)
        print("1. 🔄 現在のセーブデータを再読み込み")
        print("2. 📊 セーブデータ情報を表示")
        print("3. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-3): ").strip()
            
            if choice == "1":
                self._reload_game_state()
            elif choice == "2":
                self._show_save_data_info()
            elif choice == "3":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _reload_game_state(self):
        """ゲーム状態を再読み込み"""
        print("🔄 ゲーム状態を再読み込み中...")
        
        # GameEngineの状態を再読み込み
        self.game_engine.load_state()
        self.game_engine.load_wallet()
        
        # main.pyの状態をGameEngineと同期
        self.current_day = self.game_engine.state.get('current_day', 1)
        self.actions_remaining = self.game_engine.state.get('actions_remaining', 3)
        
        print("✅ ゲーム状態を再読み込みしました")
        print(f"   📅 現在の日: {self.current_day}日目")
        print(f"   ⚡ 残り行動: {self.actions_remaining}/3")
        print(f"   💰 Crypto残高: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        print(f"   💎 経験値: {self.game_engine.experience}")
    
    def _show_save_data_info(self):
        """セーブデータ情報を表示"""
        print(f"\n📊 セーブデータ情報")
        print("="*40)
        
        # GameEngineの状態情報
        print("🎮 ゲーム状態:")
        print(f"   📅 現在の日: {self.game_engine.state.get('current_day', 1)}日目")
        print(f"   ⚡ 残り行動: {self.game_engine.state.get('actions_remaining', 3)}/3")
        print(f"   🏆 獲得称号数: {len(self.game_engine.state.get('titles', []))}")
        print(f"   📈 総行動回数: {self.game_engine.state.get('total_actions', 0)}")
        
        print("\n💰 ウォレット情報:")
        print(f"   💰 Crypto残高: {self.game_engine.wallet.get('crypto_balance', 0):.6f} XMR")
        print(f"   💰 累積Crypto: {self.game_engine.wallet.get('total_crypto_balance', 0):.6f} XMR")
        print(f"   ⚡ 消費電力: {self.game_engine.wallet.get('energy_consumed', 0):.2f} kWh")
        print(f"   ⚡ 発電量: {self.game_engine.wallet.get('energy_generated', 0):.2f} kWh")
        
        print("\n📈 活動履歴:")
        print(f"   ⛏️ マイニング回数: {len(self.game_engine.wallet.get('mining_history', []))}")
        print(f"   🚀 CEA計算回数: {len(self.game_engine.wallet.get('cea_calculations', []))}")
        print(f"   🏭 発電所設計回数: {len(self.game_engine.wallet.get('plant_designs', []))}")
        print(f"   🔭 天体観測回数: {len(self.game_engine.wallet.get('optics_observations', []))}")
        
        # 最終更新日時
        if 'last_action_date' in self.game_engine.state:
            print(f"\n⏰ 最終更新: {self.game_engine.state['last_action_date'][:19]}")
        
        if 'game_start_date' in self.game_engine.state:
            print(f"🎮 ゲーム開始: {self.game_engine.state['game_start_date'][:19]}")

def main():
    """メイン関数"""
    try:
        game = CryptoAdventureRPG()
        game.start_game()
    except KeyboardInterrupt:
        print("\n👋 ゲームを終了します")
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
