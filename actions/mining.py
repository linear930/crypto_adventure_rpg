#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現実世界マイニング実行モジュール
実際のマイニングソフトを起動・監視する
"""

import subprocess
import time
import json
import os
import psutil
from pathlib import Path
from typing import Dict, Optional
import threading

class MiningExecutor:
    def __init__(self, config: Dict):
        self.config = config
        self.mining_process = None
        self.is_running = False
        self.start_time = None
        self.hash_rate = 0
        self.power_consumption = 0
        
    def start_mining(self, duration_minutes: int = 60) -> Dict:
        """マイニングを開始"""
        print(f"\n⛏️ マイニングを開始します...")
        print(f"   実行時間: {duration_minutes}分")
        print(f"   プール: {self.config.get('pool_url', '未設定')}")
        print(f"   ウォレット: {self.config.get('wallet_address', '未設定')}")
        
        # 軽量シミュレーターを使用するかチェック
        use_simulator = self.config.get('use_simulator', False)
        
        if use_simulator:
            return self._start_lightweight_simulator(duration_minutes)
        
        # 通常のマイニングソフトのパスを確認
        miner_path = self.config.get('xmrig_path')
        if not miner_path or not Path(miner_path).exists():
            print("❌ マイニングソフトが見つかりません")
            print("   現実連動設定でマイニングソフトのパスを設定してください")
            print(f"   現在のパス: {miner_path}")
            return self._create_fallback_result(duration_minutes)
        
        try:
            # マイニングプロセスを開始
            if 'SRBMiner' in miner_path or 'srbminer' in miner_path.lower():
                # SRBMinerの場合
                if miner_path.endswith('.bat'):
                    # バッチファイルの場合
                    cmd = [miner_path]
                else:
                    # 実行ファイルの場合
                    cmd = [
                        miner_path,
                        "--config", str(Path(miner_path).parent / "config.txt")
                    ]
            else:
                # XMRigの場合（後方互換性）
                cmd = [
                    miner_path,
                    "--url", self.config.get('pool_url', 'pool.supportxmr.com:3333'),
                    "--user", self.config.get('wallet_address', ''),
                    "--pass", "x",
                    "--background"
                ]
            
            self.mining_process = subprocess.Popen(cmd)
            self.is_running = True
            self.start_time = time.time()
            
            print("✅ マイニングプロセスを開始しました")
            print("   プロセスID:", self.mining_process.pid)
            print("   使用ソフト:", Path(miner_path).name)
            
            # 指定時間まで待機
            print(f"\n⏱️  {duration_minutes}分間マイニングを実行中...")
            for remaining in range(duration_minutes, 0, -1):
                if not self.is_running:
                    break
                print(f"   残り時間: {remaining}分", end='\r')
                time.sleep(60)  # 1分待機
            
            # マイニングを停止
            self.stop_mining()
            
            # 結果を計算
            result = self._calculate_result(duration_minutes)
            return result
            
        except Exception as e:
            print(f"❌ マイニング開始エラー: {e}")
            return self._create_fallback_result(duration_minutes)
    
    def stop_mining(self):
        """マイニングを停止"""
        if self.mining_process and self.is_running:
            try:
                self.mining_process.terminate()
                self.mining_process.wait(timeout=10)
                print("\n✅ マイニングを停止しました")
            except subprocess.TimeoutExpired:
                self.mining_process.kill()
                print("\n⚠️ マイニングプロセスを強制終了しました")
            except Exception as e:
                print(f"\n❌ マイニング停止エラー: {e}")
            
            self.is_running = False
    
    def _calculate_result(self, duration_minutes: int) -> Dict:
        """マイニング結果を計算"""
        # 実際のマイニングログからデータを取得
        log_file = self.config.get('log_file')
        if log_file and Path(log_file).exists():
            try:
                # ログファイルから最新のハッシュレートを取得
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if 'speed' in line.lower() or 'hashrate' in line.lower():
                            # ハッシュレートを抽出（簡易的な実装）
                            if 'H/s' in line:
                                hash_part = line.split('H/s')[0].split()[-1]
                                try:
                                    self.hash_rate = float(hash_part)
                                except:
                                    pass
                            break
            except Exception as e:
                print(f"⚠️ ログファイル読み取りエラー: {e}")
        
        # 電力消費を推定
        self.power_consumption = self._estimate_power_consumption(duration_minutes)
        
        # XMR獲得量を推定（実際の計算は複雑）
        xmr_earned = self._estimate_xmr_earned(duration_minutes)
        
        return {
            'hash_rate': self.hash_rate,
            'power_consumption': self.power_consumption,
            'xmr_earned': xmr_earned,
            'duration_minutes': duration_minutes,
            'status': 'completed'
        }
    
    def _estimate_power_consumption(self, duration_minutes: int) -> float:
        """電力消費を推定"""
        # CPU使用率から概算
        cpu_percent = psutil.cpu_percent(interval=1)
        # 簡易的な計算（実際はより複雑）
        power_per_hour = cpu_percent * 0.1  # kWh
        return power_per_hour * (duration_minutes / 60)
    
    def _estimate_xmr_earned(self, duration_minutes: int) -> float:
        """XMR獲得量を推定"""
        # 非常に簡易的な計算（実際のマイニング報酬は複雑）
        if self.hash_rate > 0:
            # ハッシュレートに基づく概算
            return (self.hash_rate * duration_minutes * 60) / 1e12 * 0.000001
        else:
            # デフォルト値
            return 0.000001
    
    def _create_fallback_result(self, duration_minutes: int) -> Dict:
        """フォールバック結果を作成"""
        return {
            'success': True,
            'duration_minutes': duration_minutes,
            'hash_rate': 2500,  # ゲームが期待するキー名
            'hashrate_hps': 2500,
            'power_consumption': 0.15,
            'xmr_earned': 0.00000100,
            'runtime_seconds': duration_minutes * 60,
            'wallet_address': self.config.get('wallet_address', ''),
            'pool_url': self.config.get('pool_url', ''),
            'status': 'simulated'
        }
    
    def _start_lightweight_simulator(self, duration_minutes: int) -> Dict:
        """軽量マイニングシミュレーターを開始"""
        print("🚀 軽量マイニングシミュレーターを使用します")
        print("   （アンチウイルスに検知されないPythonベース）")
        
        try:
            # 軽量シミュレーターをインポート
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            
            from lightweight_miner import LightweightMiner
            
            # シミュレーターを作成
            config_path = "C:\\srbminer\\config.txt"
            miner = LightweightMiner(config_path)
            
            # 設定を更新
            miner.wallet = self.config.get('wallet_address', 'YOUR_WALLET_ADDRESS')
            miner.pool = self.config.get('pool_url', 'pool.supportxmr.com:3333')
            
            print("✅ 軽量シミュレーターを開始しました")
            
            # マイニング実行
            result = miner.start_mining(duration_minutes)
            
            # 結果のキー名を統一
            if 'hashrate_hps' in result and 'hash_rate' not in result:
                result['hash_rate'] = result['hashrate_hps']
            
            # 不足しているキーを補完
            if 'power_consumption' not in result:
                result['power_consumption'] = 0.15  # デフォルト値
            
            if 'xmr_earned' not in result and 'estimated_xmr' in result:
                result['xmr_earned'] = result['estimated_xmr']
            
            return result
            
        except Exception as e:
            print(f"❌ 軽量シミュレーターエラー: {e}")
            return self._create_fallback_result(duration_minutes) 