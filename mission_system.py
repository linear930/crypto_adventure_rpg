#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミッション・称号管理システム

JSON形式で定義されたミッション/称号の進行状況を追跡し、
プレイヤーのアクションによってミッション達成・称号解放を判定します。

データファイル構成:
    data/missions.json        - ミッション定義（main_missions, sub_missions）
    data/titles.json          - 称号定義
    data/mission_progress.json - プレイヤーの進行状況（累計/日次カウント等）
    data/action_logs.json     - アクションの生ログ（全履歴）

新しいミッションを追加する方法:
    1. missions.json の main_missions または sub_missions にエントリを追加する
    2. "condition" は condition_parser.py が解析できるテキスト形式で記述する
       例: {"type": "total_action_count", "action": "cea", "operator": ">=", "count": 5}
    3. ゲームを再起動すると自動的に読み込まれます

新しいアクション種別を追加する方法:
    1. _get_empty_action_counts() にアクション名（str）を追加する
    2. ゲームコード側で log_action(新アクション名, データ) を呼び出す
    3. condition_parser.py の action_mapping にもマッピングを追加する
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from condition_parser import ConditionParser


class MissionSystem:
    """
    ミッション達成と称号解放を管理するクラス。

    使い方:
        ms = MissionSystem()
        ms.log_action("cea", {"isp": 420, "Pc": 200})  # アクションを記録
        completed = ms.check_missions("cea", action_data)  # 達成したミッションを取得
        titles    = ms.check_titles("cea", action_data)    # 解放された称号を取得
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

        # データファイルパス（将来的にファイル名を変える場合はここを変更）
        self.missions_file  = self.data_dir / "missions.json"
        self.titles_file    = self.data_dir / "titles.json"
        self.progress_file  = self.data_dir / "mission_progress.json"
        self.action_logs_file = self.data_dir / "action_logs.json"

        # 起動時に全データをメモリに読み込む
        self.missions    = self._load_json(self.missions_file,    {"main_missions": [], "sub_missions": []})
        self.titles      = self._load_json(self.titles_file,      {"titles": []})
        self.progress    = self._load_progress()
        self.action_logs = self._load_json(self.action_logs_file, [])

        self.condition_parser = ConditionParser()

    # ------------------------------------------------------------------
    # アクション記録（ゲーム側から呼び出すメインAPI）
    # ------------------------------------------------------------------

    def log_action(self, action_type: str, action_data: Dict = None):
        """
        プレイヤーのアクションを記録します。
        ミッション判定の前に必ずこのメソッドを呼び出してください。

        Args:
            action_type: アクション種別（例: "cea", "power_plant", "astronomy"）
            action_data: アクションの詳細データ（例: {"isp": 420, "Pc": 150}）
        """
        log_entry = {
            "timestamp":   datetime.now().isoformat(),
            "date":        datetime.now().strftime("%Y-%m-%d"),
            "action_type": action_type,
            "data":        action_data or {},
        }

        self.action_logs.append(log_entry)
        self._save_json(self.action_logs_file, self.action_logs)

        # 累計・日次カウントを更新
        self._update_action_count(action_type)

        # 数値メトリクス（kWh等）を更新
        if action_data:
            self._update_daily_metrics(action_data)

    # ------------------------------------------------------------------
    # ミッション・称号チェック
    # ------------------------------------------------------------------

    def check_missions(self, action_type: str, action_data: Dict = None) -> List[Dict]:
        """
        今回のアクションで達成されたミッションを返します。

        Args:
            action_type: 実行されたアクション種別
            action_data: アクションの詳細データ

        Returns:
            新たに達成されたミッションのリスト（空の場合あり）
        """
        newly_completed = []

        all_missions = (
            self.missions.get("main_missions", []) +
            self.missions.get("sub_missions", [])
        )

        for mission in all_missions:
            mission_id = mission["id"]
            already_done = mission_id in self.progress["completed_missions"]
            if not already_done and self._check_condition(mission, action_type, action_data):
                newly_completed.append(mission)
                self.progress["completed_missions"].append(mission_id)

        self._save_progress()
        return newly_completed

    def check_titles(self, action_type: str, action_data: Dict = None) -> List[Dict]:
        """
        今回のアクションで解放された称号を返します。

        Args:
            action_type: 実行されたアクション種別
            action_data: アクションの詳細データ

        Returns:
            新たに解放された称号のリスト（空の場合あり）
        """
        newly_unlocked = []

        for title in self.titles.get("titles", []):
            title_id = title["id"]
            already_unlocked = title_id in self.progress["unlocked_titles"]
            if not already_unlocked and self._check_condition(title, action_type, action_data):
                newly_unlocked.append(title)
                self.progress["unlocked_titles"].append(title_id)

        self._save_progress()
        return newly_unlocked

    # ------------------------------------------------------------------
    # データ参照
    # ------------------------------------------------------------------

    def get_available_missions(self) -> Dict:
        """未完了のミッション一覧を返します。"""
        completed_ids = set(self.progress["completed_missions"])
        return {
            "main_missions": [
                m for m in self.missions.get("main_missions", [])
                if m["id"] not in completed_ids
            ],
            "sub_missions": [
                m for m in self.missions.get("sub_missions", [])
                if m["id"] not in completed_ids
            ],
        }

    def get_unlocked_titles(self) -> List[Dict]:
        """解放済みの称号リストを返します。"""
        unlocked_ids = set(self.progress["unlocked_titles"])
        return [t for t in self.titles.get("titles", []) if t["id"] in unlocked_ids]

    # ------------------------------------------------------------------
    # データ追加（スクリプトからミッション/称号を動的追加する場合に使用）
    # ------------------------------------------------------------------

    def add_mission(self, mission_data: Dict, mission_type: str = "sub_missions"):
        """
        ミッションをメモリとファイルに追加します。

        Args:
            mission_data: ミッション定義辞書
            mission_type: "main_missions" または "sub_missions"
        """
        self.missions.setdefault(mission_type, [])
        self.missions[mission_type].append(mission_data)
        self._save_json(self.missions_file, self.missions)

    def add_title(self, title_data: Dict):
        """称号をメモリとファイルに追加します。"""
        self.titles.setdefault("titles", [])
        self.titles["titles"].append(title_data)
        self._save_json(self.titles_file, self.titles)

    # ------------------------------------------------------------------
    # ミッション条件チェック（内部ロジック）
    # ------------------------------------------------------------------

    def _check_condition(self, mission_or_title: Dict, action_type: str, action_data: Dict) -> bool:
        """
        ミッション/称号の条件を評価します。

        新しい condition type を追加する場合はここに elif 節を追加してください。
        """
        condition = mission_or_title.get("condition", {})
        cond_type = condition.get("type", "unknown")

        if cond_type == "simple":
            return self._check_simple(condition, action_type, action_data)
        elif cond_type == "total_action_count":
            return self._check_total_action_count(condition, action_type)
        elif cond_type == "daily_action_count":
            return self._check_daily_action_count(condition, action_type)
        elif cond_type == "completion":
            return self._check_completion(condition, action_type, action_data)
        elif cond_type == "compound_and":
            return self._check_compound_and(condition, action_type, action_data)
        elif cond_type == "consecutive_days":
            return self._check_consecutive_days(condition, action_type)
        elif cond_type == "incremental_increase":
            return self._check_incremental_increase(condition)
        elif cond_type == "same_day_both":
            return self._check_same_day_both(condition, action_type)
        elif cond_type == "over_period":
            return self._check_over_period(condition, action_type, action_data)
        elif cond_type == "percentage":
            return self._check_percentage(condition, action_type, action_data)
        elif cond_type == "range_check":
            return self._check_range(condition, action_type, action_data)
        elif cond_type == "first_action":
            # レガシー互換: 最初のアクション達成
            return (
                condition.get("action") == action_type and
                self.progress["action_counts"].get(action_type, 0) == 1
            )

        return False  # 未知の条件タイプは達成しない

    def _check_simple(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """単一メトリクスの閾値比較: `action` の `metric` operator value"""
        if condition.get("action") != action_type or not action_data:
            return False

        metric = condition["metric"]
        if metric not in action_data:
            return False

        return self._compare(action_data[metric], condition["operator"], condition["value"])

    def _check_total_action_count(self, condition: Dict, action_type: str) -> bool:
        """累計実行回数チェック"""
        if condition.get("action") != action_type:
            return False

        current_count = self.progress["action_counts"].get(action_type, 0)
        return self._compare(current_count, condition["operator"], condition["count"])

    def _check_daily_action_count(self, condition: Dict, action_type: str) -> bool:
        """当日の実行回数チェック"""
        if condition.get("action") != action_type:
            return False

        current_count = self.progress["daily_actions"].get(action_type, 0)
        return self._compare(current_count, condition["operator"], condition["count"])

    def _check_completion(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """
        特定サブ条件の完了チェック（現在は簡易実装）。
        将来的により詳細な条件評価が必要な場合はここを拡張してください。
        """
        if condition.get("action") != action_type or not action_data:
            return False
        return True  # TODO: condition["condition"] の文字列内容に基づいた詳細チェック

    def _check_compound_and(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """AND複合条件: 全サブ条件が True の場合のみ True"""
        return all(
            self._check_simple(sub_cond, action_type, action_data)
            for sub_cond in condition.get("conditions", [])
        )

    def _check_consecutive_days(self, condition: Dict, action_type: str) -> bool:
        """連続日数チェック"""
        if condition.get("action") != action_type:
            return False

        current_consecutive = self.progress["consecutive_days"].get(action_type, 0)
        return current_consecutive >= condition["days"]

    def _check_incremental_increase(self, condition: Dict) -> bool:
        """指定期間にわたってメトリクスが継続的に増加しているかチェック"""
        metric = condition["metric"]
        required_days = condition["days"]

        # 直近 required_days 件のログからメトリクスを抽出
        relevant_logs = [
            log for log in self.action_logs[-required_days:]
            if metric in log.get("data", {})
        ]

        if len(relevant_logs) < required_days:
            return False  # データ不足

        # 時系列で単調増加しているか確認
        values = [log["data"][metric] for log in relevant_logs]
        return all(values[i] > values[i - 1] for i in range(1, len(values)))

    def _check_same_day_both(self, condition: Dict, action_type: str) -> bool:
        """同日中に複数アクションを両方実行したかチェック"""
        required_actions = condition.get("actions", [])
        today = datetime.now().strftime("%Y-%m-%d")

        today_action_types = {
            log["action_type"] for log in self.action_logs
            if log.get("date") == today
        }

        return all(action in today_action_types for action in required_actions)

    def _check_over_period(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """指定期間内の全アクションが条件を満たすかチェック"""
        if condition.get("action") != action_type or not action_data:
            return False

        metric    = condition["metric"]
        operator  = condition["operator"]
        threshold = condition["value"]
        days      = condition["days"]

        # 直近 N 件から対象アクションのログを抽出
        relevant_logs = [
            log for log in self.action_logs[-days:]
            if log.get("action_type") == action_type and metric in log.get("data", {})
        ]

        if not relevant_logs:
            return False

        # 全ログが条件を満たすか確認
        return all(self._compare(log["data"][metric], operator, threshold) for log in relevant_logs)

    def _check_percentage(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """
        パーセンテージ条件チェック（現在は簡易実装）。
        将来的により詳細な計算が必要な場合はここを拡張してください。
        """
        if condition.get("action") != action_type or not action_data:
            return False
        metric = condition.get("metric")
        if not metric or metric not in action_data:
            return False
        # TODO: condition["percentage"] を使った実際のパーセンテージ計算
        return True

    def _check_range(self, condition: Dict, action_type: str, action_data: Dict) -> bool:
        """メトリクスが指定値リストのいずれかに一致するかチェック"""
        if condition.get("action") != action_type or not action_data:
            return False

        metric = condition["metric"]
        if metric not in action_data:
            return False

        return action_data[metric] in condition.get("values", [])

    # ------------------------------------------------------------------
    # アクション統計の更新
    # ------------------------------------------------------------------

    def _update_action_count(self, action_type: str):
        """累計・日次カウントを更新し、連続日数も管理します。"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 日付が変わっていたら日次カウントをリセット
        if self.progress["daily_actions"].get("date") != today:
            self.progress["daily_actions"] = {
                "date": today,
                **{k: 0 for k in self._get_empty_action_counts()},
            }
            # 日次メトリクスもリセット
            self.progress["daily_metrics"] = self._get_empty_daily_metrics()

        # 累計・日次カウントをインクリメント
        action_counts = self.progress["action_counts"]
        daily_actions = self.progress["daily_actions"]

        if action_type in action_counts:
            action_counts[action_type] += 1
        if action_type in daily_actions:
            daily_actions[action_type] += 1

        # advance_day アクション時は連続日数を更新
        if action_type == "advance_day":
            self._update_consecutive_days()

        self._save_progress()

    def _update_consecutive_days(self):
        """
        advance_day アクションごとに連続日数を更新します。
        前日に実行していれば+1、途切れていればリセットします。
        """
        today     = datetime.now().strftime("%Y-%m-%d")
        last_date = self.progress["consecutive_days"].get("last_date")

        if last_date:
            days_gap = (
                datetime.strptime(today, "%Y-%m-%d") -
                datetime.strptime(last_date, "%Y-%m-%d")
            ).days

            if days_gap == 1:
                self.progress["consecutive_days"]["advance_day"] += 1
            else:
                # 連続が途切れた → 1にリセット
                self.progress["consecutive_days"]["advance_day"] = 1
        else:
            # 初回
            self.progress["consecutive_days"]["advance_day"] = 1

        self.progress["consecutive_days"]["last_date"] = today

    def _update_daily_metrics(self, action_data: Dict):
        """
        発電量など数値メトリクスを当日の合計値に加算します。
        新しいメトリクスを追跡する場合はここに追記してください。
        """
        metrics = self.progress["daily_metrics"]

        if "expected_output_kwh_per_day" in action_data:
            metrics["expected_output_kwh_per_day"] += action_data["expected_output_kwh_per_day"]

    # ------------------------------------------------------------------
    # ユーティリティ
    # ------------------------------------------------------------------

    @staticmethod
    def _compare(actual: Any, operator: str, target: Any) -> bool:
        """
        actual と target を operator で比較します。
        新しい演算子が必要な場合はここに追加してください。

        Args:
            actual:   実測値
            operator: 比較演算子文字列（">=", "<=", "==", "!=", ">", "<"）
            target:   閾値

        Returns:
            比較結果
        """
        if operator == ">=": return actual >= target
        if operator == "<=": return actual <= target
        if operator == "==": return actual == target
        if operator == "!=": return actual != target
        if operator == ">":  return actual > target
        if operator == "<":  return actual < target
        return False

    @staticmethod
    def _get_empty_action_counts() -> Dict[str, int]:
        """
        ゼロ初期化されたアクションカウント辞書を返します。
        新しいアクション種別を追加したらここにも追記してください。
        """
        return {
            "cea":         0,
            "power_plant": 0,
            "astronomy":   0,
            "build":       0,
            "advance_day": 0,
            "learning":    0,
            "review_day":  0,
        }

    @staticmethod
    def _get_empty_daily_metrics() -> Dict[str, float]:
        """
        ゼロ初期化された日次メトリクス辞書を返します。
        新しいメトリクスを追跡する場合はここに追加してください。
        """
        return {
            "power_usage_W":               0.0,
            "expected_output_kwh_per_day": 0.0,
        }

    def _load_progress(self) -> Dict:
        """進行状況ファイルを読み込みます。存在しない場合は初期値を返します。"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass  # 読み込み失敗時は初期値にフォールバック

        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "completed_missions": [],
            "unlocked_titles":    [],
            "action_counts":      self._get_empty_action_counts(),
            "daily_actions":      {"date": today, **self._get_empty_action_counts()},
            "consecutive_days":   {"advance_day": 0, "last_date": None},
            "daily_metrics":      self._get_empty_daily_metrics(),
        }

    def _save_progress(self):
        """進行状況をファイルに書き込みます。"""
        self._save_json(self.progress_file, self.progress)

    @staticmethod
    def _load_json(filepath: Path, default: Any) -> Any:
        """JSONファイルを読み込みます。存在しない/壊れている場合は default を返します。"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    @staticmethod
    def _save_json(filepath: Path, data: Any):
        """オブジェクトを JSON ファイルに書き込みます。"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------
# 動作確認用スクリプト
# ------------------------------------------------------------------

def main():
    """基本的なミッションシステムの動作確認。"""
    system = MissionSystem()

    print("🎯 ミッションシステムテスト")
    print("=" * 50)

    test_action_data = {
        "power_usage_W":               15,
        "expected_output_kwh_per_day": 2.5,
    }

    system.log_action("power_plant", test_action_data)
    completed = system.check_missions("power_plant", test_action_data)
    unlocked  = system.check_titles("power_plant", test_action_data)

    print(f"✅ 完了したミッション: {len(completed)}")
    print(f"🏆 獲得した称号: {len(unlocked)}")

    available = system.get_available_missions()
    print(f"📋 利用可能なメインミッション: {len(available['main_missions'])}")
    print(f"📋 利用可能なサブミッション: {len(available['sub_missions'])}")


if __name__ == "__main__":
    main()