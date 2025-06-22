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
        
        # 基本情報入力
        print("📊 マイニングセッション情報を入力してください:")
        
        session_name = input("セッション名 (例: 朝のマイニング、夜間セッション): ").strip()
        start_time = input("開始時刻 (YYYY-MM-DD HH:MM): ").strip()
        end_time = input("終了時刻 (YYYY-MM-DD HH:MM): ").strip()
        
        # マイニング設定入力
        print(f"\n⚙️ マイニング設定:")
        pool_url = input("プールURL [pool.supportxmr.com:3333]: ").strip() or "pool.supportxmr.com:3333"
        wallet_address = input("ウォレットアドレス: ").strip()
        worker_name = input("ワーカー名 [crypto_adventure_worker]: ").strip() or "crypto_adventure_worker"
        
        # ハードウェア情報入力
        print(f"\n🖥️ ハードウェア情報:")
        cpu_model = input("CPUモデル: ").strip()
        gpu_model = input("GPUモデル (使用する場合): ").strip()
        ram_gb = input("RAM容量 (GB): ").strip()
        
        # マイニング結果入力
        print(f"\n📈 マイニング結果:")
        try:
            hashrate = float(input("ハッシュレート (H/s) [1000]: ").strip() or "1000")
            shares_submitted = int(input("提出したシェア数 [10]: ").strip() or "10")
            accepted_shares = int(input("承認されたシェア数 [8]: ").strip() or "8")
            rejected_shares = int(input("拒否されたシェア数 [2]: ").strip() or "2")
            power_consumption = float(input("消費電力 (W) [100]: ").strip() or "100")
            
        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            hashrate, shares_submitted, accepted_shares, rejected_shares, power_consumption = 1000, 10, 8, 2, 100
        
        # 学習メモ入力
        print(f"\n📝 学習メモ:")
        challenges = input("課題や問題点: ").strip()
        optimizations = input("最適化や改善点: ").strip()
        learnings = input("学んだこと: ").strip()
        
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
        
        guide = {
            'getting_started': {
                'title': '🚀 始め方',
                'steps': [
                    'Moneroウォレットを作成',
                    'マイニングプールを選択',
                    'マイニングソフトウェアをダウンロード',
                    '設定ファイルを作成',
                    'マイニングを開始'
                ]
            },
            'hardware_requirements': {
                'title': '🖥️ ハードウェア要件',
                'requirements': {
                    'CPU': 'RandomXアルゴリズムに最適化されたCPU',
                    'RAM': '最低4GB、推奨8GB以上',
                    'Storage': 'SSD推奨',
                    'Network': '安定したインターネット接続'
                }
            },
            'popular_pools': {
                'title': '🏊 人気プール',
                'pools': [
                    'pool.supportxmr.com',
                    'xmr.2miners.com',
                    'xmrpool.eu',
                    'nanopool.org'
                ]
            },
            'optimization_tips': {
                'title': '⚡ 最適化のヒント',
                'tips': [
                    'CPUの全コアを使用',
                    'RAMを十分に確保',
                    '電力効率を考慮',
                    '安定したネットワーク接続',
                    '定期的なメンテナンス'
                ]
            }
        }
        
        for section_id, section in guide.items():
            print(f"\n{section['title']}:")
            if 'steps' in section:
                for i, step in enumerate(section['steps'], 1):
                    print(f"   {i}. {step}")
            elif 'requirements' in section:
                for req, desc in section['requirements'].items():
                    print(f"   • {req}: {desc}")
            elif 'pools' in section:
                for pool in section['pools']:
                    print(f"   • {pool}")
            elif 'tips' in section:
                for tip in section['tips']:
                    print(f"   • {tip}")
    
    def check_system_compatibility(self) -> Dict:
        """システム互換性をチェック"""
        print(f"\n🔍 システム互換性チェック")
        print("="*40)
        
        compatibility = {
            'os': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'cpu_cores': 0,
            'ram_gb': 0,
            'mining_ready': False
        }
        
        # CPU情報
        try:
            import psutil
            compatibility['cpu_cores'] = psutil.cpu_count()
            compatibility['ram_gb'] = psutil.virtual_memory().total / (1024**3)
        except ImportError:
            print("⚠️ psutilライブラリがインストールされていません")
            compatibility['cpu_cores'] = 4  # 推定値
            compatibility['ram_gb'] = 8     # 推定値
        
        # マイニング準備状況
        compatibility['mining_ready'] = (
            compatibility['cpu_cores'] >= 2 and
            compatibility['ram_gb'] >= 4
        )
        
        print(f"💻 OS: {compatibility['os']}")
        print(f"🏗️ アーキテクチャ: {compatibility['architecture']}")
        print(f"🐍 Python: {compatibility['python_version']}")
        print(f"🔢 CPUコア数: {compatibility['cpu_cores']}")
        print(f"💾 RAM: {compatibility['ram_gb']:.1f} GB")
        print(f"⛏️ マイニング準備: {'✅' if compatibility['mining_ready'] else '❌'}")
        
        return compatibility 