#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール
環境変数と機密情報を安全に管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

class ConfigManager:
    def __init__(self, config_dir: Path = Path("data")):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = config_dir / "reality_config.json"
        self.template_file = Path("config_template.json")
        
    def load_config(self) -> Dict:
        """設定を読み込み（環境変数を優先）"""
        config = self._load_from_file()
        
        # 環境変数で上書き
        config = self._override_with_env_vars(config)
        
        return config
    
    def _load_from_file(self) -> Dict:
        """ファイルから設定を読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 設定ファイル読み込みエラー: {e}")
        
        # テンプレートファイルから読み込み
        if self.template_file.exists():
            try:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ テンプレートファイル読み込みエラー: {e}")
        
        # デフォルト設定
        return self._get_default_config()
    
    def _override_with_env_vars(self, config: Dict) -> Dict:
        """環境変数で設定を上書き"""
        # マイニング設定
        if os.getenv('MINING_WALLET_ADDRESS'):
            config['mining']['wallet_address'] = os.getenv('MINING_WALLET_ADDRESS')
        
        if os.getenv('MINING_POOL_URL'):
            config['mining']['pool_url'] = os.getenv('MINING_POOL_URL')
        
        if os.getenv('MINING_WORKER_NAME'):
            config['mining']['worker_name'] = os.getenv('MINING_WORKER_NAME')
        
        # CEA設定
        if os.getenv('CEA_PATH'):
            config['cea']['cea_path'] = os.getenv('CEA_PATH')
        
        # 監視設定
        if os.getenv('MONITORING_INTERVAL'):
            try:
                config['monitoring']['interval'] = int(os.getenv('MONITORING_INTERVAL'))
            except ValueError:
                pass
        
        # 音声設定
        if os.getenv('BGM_VOLUME'):
            try:
                config['audio']['bgm_volume'] = float(os.getenv('BGM_VOLUME'))
            except ValueError:
                pass
        
        if os.getenv('EFFECT_VOLUME'):
            try:
                config['audio']['effect_volume'] = float(os.getenv('EFFECT_VOLUME'))
            except ValueError:
                pass
        
        return config
    
    def _get_default_config(self) -> Dict:
        """デフォルト設定を取得"""
        return {
            'game_name': 'Crypto Adventure RPG',
            'version': '2.0.0',
            'output_dir': 'data',
            'mining': {
                'enabled': True,
                'pool_url': 'pool.supportxmr.com:3333',
                'wallet_address': 'YOUR_WALLET_ADDRESS_HERE',
                'worker_name': 'crypto_adventure_worker',
                'use_simulator': True
            },
            'power_plant': {
                'enabled': True,
                'monitoring_interval': 3600
            },
            'monitoring': {
                'enabled': True,
                'interval': 30,
                'auto_sync': True
            },
            'cea': {
                'cea_path': 'C:\\CEA\\cea.exe',
                'input_files': [],
                'output_dir': 'data/cea_results'
            },
            'power_plants': {
                'monitoring_enabled': True,
                'solar_panels': [],
                'wind_turbines': [],
                'battery_systems': [],
                'output_dir': 'data/power_plant_designs'
            },
            'file_watchers': {
                'enabled': True,
                'watch_dirs': [
                    'C:\\srbminer',
                    'C:\\CEA\\output',
                    'data'
                ],
                'file_patterns': [
                    '*.log',
                    '*.txt',
                    '*.json',
                    '*.out'
                ]
            },
            'audio': {
                'bgm_volume': 0.5,
                'effect_volume': 0.7,
                'enabled': True
            }
        }
    
    def save_config(self, config: Dict):
        """設定を保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ 設定を保存しました: {self.config_file}")
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
    
    def create_config_from_template(self):
        """テンプレートから設定ファイルを作成"""
        if self.config_file.exists():
            print(f"⚠️ 設定ファイルは既に存在します: {self.config_file}")
            return False
        
        if not self.template_file.exists():
            print(f"❌ テンプレートファイルが見つかりません: {self.template_file}")
            return False
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            self.save_config(template)
            print(f"✅ テンプレートから設定ファイルを作成しました: {self.config_file}")
            print("📝 設定ファイルを編集して、ウォレットアドレスなどを設定してください")
            return True
        except Exception as e:
            print(f"❌ テンプレートからの設定作成エラー: {e}")
            return False
    
    def get_sensitive_config(self) -> Dict:
        """機密設定を取得（環境変数から）"""
        return {
            'mining_wallet': os.getenv('MINING_WALLET_ADDRESS', 'NOT_SET'),
            'mining_pool': os.getenv('MINING_POOL_URL', 'NOT_SET'),
            'cea_path': os.getenv('CEA_PATH', 'NOT_SET'),
            'bgm_volume': os.getenv('BGM_VOLUME', '0.5'),
            'effect_volume': os.getenv('EFFECT_VOLUME', '0.7')
        }
    
    def validate_config(self, config: Dict) -> bool:
        """設定の妥当性をチェック"""
        required_fields = [
            'mining.wallet_address',
            'mining.pool_url',
            'mining.worker_name'
        ]
        
        for field in required_fields:
            keys = field.split('.')
            value = config
            for key in keys:
                if key not in value:
                    print(f"❌ 必須設定が不足: {field}")
                    return False
                value = value[key]
            
            if value == 'YOUR_WALLET_ADDRESS_HERE':
                print(f"⚠️ デフォルト値が設定されています: {field}")
        
        return True 