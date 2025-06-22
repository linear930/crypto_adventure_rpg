#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現実連動システム
実際のマイニング、CEA計算、発電所設計などの活動を
ゲームに反映させるモジュール
"""

import json
import os
import time
import psutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

class RealityConnector:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logs_dir = data_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'reality_connector.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 監視対象プロセス
        self.monitored_processes = {
            'xmrig': {
                'keywords': ['xmrig', 'xmr-stak', 'monero'],
                'log_patterns': ['hashrate', 'accepted', 'rejected'],
                'type': 'mining'
            },
            'cea': {
                'keywords': ['cea', 'rocket', 'propulsion'],
                'log_patterns': ['isp', 'thrust', 'chamber'],
                'type': 'cea'
            },
            'python': {
                'keywords': ['python', 'script'],
                'log_patterns': ['calculation', 'simulation'],
                'type': 'general'
            }
        }
        
        # 監視状態
        self.monitoring_active = False
        self.monitor_thread = None
        self.activity_log = []
        
        # 設定ファイル
        self.config_file = self.data_dir / "reality_config.json"
        self.load_config()
    
    def load_config(self):
        """設定の読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"設定ファイルの読み込みに失敗: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """デフォルト設定の作成"""
        self.config = {
            'monitoring': {
                'enabled': True,
                'interval': 30,  # 秒
                'auto_sync': True
            },
            'mining': {
                'xmrig_path': '',
                'log_file': '',
                'wallet_address': '',
                'pool_url': ''
            },
            'cea': {
                'cea_path': '',
                'input_files': [],
                'output_dir': ''
            },
            'power_plants': {
                'monitoring_enabled': True,
                'solar_panels': [],
                'wind_turbines': [],
                'battery_systems': []
            },
            'file_watchers': {
                'enabled': True,
                'watch_dirs': [],
                'file_patterns': ['*.log', '*.txt', '*.json']
            }
        }
        self.save_config()
    
    def save_config(self):
        """設定の保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"設定ファイルの保存に失敗: {e}")
    
    def start_monitoring(self):
        """監視の開始"""
        if self.monitoring_active:
            self.logger.info("監視は既に開始されています")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("現実連動監視を開始しました")
    
    def stop_monitoring(self):
        """監視の停止"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("現実連動監視を停止しました")
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.monitoring_active:
            try:
                self._check_processes()
                self._check_file_changes()
                self._check_power_consumption()
                time.sleep(self.config['monitoring']['interval'])
            except Exception as e:
                self.logger.error(f"監視ループでエラー: {e}")
                time.sleep(10)
    
    def _check_processes(self):
        """プロセス監視"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_info = proc.info
                for process_type, config in self.monitored_processes.items():
                    if self._is_target_process(proc_info, config):
                        self._handle_process_activity(process_type, proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _is_target_process(self, proc_info: Dict, config: Dict) -> bool:
        """対象プロセスかどうか判定"""
        name = proc_info.get('name', '').lower()
        cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
        
        for keyword in config['keywords']:
            if keyword.lower() in name or keyword.lower() in cmdline:
                return True
        return False
    
    def _handle_process_activity(self, process_type: str, proc_info: Dict):
        """プロセス活動の処理"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'type': process_type,
            'process_name': proc_info.get('name', ''),
            'pid': proc_info.get('pid'),
            'activity': 'running'
        }
        
        self.activity_log.append(activity)
        self.logger.info(f"プロセス活動検出: {process_type} - {proc_info.get('name', '')}")
    
    def _check_file_changes(self):
        """ファイル変更監視"""
        if not self.config['file_watchers']['enabled']:
            return
        
        for watch_dir in self.config['file_watchers']['watch_dirs']:
            watch_path = Path(watch_dir)
            if not watch_path.exists():
                continue
            
            for pattern in self.config['file_watchers']['file_patterns']:
                for file_path in watch_path.glob(pattern):
                    if self._is_recently_modified(file_path):
                        self._handle_file_activity(file_path)
    
    def _is_recently_modified(self, file_path: Path) -> bool:
        """ファイルが最近変更されたかチェック"""
        try:
            mtime = file_path.stat().st_mtime
            return time.time() - mtime < 300  # 5分以内
        except:
            return False
    
    def _handle_file_activity(self, file_path: Path):
        """ファイル活動の処理"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'type': 'file_change',
            'file_path': str(file_path),
            'activity': 'modified'
        }
        
        self.activity_log.append(activity)
        self.logger.info(f"ファイル変更検出: {file_path}")
    
    def _check_power_consumption(self):
        """電力消費監視"""
        try:
            # CPU使用率から概算電力消費を計算
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # 簡易的な電力消費計算（概算）
            estimated_power = (cpu_percent * 0.1) + (memory_percent * 0.05)  # kWh
            
            activity = {
                'timestamp': datetime.now().isoformat(),
                'type': 'power_consumption',
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'estimated_power': estimated_power,
                'activity': 'monitoring'
            }
            
            self.activity_log.append(activity)
            
        except Exception as e:
            self.logger.error(f"電力消費監視エラー: {e}")
    
    def get_mining_data(self) -> Optional[Dict]:
        """マイニングデータの取得"""
        mining_activities = [a for a in self.activity_log if a['type'] == 'xmrig']
        
        if not mining_activities:
            return None
        
        # 最新のマイニング活動からデータを抽出
        latest_activity = mining_activities[-1]
        
        # 実際のマイニングログファイルからデータを読み取り
        mining_log = self._read_mining_log()
        
        return {
            'hash_rate': mining_log.get('hash_rate', 0),
            'power_consumption': mining_log.get('power_consumption', 0),
            'xmr_earned': mining_log.get('xmr_earned', 0),
            'duration_minutes': mining_log.get('duration_minutes', 60),
            'timestamp': latest_activity['timestamp']
        }
    
    def _read_mining_log(self) -> Dict:
        """マイニングログの読み取り"""
        mining_log_file = self.data_dir / "mining_log.json"
        
        if mining_log_file.exists():
            try:
                with open(mining_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"マイニングログ読み取りエラー: {e}")
        
        return {}
    
    def get_cea_data(self) -> Optional[Dict]:
        """CEA計算データの取得"""
        cea_activities = [a for a in self.activity_log if a['type'] == 'cea']
        
        if not cea_activities:
            return None
        
        # CEA計算結果ファイルからデータを読み取り
        cea_result_file = self.data_dir / "cea_result.json"
        
        if cea_result_file.exists():
            try:
                with open(cea_result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"CEA結果読み取りエラー: {e}")
        
        return None
    
    def get_power_plant_data(self) -> Optional[Dict]:
        """発電所データの取得"""
        # 実際の発電所監視システムからデータを取得
        # ここでは簡易的なシミュレーションデータを返す
        return {
            'type': 'solar',
            'capacity': 2.5,
            'daily_generation': 10.0,
            'current_output': 1.2,
            'efficiency': 0.18,
            'timestamp': datetime.now().isoformat()
        }
    
    def sync_to_game(self, game_engine) -> Dict:
        """ゲームエンジンへの同期"""
        sync_results = {
            'mining_synced': False,
            'cea_synced': False,
            'power_plant_synced': False,
            'activities_count': len(self.activity_log)
        }
        
        # マイニングデータの同期
        mining_data = self.get_mining_data()
        if mining_data:
            game_engine.add_mining_result(mining_data)
            sync_results['mining_synced'] = True
            self.logger.info("マイニングデータをゲームに同期しました")
        
        # CEAデータの同期
        cea_data = self.get_cea_data()
        if cea_data:
            game_engine.add_cea_result(cea_data)
            sync_results['cea_synced'] = True
            self.logger.info("CEAデータをゲームに同期しました")
        
        # 発電所データの同期
        power_plant_data = self.get_power_plant_data()
        if power_plant_data:
            game_engine.add_plant_design(power_plant_data)
            sync_results['power_plant_synced'] = True
            self.logger.info("発電所データをゲームに同期しました")
        
        return sync_results
    
    def get_activity_summary(self) -> Dict:
        """活動サマリーの取得"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_activities = [
            a for a in self.activity_log 
            if datetime.fromisoformat(a['timestamp']) >= today_start
        ]
        
        return {
            'total_activities': len(self.activity_log),
            'today_activities': len(today_activities),
            'mining_activities': len([a for a in today_activities if a['type'] == 'xmrig']),
            'cea_activities': len([a for a in today_activities if a['type'] == 'cea']),
            'file_changes': len([a for a in today_activities if a['type'] == 'file_change']),
            'last_activity': self.activity_log[-1]['timestamp'] if self.activity_log else None
        }
    
    def cleanup(self):
        """クリーンアップ"""
        self.stop_monitoring()
        self.logger.info("現実連動システムを終了しました") 