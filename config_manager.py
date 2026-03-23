#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール

環境変数とJSONファイルから設定を読み込み、ゲーム全体に提供します。
読み込み優先順位: 環境変数 > data/reality_config.json > config_template.json > デフォルト値

新しい設定項目を追加する場合:
    1. _get_default_config() に項目を追加する
    2. _override_with_env_vars() に対応する環境変数マッピングを追加する（任意）
    3. config_template.json と .env.example にも記載を追加する
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    """
    ゲーム設定を一元管理するクラス。

    ゲーム起動時に一度インスタンス化して load_config() を呼び出すことで、
    全サブシステムが共通の設定辞書を参照できるようになります。
    """

    def __init__(self, config_dir: Path = Path("data")):
        """
        Args:
            config_dir: 設定ファイルを格納するディレクトリ (デフォルト: data/)
        """
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)

        # ユーザーが編集する設定ファイル
        self.config_file = config_dir / "reality_config.json"
        # 初回セットアップ用のテンプレート
        self.template_file = Path("config_template.json")

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def load_config(self) -> Dict:
        """
        設定を読み込んで返します。
        環境変数がファイルの値より優先されます。

        Returns:
            設定辞書。キー構造は _get_default_config() を参照。
        """
        config = self._load_from_file()
        config = self._override_with_env_vars(config)
        return config

    def save_config(self, config: Dict):
        """
        設定ファイルに書き込みます。

        Args:
            config: 保存する設定辞書
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ 設定を保存しました: {self.config_file}")
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")

    def create_config_from_template(self) -> bool:
        """
        config_template.json を元に設定ファイルを生成します。
        ゲーム初回起動時のセットアップに使用します。

        Returns:
            True: 作成成功、False: 既存ファイルがある・テンプレートが見つからない
        """
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
        """
        機密情報（APIキー等）を環境変数から取得します。
        これらの値は設定ファイルではなく環境変数で管理してください。

        Returns:
            機密設定の辞書。値が未設定の場合は 'NOT_SET' を返します。
        """
        return {
            'cea_path': os.getenv('CEA_PATH', 'NOT_SET'),
            'bgm_volume': os.getenv('BGM_VOLUME', '0.5'),
            'effect_volume': os.getenv('EFFECT_VOLUME', '0.7'),
        }

    def validate_config(self, config: Dict) -> bool:
        """
        設定の妥当性をチェックします。
        必須フィールドが存在し、デフォルト値のままになっていないか検証します。

        新しい必須フィールドを追加する場合は required_fields リストに追記してください。

        Args:
            config: 検証する設定辞書

        Returns:
            True: 検証OK、False: 必須項目が不足
        """
        # 現状は必須フィールドなし。将来の拡張のためにロジックを残す。
        required_fields: list = []

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

    # ------------------------------------------------------------------
    # 内部ヘルパー
    # ------------------------------------------------------------------

    def _load_from_file(self) -> Dict:
        """
        設定ファイルを優先順位に従って読み込みます。
        ファイルが壊れていたり存在しない場合はデフォルト設定を返します。
        """
        # ユーザー設定ファイルを最優先
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 設定ファイル読み込みエラー: {e}")

        # フォールバック: テンプレートを読む
        if self.template_file.exists():
            try:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ テンプレートファイル読み込みエラー: {e}")

        # 最終フォールバック: コード内のデフォルト値
        return self._get_default_config()

    def _override_with_env_vars(self, config: Dict) -> Dict:
        """
        環境変数で設定値を上書きします。
        .env ファイルや CI/CD の秘密変数から安全に値を注入するために使います。

        新しい環境変数を追加する場合はここに追記してください。
        """
        # CEA実行ファイルのパス
        if os.getenv('CEA_PATH'):
            config['cea']['cea_path'] = os.getenv('CEA_PATH')

        # ニュースAPIキー（世界観測システム用）
        if os.getenv('NEWS_API_KEY'):
            config.setdefault('world_observation', {})
            config['world_observation']['news_api_key'] = os.getenv('NEWS_API_KEY')

        # 監視間隔（秒）
        if os.getenv('MONITORING_INTERVAL'):
            try:
                config['monitoring']['interval'] = int(os.getenv('MONITORING_INTERVAL'))
            except ValueError:
                pass  # 不正な値は無視してファイルの設定を使う

        # BGM音量 (0.0〜1.0)
        if os.getenv('BGM_VOLUME'):
            try:
                config['audio']['bgm_volume'] = float(os.getenv('BGM_VOLUME'))
            except ValueError:
                pass

        # 効果音音量 (0.0〜1.0)
        if os.getenv('EFFECT_VOLUME'):
            try:
                config['audio']['effect_volume'] = float(os.getenv('EFFECT_VOLUME'))
            except ValueError:
                pass

        return config

    def _get_default_config(self) -> Dict:
        """
        設定ファイルが存在しない場合に使われるデフォルト設定です。
        新しいサブシステムを追加したら、このメソッドにもデフォルト値を追加してください。
        """
        return {
            'game_name': 'Crypto Adventure RPG',
            'version': '2.0.0',
            'output_dir': 'data',

            # 発電所システム設定
            'power_plant': {
                'enabled': True,
                'monitoring_interval': 3600,  # 秒
            },

            # ファイル監視設定
            'monitoring': {
                'enabled': True,
                'interval': 30,       # 秒
                'auto_sync': True,
            },

            # 世界観測（ニュースAPI）設定
            'world_observation': {
                'enabled': True,
                'news_api_key': '',   # 環境変数 NEWS_API_KEY で指定を推奨
            },

            # CEA計算ツール設定
            'cea': {
                'cea_path': 'C:\\CEA\\cea.exe',
                'input_files': [],
                'output_dir': 'data/cea_results',
            },

            # 発電所設計ファイル保存設定
            'power_plants': {
                'monitoring_enabled': True,
                'solar_panels': [],
                'wind_turbines': [],
                'battery_systems': [],
                'output_dir': 'data/power_plant_designs',
            },

            # ファイル監視対象設定
            'file_watchers': {
                'enabled': True,
                'watch_dirs': [
                    'C:\\srbminer',
                    'C:\\CEA\\output',
                    'data',
                ],
                'file_patterns': ['*.log', '*.txt', '*.json', '*.out'],
            },

            # 音声設定
            'audio': {
                'bgm_volume': 0.5,     # 0.0（無音）〜1.0（最大）
                'effect_volume': 0.7,  # 0.0（無音）〜1.0（最大）
                'enabled': True,
            },
        }