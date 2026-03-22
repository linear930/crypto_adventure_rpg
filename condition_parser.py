#!/usr/bin/env python3
"""
条件パーサー - テキスト形式の条件を解析して判定可能な形式に変換
"""

import re
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta

class ConditionParser:
    def __init__(self):
        # アクション名のマッピング
        self.action_mapping = {
            'design_plant': 'power_plant',
            'cea_run': 'cea',
            'observe_optics': 'astronomy',
            'build_module': 'build',
            'advance_day': 'advance_day',
            'log_learning': 'learning',
            'review_day': 'review_day'
        }
        
        # 演算子のマッピング
        self.operator_mapping = {
            '≥': '>=',
            '≤': '<=',
            '==': '==',
            '!=': '!=',
            '>': '>',
            '<': '<'
        }
    
    def parse_condition_text(self, condition_text: str) -> Dict:
        """テキスト形式の条件を解析"""
        # 基本的なパターンマッチング
        patterns = [
            # パターン1: action の metric operator value
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン2: action 実行回数 operator value
            r'`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',
            # パターン3: 累計 action 実行回数 operator value
            r'累計\s+`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',
            # パターン4: 1日内の action 回数 operator value
            r'1日内の\s+`(\w+)`\s+回数\s+([≥≤==!=><]+)\s+(\d+)',
            # パターン5: 1日内に action 実行回数 operator value
            r'1日内に\s+`(\w+)`\s+実行回数\s+([≥≤==!=><]+)\s+(\d+)',
            # パターン6: action で condition を1回完了
            r'`(\w+)`\s+で\s+`([^`]+)`\s+を1回完了',
            # パターン7: action の metric operator value and condition
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+and\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン8: action の metric operator value かつ condition
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン9: 複合条件（日次+条件）
            r'1日内の\s+`(\w+)`\s+回数\s+([≥≤==!=><]+)\s+(\d+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン10: 連続条件
            r'(\d+)日連続で\s+`(\w+)`\s+を実行',
            # パターン11: 日次増分条件
            r'累計\s+`(\w+)`\s+の日次増分が(\d+)日連続で増加',
            # パターン12: 同日実行条件
            r'`(\w+)`\s+と\s+`(\w+)`\s+を同日に両方実行\s+([≥≤==!=><]+)\s+(\d+)',
            # パターン13: 特定値条件
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+over\s+(\d+)\s+day',
            # パターン14: パーセンテージ条件
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+(\d+)%',
            # パターン15: 特定値の範囲条件
            r'`(\w+)`\s+の\s+`(\w+)`\s+in\s+\[([\d,]+)\]\s+のいずれかで起動',
            # パターン16: 累計 metric operator value
            r'累計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン17: 1日内の合計 metric operator value
            r'1日内の合計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン18: 1日内 metric 合計 operator value
            r'1日内\s+`(\w+)`\s+合計\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン19: action の metric operator value がN日連続で改善
            r'`(\w+)`\s+の\s+`(\w+)`\s+が(\d+)日連続で改善',
            # パターン20: action の metric operator value がN日連続で50%以上維持
            r'`(\w+)`\s+の\s+`(\w+)`\s+が(\d+)日連続で50%以上維持',
            # パターン21: 累計 metric operator value over N day
            r'累計\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+over\s+(\d+)\s+day',
            # パターン22: action で metric operator value を1回使用
            r'`(\w+)`\s+で\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+を1回使用',
            # パターン23: action で metric operator value を1回完了
            r'`(\w+)`\s+で\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+を1回完了',
            # パターン24: action にて metric operator value かつ metric operator value
            r'`(\w+)`\s+にて\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+かつ\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン25: action を Pool ではなく Solo モードで1回実行
            r'`(\w+)`\s+を\s+Pool\s+ではなく\s+Solo\s+モードで1回実行',
            # パターン26: action で月を含む観測1回完了
            r'`(\w+)`\s+で月を含む観測1回完了',
            # パターン27: action の metric operator value / metric operator value
            r'`(\w+)`\s+の\s+`(\w+)`\s+/\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン28: action の metric operator value × metric operator value
            r'`(\w+)`\s+の\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)\s+×\s+`(\w+)`\s+([≥≤==!=><]+)\s+([\w\.]+)',
            # パターン29: action 実行回数 for type=value operator value
            r'`(\w+)`\s+実行回数\s+for\s+type=`(\w+)`\s+([≥≤==!=><]+)\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, condition_text)
            if match:
                return self._parse_matched_condition(match, pattern)
        
        # デフォルト条件（解析できない場合）
        return {
            "type": "unknown",
            "action": "unknown",
            "description": condition_text
        }
    
    def _parse_matched_condition(self, match, pattern: str) -> Dict:
        """マッチした条件を解析"""
        groups = match.groups()
        
        if "実行回数" in pattern and "for type=" in pattern:
            return self._parse_type_count_condition(groups)
        elif "実行回数" in pattern:
            return self._parse_count_condition(groups)
        elif "累計" in pattern and "実行回数" in pattern:
            return self._parse_total_count_condition(groups)
        elif "累計" in pattern and "日次増分" in pattern:
            return self._parse_incremental_condition(groups)
        elif "累計" in pattern:
            return self._parse_total_metric_condition(groups)
        elif "1日内" in pattern and "合計" in pattern:
            return self._parse_daily_total_condition(groups)
        elif "1日内" in pattern and "かつ" in pattern:
            return self._parse_daily_compound_condition(groups)
        elif "1日内" in pattern:
            return self._parse_daily_condition(groups)
        elif "を1回完了" in pattern and "月を含む" in pattern:
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
    
    def _parse_simple_condition(self, groups) -> Dict:
        """シンプルな条件を解析"""
        action, metric, operator, value = groups
        return {
            "type": "simple",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value": self._parse_value(value)
        }
    
    def _parse_count_condition(self, groups) -> Dict:
        """実行回数条件を解析"""
        action, operator, value = groups
        return {
            "type": "total_action_count",
            "action": self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count": int(value)
        }
    
    def _parse_type_count_condition(self, groups) -> Dict:
        """タイプ別実行回数条件を解析"""
        action, type_value, operator, value = groups
        return {
            "type": "type_action_count",
            "action": self.action_mapping.get(action, action),
            "type": type_value,
            "operator": self.operator_mapping.get(operator, operator),
            "count": int(value)
        }
    
    def _parse_total_count_condition(self, groups) -> Dict:
        """累計実行回数条件を解析"""
        action, operator, value = groups
        return {
            "type": "total_action_count",
            "action": self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count": int(value)
        }
    
    def _parse_total_metric_condition(self, groups) -> Dict:
        """累計メトリクス条件を解析"""
        metric, operator, value = groups
        return {
            "type": "total_metric",
            "metric": metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value": self._parse_value(value)
        }
    
    def _parse_daily_condition(self, groups) -> Dict:
        """日次条件を解析"""
        action, operator, value = groups
        return {
            "type": "daily_action_count",
            "action": self.action_mapping.get(action, action),
            "operator": self.operator_mapping.get(operator, operator),
            "count": int(value)
        }
    
    def _parse_daily_total_condition(self, groups) -> Dict:
        """日次合計条件を解析"""
        metric, operator, value = groups
        return {
            "type": "daily_total_metric",
            "metric": metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value": self._parse_value(value)
        }
    
    def _parse_daily_compound_condition(self, groups) -> Dict:
        """日次複合条件を解析"""
        action, operator1, count, metric, operator2, value = groups
        return {
            "type": "daily_compound",
            "action": self.action_mapping.get(action, action),
            "action_operator": self.operator_mapping.get(operator1, operator1),
            "action_count": int(count),
            "metric": metric,
            "metric_operator": self.operator_mapping.get(operator2, operator2),
            "metric_value": self._parse_value(value)
        }
    
    def _parse_completion_condition(self, groups) -> Dict:
        """完了条件を解析"""
        action, condition = groups
        return {
            "type": "completion",
            "action": self.action_mapping.get(action, action),
            "condition": condition
        }
    
    def _parse_usage_condition(self, groups) -> Dict:
        """使用条件を解析"""
        action, metric, operator, value = groups
        return {
            "type": "usage",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "operator": self.operator_mapping.get(operator, operator),
            "value": self._parse_value(value)
        }
    
    def _parse_moon_observation_condition(self, groups) -> Dict:
        """月観測条件を解析"""
        action = groups[0]
        return {
            "type": "moon_observation",
            "action": self.action_mapping.get(action, action)
        }
    
    def _parse_solo_mode_condition(self, groups) -> Dict:
        """ソロモード条件を解析"""
        action = groups[0]
        return {
            "type": "solo_mode",
            "action": self.action_mapping.get(action, action)
        }
    
    def _parse_compound_condition(self, groups) -> Dict:
        """複合条件を解析"""
        if len(groups) == 7:  # AND条件
            action1, metric1, op1, val1, metric2, op2, val2 = groups
            return {
                "type": "compound_and",
                "conditions": [
                    {
                        "action": self.action_mapping.get(action1, action1),
                        "metric": metric1,
                        "operator": self.operator_mapping.get(op1, op1),
                        "value": self._parse_value(val1)
                    },
                    {
                        "action": self.action_mapping.get(action1, action1),
                        "metric": metric2,
                        "operator": self.operator_mapping.get(op2, op2),
                        "value": self._parse_value(val2)
                    }
                ]
            }
        else:
            return {"type": "unknown", "description": f"Compound condition: {groups}"}
    
    def _parse_consecutive_condition(self, groups) -> Dict:
        """連続条件を解析"""
        days, action = groups
        return {
            "type": "consecutive_days",
            "action": self.action_mapping.get(action, action),
            "days": int(days)
        }
    
    def _parse_improvement_condition(self, groups) -> Dict:
        """改善条件を解析"""
        action, metric, days = groups
        return {
            "type": "consecutive_improvement",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "days": int(days)
        }
    
    def _parse_maintenance_condition(self, groups) -> Dict:
        """維持条件を解析"""
        action, metric, days = groups
        return {
            "type": "consecutive_maintenance",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "days": int(days),
            "threshold": 0.5  # 50%
        }
    
    def _parse_incremental_condition(self, groups) -> Dict:
        """増分条件を解析"""
        metric, days = groups
        return {
            "type": "incremental_increase",
            "metric": metric,
            "days": int(days)
        }
    
    def _parse_same_day_condition(self, groups) -> Dict:
        """同日実行条件を解析"""
        action1, action2, operator, value = groups
        return {
            "type": "same_day_both",
            "actions": [
                self.action_mapping.get(action1, action1),
                self.action_mapping.get(action2, action2)
            ],
            "operator": self.operator_mapping.get(operator, operator),
            "count": int(value)
        }
    
    def _parse_over_period_condition(self, groups) -> Dict:
        """期間条件を解析"""
        if len(groups) == 5:
            action, metric, operator, value, days = groups
            return {
                "type": "over_period",
                "action": self.action_mapping.get(action, action),
                "metric": metric,
                "operator": self.operator_mapping.get(operator, operator),
                "value": self._parse_value(value),
                "days": int(days)
            }
        else:
            metric, operator, value, days = groups
            return {
                "type": "over_period_total",
                "metric": metric,
                "operator": self.operator_mapping.get(operator, operator),
                "value": self._parse_value(value),
                "days": int(days)
            }
    
    def _parse_percentage_condition(self, groups) -> Dict:
        """パーセンテージ条件を解析"""
        action, metric, operator, value = groups
        return {
            "type": "percentage",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "operator": self.operator_mapping.get(operator, operator),
            "percentage": float(value)
        }
    
    def _parse_range_condition(self, groups) -> Dict:
        """範囲条件を解析"""
        action, metric, values = groups
        value_list = [int(v.strip()) for v in values.split(',')]
        return {
            "type": "range_check",
            "action": self.action_mapping.get(action, action),
            "metric": metric,
            "values": value_list
        }
    
    def _parse_ratio_condition(self, groups) -> Dict:
        """比率条件を解析"""
        action, metric1, metric2, operator, value = groups
        return {
            "type": "ratio",
            "action": self.action_mapping.get(action, action),
            "metric1": metric1,
            "metric2": metric2,
            "operator": self.operator_mapping.get(operator, operator),
            "value": self._parse_value(value)
        }
    
    def _parse_multiplication_condition(self, groups) -> Dict:
        """乗算条件を解析"""
        action, metric1, op1, val1, metric2, op2, val2 = groups
        return {
            "type": "multiplication",
            "action": self.action_mapping.get(action, action),
            "metric1": metric1,
            "operator1": self.operator_mapping.get(op1, op1),
            "value1": self._parse_value(val1),
            "metric2": metric2,
            "operator2": self.operator_mapping.get(op2, op2),
            "value2": self._parse_value(val2)
        }
    
    def _parse_value(self, value_str: str) -> Union[int, float, str, bool]:
        """値を適切な型に変換"""
        value_str = value_str.strip()
        
        # ブール値
        if value_str.lower() in ['true', 'false']:
            return value_str.lower() == 'true'
        
        # 数値
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            return value_str

def main():
    """テスト用"""
    parser = ConditionParser()
    
    # テスト条件
    test_conditions = [
        "`design_plant` の `expected_output_kwh_per_day` ≥ 1.0",
        "累計 `cea_run` 実行回数 ≥ 10",
        "3日連続で `advance_day` を実行"
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