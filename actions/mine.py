#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moneroマイニング記録・学習モジュール
実際のマイニング活動を記録し、学習効果を促進するシステム
"""

import json
import time
import math
import subprocess
import platform
import threading
import signal
import os
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class MoneroMiningLearningSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.mining_dir = Path(config.get('output_dir', 'data/mining_activities'))
        self.mining_dir.mkdir(exist_ok=True)
        
        # マイニング履歴
        self.mining_history = []
        
        # 学習目標
        self.learning_goals = self._initialize_learning_goals()
        
        # マイニング設定
        self.mining_config = config.get('mining', {})
        
        # 現在のマイニングプロセス
        self.current_mining_process = None
        self.mining_thread = None
        self.is_mining = False
        self.mining_start_time = None
        self.mining_stats = {
            'hashrate': 0,
            'shares_submitted': 0,
            'accepted_shares': 0,
            'rejected_shares': 0,
            'power_consumption': 0
        }
        
    def _initialize_learning_goals(self) -> Dict:
        """学習目標の初期化"""
        return {
            'basic_goals': [
                {
                    'id': 'first_mining',
                    'name': '初めてのマイニング',
                    'description': '初めてマイニングを記録した',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 100, 'crypto': 0.001},
                    'status': 'locked'
                },
                {
                    'id': 'consistent_mining',
                    'name': '継続マイニング',
                    'description': '7日間連続でマイニングを記録',
                    'type': 'streak',
                    'target': 7,
                    'current': 0,
                    'reward': {'experience': 300, 'crypto': 0.003},
                    'status': 'active'
                }
            ],
            'technical_goals': [
                {
                    'id': 'hashrate_optimization',
                    'name': 'ハッシュレート最適化',
                    'description': 'ハッシュレートを10%以上改善',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 200, 'crypto': 0.002},
                    'status': 'active'
                },
                {
                    'id': 'efficiency_mastery',
                    'name': '効率マスター',
                    'description': '電力効率を最適化したマイニング設定を記録',
                    'type': 'achievement',
                    'target': 1,
                    'current': 0,
                    'reward': {'experience': 250, 'crypto': 0.0025},
                    'status': 'active'
                }
            ],
            'advanced_goals': [
                {
                    'id': 'pool_experience',
                    'name': 'プール経験',
                    'description': '3種類以上の異なるマイニングプールを試行',
                    'type': 'collection',
                    'target': 3,
                    'current': 0,
                    'reward': {'experience': 400, 'crypto': 0.004},
                    'status': 'active'
                },
                {
                    'id': 'hardware_mastery',
                    'name': 'ハードウェアマスター',
                    'description': '異なるハードウェアでマイニングを記録',
                    'type': 'collection',
                    'target': 2,
                    'current': 0,
                    'reward': {'experience': 350, 'crypto': 0.0035},
                    'status': 'active'
                }
            ]
        }
    
    def record_mining_session(self) -> Dict:
        """マイニングセッションを記録"""
        print(f"\n⛏️  Moneroマイニング記録")
        print("="*40)
        print("💡 入力中に「abort」と入力すると記録を中断できます")
        print("-" * 40)
        
        # 基本情報入力
        print("📊 マイニングセッション情報を入力してください:")
        
        session_name = input("セッション名 (例: 朝のマイニング、夜間セッション): ").strip()
        if session_name.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        start_time = input("開始時刻 (YYYY-MM-DD HH:MM): ").strip()
        if start_time.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        end_time = input("終了時刻 (YYYY-MM-DD HH:MM): ").strip()
        if end_time.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # マイニング設定入力
        print(f"\n⚙️ マイニング設定:")
        pool_url = input("プールURL [pool.supportxmr.com:3333]: ").strip()
        if pool_url.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        pool_url = pool_url or "pool.supportxmr.com:3333"
        
        wallet_address = input("ウォレットアドレス: ").strip()
        if wallet_address.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        worker_name = input("ワーカー名 [crypto_adventure_worker]: ").strip()
        if worker_name.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        worker_name = worker_name or "crypto_adventure_worker"
        
        # ハードウェア情報入力
        print(f"\n🖥️ ハードウェア情報:")
        cpu_model = input("CPUモデル: ").strip()
        if cpu_model.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        gpu_model = input("GPUモデル (使用する場合): ").strip()
        if gpu_model.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        ram_gb = input("RAM容量 (GB): ").strip()
        if ram_gb.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # マイニング結果入力
        print(f"\n📈 マイニング結果:")
        try:
            hashrate_input = input("ハッシュレート (H/s) [1000]: ").strip()
            if hashrate_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            hashrate = float(hashrate_input or "1000")
            
            shares_sub_input = input("提出したシェア数 [10]: ").strip()
            if shares_sub_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            shares_submitted = int(shares_sub_input or "10")
            
            accepted_shares_input = input("承認されたシェア数 [8]: ").strip()
            if accepted_shares_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            accepted_shares = int(accepted_shares_input or "8")
            
            rejected_shares_input = input("拒否されたシェア数 [2]: ").strip()
            if rejected_shares_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            rejected_shares = int(rejected_shares_input or "2")
            
            power_input = input("消費電力 (W) [100]: ").strip()
            if power_input.lower() == "abort":
                print("❌ 記録を中断しました")
                return None
            power_consumption = float(power_input or "100")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            hashrate, shares_submitted, accepted_shares, rejected_shares, power_consumption = 1000, 10, 8, 2, 100
        
        # 学習メモ入力
        print(f"\n📝 学習メモ:")
        challenges = input("課題や問題点: ").strip()
        if challenges.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        optimizations = input("最適化や改善点: ").strip()
        if optimizations.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        learnings = input("学んだこと: ").strip()
        if learnings.lower() == "abort":
            print("❌ 記録を中断しました")
            return None
        
        # 結果をまとめる
        result = {
            'timestamp': datetime.now().isoformat(),
            'session_name': session_name,
            'start_time': start_time,
            'end_time': end_time,
            'mining_config': {
                'pool_url': pool_url,
                'wallet_address': wallet_address,
                'worker_name': worker_name
            },
            'hardware': {
                'cpu_model': cpu_model,
                'gpu_model': gpu_model,
                'ram_gb': ram_gb
            },
            'results': {
                'hashrate': hashrate,
                'shares_submitted': shares_submitted,
                'accepted_shares': accepted_shares,
                'rejected_shares': rejected_shares,
                'power_consumption': power_consumption,
                'efficiency': hashrate / power_consumption if power_consumption > 0 else 0
            },
            'notes': {
                'challenges': challenges,
                'optimizations': optimizations,
                'learnings': learnings
            },
            'status': 'recorded'
        }
        
        # 履歴に追加
        self.mining_history.append(result)
        
        # 学習目標の進捗を更新
        self._update_learning_progress(result)
        
        # ファイルに保存
        self._save_mining_record(result)
        
        print(f"\n✅ マイニングセッションを記録しました!")
        print(f"   ⛏️ セッション: {session_name}")
        print(f"   ⏱️ 時間: {start_time} - {end_time}")
        print(f"   ⚡ ハッシュレート: {hashrate} H/s")
        print(f"   💡 効率: {result['results']['efficiency']:.2f} H/s/W")
        
        return result
    
    def _update_learning_progress(self, result: Dict):
        """学習目標の進捗を更新"""
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_mining':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'consistent_mining':
                # 連続日数の計算
                consecutive_days = self._calculate_consecutive_days()
                goal['current'] = consecutive_days
        
        # 技術目標の更新
        for goal in self.learning_goals['technical_goals']:
            if goal['id'] == 'hashrate_optimization':
                # ハッシュレート改善のチェック
                if len(self.mining_history) >= 2:
                    current_hashrate = result['results']['hashrate']
                    previous_hashrate = self.mining_history[-2]['results']['hashrate']
                    improvement = (current_hashrate - previous_hashrate) / previous_hashrate
                    if improvement >= 0.1:  # 10%以上改善
                        goal['current'] = 1
            elif goal['id'] == 'efficiency_mastery':
                # 効率最適化のチェック
                efficiency = result['results']['efficiency']
                if efficiency > 10:  # 10 H/s/W以上
                    goal['current'] = 1
        
        # 高度目標の更新
        for goal in self.learning_goals['advanced_goals']:
            if goal['id'] == 'pool_experience':
                # ユニークなプールをカウント
                unique_pools = set()
                for session in self.mining_history:
                    unique_pools.add(session['mining_config']['pool_url'])
                goal['current'] = len(unique_pools)
            elif goal['id'] == 'hardware_mastery':
                # ユニークなハードウェアをカウント
                unique_hardware = set()
                for session in self.mining_history:
                    hardware_key = f"{session['hardware']['cpu_model']}_{session['hardware']['gpu_model']}"
                    unique_hardware.add(hardware_key)
                goal['current'] = len(unique_hardware)
    
    def _calculate_consecutive_days(self) -> int:
        """連続日数を計算"""
        if not self.mining_history:
            return 0
        
        # 日付をソート
        dates = []
        for session in self.mining_history:
            try:
                start_date = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M').date()
                dates.append(start_date)
            except:
                continue
        
        if not dates:
            return 0
        
        dates.sort()
        unique_dates = list(set(dates))
        unique_dates.sort()
        
        # 連続日数を計算
        consecutive = 1
        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i-1]).days == 1:
                consecutive += 1
            else:
                consecutive = 1
        
        return consecutive
    
    def _save_mining_record(self, result: Dict):
        """マイニング記録をファイルに保存"""
        timestamp = int(time.time())
        filename = f"mining_session_{timestamp}.json"
        filepath = self.mining_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 マイニング記録を保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 マイニング学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'technical': '⚙️ 技術目標', 
            'advanced': '🚀 高度目標',
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
        elif category == "technical":
            goals = self.learning_goals['technical_goals']
        elif category == "advanced":
            goals = self.learning_goals['advanced_goals']
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
        
        for category in ['basic_goals', 'technical_goals', 'advanced_goals']:
            for goal in self.learning_goals[category]:
                if goal['status'] == 'active' and goal['current'] >= goal['target']:
                    goal['status'] = 'completed'
                    goal['completion_time'] = datetime.now().isoformat()
                    completed_goals.append(goal)
        
        return completed_goals
    
    def get_mining_statistics(self) -> Dict:
        """マイニング統計を取得"""
        if not self.mining_history:
            return {'status': 'no_data'}
        
        # 統計計算
        total_sessions = len(self.mining_history)
        total_hashrate = 0
        total_power = 0
        total_shares = 0
        unique_pools = set()
        unique_hardware = set()
        
        for session in self.mining_history:
            total_hashrate += session['results']['hashrate']
            total_power += session['results']['power_consumption']
            total_shares += session['results']['accepted_shares']
            unique_pools.add(session['mining_config']['pool_url'])
            
            hardware_key = f"{session['hardware']['cpu_model']}_{session['hardware']['gpu_model']}"
            unique_hardware.add(hardware_key)
        
        avg_hashrate = total_hashrate / total_sessions if total_sessions > 0 else 0
        avg_power = total_power / total_sessions if total_sessions > 0 else 0
        avg_efficiency = avg_hashrate / avg_power if avg_power > 0 else 0
        
        return {
            'status': 'success',
            'total_sessions': total_sessions,
            'total_shares': total_shares,
            'avg_hashrate': avg_hashrate,
            'avg_power': avg_power,
            'avg_efficiency': avg_efficiency,
            'unique_pools': len(unique_pools),
            'unique_hardware': len(unique_hardware),
            'pools': list(unique_pools)
        }
    
    def show_mining_history(self):
        """マイニング履歴を表示"""
        print(f"\n📚 マイニング履歴")
        print("="*50)
        
        if not self.mining_history:
            print("📝 マイニング履歴がありません")
            return
        
        for i, session in enumerate(self.mining_history[-5:], 1):  # 最新5件
            print(f"\n{i}. {session['session_name']}")
            print(f"   ⏱️ 時間: {session['start_time']} - {session['end_time']}")
            print(f"   ⚡ ハッシュレート: {session['results']['hashrate']} H/s")
            print(f"   💡 効率: {session['results']['efficiency']:.2f} H/s/W")
            print(f"   🖥️ CPU: {session['hardware']['cpu_model']}")
            if session['hardware']['gpu_model']:
                print(f"   🎮 GPU: {session['hardware']['gpu_model']}")
            if session['notes']['learnings']:
                print(f"   📝 学んだこと: {session['notes']['learnings'][:50]}...")
    
    def show_mining_guide(self):
        """マイニングガイドを表示"""
        print(f"\n📖 Moneroマイニングガイド")
        print("="*50)
        
        print("🔧 セットアップ手順:")
        print("1. cpuminer-optのインストール")
        print("2. ウォレットの準備")
        print("3. プールの選択")
        print("4. マイニング設定")
        print("5. マイニング開始")
        
        print(f"\n📦 cpuminer-optのインストール:")
        if platform.system() == "Windows":
            print("🪟 Windows用インストール手順:")
            print("1. GitHubからダウンロード:")
            print("   https://github.com/JayDDee/cpuminer-opt/releases")
            print("2. 最新版のWindows x64版をダウンロード")
            print("3. ファイルを解凍")
            print("4. 解凍したフォルダをC:\\cpuminer-optに移動")
            print("5. システム環境変数PATHにC:\\cpuminer-optを追加")
            print("6. コマンドプロンプトで確認:")
            print("   cpuminer-opt --help")
        elif platform.system() == "Linux":
            print("🐧 Linux用インストール手順:")
            print("1. 必要なパッケージをインストール:")
            print("   sudo apt-get update")
            print("   sudo apt-get install build-essential git")
            print("2. ソースコードをクローン:")
            print("   git clone https://github.com/JayDDee/cpuminer-opt.git")
            print("3. ビルドディレクトリに移動:")
            print("   cd cpuminer-opt")
            print("4. ビルドスクリプトを実行:")
            print("   ./build.sh")
            print("5. 実行ファイルをシステムパスにコピー:")
            print("   sudo cp cpuminer /usr/local/bin/cpuminer-opt")
            print("6. 動作確認:")
            print("   cpuminer-opt --help")
        elif platform.system() == "Darwin":
            print("🍎 macOS用インストール手順:")
            print("1. Homebrewがインストールされていない場合:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. cpuminer-optをインストール:")
            print("   brew install cpuminer-opt")
            print("3. 動作確認:")
            print("   cpuminer-opt --help")
        
        print(f"\n💰 ウォレット準備:")
        print("   1. Moneroウォレットを作成")
        print("   2. ウォレットアドレスをコピー")
        print("   3. セキュリティを確保")
        
        print(f"\n📡 プール選択:")
        print("   推奨プール:")
        print("   - pool.supportxmr.com:3333")
        print("   - xmr.pool.gntl.co.uk:10009")
        print("   - poolto.be:3333")
        
        print(f"\n⚙️ 設定パラメータ:")
        print("   - スレッド数: CPUコア数に応じて設定")
        print("   - 強度: 1-20の範囲で設定")
        print("   - ワーカー名: 識別用の名前")
        
        print(f"\n⚠️  注意事項:")
        print("   - 電力消費に注意")
        print("   - システム温度を監視")
        print("   - ネットワーク接続を確保")
        print("   - セキュリティソフトの設定")
        
        print(f"\n💡 トラブルシューティング:")
        print("   - 接続エラー: プールURLを確認")
        print("   - 低ハッシュレート: スレッド数と強度を調整")
        print("   - 高CPU使用率: 強度を下げる")
        print("   - プロセス終了: ログを確認")

    def install_cpuminer_guide(self):
        """cpuminer-optのインストールガイド"""
        print(f"\n📦 cpuminer-optインストールガイド")
        print("="*50)
        
        os_name = platform.system()
        
        if os_name == "Windows":
            print("🪟 Windows用インストール手順:")
            print("1. GitHubからダウンロード:")
            print("   https://github.com/JayDDee/cpuminer-opt/releases")
            print("2. 最新版のWindows x64版をダウンロード")
            print("3. ファイルを解凍")
            print("4. 解凍したフォルダをC:\\cpuminer-optに移動")
            print("5. システム環境変数PATHにC:\\cpuminer-optを追加")
            print("6. コマンドプロンプトで確認:")
            print("   cpuminer-opt --help")
            
        elif os_name == "Linux":
            print("🐧 Linux用インストール手順:")
            print("1. 必要なパッケージをインストール:")
            print("   sudo apt-get update")
            print("   sudo apt-get install build-essential git")
            print("2. ソースコードをクローン:")
            print("   git clone https://github.com/JayDDee/cpuminer-opt.git")
            print("3. ビルドディレクトリに移動:")
            print("   cd cpuminer-opt")
            print("4. ビルドスクリプトを実行:")
            print("   ./build.sh")
            print("5. 実行ファイルをシステムパスにコピー:")
            print("   sudo cp cpuminer /usr/local/bin/cpuminer-opt")
            print("6. 動作確認:")
            print("   cpuminer-opt --help")
            
        elif os_name == "Darwin":
            print("🍎 macOS用インストール手順:")
            print("1. Homebrewがインストールされていない場合:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. cpuminer-optをインストール:")
            print("   brew install cpuminer-opt")
            print("3. 動作確認:")
            print("   cpuminer-opt --help")
        
        print(f"\n✅ インストール完了後、このゲームでマイニングを開始できます！")

    def check_system_compatibility(self) -> Dict:
        """システム互換性をチェック"""
        compatibility = {
            'os': platform.system(),
            'cpu_cores': 0,
            'ram_gb': 0,
            'cpuminer_available': False,
            'cpuminer_opt_available': False,
            'xmr_stak_available': False,
            'mining_supported': False,
            'available_miners': []
        }
        
        # CPU情報
        try:
            compatibility['cpu_cores'] = psutil.cpu_count()
            compatibility['ram_gb'] = psutil.virtual_memory().total / (1024**3)
        except:
            pass
        
        # 各種マイニングソフトウェアの存在確認
        miners_to_check = [
            ('cpuminer-opt', 'cpuminer-opt'),
            ('cpuminer', 'cpuminer'),
            ('xmr-stak', 'xmr-stak'),
            ('xmrig', 'xmrig')
        ]
        
        for miner_name, command in miners_to_check:
            try:
                result = subprocess.run([command, '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    compatibility[f'{miner_name}_available'] = True
                    compatibility['available_miners'].append(miner_name)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        # マイニングサポート判定
        compatibility['mining_supported'] = (
            compatibility['cpu_cores'] >= 2 and 
            compatibility['ram_gb'] >= 2.0 and
            len(compatibility['available_miners']) > 0
        )
        
        return compatibility

    def configure_mining(self) -> Dict:
        """マイニング設定を構成"""
        print(f"\n⚙️ マイニング設定")
        print("="*40)
        print("💡 入力中に「abort」と入力すると設定を中断できます")
        print("-" * 40)
        
        # 利用可能なマイニングソフトウェアを確認
        compatibility = self.check_system_compatibility()
        if not compatibility['available_miners']:
            print("❌ 利用可能なマイニングソフトウェアが見つかりません")
            print("📦 インストールガイドを参照してください")
            return None
        
        print(f"✅ 利用可能なマイニングソフトウェア: {', '.join(compatibility['available_miners'])}")
        
        # マイニングソフトウェア選択
        print(f"\n🔧 マイニングソフトウェア選択:")
        for i, miner in enumerate(compatibility['available_miners'], 1):
            print(f"   {i}. {miner}")
        
        try:
            miner_choice = input(f"選択してください (1-{len(compatibility['available_miners'])}): ").strip()
            if miner_choice.lower() == "abort":
                print("❌ 設定を中断しました")
                return None
            
            selected_miner = compatibility['available_miners'][int(miner_choice) - 1]
        except (ValueError, IndexError):
            print("❌ 無効な選択です。最初のマイニングソフトウェアを使用します。")
            selected_miner = compatibility['available_miners'][0]
        
        # プール設定
        print(f"\n📊 プール設定:")
        pool_url = input("プールURL [pool.supportxmr.com:3333]: ").strip()
        if pool_url.lower() == "abort":
            print("❌ 設定を中断しました")
            return None
        pool_url = pool_url or "pool.supportxmr.com:3333"
        
        wallet_address = input("ウォレットアドレス: ").strip()
        if wallet_address.lower() == "abort":
            print("❌ 設定を中断しました")
            return None
        
        worker_name = input("ワーカー名 [crypto_adventure_worker]: ").strip()
        if worker_name.lower() == "abort":
            print("❌ 設定を中断しました")
            return None
        worker_name = worker_name or "crypto_adventure_worker"
        
        # マイニング設定
        print(f"\n⛏️ マイニング設定:")
        try:
            threads_input = input("スレッド数 [4]: ").strip()
            if threads_input.lower() == "abort":
                print("❌ 設定を中断しました")
                return None
            threads = int(threads_input or "4")
            
            intensity_input = input("強度 (1-20) [10]: ").strip()
            if intensity_input.lower() == "abort":
                print("❌ 設定を中断しました")
                return None
            intensity = int(intensity_input or "10")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            threads, intensity = 4, 10
        
        # 設定を保存
        self.mining_config = {
            'miner': selected_miner,
            'pool_url': pool_url,
            'wallet_address': wallet_address,
            'worker_name': worker_name,
            'threads': threads,
            'intensity': intensity
        }
        
        print(f"\n✅ マイニング設定を保存しました:")
        print(f"   🔧 マイニングソフト: {selected_miner}")
        print(f"   📡 プール: {pool_url}")
        print(f"   💰 ウォレット: {wallet_address[:10]}...")
        print(f"   👷 ワーカー: {worker_name}")
        print(f"   🧵 スレッド数: {threads}")
        print(f"   ⚡ 強度: {intensity}")
        
        return self.mining_config

    def start_mining(self) -> bool:
        """マイニングを開始"""
        if self.is_mining:
            print("❌ 既にマイニング中です")
            return False
        
        if not self.mining_config:
            print("❌ マイニング設定が未設定です。先に設定を行ってください。")
            return False
        
        print(f"\n🚀 マイニングを開始します...")
        print(f"   🔧 マイニングソフト: {self.mining_config['miner']}")
        print(f"   📡 プール: {self.mining_config['pool_url']}")
        print(f"   👷 ワーカー: {self.mining_config['worker_name']}")
        print(f"   🧵 スレッド数: {self.mining_config['threads']}")
        print(f"   ⚡ 強度: {self.mining_config['intensity']}")
        
        try:
            # マイニングソフトウェアに応じたコマンドを構築
            cmd = self._build_mining_command()
            
            print(f"\n🔧 実行コマンド: {' '.join(cmd)}")
            
            # マイニングプロセスを開始
            self.current_mining_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_mining = True
            self.mining_start_time = datetime.now()
            
            print("✅ マイニングプロセスを開始しました")
            print("💡 マイニングを停止するには、メニューから「マイニング停止」を選択してください")
            
            # マイニング監視スレッドを開始
            self.mining_thread = threading.Thread(target=self._monitor_mining)
            self.mining_thread.daemon = True
            self.mining_thread.start()
            
            return True
            
        except FileNotFoundError:
            print(f"❌ {self.mining_config['miner']}が見つかりません。インストールしてください。")
            return False
        except Exception as e:
            print(f"❌ マイニング開始エラー: {e}")
            return False

    def _build_mining_command(self) -> List[str]:
        """マイニングソフトウェアに応じたコマンドを構築"""
        miner = self.mining_config['miner']
        
        if miner == 'cpuminer-opt':
            return [
                'cpuminer-opt',
                '-o', f"stratum+tcp://{self.mining_config['pool_url']}",
                '-u', self.mining_config['wallet_address'],
                '-p', self.mining_config['worker_name'],
                '-t', str(self.mining_config['threads']),
                '--cpu-priority', str(self.mining_config['intensity'])
            ]
        elif miner == 'cpuminer':
            return [
                'cpuminer',
                '-o', f"stratum+tcp://{self.mining_config['pool_url']}",
                '-u', self.mining_config['wallet_address'],
                '-p', self.mining_config['worker_name'],
                '-t', str(self.mining_config['threads'])
            ]
        elif miner == 'xmrig':
            return [
                'xmrig',
                '-o', self.mining_config['pool_url'],
                '-u', self.mining_config['wallet_address'],
                '-p', self.mining_config['worker_name'],
                '--threads', str(self.mining_config['threads'])
            ]
        else:
            # デフォルトはcpuminer-opt形式
            return [
                miner,
                '-o', f"stratum+tcp://{self.mining_config['pool_url']}",
                '-u', self.mining_config['wallet_address'],
                '-p', self.mining_config['worker_name'],
                '-t', str(self.mining_config['threads'])
            ]

    def stop_mining(self) -> bool:
        """マイニングを停止"""
        if not self.is_mining:
            print("❌ マイニング中ではありません")
            return False
        
        print("\n🛑 マイニングを停止しています...")
        
        try:
            if self.current_mining_process:
                self.current_mining_process.terminate()
                self.current_mining_process.wait(timeout=10)
            
            self.is_mining = False
            self.mining_start_time = None
            
            print("✅ マイニングを停止しました")
            return True
            
        except subprocess.TimeoutExpired:
            print("⚠️ プロセスの強制終了が必要です...")
            if self.current_mining_process:
                self.current_mining_process.kill()
            self.is_mining = False
            return True
        except Exception as e:
            print(f"❌ マイニング停止エラー: {e}")
            return False

    def _monitor_mining(self):
        """マイニングプロセスを監視"""
        while self.is_mining and self.current_mining_process:
            try:
                # プロセスの状態をチェック
                if self.current_mining_process.poll() is not None:
                    print("❌ マイニングプロセスが終了しました")
                    self.is_mining = False
                    break
                
                # 出力を読み取り
                output = self.current_mining_process.stdout.readline()
                if output:
                    self._parse_mining_output(output.strip())
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ 監視エラー: {e}")
                break

    def _parse_mining_output(self, output: str):
        """マイニング出力を解析"""
        if "accepted" in output.lower():
            self.mining_stats['accepted_shares'] += 1
            self.mining_stats['shares_submitted'] += 1
            print(f"✅ シェア承認: {output}")
        elif "rejected" in output.lower():
            self.mining_stats['rejected_shares'] += 1
            self.mining_stats['shares_submitted'] += 1
            print(f"❌ シェア拒否: {output}")
        elif "hashrate" in output.lower():
            # ハッシュレートを抽出
            try:
                hashrate_str = output.split('hashrate')[1].split()[0]
                self.mining_stats['hashrate'] = float(hashrate_str)
            except:
                pass
        elif "error" in output.lower():
            print(f"⚠️ エラー: {output}")

    def get_mining_status(self) -> Dict:
        """マイニング状態を取得"""
        if not self.is_mining:
            return {'status': 'stopped'}
        
        runtime = datetime.now() - self.mining_start_time if self.mining_start_time else None
        
        return {
            'status': 'running',
            'start_time': self.mining_start_time.isoformat() if self.mining_start_time else None,
            'runtime': str(runtime) if runtime else None,
            'stats': self.mining_stats.copy(),
            'process_alive': self.current_mining_process.poll() is None if self.current_mining_process else False
        }

    def show_mining_status(self):
        """マイニング状態を表示"""
        status = self.get_mining_status()
        
        print(f"\n📊 マイニング状態")
        print("="*40)
        
        if status['status'] == 'stopped':
            print("⏸️  マイニング停止中")
            return
        
        print(f"🟢 マイニング実行中")
        print(f"   🕐 開始時刻: {status['start_time']}")
        print(f"   ⏱️  実行時間: {status['runtime']}")
        print(f"   ⚡ ハッシュレート: {status['stats']['hashrate']:.2f} H/s")
        print(f"   📊 提出シェア: {status['stats']['shares_submitted']}")
        print(f"   ✅ 承認シェア: {status['stats']['accepted_shares']}")
        print(f"   ❌ 拒否シェア: {status['stats']['rejected_shares']}")
        print(f"   🔌 消費電力: {status['stats']['power_consumption']} W")
        
        if status['process_alive']:
            print(f"   🟢 プロセス状態: 実行中")
        else:
            print(f"   🔴 プロセス状態: 停止") 