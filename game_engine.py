#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ゲームエンジンモジュール

プレイヤーの状態（経験値・日数・称号）とウォレット（Crypto残高・活動履歴）を
一元管理するゲームの中核クラスです。

セーブデータ構成:
    state.json  - ゲーム進行状態（日数・経験値・称号リスト等）
    wallet.json - 資産と活動履歴（Crypto残高・CEA/発電/観測の記録リスト）

新しい「アクティビティ（活動種別）」を追加する場合:
    1. create_default_wallet() にリスト/カウンターを追加する
    2. add_xxx_result(result) のようなメソッドを実装して wallet に追記 + 称号チェックを呼ぶ
    3. calculate_stats() に新しいカウントを追加する

新しい「称号」を追加する場合:
    1. assets/titles.json にエントリを追加する（ゲーム起動時に自動読み込み）
    2. check_title_condition() に対応する評価ロジックを追加する
    3. _get_title_progress() にも進捗表示の文字列を追加する
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from audio_manager import AudioManager
from reality_connector import RealityConnector


class GameEngine:
    """
    ゲームの状態とウォレットを管理する中核クラス。

    全てのサブシステム（CEA・発電・観測等）はこのクラスを通じて
    経験値・Crypto・活動履歴を記録します。
    """

    def __init__(self, data_dir: Path, assets_dir: Path, save_dir: Path):
        """
        Args:
            data_dir:   データファイル格納ディレクトリ (例: Path("data"))
            assets_dir: 称号定義など静的ファイルのディレクトリ (例: Path("assets"))
            save_dir:   セーブファイルのディレクトリ (例: Path("save"))
        """
        self.data_dir   = data_dir
        self.assets_dir = assets_dir
        self.save_dir   = save_dir

        # セーブファイルはプロジェクトルートに置く（起動ディレクトリ固定前提）
        self.state_file  = Path("state.json")
        self.wallet_file = Path("wallet.json")

        # サブシステムの初期化
        self.audio_manager    = AudioManager(data_dir)
        self.reality_connector = RealityConnector(data_dir)

        # 起動時にセーブデータを読み込む
        self.load_state()
        self.load_wallet()
        self.initialize_titles()

        # BGMファイルがある場合のみ再生開始
        if self.audio_manager.bgm_files:
            self.audio_manager.play_bgm()

        # 現実連動（ファイル監視など）を開始
        self.reality_connector.start_monitoring()

    # ------------------------------------------------------------------
    # セーブ・ロード
    # ------------------------------------------------------------------

    def load_state(self):
        """state.json からゲーム状態を読み込みます。読み込み失敗時はデフォルトを生成します。"""
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

    def save_state(self):
        """ゲーム状態を state.json に書き込みます。"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ゲーム状態の保存に失敗: {e}")
            self.audio_manager.play_effect('error')

    def load_wallet(self):
        """wallet.json からウォレット情報を読み込みます。読み込み失敗時はデフォルトを生成します。"""
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

    def save_wallet(self):
        """ウォレット情報を wallet.json に書き込みます。"""
        try:
            with open(self.wallet_file, 'w', encoding='utf-8') as f:
                json.dump(self.wallet, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ウォレット情報の保存に失敗: {e}")
            self.audio_manager.play_effect('error')

    def create_default_state(self):
        """
        初回起動時や読み込み失敗時のデフォルトゲーム状態を作成します。
        新しい状態フィールドを追加する場合はこの辞書に追記してください。
        """
        self.state = {
            "current_day":     1,
            "experience":      0,
            "total_actions":   0,
            "titles":          [],       # 獲得済み称号ID のリスト
            "title_history":   [],       # 称号獲得の詳細ログ
            "story_progress":  0,
            "achievements":    [],
            "quests":          [],
            "energy_balance":  0.0,
            "last_action_date":   datetime.now().isoformat(),
            "game_start_date":    datetime.now().isoformat(),
        }
        self.save_state()

    def create_default_wallet(self):
        """
        初回起動時や読み込み失敗時のデフォルトウォレットを作成します。
        新しいアクティビティを追加する場合はこの辞書に追記してください。
        """
        self.wallet = {
            # --- Crypto残高 ---
            "crypto_balance":       0.0,  # 当日分（日次リセットされる）
            "total_crypto_balance": 0.0,  # 累計

            # --- エネルギー ---
            "energy_consumed":       0.0,  # 当日消費量 kWh（日次リセット）
            "total_energy_consumed": 0.0,  # 累計
            "energy_generated":      0.0,  # 当日発電量 kWh（日次リセット）
            "total_energy_generated":0.0,  # 累計

            # --- 活動履歴リスト（全期間） ---
            "cea_calculations":   [],  # CEA計算記録
            "plant_designs":      [],  # 発電所設計記録
            "optics_observations":[],  # 天体観測記録

            # --- 活動累計カウント ---
            "total_cea_time":    0,   # CEA実行回数
            "total_plant_time":  0,   # 発電所設計回数
            "total_optics_time": 0,   # 観測合計時間（分）
        }
        self.save_wallet()

    # ------------------------------------------------------------------
    # 活動記録（サブシステムからの結果を受け取るメソッド群）
    # ------------------------------------------------------------------

    def add_cea_result(self, result: Dict):
        """
        CEA計算結果をウォレットに追記し、称号チェックを行います。

        Args:
            result: CEALearningSystem.record_cea_calculation() の戻り値
        """
        self.wallet['cea_calculations'].append(result)
        self.wallet['total_cea_time'] += 1
        self.save_wallet()
        self.check_titles()

    def add_power_plant_result(self, result: Dict):
        """
        発電所設計結果をウォレットに追記し、当日発電量に加算します。

        Args:
            result: PowerGenerationLearningSystem.record_power_generation() の戻り値
        """
        self.wallet['plant_designs'].append(result)

        # 年間発電量 → 1日分に換算して当日残高に加算
        daily_generation = result.get('annual_generation', 0) / 365
        self.wallet['energy_generated'] += daily_generation

        self.wallet['total_plant_time'] += 1
        self.save_wallet()
        self.check_titles()

    def add_plant_design(self, result: Dict):
        """add_power_plant_result() の別名（後方互換性のために残してあります）。"""
        self.add_power_plant_result(result)

    def add_optics_observation(self, result: Dict):
        """
        天体観測結果をウォレットに追記し、称号チェックを行います。

        Args:
            result: AstronomicalObservationSystem.record_observation() の戻り値
        """
        self.wallet['optics_observations'].append(result)
        self.wallet['total_optics_time'] += result.get('duration_minutes', 0)
        self.save_wallet()
        self.check_titles()

    def add_experience(self, experience: int):
        """
        経験値を追加します。

        Args:
            experience: 追加する経験値（整数）
        """
        self.state.setdefault('experience', 0)
        self.state['experience'] += experience
        self.save_state()
        print(f"💎 経験値 +{experience} 獲得! (総経験値: {self.state['experience']})")
        self.audio_manager.play_effect('action_select')

    def add_crypto(self, amount: float):
        """
        Crypto残高を追加します。

        Args:
            amount: 追加するXMR量（浮動小数点数）
        """
        self.wallet['crypto_balance'] += amount
        self.save_wallet()
        print(f"💰 Crypto +{amount:.6f} XMR 獲得! (残高: {self.wallet['crypto_balance']:.6f} XMR)")
        self.audio_manager.play_effect('action_select')

    def use_action(self) -> bool:
        """
        行動回数を1消費します。残り0の場合は False を返します。

        Returns:
            True: 消費成功、False: 行動回数不足
        """
        if self.state.get('actions_remaining', 0) > 0:
            self.state['actions_remaining'] -= 1
            self.state['total_actions']     += 1
            self.save_state()
            self.audio_manager.play_effect('action_select')
            return True
        return False

    # ------------------------------------------------------------------
    # 日数進行
    # ------------------------------------------------------------------

    def advance_to_next_day(self) -> bool:
        """
        メインメニューから呼び出される「次の日へ進む」のエントリポイント。

        Returns:
            True: 進行成功、False: エラー発生
        """
        try:
            result = self.advance_day()
            return bool(result)
        except Exception as e:
            print(f"❌ 次の日への進行でエラーが発生: {e}")
            return False

    def advance_day(self) -> Dict:
        """
        日数を1進め、日次リセット・称号チェック・ストーリーイベントを処理します。

        Returns:
            {
                'new_day':      int,  新しい日数
                'today_summary': Dict, 前日のアクティビティサマリー
                'new_titles':   List, 新たに獲得した称号リスト
                'story_event':  Dict|None, ストーリーイベント（ない場合は None）
            }
        """
        print(f"\n🌅 {self.state['current_day']}日目を終了")
        print("=" * 50)
        self.audio_manager.play_effect('next_day')

        # 翌日に進む前に当日のサマリーを取得（リセット前に呼ぶ必要がある）
        today_summary = self.get_today_summary()

        # 日付を進める
        self.state['current_day']    += 1
        self.state['story_progress'] += 1

        # 日次データをリセットし、累計に加算
        self._reset_daily_values()

        # 称号チェック・ストーリーイベント取得
        new_titles   = self.check_titles()
        story_event  = self.get_story_event()

        self.save_state()
        self.save_wallet()

        return {
            'new_day':      self.state['current_day'],
            'today_summary': today_summary,
            'new_titles':   new_titles,
            'story_event':  story_event,
        }

    def _reset_daily_values(self):
        """
        当日の Crypto/エネルギー残高を累計に移し、日次値をゼロにリセットします。
        日次でリセットされるべき値を追加した場合はこのメソッドを更新してください。
        """
        # 累計に加算
        self.wallet['total_crypto_balance']    += self.wallet['crypto_balance']
        self.wallet['total_energy_consumed']   += self.wallet['energy_consumed']
        self.wallet['total_energy_generated']  += self.wallet['energy_generated']

        # 日次値をリセット
        self.wallet['crypto_balance']  = 0.0
        self.wallet['energy_consumed'] = 0.0
        self.wallet['energy_generated']= 0.0

        print("🔄 日次リセット完了:")
        print(f"   💰 日次Crypto残高: 0.000000 XMR")
        print(f"   ⚡ 日次消費電力: 0.00 kWh")
        print(f"   🌞 日次発電量: 0.00 kWh")
        print(f"   📊 累積Crypto残高: {self.wallet['total_crypto_balance']:.6f} XMR")
        print(f"   📊 累積消費電力: {self.wallet['total_energy_consumed']:.2f} kWh")
        print(f"   📊 累積発電量: {self.wallet['total_energy_generated']:.2f} kWh")

    # ------------------------------------------------------------------
    # 統計・サマリー
    # ------------------------------------------------------------------

    def calculate_stats(self) -> Dict:
        """
        称号チェックや統計表示で使う現在のプレイヤー統計を計算します。
        新しい称号の条件に使う統計値を追加する場合はここに追記してください。
        """
        cea_count    = len(self.wallet.get('cea_calculations', []))
        plant_count  = len(self.wallet.get('plant_designs', []))
        optics_count = len(self.wallet.get('optics_observations', []))

        # 発電所タイプ別カウント（称号条件で使用）
        plant_designs    = self.wallet.get('plant_designs', [])
        solar_plant_count = sum(1 for p in plant_designs if p.get('type') == 'solar')
        wind_plant_count  = sum(1 for p in plant_designs if p.get('type') == 'wind')

        # マスター判定: 全カテゴリで一定回数をこなしているか
        all_categories_master = (
            cea_count    >= 10 and
            plant_count  >= 5  and
            optics_count >= 5
        )

        return {
            'cea_count':           cea_count,
            'plant_count':         plant_count,
            'optics_count':        optics_count,
            'solar_plant_count':   solar_plant_count,
            'wind_plant_count':    wind_plant_count,
            'crypto_balance':      self.wallet.get('crypto_balance', 0.0),
            'energy_consumed':     self.wallet.get('energy_consumed', 0.0),
            'energy_generated':    self.wallet.get('energy_generated', 0.0),
            'all_categories_master': all_categories_master,
        }

    def get_today_summary(self) -> Dict:
        """当日のアクティビティ集計を返します（翌日進行前の振り返りに使います）。"""
        today = self.state['current_day']

        today_cea    = [c for c in self.wallet.get('cea_calculations', [])   if c.get('day') == today]
        today_plant  = [p for p in self.wallet.get('plant_designs', [])      if p.get('day') == today]
        today_optics = [o for o in self.wallet.get('optics_observations', []) if o.get('day') == today]

        return {
            'cea_count':        len(today_cea),
            'plant_count':      len(today_plant),
            'optics_count':     len(today_optics),
            'xmr_earned':       0,   # 将来的に詳細集計を追加予定
            'energy_consumed':  0,
            'energy_generated': sum(p.get('daily_generation', 0) for p in today_plant),
        }

    def get_game_status(self) -> Dict:
        """メインメニューや統計画面で使うゲーム状態のスナップショットを返します。"""
        return {
            'current_day':   self.state['current_day'],
            'total_actions': self.state['total_actions'],
            'story_progress':self.state['story_progress'],
            'titles':        self.state['titles'],
            'stats':         self.calculate_stats(),
            'wallet':        self.wallet,
        }

    def get_story_event(self) -> Optional[Dict]:
        """
        現在の日数に対応するストーリーイベントを返します。
        新しいマイルストーンを追加する場合は story_events 辞書に追記してください。
        """
        story_events = {
            1: {
                'title':       '冒険の始まり',
                'description': 'あなたの技術者としての旅が始まりました。',
                'type':        'story',
            },
            7: {
                'title':       '一週間の成果',
                'description': '一週間の活動を振り返り、新たな目標が見えてきました。',
                'type':        'milestone',
            },
            30: {
                'title':       '一ヶ月の軌跡',
                'description': '一ヶ月の活動により、技術者として大きく成長しました。',
                'type':        'milestone',
            },
            100: {
                'title':       '百日の挑戦',
                'description': '百日の継続により、真の技術者への道が開けました。',
                'type':        'milestone',
            },
        }
        return story_events.get(self.state['current_day'])

    # ------------------------------------------------------------------
    # 称号システム
    # ------------------------------------------------------------------

    def initialize_titles(self):
        """
        assets/titles.json が存在しない場合にデフォルト称号ファイルを生成します。
        新しい称号を追加したい場合は assets/titles.json を直接編集してください。
        """
        titles_file = self.assets_dir / "titles.json"
        if titles_file.exists():
            return  # 既に存在する場合は何もしない

        default_titles = {
            "titles": [
                {
                    "id": "rocket_scientist",
                    "name": "重力を操る者",
                    "description": "CEA計算を10回実行した",
                    "condition": "cea_count >= 10",
                    "category": "cea",
                },
                {
                    "id": "energy_wizard",
                    "name": "エネルギー魔術師",
                    "description": "発電所を5基設計した",
                    "condition": "plant_count >= 5",
                    "category": "plant",
                },
                {
                    "id": "solar_master",
                    "name": "太陽の使い手",
                    "description": "太陽光発電所を3基設計した",
                    "condition": "solar_plant_count >= 3",
                    "category": "plant",
                },
                {
                    "id": "wind_master",
                    "name": "風の使い手",
                    "description": "風力発電所を2基設計した",
                    "condition": "wind_plant_count >= 2",
                    "category": "plant",
                },
                {
                    "id": "optics_observer",
                    "name": "星の観測者",
                    "description": "天体観測を5回実行した",
                    "condition": "optics_count >= 5",
                    "category": "optics",
                },
                {
                    "id": "energy_self_sufficient",
                    "name": "エネルギー自給自足",
                    "description": "発電量が消費量を上回った",
                    "condition": "energy_generated > energy_consumed",
                    "category": "energy",
                },
                {
                    "id": "master_engineer",
                    "name": "マスターエンジニア",
                    "description": "全ての分野で称号を獲得した",
                    "condition": "all_categories_master",
                    "category": "master",
                },
            ]
        }

        try:
            with open(titles_file, 'w', encoding='utf-8') as f:
                json.dump(default_titles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 称号ファイルの作成に失敗: {e}")

    def check_titles(self) -> List[Dict]:
        """
        全称号の獲得条件を評価し、新たに獲得した称号があれば State に記録して返します。

        Returns:
            新たに獲得した称号のリスト（既存のものは含まない）
        """
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

        stats     = self.calculate_stats()
        new_titles = []

        for title in titles_data.get('titles', []):
            title_id = title.get('id')

            # 既に獲得済みはスキップ
            if title_id in self.state.get('titles', []):
                continue

            if self.check_title_condition(title, stats):
                # 称号獲得時の詳細情報を付与
                title_info = {
                    'id':          title_id,
                    'name':        title['name'],
                    'description': title['description'],
                    'category':    title.get('category', 'general'),
                    'earned_date': datetime.now().isoformat(),
                    'earned_day':  self.state['current_day'],
                    'stats_at_earning': stats.copy(),  # 獲得時点の統計スナップショット
                }

                self.state.setdefault('title_history', []).append(title_info)
                self.state.setdefault('titles', []).append(title_id)
                new_titles.append(title_info)

                self.audio_manager.play_effect('title_earned')
                self._show_title_notification(title_info)

        if new_titles:
            self.save_state()
            print(f"\n🏆 新しく獲得した称号: {len(new_titles)}個")

        return new_titles

    def check_title_condition(self, title: Dict, stats: Dict) -> bool:
        """
        1件の称号の獲得条件を評価します。
        新しい称号条件を追加した場合はこのメソッドに elif を追加してください。

        Args:
            title: 称号定義辞書（titles.json の1エントリ）
            stats: calculate_stats() の戻り値

        Returns:
            True: 達成済み、False: 未達成
        """
        condition = title.get('condition', '')

        # 条件文字列 → 評価ロジックのマッピング
        condition_checks = {
            "crypto_balance >= 1.0":         lambda: stats['crypto_balance'] >= 1.0,
            "cea_count >= 10":               lambda: stats['cea_count'] >= 10,
            "plant_count >= 5":              lambda: stats['plant_count'] >= 5,
            "solar_plant_count >= 3":        lambda: stats['solar_plant_count'] >= 3,
            "wind_plant_count >= 2":         lambda: stats['wind_plant_count'] >= 2,
            "optics_count >= 5":             lambda: stats['optics_count'] >= 5,
            "energy_generated > energy_consumed": lambda: stats['energy_generated'] > stats['energy_consumed'],
            "all_categories_master":         lambda: stats['all_categories_master'],
        }

        check_fn = condition_checks.get(condition)
        return check_fn() if check_fn else False

    def _get_title_progress(self, title: Dict, stats: Dict) -> str:
        """
        未獲得の称号について、現在の進捗を人間が読める文字列で返します。
        新しい称号条件を追加した場合はここにも追記してください。

        Returns:
            進捗文字列（例: "3/10 回"）、対応する条件がない場合は空文字列
        """
        condition = title.get('condition', '')

        progress_templates = {
            "crypto_balance >= 1.0":  lambda: f"{stats['crypto_balance']:.6f}/1.0 XMR",
            "cea_count >= 10":        lambda: f"{stats['cea_count']}/10 回",
            "plant_count >= 5":       lambda: f"{stats['plant_count']}/5 基",
            "solar_plant_count >= 3": lambda: f"{stats['solar_plant_count']}/3 基",
            "wind_plant_count >= 2":  lambda: f"{stats['wind_plant_count']}/2 基",
            "optics_count >= 5":      lambda: f"{stats['optics_count']}/5 回",
        }

        template_fn = progress_templates.get(condition)
        return template_fn() if template_fn else ""

    def _show_title_notification(self, title_info: Dict):
        """称号獲得時のコンソール通知を表示します。"""
        print(f"\n" + "=" * 60)
        print(f"🏆 新しい称号を獲得しました！")
        print(f"   📛 {title_info['name']}")
        print(f"   📝 {title_info['description']}")
        print(f"   🏷️ カテゴリ: {title_info['category']}")
        print(f"   📅 獲得日: {self.state['current_day']}日目")
        print(f"   ⏰ 獲得時刻: {title_info['earned_date'][:19]}")
        print("=" * 60)

    def get_title_history(self) -> List[Dict]:
        """称号獲得履歴を返します。"""
        return self.state.get('title_history', [])

    def show_title_status(self):
        """全称号の獲得状況を、カテゴリ別に進捗付きで表示します。"""
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

        stats         = self.calculate_stats()
        earned_ids    = set(self.state.get('titles', []))

        print(f"\n🏆 称号状況 ({self.state['current_day']}日目)")
        print("=" * 60)

        # カテゴリ別にグルーピングして表示
        categories: Dict[str, List] = {}
        for title in titles_data.get('titles', []):
            category = title.get('category', 'general')
            categories.setdefault(category, []).append(title)

        for category, titles in categories.items():
            print(f"\n📂 {category.upper()} カテゴリ:")
            for title in titles:
                status_icon = "✅" if title['id'] in earned_ids else "⏳"
                print(f"   {status_icon} {title['name']}: {title['description']}")

                if title['id'] not in earned_ids:
                    progress = self._get_title_progress(title, stats)
                    if progress:
                        print(f"      📊 進捗: {progress}")

        # 最近の獲得履歴（最大5件）
        history = self.get_title_history()
        if history:
            print(f"\n📜 最近獲得した称号:")
            for title in history[-5:]:
                print(f"   🏆 {title['name']} ({title['earned_day']}日目)")

    # ------------------------------------------------------------------
    # 統計ダッシュボード
    # ------------------------------------------------------------------

    def show_mission_status(self):
        """ミッション状況ダッシュボードを表示します。"""
        stats = self.calculate_stats()

        print("📊 ミッション統計:")
        print(f"   📅 現在の日: {self.state['current_day']}日目")
        print(f"   💰 日次Crypto残高: {self.wallet.get('crypto_balance', 0):.6f} XMR")
        print(f"   ⚡ 日次消費電力: {self.wallet.get('energy_consumed', 0):.2f} kWh")
        print(f"   🌞 日次発電量: {self.wallet.get('energy_generated', 0):.2f} kWh")

        print("\n📊 累積統計:")
        print(f"   💰 累積Crypto残高: {self.wallet.get('total_crypto_balance', 0):.6f} XMR")
        print(f"   ⚡ 累積消費電力: {self.wallet.get('total_energy_consumed', 0):.2f} kWh")
        print(f"   🌞 累積発電量: {self.wallet.get('total_energy_generated', 0):.2f} kWh")

        print("\n📈 活動統計:")
        print(f"   🚀 CEA計算回数: {stats['cea_count']}回")
        print(f"   📊 発電監視回数: {stats['plant_count']}回")
        print(f"   🔭 天体観測回数: {stats['optics_count']}回")

        earned_count = len(self.state.get('titles', []))
        print(f"\n🏆 称号統計:")
        print(f"   🏆 獲得称号: {earned_count}個")

        if 'experience' in self.state:
            print(f"   💎 総経験値: {self.state['experience']}")

        print("\n💡 ヒント:")
        print("   • 発電監視・ミッションで発電データを記録するとミッションが進行します")
        print("   • ミッションを完了すると経験値とCryptoを獲得できます")
        print("   • 日次・週次・実績ミッションがあります")