#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
条件パーサー

ミッション/称号のJSONに記述されたテキスト形式の条件式を解析し、
プログラムが評価できる辞書形式に変換します。

条件テキストの書き方 (mission_system.py や missions.json に条件を追加する際の参考):
    - 累計回数: 「累計 `action名` 実行回数 ≥ N」
    - 日次回数: 「1日内の `action名` 回数 ≥ N」
    - 数値比較: 「`action名` の `メトリクス名` ≥ 値」
    - AND条件: 「`action名` の `m1` ≥ v1 かつ `m2` ≥ v2」
    - 連続日数: 「N日連続で `action名` を実行」

対応するアクション名 (action_mapping キーを参照):
    design_plant, cea_run, observe_optics, build_module,
    advance_day, log_learning, review_day
"""

import re
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta


class ConditionParser:
    """
    自然言語に近い日本語テキスト条件式を、プログラムが評価できる辞書に変換するクラス。

    新しいアクション名を追加する場合: action_mapping に追記してください。
    新しい条件パターンを追加する場合:
        1. parse_condition_text() の patterns リストに正規表現を追加
        2. _parse_matched_condition() の振り分けロジックに追加
        3. 対応する _parse_xxx_condition() メソッドを実装
    """

    def __init__(self):
        # ゲーム内アクション名 → 内部識別子のマッピング
        # mission.json でアクション名を指定する際はキー側の文字列を使います
        self.action_mapping = {
            'design_plant':  'power_plant',   # 発電所設計
            'cea_run':       'cea',            # CEA計算実行
            'observe_optics': 'astronomy',    # 天体観測
            'build_module':  'build',          # モジュール建設
            'advance_day':   'advance_day',    # 次の日へ進む
            'log_learning':  'learning',       # 学習記録
            'review_day':    'review_day',     # 日次レビュー
        }

        # テキスト演算子 → Python演算子文字列のマッピング
        self.operator_mapping = {
            '≥': '>=',
            '≤': '<=',
            '==': '==',
            '!=': '!=',
            '>':  '>',
            '<':  '<',
        }

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def parse_condition_text(self, condition_text: str) -> Dict:
        """
        テキスト形式の条件式を解析し、構造化された辞書を返します。

        Args:
            condition_text: 例「累計 `cea_run` 実行回数 ≥ 10」

        Returns:
            {"type": "total_action_count", "action": "cea", "operator": ">=", "count": 10}
            解析できない場合は {"type": "unknown", ...} を返します。
        """
        patterns = self._get_condition_patterns()

        for pattern in patterns:
            match = re.search(pattern, condition_text)
            if match:
                return self._parse_matched_condition(match, pattern)

        # どのパターンにもマッチしなかった場合
        return {
            "type": "unknown",
            "action": "unknown",
            "description": condition_text,
        }

    # ------------------------------------------------------------------
    # パターン定義（条件を追加する場合はここに正規表現を追加）
    # ------------------------------------------------------------------

    def _get_condition_patterns(self) -> List[str]:
        """
        認識可能な条件パターンの正規表現リストを返します。

        上から順にマッチを試みます。より具体的なパターンを上に書いてください。
        新しいパターンを追加した場合は _parse_matched_condition() にも振り分けを追加してください。
        """
        return [
            # 例: `` `design_plant` の `expected_output_kwh_per_day` ≥ 1.0 ``
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: `` `cea_run` 実行回数 ≥ 10 ``
            r'`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',

            # 例: 「累計 `cea_run` 実行回数 ≥ 10」
            r'累計\s+`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',

            # 例: 「1日内の `design_plant` 回数 ≥ 2」
            r'1日内の\s+`(\w+)`\s+回数\s+([≥≤==!=><]+)\s+(\d+)',

            # 例: 「1日内に `cea_run` 実行回数 ≥ 1」
            r'1日内に\s+`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',

            # 例: `` `observe_optics` で `星雲観測` を1回完了 ``
            r'`(\w+)`\s+で\s+`([^`]+)`\s+を1回完了',

            # 例: 「`cea_run` の `isp` ≥ 400 and `Pc` ≥ 200」
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+and\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「`cea_run` の `isp` ≥ 400 かつ `Pc` ≥ 200」
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「1日内の `cea_run` 回数 ≥ 2 かつ `isp` ≥ 400」
            r'1日内の\s+`(\w+)`\s+回数\s+([≥≤==!=><]+)\s+(\d+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「3日連続で `advance_day` を実行」
            r'(\d+)日連続で\s+`(\w+)`\s+を実行',

            # 例: 「累計 `cea_run` の日次増分が3日連続で増加」
            r'累計\s+`(\w+)`\s+の日次増分が(\d+)日連続で増加',

            # 例: 「`cea_run` と `design_plant` を同日に両方実行 ≥ 1」
            r'`(\w+)`\s+と\s+`(\w+)`\s+を同日に両方実行\s+([≥≤==!=><]+)\s+(\d+)',

            # 例: 「`cea_run` の `isp` ≥ 400 over 7 day」
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+over\s+(\d+)\s+day',

            # 例: 「`cea_run` の `efficiency` ≥ 95%」
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+(\d+)%',

            # 例: 「`design_plant` の `type` in [1,2,3] のいずれかで起動」
            r'`(\w+)`\s+の\s+`(\w+)`\s+in\s+\[([\d,]+)\]\s+のいずれかで起動',

            # 例: 「累計 `energy_generated` ≥ 100.0」
            r'累計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「1日内の合計 `energy_kwh` ≥ 10.0」
            r'1日内の合計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「1日内 `energy_kwh` 合計 ≥ 10.0」
            r'1日内\s+`(\w+)`\s+合計\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「`cea_run` の `isp` が5日連続で改善」
            r'`(\w+)`\s+の\s+`(\w+)`\s+が(\d+)日連続で改善',

            # 例: 「`cea_run` の `efficiency` が7日連続で50%以上維持」
            r'`(\w+)`\s+の\s+`(\w+)`\s+が(\d+)日連続で50%以上維持',

            # 例: 「累計 `energy_generated` ≥ 100.0 over 30 day」
            r'累計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+over\s+(\d+)\s+day',

            # 例: 「`cea_run` で `isp` ≥ 400 を1回使用」
            r'`(\w+)`\s+で\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+を1回使用',

            # 例: 「`cea_run` で `isp` ≥ 400 を1回完了」
            r'`(\w+)`\s+で\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+を1回完了',

            # 例: 「`cea_run` にて `isp` ≥ 400 かつ `Pc` ≥ 200」
            r'`(\w+)`\s+にて\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「`mining` を Pool ではなく Solo モードで1回実行」
            r'`(\w+)`\s+を\s+Pool\s+ではなく\s+Solo\s+モードで1回実行',

            # 例: 「`observe_optics` で月を含む観測1回完了」
            r'`(\w+)`\s+で月を含む観測1回完了',

            # 例: 「`cea_run` の `thrust` / `mass` ≥ 50.0」
            r'`(\w+)`\s+の\s+`(\w+)`\s+/\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: 「`cea_run` の `isp` ≥ 400 × `efficiency` ≥ 90」
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+×\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',

            # 例: `` `design_plant` 実行回数 for type=`solar` ≥ 3 ``
            r'`(\w+)`\s+実行回数\s+for\s+type=`(\w+)`\s+([≥≤==!=><]+)\s+(\d+)',
        ]

    # ------------------------------------------------------------------
    # パターンの振り分けと個別パーサー
    # ------------------------------------------------------------------

    def _parse_matched_condition(self, match: re.Match, pattern: str) -> Dict:
        """
        マッチした条件をパターンの特徴で判別し、適切なパーサーに委譲します。
        新しいパターンを追加した場合はここにも elif 節を追加してください。
        """
        groups = match.groups()

        # --- 特殊修飾子の確認（パターンの文字列特徴で分岐）---
        if "実行回数" in pattern and "for type=" in pattern:
            return self._parse_type_count_condition(groups)
        elif "累計" in pattern and "実行回数" in pattern:
            return self._parse_total_count_condition(groups)
        elif "累計" in pattern and "日次増分" in pattern:
            return self._parse_incremental_condition(groups)
        elif "累計" in pattern and "over" in pattern:
            return self._parse_over_period_condition(groups)
        elif "累計" in pattern:
            return self._parse_total_metric_condition(groups)
        elif "1日内" in pattern and "合計" in pattern:
            return self._parse_daily_total_condition(groups)
        elif "1日内" in pattern and "かつ" in pattern:
            return self._parse_daily_compound_condition(groups)
        elif "1日内" in pattern:
            return self._parse_daily_condition(groups)
        elif "実行回数" in pattern:
            return self._parse_count_condition(groups)
        elif "で月を含む" in pattern:
            return self._parse_moon_observation_condition(groups)
        elif "を1回完了" in pattern:
            return self._parse_completion_condition(groups)
        elif "を1回使用" in pattern:
            return self._parse_usage_condition(groups)
        elif "and" in pattern or "かつ" in pattern or "にて" in pattern:
            return self._parse_compound_condition(groups)
        elif "日連続" in pattern and "改善" in pattern:
            return self._parse_improvement_condition(groups)
        elif "日連続" in pattern and "50%以上維持" in pattern:
            return self._parse_maintenance_condition(groups)
        elif "日連続" in pattern:
            return self._parse_consecutive_condition(groups)
        elif "同日に両方実行" in pattern:
            return self._parse_same_day_condition(groups)
        elif "over" in pattern:
            return self._parse_over_period_condition(groups)
        elif "%" in pattern:
            return self._parse_percentage_condition(groups)
        elif "in" in pattern and "のいずれか" in pattern:
            return self._parse_range_condition(groups)
        elif "/" in pattern:
            return self._parse_ratio_condition(groups)
        elif "×" in pattern:
            return self._parse_multiplication_condition(groups)
        elif "Pool ではなく Solo" in pattern:
            return self._parse_solo_mode_condition(groups)
        else:
            return self._parse_simple_condition(groups)

    # --- 個別パーサー群 ---
    # 各メソッドは groups（正規表現のキャプチャグループ）を受け取り、
    # MissionSystem が評価できる辞書を返します。

    def _parse_simple_condition(self, groups) -> Dict:
        """`action` の `metric` operator value 形式"""
        action, metric, operator, value = groups
        return {
            "type": "simple",
            "action":    self.action_mapping.get(action, action),
            "metric":    metric,
            "operator":  self.operator_mapping.get(operator, operator),
            "value":     self._parse_value(value),
        }

    def _parse_count_condition(self, groups) -> Dict:
        """`action` 実行回数 operator N 形式"""
        action, operator, value = groups
        return {
            "type":     "total_action_count",
            "action":   self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count":    int(value),
        }

    def _parse_type_count_condition(self, groups) -> Dict:
        """`action` 実行回数 for type=`type_value` operator N 形式（タイプ別集計）"""
        action, type_value, operator, value = groups
        return {
            "type":     "type_action_count",
            "action":   self.action_mapping.get(action, action),
            "type":     type_value,
            "operator": self.operator_mapping.get(operator, operator),
            "count":    int(value),
        }

    def _parse_total_count_condition(self, groups) -> Dict:
        """累計 `action` 実行回数 operator N 形式"""
        action, operator, value = groups
        return {
            "type":     "total_action_count",
            "action":   self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count":    int(value),
        }

    def _parse_total_metric_condition(self, groups) -> Dict:
        """累計 `metric` operator value 形式（アクション横断の累計値）"""
        metric, operator, value = groups
        return {
            "type":     "total_metric",
            "metric":   metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value":    self._parse_value(value),
        }

    def _parse_daily_condition(self, groups) -> Dict:
        """1日内の `action` 回数 operator N 形式"""
        action, operator, value = groups
        return {
            "type":     "daily_action_count",
            "action":   self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count":    int(value),
        }

    def _parse_daily_total_condition(self, groups) -> Dict:
        """1日内の合計 `metric` operator value 形式（当日の数値合計）"""
        metric, operator, value = groups
        return {
            "type":     "daily_total_metric",
            "metric":   metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value":    self._parse_value(value),
        }

    def _parse_daily_compound_condition(self, groups) -> Dict:
        """1日内の `action` 回数 operator N かつ `metric` operator value 形式"""
        action, operator1, count, metric, operator2, value = groups
        return {
            "type":            "daily_compound",
            "action":          self.action_mapping.get(action, action),
            "action_operator": self.operator_mapping.get(operator1, operator1),
            "action_count":    int(count),
            "metric":          metric,
            "metric_operator": self.operator_mapping.get(operator2, operator2),
            "metric_value":    self._parse_value(value),
        }

    def _parse_completion_condition(self, groups) -> Dict:
        """`action` で `condition_text` を1回完了 形式"""
        action, condition = groups
        return {
            "type":      "completion",
            "action":    self.action_mapping.get(action, action),
            "condition": condition,
        }

    def _parse_usage_condition(self, groups) -> Dict:
        """`action` で `metric` operator value を1回使用 形式"""
        action, metric, operator, value = groups
        return {
            "type":     "usage",
            "action":   self.action_mapping.get(action, action),
            "metric":   metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value":    self._parse_value(value),
        }

    def _parse_moon_observation_condition(self, groups) -> Dict:
        """`action` で月を含む観測1回完了 形式"""
        action = groups[0]
        return {
            "type":   "moon_observation",
            "action": self.action_mapping.get(action, action),
        }

    def _parse_solo_mode_condition(self, groups) -> Dict:
        """`action` を Pool ではなく Solo モードで1回実行 形式"""
        action = groups[0]
        return {
            "type":   "solo_mode",
            "action": self.action_mapping.get(action, action),
        }

    def _parse_compound_condition(self, groups) -> Dict:
        """`action` の `m1` op1 v1 かつ `m2` op2 v2 形式（AND複合条件）"""
        if len(groups) == 7:
            action1, metric1, op1, val1, metric2, op2, val2 = groups
            return {
                "type": "compound_and",
                "conditions": [
                    {
                        "action":   self.action_mapping.get(action1, action1),
                        "metric":   metric1,
                        "operator": self.operator_mapping.get(op1, op1),
                        "value":    self._parse_value(val1),
                    },
                    {
                        "action":   self.action_mapping.get(action1, action1),
                        "metric":   metric2,
                        "operator": self.operator_mapping.get(op2, op2),
                        "value":    self._parse_value(val2),
                    },
                ],
            }
        return {"type": "unknown", "description": f"Compound condition: {groups}"}

    def _parse_consecutive_condition(self, groups) -> Dict:
        """N日連続で `action` を実行 形式"""
        days, action = groups
        return {
            "type":   "consecutive_days",
            "action": self.action_mapping.get(action, action),
            "days":   int(days),
        }

    def _parse_improvement_condition(self, groups) -> Dict:
        """`action` の `metric` がN日連続で改善 形式"""
        action, metric, days = groups
        return {
            "type":   "consecutive_improvement",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "days":   int(days),
        }

    def _parse_maintenance_condition(self, groups) -> Dict:
        """`action` の `metric` がN日連続で50%以上維持 形式"""
        action, metric, days = groups
        return {
            "type":      "consecutive_maintenance",
            "action":    self.action_mapping.get(action, action),
            "metric":    metric,
            "days":      int(days),
            "threshold": 0.5,  # 50% 固定
        }

    def _parse_incremental_condition(self, groups) -> Dict:
        """累計 `metric` の日次増分がN日連続で増加 形式"""
        metric, days = groups
        return {
            "type":   "incremental_increase",
            "metric": metric,
            "days":   int(days),
        }

    def _parse_same_day_condition(self, groups) -> Dict:
        """`a1` と `a2` を同日に両方実行 operator N 形式"""
        action1, action2, operator, value = groups
        return {
            "type":     "same_day_both",
            "actions":  [
                self.action_mapping.get(action1, action1),
                self.action_mapping.get(action2, action2),
            ],
            "operator": self.operator_mapping.get(operator, operator),
            "count":    int(value),
        }

    def _parse_over_period_condition(self, groups) -> Dict:
        """N日間にわたって条件を継続満足する形式"""
        if len(groups) == 5:
            # `action` の `metric` operator value over N day
            action, metric, operator, value, days = groups
            return {
                "type":     "over_period",
                "action":   self.action_mapping.get(action, action),
                "metric":   metric,
                "operator": self.operator_mapping.get(operator, operator),
                "value":    self._parse_value(value),
                "days":     int(days),
            }
        else:
            # 累計 `metric` operator value over N day
            metric, operator, value, days = groups
            return {
                "type":     "over_period_total",
                "metric":   metric,
                "operator": self.operator_mapping.get(operator, operator),
                "value":    self._parse_value(value),
                "days":     int(days),
            }

    def _parse_percentage_condition(self, groups) -> Dict:
        """`action` の `metric` operator N% 形式"""
        action, metric, operator, value = groups
        return {
            "type":       "percentage",
            "action":     self.action_mapping.get(action, action),
            "metric":     metric,
            "operator":   self.operator_mapping.get(operator, operator),
            "percentage": float(value),
        }

    def _parse_range_condition(self, groups) -> Dict:
        """`action` の `metric` in [v1,v2,...] のいずれかで起動 形式"""
        action, metric, values = groups
        value_list = [int(v.strip()) for v in values.split(',')]
        return {
            "type":   "range_check",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "values": value_list,
        }

    def _parse_ratio_condition(self, groups) -> Dict:
        """`action` の `m1` / `m2` operator value 形式（比率比較）"""
        action, metric1, metric2, operator, value = groups
        return {
            "type":     "ratio",
            "action":   self.action_mapping.get(action, action),
            "metric1":  metric1,
            "metric2":  metric2,
            "operator": self.operator_mapping.get(operator, operator),
            "value":    self._parse_value(value),
        }

    def _parse_multiplication_condition(self, groups) -> Dict:
        """`action` の `m1` op1 v1 × `m2` op2 v2 形式（積の複合条件）"""
        action, metric1, op1, val1, metric2, op2, val2 = groups
        return {
            "type":      "multiplication",
            "action":    self.action_mapping.get(action, action),
            "metric1":   metric1,
            "operator1": self.operator_mapping.get(op1, op1),
            "value1":    self._parse_value(val1),
            "metric2":   metric2,
            "operator2": self.operator_mapping.get(op2, op2),
            "value2":    self._parse_value(val2),
        }

    # ------------------------------------------------------------------
    # ユーティリティ
    # ------------------------------------------------------------------

    def _parse_value(self, value_str: str) -> Union[int, float, str, bool]:
        """
        文字列を適切なPython型に変換します。
        True/False → bool、整数 → int、小数 → float、それ以外 → str
        """
        value_str = value_str.strip()

        if value_str.lower() in ('true', 'false'):
            return value_str.lower() == 'true'

        try:
            return float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            return value_str  # 変換できなければ文字列のまま返す


# ------------------------------------------------------------------
# 動作確認用スクリプト（直接実行した場合のみ動く）
# ------------------------------------------------------------------

def main():
    """パーサーの動作確認。新しいパターンを追加した後に実行してください。"""
    parser = ConditionParser()

    test_conditions = [
        "`design_plant` の `expected_output_kwh_per_day` ≥ 1.0",
        "累計 `cea_run` 実行回数 ≥ 10",
        "3日連続で `advance_day` を実行",
    ]

    print("🧪 条件パーサーテスト")
    print("=" * 50)

    for condition in test_conditions:
        result = parser.parse_condition_text(condition)
        print(f"条件: {condition}")
        print(f"解析結果: {result}")
        print()


if __name__ == "__main__":
    main()