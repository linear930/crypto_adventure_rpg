#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crypto Adventure RPG - メインファイル
現実連動型CLIゲーム
"""

import json
import time
import random
import os
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
        
        # 各システム用のディレクトリを作成
        (self.data_dir / "cea_calculation").mkdir(exist_ok=True)
        (self.data_dir / "power_generation").mkdir(exist_ok=True)
        (self.data_dir / "optics_observations").mkdir(exist_ok=True)
        (self.data_dir / "mining_activities").mkdir(exist_ok=True)
        
        # 必要な履歴ファイルを初期化
        self._initialize_history_files()
        
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
        
    def _initialize_history_files(self):
        """履歴ファイルを初期化"""
        # CEA計算履歴ファイル
        cea_file = self.data_dir / "cea_calculation" / "cea_calculations.json"
        if not cea_file.exists():
            with open(cea_file, 'w', encoding='utf-8') as f:
                json.dump({"calculations": []}, f, ensure_ascii=False, indent=2)
        
        # 発電記録履歴ファイル
        power_file = self.data_dir / "power_generation" / "power_generations.json"
        if not power_file.exists():
            with open(power_file, 'w', encoding='utf-8') as f:
                json.dump({"generations": []}, f, ensure_ascii=False, indent=2)
        
        # 観測記録履歴ファイル
        optics_file = self.data_dir / "optics_observations" / "optics_observations.json"
        if not optics_file.exists():
            with open(optics_file, 'w', encoding='utf-8') as f:
                json.dump({"observations": []}, f, ensure_ascii=False, indent=2)
        
        # マイニング履歴ファイル
        mining_file = self.data_dir / "mining_activities" / "mining_sessions.json"
        if not mining_file.exists():
            with open(mining_file, 'w', encoding='utf-8') as f:
                json.dump({"sessions": []}, f, ensure_ascii=False, indent=2)
        
    def _load_config(self) -> Dict:
        """設定ファイルを読み込み（非推奨 - ConfigManagerを使用）"""
        return self.config_manager.load_config()
    
    def start_game(self):
        """ゲーム開始"""
        print("🚀 Crypto Adventure RPG へようこそ！")
        print("="*50)
        
        # 設定読み込み
        self.config = self._load_config()
        
        # ゲーム状態読み込み
        self._load_game_state()
        
        # メインメニュー表示
        self._show_main_menu()
        
        # ゲーム終了時に自動保存
        print("\n💾 ゲームを保存中...")
        self._save_game_state()
        print("✅ ゲームを保存しました")
    
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
        # GameEngineの状態を保存（これがメインのセーブデータ）
        self.game_engine.save_state()
        self.game_engine.save_wallet()
        
        # 旧式のセーブファイルも更新（互換性のため）
        save_file = Path("data/game_state.json")
        save_file.parent.mkdir(exist_ok=True)
        
        state = {
            'current_day': self.current_day,
            'actions_remaining': self.actions_remaining,
            'last_action_time': datetime.now().isoformat(),
            'save_time': datetime.now().isoformat(),
            'experience': self.game_engine.experience,
            'crypto_balance': self.game_engine.wallet['crypto_balance'],
            'total_actions': self.game_engine.state.get('total_actions', 0)
        }
        
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ゲーム状態保存エラー: {e}")
    
    def _show_main_menu(self):
        """メインメニューを表示"""
        while True:
            # 画面をクリア（Windows用）
            os.system('cls' if os.name == 'nt' else 'clear')
            
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
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "2":
                    self._power_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "3":
                    self._optics_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "4":
                    self._mining_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "5":
                    self._power_missions_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "6":
                    self._statistics_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "7":
                    self._learning_goals_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "8":
                    self._bgm_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "9":
                    self._save_game_state()
                    print("✅ ゲームを保存しました")
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "10":
                    self._load_game_menu()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "11":
                    print("👋 ゲームを終了します。お疲れ様でした！")
                    break
                else:
                    print("❌ 無効な選択です")
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                    
            except KeyboardInterrupt:
                print("\n👋 ゲームを終了します")
                break
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
                input("\n🔙 メインメニューに戻るにはEnterを押してください...")
    
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
                    # 履歴をGameEngineに保存
                    self.game_engine.add_cea_result(result)
                    
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
                    # 履歴をGameEngineに保存
                    self.game_engine.add_power_plant_result(result)
                    
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
                    # 履歴をGameEngineに保存
                    self.game_engine.add_optics_observation(result)
                    
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
        print("2. ⚙️  マイニング設定")
        print("3. 🚀 マイニング開始")
        print("4. 🛑 マイニング停止")
        print("5. 📊 マイニング状態")
        print("6. 🎯 学習目標を確認")
        print("7. 📚 マイニング履歴を表示")
        print("8. 📈 統計を表示")
        print("9. 📖 マイニングガイド")
        print("10. 🔍 システム互換性チェック")
        print("11. 📦 cpuminer-optインストールガイド")
        print("12. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-12): ").strip()
            
            if choice == "1":
                result = self.miner.record_mining_session()
                if result:
                    # 履歴をGameEngineに保存
                    self.game_engine.add_mining_result(result)
                    
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
                config = self.miner.configure_mining()
                if config:
                    print("✅ マイニング設定を保存しました")
                    
            elif choice == "3":
                if self.miner.start_mining():
                    print("✅ マイニングを開始しました")
                    print("💡 マイニングを停止するには、メニューから「マイニング停止」を選択してください")
                    
            elif choice == "4":
                if self.miner.stop_mining():
                    print("✅ マイニングを停止しました")
                    
            elif choice == "5":
                self.miner.show_mining_status()
                
            elif choice == "6":
                self.miner.show_learning_goals()
                
            elif choice == "7":
                self.miner.show_mining_history()
                
            elif choice == "8":
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
                    
            elif choice == "9":
                self.miner.show_mining_guide()
                
            elif choice == "10":
                compatibility = self.miner.check_system_compatibility()
                print(f"\n🔍 システム互換性チェック:")
                print(f"   OS: {compatibility['os']}")
                print(f"   CPU: {compatibility['cpu_cores']}コア")
                print(f"   RAM: {compatibility['ram_gb']:.1f} GB")
                
                if compatibility['available_miners']:
                    print(f"   ✅ 利用可能なマイニングソフト: {', '.join(compatibility['available_miners'])}")
                else:
                    print(f"   ❌ 利用可能なマイニングソフト: なし")
                    print(f"   📦 インストールが必要です")
                
                print(f"   🎯 マイニングサポート: {'✅ 可能' if compatibility['mining_supported'] else '❌ 不可能'}")
                
            elif choice == "11":
                self.miner.install_cpuminer_guide()
                
            elif choice == "12":
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
                
                # ゲーム状態を自動保存
                self.game_engine.save_state()
                self.game_engine.save_wallet()
                
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
        print("3. 🔍 セーブデータ整合性チェック")
        print("4. 🔧 セーブデータ自動修復")
        print("5. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-5): ").strip()
            
            if choice == "1":
                self._reload_game_state()
            elif choice == "2":
                self._show_save_data_info()
            elif choice == "3":
                self._check_save_data_integrity()
            elif choice == "4":
                self._repair_save_data()
            elif choice == "5":
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
        
        # 履歴データの同期
        self._sync_history_data()
        
        # main.pyの状態をGameEngineと同期
        self.current_day = self.game_engine.state.get('current_day', 1)
        self.actions_remaining = self.game_engine.state.get('actions_remaining', 3)
        
        print("✅ ゲーム状態を再読み込みしました")
        print(f"   📅 現在の日: {self.current_day}日目")
        print(f"   ⚡ 残り行動: {self.actions_remaining}/3")
        print(f"   💰 Crypto残高: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        print(f"   💎 経験値: {self.game_engine.experience}")
        
        # 履歴情報も表示
        cea_count = len(self.game_engine.wallet.get('cea_calculations', []))
        power_count = len(self.game_engine.wallet.get('plant_designs', []))
        optics_count = len(self.game_engine.wallet.get('optics_observations', []))
        mining_count = len(self.game_engine.wallet.get('mining_history', []))
        
        print(f"   📊 履歴: CEA{cea_count}回, 発電{power_count}回, 観測{optics_count}回, マイニング{mining_count}回")
    
    def _sync_history_data(self):
        """履歴データを同期"""
        try:
            # CEA計算履歴の同期
            cea_file = self.data_dir / "cea_calculation" / "cea_calculations.json"
            if cea_file.exists():
                with open(cea_file, 'r', encoding='utf-8') as f:
                    cea_data = json.load(f)
                    if 'calculations' in cea_data:
                        self.game_engine.wallet['cea_calculations'] = cea_data['calculations']
            
            # 発電記録履歴の同期
            power_file = self.data_dir / "power_generation" / "power_generations.json"
            if power_file.exists():
                with open(power_file, 'r', encoding='utf-8') as f:
                    power_data = json.load(f)
                    if 'generations' in power_data:
                        self.game_engine.wallet['plant_designs'] = power_data['generations']
            
            # 観測記録履歴の同期
            optics_file = self.data_dir / "optics_observations" / "optics_observations.json"
            if optics_file.exists():
                with open(optics_file, 'r', encoding='utf-8') as f:
                    optics_data = json.load(f)
                    if 'observations' in optics_data:
                        self.game_engine.wallet['optics_observations'] = optics_data['observations']
            
            # マイニング履歴の同期
            mining_file = self.data_dir / "mining_activities" / "mining_sessions.json"
            if mining_file.exists():
                with open(mining_file, 'r', encoding='utf-8') as f:
                    mining_data = json.load(f)
                    if 'sessions' in mining_data:
                        self.game_engine.wallet['mining_history'] = mining_data['sessions']
            
            # 総行動回数を更新
            total_activities = (
                len(self.game_engine.wallet.get('cea_calculations', [])) +
                len(self.game_engine.wallet.get('plant_designs', [])) +
                len(self.game_engine.wallet.get('optics_observations', [])) +
                len(self.game_engine.wallet.get('mining_history', []))
            )
            self.game_engine.state['total_actions'] = total_activities
            
            # 同期されたデータを保存
            self.game_engine.save_wallet()
            self.game_engine.save_state()
            
        except Exception as e:
            print(f"⚠️ 履歴データ同期エラー: {e}")
    
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
    
    def _check_save_data_integrity(self):
        """セーブデータの整合性をチェック"""
        print(f"\n🔍 セーブデータ整合性チェック")
        print("="*40)
        
        issues = []
        
        # GameEngineの状態チェック
        if not hasattr(self.game_engine, 'state') or not self.game_engine.state:
            issues.append("❌ GameEngineの状態が読み込まれていません")
        
        if not hasattr(self.game_engine, 'wallet') or not self.game_engine.wallet:
            issues.append("❌ GameEngineのウォレットが読み込まれていません")
        
        # 履歴データの整合性チェック
        cea_calculations = self.game_engine.wallet.get('cea_calculations', [])
        plant_designs = self.game_engine.wallet.get('plant_designs', [])
        optics_observations = self.game_engine.wallet.get('optics_observations', [])
        mining_history = self.game_engine.wallet.get('mining_history', [])
        
        total_activities = len(cea_calculations) + len(plant_designs) + len(optics_observations) + len(mining_history)
        total_actions = self.game_engine.state.get('total_actions', 0)
        
        if total_activities != total_actions:
            issues.append(f"⚠️ 行動回数の不整合: 履歴{total_activities}回 vs 記録{total_actions}回")
        
        # 各システムのファイル存在チェック
        cea_file = Path("data/cea_calculation/cea_calculations.json")
        power_file = Path("data/power_generation/power_generations.json")
        optics_file = Path("data/optics_observations/optics_observations.json")
        
        if not cea_file.exists():
            issues.append("⚠️ CEA計算ファイルが見つかりません")
        if not power_file.exists():
            issues.append("⚠️ 発電記録ファイルが見つかりません")
        if not optics_file.exists():
            issues.append("⚠️ 観測記録ファイルが見つかりません")
        
        # 結果表示
        if issues:
            print("🔍 発見された問題:")
            for issue in issues:
                print(f"   {issue}")
            print(f"\n💡 推奨対応:")
            print("   1. セーブデータを再読み込みしてください")
            print("   2. 問題が続く場合は、ゲームを再起動してください")
        else:
            print("✅ セーブデータに問題は見つかりませんでした")
            print(f"   📊 総行動回数: {total_actions}回")
            print(f"   📈 履歴データ: {total_activities}件")
        
        print(f"\n📊 詳細情報:")
        print(f"   🚀 CEA計算: {len(cea_calculations)}回")
        print(f"   ⚡ 発電記録: {len(plant_designs)}回")
        print(f"   🔭 観測記録: {len(optics_observations)}回")
        print(f"   ⛏️ マイニング: {len(mining_history)}回")
    
    def _repair_save_data(self):
        """セーブデータを自動修復"""
        print(f"\n🔧 セーブデータ自動修復")
        print("="*40)
        
        repaired = False
        
        # 必要なファイルを初期化
        self._initialize_history_files()
        print("✅ 履歴ファイルを初期化しました")
        
        # 履歴データを同期
        self._sync_history_data()
        print("✅ 履歴データを同期しました")
        
        # 総行動回数を修正
        total_activities = (
            len(self.game_engine.wallet.get('cea_calculations', [])) +
            len(self.game_engine.wallet.get('plant_designs', [])) +
            len(self.game_engine.wallet.get('optics_observations', [])) +
            len(self.game_engine.wallet.get('mining_history', []))
        )
        
        if self.game_engine.state.get('total_actions', 0) != total_activities:
            self.game_engine.state['total_actions'] = total_activities
            print(f"✅ 総行動回数を修正しました: {total_activities}回")
            repaired = True
        
        # 修復されたデータを保存
        self.game_engine.save_state()
        self.game_engine.save_wallet()
        
        if repaired:
            print("✅ セーブデータの修復が完了しました")
        else:
            print("ℹ️ 修復が必要な問題は見つかりませんでした")
        
        # 修復後の整合性チェック
        print("\n🔍 修復後の整合性チェック:")
        self._check_save_data_integrity()

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
