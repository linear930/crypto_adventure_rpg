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
# 実行場所をスクリプト/実行ファイルのディレクトリに固定
# （exe配布時に相対パスのdata/assetsが正しく参照されるようにする）
import sys
if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)
else:
    os.chdir(Path(__file__).resolve().parent)

from game_engine import GameEngine
from actions.cea import CEALearningSystem
from actions.power_plant import PowerGenerationLearningSystem
from actions.optics import AstronomicalObservationSystem
from actions.power_plant import PowerMissionSystem
from actions.world_observer import WorldObserverSystem
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
        (self.data_dir / "activity_logs").mkdir(exist_ok=True)
        
        # 必要な履歴ファイルを初期化
        self._initialize_history_files()
        
        self.game_engine = GameEngine(self.data_dir, self.assets_dir, self.save_dir)
        
        # 各システムの初期化
        self.cea_system = CEALearningSystem(self.config)
        self.power_system = PowerGenerationLearningSystem(self.config)
        self.optics_system = AstronomicalObservationSystem(self.config)
        self.power_missions = PowerMissionSystem(self.config)
        self.world_observer = WorldObserverSystem(self.config)
        
        # 各システムにGameEngineの参照を設定
        self.cea_system.set_game_engine(self.game_engine)
        self.power_system.set_game_engine(self.game_engine)
        self.optics_system.set_game_engine(self.game_engine)
        self.world_observer.set_game_engine(self.game_engine)
        self.power_missions.set_game_engine(self.game_engine)
        
        # ゲーム状態
        self.current_day = 1
        self.last_action_time = None
        
        # デバッグモード（ゲーム再起動まで有効）
        self.debug_mode = False
        
        # 報酬システム
        self.daily_rewards = {
            'cea_calculation': 0,
            'power_generation': 0,
            'optics_observation': 0
        }
        self.consecutive_days_bonus = 0
        
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
        
        # 履歴データを同期
        self._sync_history_data()
        
        # main.pyの状態をGameEngineと同期
        self.current_day = self.game_engine.state.get('current_day', 1)
        
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
            'last_action_time': datetime.now().isoformat(),
            'save_time': datetime.now().isoformat(),
            'experience': self.game_engine.state.get('experience', 0),
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
            print(f"💎 経験値: {self.game_engine.state.get('experience', 0)}")
            print(f"💰 Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
            
            # デバッグモード表示
            if self.debug_mode:
                print(f"🐛 デバッグモード: 有効")
            
            print()
            
            # 日次ダッシュボードを表示
            self._show_daily_dashboard()
            print()
            
            print("📋 アクション選択:")
            print("   1. 🚀 CEA計算記録・学習")
            print("   2. ⚡ 発電方法記録・学習")
            print("   3. 🔭 天体観測記録・学習")
            print("   4. 🌍 世界観測（News Sensors）")
            print("   5. 🏭 発電所ミッション")
            print("   6. 📊 統計・履歴表示")
            print("   7. 🎯 学習目標確認")
            print("   8. 🎵 BGM変更")
            print("   9. 💾 ゲーム保存")
            print("   10. 📂 セーブデータ読み込み")
            print("   11. 📅 次の日へ進む")
            print("   12. ❌ 終了")
            
            try:
                choice = input(f"\n選択してください (1-12): ").strip()
                
                # デバッグコマンドチェック
                if choice.lower() in ['debug', 'd', 'デバッグ']:
                    self._toggle_debug_mode()
                    continue
                
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
                    self._world_observation_menu()
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
                    self._advance_to_next_day()
                    input("\n🔙 メインメニューに戻るにはEnterを押してください...")
                elif choice == "12":
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
    
    def _toggle_debug_mode(self):
        """デバッグモードの切り替え"""
        if self.debug_mode:
            print("🐛 デバッグモードを無効にしました")
            self.debug_mode = False
        else:
            print("🐛 デバッグモードを有効にしました")
            print("💡 デバッグモードでは:")
            print("   - 行動回数制限が無効になります")
            print("   - 追加のデバッグ情報が表示されます")
            print("   - ゲーム再起動まで有効です")
            self.debug_mode = True
        
        input("\nEnterキーを押して続行...")
    
    def _show_daily_dashboard(self):
        """日次ダッシュボードを表示"""
        print("📊 今日のダッシュボード")
        print("-" * 30)
        
        # 今日の活動状況
        today_activities = self._get_today_activities()
        
        if today_activities:
            print("✅ 今日の活動:")
            for activity in today_activities:
                print(f"   {activity}")
        else:
            print("📝 今日はまだ活動していません")
        
        # 推奨アクション
        print(f"\n🎯 今日の推奨アクション:")
        if not today_activities:
            print("   🚀 新しい推進剤の組み合わせを試してみましょう")
            print("   ⚡ 発電方法の研究を始めましょう")
            print("   🔭 天体観測で新しい発見をしましょう")
        else:
            print("   💪 更なる高みを目指して活動を続けましょう！")
            print("   🎯 学習目標の達成も忘れずに。")
        
        # 連続活動ボーナス
        consecutive_days = self._get_consecutive_active_days()
        if consecutive_days > 1:
            print(f"\n🔥 連続{consecutive_days}日活動中！")
            if consecutive_days >= 7:
                print("   🏆 週間継続ボーナス獲得中！")
            elif consecutive_days >= 3:
                print("   ⭐ 3日連続ボーナス獲得中！")
    
    def _get_today_activities(self) -> List[str]:
        """今日の活動を取得"""
        activities = []
        
        # 今日の日付文字列を取得
        today_str = self._get_date_string(self.current_day)
        
        # 各活動をカウント
        cea_count = self._count_activities_by_date('cea_calculations', today_str)
        power_count = self._count_activities_by_date('plant_designs', today_str)
        optics_count = self._count_activities_by_date('optics_observations', today_str)
        
        if cea_count > 0:
            activities.append(f"🚀 CEA計算: {cea_count}回")
        if power_count > 0:
            activities.append(f"⚡ 発電記録: {power_count}回")
        if optics_count > 0:
            activities.append(f"🔭 天体観測: {optics_count}回")
        
        return activities
    
    def _get_consecutive_active_days(self) -> int:
        """連続活動日数を取得"""
        consecutive_days = 0
        current_day = self.current_day
        
        # 過去の日を遡って連続活動日数を計算
        while current_day > 0:
            activities = self._get_previous_day_activities(current_day)
            if activities:
                consecutive_days += 1
                current_day -= 1
            else:
                break
        
        return consecutive_days
    
    def _cea_menu(self):
        """CEA計算メニュー"""
        print(f"\n🚀 CEA計算記録・学習システム")
        print("="*40)
        print("1. 📝 計算結果を記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 計算履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 🔥 推進剤リストを表示")
        print("6. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-6): ").strip()
            
            if choice == "1":
                result = self.cea_system.record_cea_calculation()
                if result:
                    # 報酬を計算
                    reward = self._get_activity_reward("cea_calculation", result)
                    
                    # 活動をテキストファイルに記録
                    log_details = result.copy()
                    log_details.update(reward)
                    self._record_activity("cea_calculation", log_details)
                    
                    # 履歴をGameEngineに保存
                    self.game_engine.add_cea_result(result)
                    
                    # 報酬を付与
                    self.game_engine.add_experience(reward['total_experience'])
                    self.game_engine.add_crypto(reward['crypto_earned'])
                    
                    # 報酬表示
                    print(f"\n🎁 報酬獲得!")
                    print(f"   💎 基本報酬: +{reward['base_reward']} 経験値")
                    if reward['bonus_reward'] > 0:
                        print(f"   ⭐ 追加報酬: +{reward['bonus_reward']} 経験値")
                    if reward['consecutive_bonus'] > 0:
                        print(f"   🔥 連続活動ボーナス: +{reward['consecutive_bonus']} 経験値")
                    print(f"   💰 Crypto: +{reward['crypto_earned']:.6f} XMR")
                    print(f"   📊 総獲得経験値: {reward['total_experience']}")
                    
                    # 学習目標の完了チェック
                    completed_goals = self.cea_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        print()  # 改行を追加
                        
            elif choice == "2":
                # デバッグ除外: 学習目標確認は行動回数を消費しない
                self.cea_system.show_learning_goals()
            elif choice == "3":
                # デバッグ除外: 履歴表示は行動回数を消費しない
                self.cea_system.show_calculation_history()
            elif choice == "4":
                # デバッグ除外: 統計表示は行動回数を消費しない
                stats = self.cea_system.get_calculation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 CEA計算統計:")
                    print(f"   総計算回数: {stats['total_calculations']}")
                    print(f"   ユニーク推進剤: {stats['unique_propellants']}")
                    print(f"   最高比推力: {stats['max_isp']} s")
                    print(f"   最高圧力: {stats['max_pressure']} bar")
                    print(f"\n🚀 推進剤使用統計:")
                    print(f"   UDMH使用回数: {stats['udmh_usage']}")
                    print(f"   フッ素(F2)使用回数: {stats['fluorine_usage']}")
                    print(f"   高エネルギー酸化剤使用回数: {stats['high_energy_oxidizer_usage']}")
                    print(f"   ヒドラジン族使用回数: {stats['hydrazine_family_usage']}")
                    print(f"   炭化水素燃料使用回数: {stats['hydrocarbon_usage']}")
                    print(f"   高濃度酸化剤使用回数: {stats['concentrated_oxidizer_usage']}")
                    print(f"   危険推進剤使用回数: {stats['dangerous_propellant_usage']}")
                else:
                    print("📝 計算データがありません")
            elif choice == "5":
                # デバッグ除外: 推進剤リスト表示は行動回数を消費しない
                self.cea_system.show_propellant_list()
                input("\nEnterキーを押して続行...")
            elif choice == "6":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _power_menu(self):
        """発電方法メニュー"""
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
                    # 報酬を計算
                    reward = self._get_activity_reward("power_generation", result)
                    
                    # 活動をテキストファイルに記録
                    log_details = result.copy()
                    log_details.update(reward)
                    self._record_activity("power_generation", log_details)
                    
                    # 履歴をGameEngineに保存
                    self.game_engine.add_power_plant_result(result)
                    
                    # 報酬を付与
                    self.game_engine.add_experience(reward['total_experience'])
                    self.game_engine.add_crypto(reward['crypto_earned'])
                    
                    # 報酬表示
                    print(f"\n🎁 報酬獲得!")
                    print(f"   💎 基本報酬: +{reward['base_reward']} 経験値")
                    if reward['bonus_reward'] > 0:
                        print(f"   ⭐ 追加報酬: +{reward['bonus_reward']} 経験値")
                    if reward['consecutive_bonus'] > 0:
                        print(f"   🔥 連続活動ボーナス: +{reward['consecutive_bonus']} 経験値")
                    print(f"   💰 Crypto: +{reward['crypto_earned']:.6f} XMR")
                    print(f"   📊 総獲得経験値: {reward['total_experience']}")
                    
                    # 学習目標の完了チェック
                    completed_goals = self.power_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        print()  # 改行を追加
                        
            elif choice == "2":
                # デバッグ除外: 学習目標確認は行動回数を消費しない
                self.power_system.show_learning_goals()
            elif choice == "3":
                # デバッグ除外: 履歴表示は行動回数を消費しない
                self.power_system.show_generation_history()
            elif choice == "4":
                # デバッグ除外: 統計表示は行動回数を消費しない
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
                # デバッグ除外: ガイド表示は行動回数を消費しない
                self.power_system.show_power_methods_guide()
            elif choice == "6":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    def _optics_menu(self):
        """天体観測メニュー"""
        print(f"\n🔭 天体観測記録・学習システム")
        print("="*40)
        print("1. 📝 観測を記録")
        print("2. 🎯 学習目標を確認")
        print("3. 📚 観測履歴を表示")
        print("4. 📊 統計を表示")
        print("5. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-5): ").strip()
            
            if choice == "1":
                result = self.optics_system.record_observation()
                if result:
                    # 報酬を計算
                    reward = self._get_activity_reward("optics_observation", result)
                    
                    # 活動をテキストファイルに記録
                    log_details = result.copy()
                    log_details.update(reward)
                    self._record_activity("optics_observation", log_details)
                    
                    # 履歴をGameEngineに保存
                    self.game_engine.add_optics_observation(result)
                    
                    # 報酬を付与
                    self.game_engine.add_experience(reward['total_experience'])
                    self.game_engine.add_crypto(reward['crypto_earned'])
                    
                    # 報酬表示
                    print(f"\n🎁 報酬獲得!")
                    print(f"   💎 基本報酬: +{reward['base_reward']} 経験値")
                    if reward['bonus_reward'] > 0:
                        print(f"   ⭐ 追加報酬: +{reward['bonus_reward']} 経験値")
                    if reward['consecutive_bonus'] > 0:
                        print(f"   🔥 連続活動ボーナス: +{reward['consecutive_bonus']} 経験値")
                    print(f"   💰 Crypto: +{reward['crypto_earned']:.6f} XMR")
                    print(f"   📊 総獲得経験値: {reward['total_experience']}")
                    
                    # 学習目標の完了チェック
                    completed_goals = self.optics_system.check_goal_completion()
                    for goal in completed_goals:
                        self.game_engine.add_experience(goal['reward']['experience'])
                        self.game_engine.add_crypto(goal['reward']['crypto'])
                        print(f"🎉 学習目標達成: {goal['name']}!")
                        print(f"   💎 経験値 +{goal['reward']['experience']}")
                        print(f"   💰 Crypto +{goal['reward']['crypto']:.6f} XMR")
                        print()  # 改行を追加
                        
            elif choice == "2":
                # デバッグ除外: 学習目標確認は行動回数を消費しない
                self.optics_system.show_learning_goals()
            elif choice == "3":
                # デバッグ除外: 履歴表示は行動回数を消費しない
                self.optics_system.show_observation_history()
            elif choice == "4":
                # デバッグ除外: 統計表示は行動回数を消費しない
                stats = self.optics_system.get_observation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 天体観測統計:")
                    print(f"   総観測回数: {stats['total_observations']}")
                    print(f"   ユニーク天体: {stats['unique_targets']}")
                    print(f"   カテゴリ数: {stats['unique_categories']}")
                    print(f"   使用機材: {len(stats['equipment_usage'])}種類")
                else:
                    print("📝 観測データがありません")
            elif choice == "5":
                return
            else:
                print("❌ 無効な選択です")
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    

    def _world_observation_menu(self):
        """世界観測メニュー"""
        print(f"\n🌍 世界線観測・エネルギー追跡システム")
        print("="*40)
        print("1. 📡 現在の世界状態を観測・記録する")
        print("2. 📊 観測履歴・レポートを表示する")
        print("3. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-3): ").strip()
            
            if choice == "1":
                self.world_observer.observe_and_record()
            elif choice == "2":
                self.world_observer.display_world_state()
            elif choice == "3":
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
                # デバッグ除外: ミッション一覧は行動回数を消費しない
                self.power_missions.show_missions()
            elif choice == "2":
                # デバッグ除外: ミッション統計は行動回数を消費しない
                self.power_missions.show_mission_statistics()
            elif choice == "3":
                # デバッグ除外: ミッションヒントは行動回数を消費しない
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
        print("5. 🔙 戻る")
        
        try:
            choice = input("選択してください (1-5): ").strip()
            
            if choice == "1":
                # デバッグ除外: ゲーム統計は行動回数を消費しない
                self._show_game_statistics()
            elif choice == "2":
                # デバッグ除外: CEA統計は行動回数を消費しない
                stats = self.cea_system.get_calculation_statistics()
                if stats['status'] == 'success':
                    print(f"\n📊 CEA計算統計:")
                    print(f"   総計算回数: {stats['total_calculations']}")
                    print(f"   ユニーク推進剤: {stats['unique_propellants']}")
                    print(f"   最高比推力: {stats['max_isp']} s")
                    print(f"   最高圧力: {stats['max_pressure']} bar")
                    print(f"\n🚀 推進剤使用統計:")
                    print(f"   UDMH使用回数: {stats['udmh_usage']}")
                    print(f"   フッ素(F2)使用回数: {stats['fluorine_usage']}")
                    print(f"   高エネルギー酸化剤使用回数: {stats['high_energy_oxidizer_usage']}")
                    print(f"   ヒドラジン族使用回数: {stats['hydrazine_family_usage']}")
                    print(f"   炭化水素燃料使用回数: {stats['hydrocarbon_usage']}")
                    print(f"   高濃度酸化剤使用回数: {stats['concentrated_oxidizer_usage']}")
                    print(f"   危険推進剤使用回数: {stats['dangerous_propellant_usage']}")
                else:
                    print("📝 計算データがありません")
            elif choice == "3":
                # デバッグ除外: 発電統計は行動回数を消費しない
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
                # デバッグ除外: 観測統計は行動回数を消費しない
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
                # デバッグ除外: 学習目標確認は行動回数を消費しない
                self.cea_system.show_learning_goals()
            elif choice == "2":
                # デバッグ除外: 学習目標確認は行動回数を消費しない
                self.power_system.show_learning_goals()
            elif choice == "3":
                # デバッグ除外: 学習目標確認は行動回数を消費しない
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
        print(f"💎 経験値: {self.game_engine.state.get('experience', 0)}")
        print(f"💰 Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        
        # 各システムの統計
        cea_stats = self.cea_system.get_calculation_statistics()
        power_stats = self.power_system.get_generation_statistics()
        optics_stats = self.optics_system.get_observation_statistics()
        
        print(f"\n📊 アクティビティ統計:")
        print(f"   🚀 CEA計算: {cea_stats.get('total_calculations', 0)}回")
        print(f"   ⚡ 発電記録: {power_stats.get('total_records', 0)}回")
        print(f"   🔭 観測記録: {optics_stats.get('total_observations', 0)}回")
    
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
        
        print("✅ ゲーム状態を再読み込みしました")
        print(f"   📅 現在の日: {self.current_day}日目")
        print(f"   💰 Crypto残高: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        print(f"   💎 経験値: {self.game_engine.state.get('experience', 0)}")
        
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
                        # CEAシステムの履歴も同期
                        self.cea_system.calculation_history = cea_data['calculations']
            
            # 発電記録履歴の同期
            power_file = self.data_dir / "power_generation" / "power_generations.json"
            if power_file.exists():
                with open(power_file, 'r', encoding='utf-8') as f:
                    power_data = json.load(f)
                    if 'generations' in power_data:
                        self.game_engine.wallet['plant_designs'] = power_data['generations']
                        # 発電システムの履歴も同期
                        self.power_system.generation_history = power_data['generations']
            
            # 観測記録履歴の同期
            optics_file = self.data_dir / "optics_observations" / "optics_observations.json"
            if optics_file.exists():
                with open(optics_file, 'r', encoding='utf-8') as f:
                    optics_data = json.load(f)
                    if 'observations' in optics_data:
                        self.game_engine.wallet['optics_observations'] = optics_data['observations']
                        # 観測システムの履歴も同期
                        self.optics_system.observation_history = optics_data['observations']
            
            # マイニング履歴の同期
            mining_file = self.data_dir / "mining_activities" / "mining_sessions.json"
            if mining_file.exists():
                with open(mining_file, 'r', encoding='utf-8') as f:
                    mining_data = json.load(f)
                    if 'sessions' in mining_data:
                        self.game_engine.wallet['mining_history'] = mining_data['sessions']
                        # マイニングシステムの履歴も同期
                        self.miner.mining_history = mining_data['sessions']
            
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
            
            print(f"✅ 履歴データを同期しました（総{total_activities}件）")
            
        except Exception as e:
            print(f"⚠️ 履歴データ同期エラー: {e}")
    
    def _show_save_data_info(self):
        """セーブデータ情報を表示"""
        print(f"\n📊 セーブデータ情報")
        print("="*40)
        
        # GameEngineの状態情報
        print("🎮 ゲーム状態:")
        print(f"   📅 現在の日: {self.game_engine.state.get('current_day', 1)}日目")
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
        
        # 各システムの履歴を修復
        try:
            # CEAシステムの履歴修復
            if hasattr(self.cea_system, 'calculation_history'):
                self.cea_system._save_calculation_history()
                print("✅ CEA履歴を修復しました")
            
            # 発電システムの履歴修復
            if hasattr(self.power_system, 'generation_history'):
                self.power_system._save_generation_history()
                print("✅ 発電履歴を修復しました")
            
            # 観測システムの履歴修復
            if hasattr(self.optics_system, 'observation_history'):
                self.optics_system._save_observation_history()
                print("✅ 観測履歴を修復しました")
            
            # マイニングシステムの履歴修復
            if hasattr(self.miner, 'mining_history'):
                self.miner._save_mining_history()
                print("✅ マイニング履歴を修復しました")
                
        except Exception as e:
            print(f"⚠️ システム履歴修復エラー: {e}")
        
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
    
    def _record_activity(self, activity_type: str, details: Dict):
        """活動をテキストファイルに記録"""
        try:
            # 日付ベースのファイル名を作成
            date_str = self._get_date_string(self.current_day)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"activity_log_{date_str}_{timestamp}.txt"
            filepath = self.data_dir / "activity_logs" / filename
            
            # 活動ログを作成
            log_content = self._create_activity_log(activity_type, details, timestamp)
            
            # ファイルに書き込み
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            print(f"📝 活動記録を保存しました: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 活動記録エラー: {e}")
            return False
    
    def _create_activity_log(self, activity_type: str, details: Dict, timestamp: str) -> str:
        """活動ログの内容を作成"""
        log_lines = []
        
        # ヘッダー
        log_lines.append("=" * 60)
        log_lines.append("🚀 Crypto Adventure RPG - 活動記録")
        log_lines.append("=" * 60)
        log_lines.append(f"📅 日付: {self._get_date_string(self.current_day)}")
        log_lines.append(f"⏰ 時刻: {timestamp}")
        log_lines.append(f"🎮 ゲーム日: Day {self.current_day}")
        log_lines.append(f"💎 経験値: {self.game_engine.state.get('experience', 0)}")
        log_lines.append(f"💰 Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        log_lines.append("")
        
        # 活動タイプに応じた詳細
        if activity_type == "cea_calculation":
            log_lines.append("🚀 CEA計算記録")
            log_lines.append("-" * 30)
            log_lines.append(f"燃料: {details.get('fuel', 'N/A')}")
            log_lines.append(f"酸化剤: {details.get('oxidizer', 'N/A')}")
            log_lines.append(f"燃焼室圧力: {details.get('Pc', 'N/A')} bar")
            log_lines.append(f"混合比: {details.get('MR', 'N/A')}")
            log_lines.append(f"比推力（真空）: {details.get('isp_vacuum', 'N/A')} s")
            log_lines.append(f"比推力（海面）: {details.get('isp_sea_level', 'N/A')} s")
            log_lines.append(f"燃焼温度: {details.get('Tc', 'N/A')} K")
            log_lines.append(f"比熱比: {details.get('gamma', 'N/A')}")
            log_lines.append(f"推力係数: {details.get('Cf', 'N/A')}")
            
        elif activity_type == "power_generation":
            log_lines.append("⚡ 発電方法記録")
            log_lines.append("-" * 30)
            log_lines.append(f"発電方法: {details.get('method', 'N/A')}")
            log_lines.append(f"容量: {details.get('capacity', 'N/A')} kW")
            log_lines.append(f"年間発電量: {details.get('annual_generation', 'N/A')} kWh")
            log_lines.append(f"効率: {details.get('efficiency', 'N/A')}%")
            log_lines.append(f"建設コスト: {details.get('construction_cost', 'N/A')} 万円")
            log_lines.append(f"運用コスト: {details.get('operation_cost', 'N/A')} 万円/年")
            
        elif activity_type == "optics_observation":
            log_lines.append("🔭 天体観測記録")
            log_lines.append("-" * 30)
            log_lines.append(f"観測対象: {details.get('target', 'N/A')}")
            log_lines.append(f"観測方法: {details.get('method', 'N/A')}")
            log_lines.append(f"観測時間: {details.get('duration_minutes', 'N/A')} 分")
            log_lines.append(f"使用機材: {details.get('equipment', 'N/A')}")
            log_lines.append(f"観測条件: {details.get('conditions', 'N/A')}")
            log_lines.append(f"発見内容: {details.get('discoveries', 'N/A')}")
            
        elif activity_type == "mining_session":
            log_lines.append("⛏️ マイニングセッション記録")
            log_lines.append("-" * 30)
            log_lines.append(f"マイニングソフト: {details.get('miner_software', 'N/A')}")
            log_lines.append(f"プール: {details.get('pool', 'N/A')}")
            log_lines.append(f"ハッシュレート: {details.get('hashrate', 'N/A')} H/s")
            log_lines.append(f"消費電力: {details.get('power_consumption', 'N/A')} W")
            log_lines.append(f"効率: {details.get('efficiency', 'N/A')} H/s/W")
            log_lines.append(f"獲得XMR: {details.get('xmr_earned', 'N/A')} XMR")
            log_lines.append(f"セッション時間: {details.get('duration_minutes', 'N/A')} 分")
        
        # 報酬情報
        log_lines.append("")
        log_lines.append("🎁 報酬情報")
        log_lines.append("-" * 30)
        log_lines.append(f"基本報酬: {details.get('base_reward', 0)} 経験値")
        log_lines.append(f"追加報酬: {details.get('bonus_reward', 0)} 経験値")
        log_lines.append(f"連続活動ボーナス: {self.consecutive_days_bonus} 経験値")
        log_lines.append(f"総獲得経験値: {details.get('total_experience', 0)}")
        log_lines.append(f"獲得Crypto: {details.get('crypto_earned', 0):.6f} XMR")
        
        # フッター
        log_lines.append("")
        log_lines.append("=" * 60)
        log_lines.append("📝 この記録は自動生成されました")
        log_lines.append("=" * 60)
        
        return "\n".join(log_lines)
    
    def _get_activity_reward(self, activity_type: str, details: Dict) -> Dict:
        """活動に対する報酬を計算"""
        base_rewards = {
            'cea_calculation': 50,
            'power_generation': 40,
            'optics_observation': 30,
            'mining_session': 25
        }
        
        base_reward = base_rewards.get(activity_type, 10)
        bonus_reward = 0
        crypto_earned = 0
        
        # 活動タイプに応じた追加報酬
        if activity_type == "cea_calculation":
            # 高エネルギー推進剤の使用でボーナス
            high_energy_propellants = ['UDMH', 'F2', 'ClF3', 'N2F4']
            if details.get('fuel') in high_energy_propellants or details.get('oxidizer') in high_energy_propellants:
                bonus_reward += 20
                crypto_earned += 0.001
            
            # 高比推力でボーナス
            if details.get('isp_vacuum', 0) > 400:
                bonus_reward += 15
                crypto_earned += 0.0005
                
        elif activity_type == "power_generation":
            # 高効率発電でボーナス
            if details.get('efficiency', 0) > 80:
                bonus_reward += 15
                crypto_earned += 0.0005
                
        elif activity_type == "optics_observation":
            # 長時間観測でボーナス
            if details.get('duration_minutes', 0) > 60:
                bonus_reward += 10
                crypto_earned += 0.0003
                
        elif activity_type == "mining_session":
            # 高効率マイニングでボーナス
            if details.get('efficiency', 0) > 100:
                bonus_reward += 10
                crypto_earned += 0.0002
        
        # 連続活動ボーナス
        consecutive_bonus = self.consecutive_days_bonus
        
        total_experience = base_reward + bonus_reward + consecutive_bonus
        
        return {
            'base_reward': base_reward,
            'bonus_reward': bonus_reward,
            'consecutive_bonus': consecutive_bonus,
            'total_experience': total_experience,
            'crypto_earned': crypto_earned
        }
    
    def _advance_to_next_day(self):
        """次の日へ進む"""
        print(f"\n📅 次の日へ進む")
        print("="*40)
        
        # 現在の状態を表示
        print(f"現在の日: Day {self.current_day}")
        print(f"経験値: {self.game_engine.state.get('experience', 0)}")
        print(f"Crypto: {self.game_engine.wallet['crypto_balance']:.6f} XMR")
        
        # 連続活動ボーナスを計算
        consecutive_days = self._get_consecutive_active_days()
        if consecutive_days > 0:
            self.consecutive_days_bonus = min(consecutive_days * 5, 50)  # 最大50経験値
            print(f"🔥 連続{consecutive_days}日活動ボーナス: +{self.consecutive_days_bonus} 経験値")
        
        # 確認
        confirm = input(f"\n次の日（Day {self.current_day + 1}）に進みますか？ (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', 'はい', '1']:
            try:
                # GameEngineで次の日へ進む
                if self.game_engine.advance_to_next_day():
                    # 状態を同期
                    self.current_day = self.game_engine.state.get('current_day', 1)
                    
                    print(f"✅ Day {self.current_day} に進みました！")
                    print(f"📅 新しい日の始まりです")
                    
                    # 日報の表示
                    self._show_daily_report()
                    
                    # 自動保存
                    self._save_game_state()
                    print("💾 ゲーム状態を自動保存しました")
                    
                else:
                    print("❌ 次の日への進行に失敗しました")
                    
            except Exception as e:
                print(f"❌ エラーが発生しました: {e}")
        else:
            print("🔄 次の日への進行をキャンセルしました")
    
    def _show_daily_report(self):
        """日報を表示"""
        print(f"\n📊 Day {self.current_day} 日報")
        print("-" * 30)
        
        # 前日の統計を表示
        previous_day = self.current_day - 1
        if previous_day > 0:
            print(f"📈 Day {previous_day} の成果:")
            
            # 前日の実際の活動を取得
            previous_activities = self._get_previous_day_activities(previous_day)
            
            if previous_activities:
                print("   📝 前日の活動記録:")
                for activity in previous_activities:
                    print(f"      {activity}")
            else:
                print("   📝 前日は休憩日でした")
        
        # 新しい日の目標
        print(f"\n🎯 Day {self.current_day} の目標:")
        print("   💪 3つの行動を活用して学習を進めましょう")
        print("   🚀 新しい推進剤の組み合わせを試してみましょう")
        print("   ⚡ 発電方法の研究を深めましょう")
        print("   🔭 天体観測で新しい発見をしましょう")
        print("   ⛏️ マイニングでCryptoを稼ぎましょう")
    
    def _get_previous_day_activities(self, day: int) -> List[str]:
        """指定日の実際の活動を取得"""
        activities = []
        
        # 日付文字列を作成（YYYY-MM-DD形式）
        date_str = self._get_date_string(day)
        
        # CEA計算の確認
        cea_count = self._count_activities_by_date('cea_calculations', date_str)
        if cea_count > 0:
            activities.append(f"🚀 CEA計算: {cea_count}回")
        
        # 発電記録の確認
        power_count = self._count_activities_by_date('plant_designs', date_str)
        if power_count > 0:
            activities.append(f"⚡ 発電記録: {power_count}回")
        
        # 天体観測の確認
        optics_count = self._count_activities_by_date('optics_observations', date_str)
        if optics_count > 0:
            activities.append(f"🔭 天体観測: {optics_count}回")
        
        # マイニングの確認
        mining_count = self._count_activities_by_date('mining_history', date_str)
        if mining_count > 0:
            activities.append(f"⛏️ マイニング: {mining_count}セッション")
        
        return activities
    
    def _count_activities_by_date(self, activity_type: str, date_str: str) -> int:
        """指定日の活動回数をカウント"""
        try:
            activities = self.game_engine.wallet.get(activity_type, [])
            count = 0
            
            for activity in activities:
                timestamp = activity.get('timestamp', '')
                if timestamp.startswith(date_str):
                    count += 1
            
            return count
        except Exception as e:
            print(f"❌ 活動カウントエラー: {e}")
            return 0
    
    def _get_date_string(self, day: int) -> str:
        """指定日の日付文字列を取得"""
        try:
            # ゲーム開始日から指定日数後の日付を計算
            game_start = datetime.fromisoformat(self.game_engine.state.get('game_start_date', datetime.now().isoformat()))
            target_date = game_start + timedelta(days=day-1)
            return target_date.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"❌ 日付計算エラー: {e}")
            return datetime.now().strftime('%Y-%m-%d')

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
