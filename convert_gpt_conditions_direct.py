#!/usr/bin/env python3
"""
GPTの条件テキストを直接変換
"""

import json
import re
from typing import Dict
from condition_parser import ConditionParser
from mission_system import MissionSystem

def convert_gpt_conditions_direct():
    """GPTの条件を直接変換"""
    
    # GPTから受け取った条件テキスト
    gpt_conditions = """
1. **黎明のソーラー設計**：`design_plant` の `expected_output_kwh_per_day` ≥ 1.0
2. **風の調律師**：`design_plant` の `panel_output_kw` ≥ 0.5 × `wind_enabled == true`
3. **影のタービン構築**：`design_plant` 実行回数 for type=`wind` ≥ 1
4. **光量子パネル最適化**：`design_plant` の `expected_output_kwh_per_day` ≥ 5.0
5. **微風発電の詩**：`mine_log` の `power_usage_W` ≤ 20
6. **乱流ハーベスター起動**：`mine_log` の `hashrate_khps` ≥ 500
7. **PVマトリクスの謎解き**：`design_plant` にて `panel_orientation=="South"` かつ `tilt_angle_deg==30`
8. **自家発電アーキテクトへの道**：`design_plant` の実行回数 ≥ 3
9. **エコ・フォージの構築**：`design_plant` の `expected_output_kwh_per_day` ≥ 10
10. **ゼロエミッション邂逅**：1日内の `mine_log` 回数 ≥ 1 かつ `power_usage_W` ≤ 0
11. **初陣！XMRマイニング**：`mine_log` の `mined_amount_XMR` ≥ 0.00001
12. **破壊的ハッシュレート突破**：`mine_log` の `hashrate_khps` ≥ 1000
13. **シルバー・ハッシュの探求**：累計 `mined_amount_XMR` ≥ 0.01
14. **乱数アルゴリズムの祝祭**：`mine_log` で `randomX == true` を1回完了
15. **クリプト・収穫祭**：1日内に `mine_log` 実行回数 ≥ 3
16. **エネルギー収支の錬金術**：1日内の合計 `power_usage_W` ≤ 100
17. **GPUコアの呪縛を解け**：`mine_log` の `cpu_temperature_C` ≤ 65
18. **冷却回路の詩人**：`mine_log` の `power_usage_W` / `hashrate_khps` ≤ 0.1
19. **ハッシュパイプラインの覇者**：累計 `hashrate_khps` ≥ 10000
20. **ソロマイニングの孤高**：`mine_log` を Pool ではなく Solo モードで1回実行
21. **CEAの扉を叩く者**：`cea_run` の実行回数 ≥ 1
22. **燃焼比の調べ**：`cea_run` の `mixture_ratio` ≥ 5.0
23. **比推力の詩的探訪**：`cea_run` の `isp_sec` ≥ 300
24. **推進剤交響曲**：`cea_run` 実行回数 ≥ 5
25. **チャンバープレッシャーの舞踏**：`cea_run` の `chamber_pressure_bar` ≥ 90
26. **水素と酸素の協奏曲**：`cea_run` で `propellant=="LH2/LOX"` を1回完了
27. **エンジンシミュの錬金術師**：累計 `cea_run` 実行回数 ≥ 10
28. **分子ダンスの観測者**：`observe_optics` の `observations_count` ≥ 1
29. **CEA聖杯探索**：`cea_run` の `isp_sec` ≥ 310 and `chamber_pressure_bar` ≥ 100
30. **最適混合比の伝説**：`cea_run` の `mixture_ratio` == 5.5
31. **星屑の望遠鏡を覗け**：`observe_optics` 実行回数 ≥ 1
32. **焦点距離の幻影**：`observe_optics` の `focal_length_mm` ≥ 50
33. **銀河眼の設計者**：`observe_optics` 累計回数 ≥ 5
34. **レンズ・リフラクションの詩**：`observe_optics` の `aperture_mm` ≥ 80
35. **暗黒天体の囁き**：`observe_optics` の `exposure_time_s` ≥ 30
36. **天体図の錬金術**：`observe_optics` で `observations_count` ≥ 10
37. **光跡を追う旅人**：`observe_optics` の `tracking_accuracy` ≥ 90%
38. **光学迷宮からの脱出**：`observe_optics` で `error_rate` ≤ 5%
39. **スペクトル・セレナーデ**：`observe_optics` の `spectrum_data_points` ≥ 100
40. **月裏の影を測れ**：`observe_optics` で月を含む観測1回完了
41. **模型エンジニアの胎動**：`build_module` の実行回数 ≥ 1
42. **段ボール・ギアの創造**：`build_module` で `material=="cardboard"` を1回使用
43. **紙クリップ歯車の叛逆**：`build_module` で `material=="paper_clip"` を1回使用
44. **ハードオフ・リバースメカニクス**：`build_module` 実行回数 ≥ 3
45. **ジャンク飛行機の幻想**：`build_module` で `project=="junk_plane"` を1回完了
46. **廃材の彫刻家**：`build_module` で `material_count` ≥ 5
47. **プロトタイプ・パズル解放**：`build_module` 実行回数 ≥ 5
48. **リサイクルテクノの詩**：`build_module` で `recycled_percentage` ≥ 50%
49. **DIYマエストロへの招待**：`build_module` 累計回数 ≥ 10
50. **未来都市の模型師**：`build_module` で `scale_model=="city"` を1回完了
51. **英雄譚の序章を記せ**：`advance_day` の `day_count` ≥ 1
52. **虚空への問いかけ**：`advance_day` の `day_count` ≥ 3
53. **運命のクエスト：序**：`advance_day` の `day_count` ≥ 5
54. **宿命分岐の岐路**：`advance_day` の `day_count` ≥ 10
55. **影の記憶を紡ぐ者**：`advance_day` の `day_count` ≥ 20
56. **言葉なき台本の執筆者**：`log_learning` の `topics_logged` ≥ 1
57. **錆びた鎖の解放**：`log_learning` の `topics_logged` ≥ 3
58. **失われた文明の探訪**：`log_learning` の `topics_logged` ≥ 5
59. **夢幻の分岐を選べ**：`advance_day` の `day_count` in [7,14,21] のいずれかで起動
60. **序章よ、永遠なれ**：`advance_day` の `day_count` ≥ 30
61. **暗号解読の儀式**：`log_learning` の `topics_logged` ≥ 10
62. **電力ログの賛歌**：`review_day` 実行回数 ≥ 1
63. **学びのアーカイブ構築**：`review_day` の `entries_logged` ≥ 3
64. **知識の碑文を刻め**：`review_day` の `entries_logged` ≥ 5
65. **実験ノートの詩人**：`log_learning` の `experiments_logged` ≥ 1
66. **数式の迷宮を征く**：`cea_run` の実行回数 ≥ 3
67. **技術伝承の継者**：`build_module` 累計回数 ≥ 20
68. **ドキュメント・マスター**：`log_learning` の `docs_created` ≥ 1
69. **思考の航海図を描け**：`log_learning` の `mindmaps_created` ≥ 1
70. **概念実証の祭壇**：`build_module` で `prototype_validated==true`
71. **時間旅行者の足跡記録**：`log_learning` の `date_logs` ≥ 3
72. **一日一善ログ**：1日内 `review_day` 実行回数 ≥ 1
73. **技術覚書の殿堂**：累計 `docs_created` ≥ 5
74. **学習ノードの探訪**：累計 `topics_logged` ≥ 20
75. **自己分析の探鉱者**：累計 `entries_logged` ≥ 10
76. **連続三日探索**：3日連続で `advance_day` を実行
77. **無限ループの旅人**：5日連続で `advance_day` を実行
78. **記録の錬金術**：累計 `experiments_logged` ≥ 3
79. **ログリバースの詩**：累計 `mined_amount_XMR` の日次増分が2日連続で増加
80. **行動の肖像画**：累計 `total_actions` ≥ 50
81. **電力貯蔵庫の守護者**：`design_plant` の `battery_storage_kw` ≥ 1
82. **風力刃の創造者**：`design_plant` の `turbine_count` ≥ 1
83. **光の回廊設計**：`design_plant` の `panel_orientation=="East-West"` を1回
84. **電源塔の賢者**：累計 `design_plant` 実行回数 ≥ 5
85. **エネルギー洪水の演奏者**：1日内 `expected_output_kwh_per_day` 合計 ≥ 20
86. **未来電網の建築学**：`design_plant` で `grid_connection==true`
87. **循環回路の吟遊詩人**：`build_module` で `circuit_loops` ≥ 1
88. **都市発電講義**：`log_learning` の `lectures_logged` ≥ 1
89. **エコアルケミストの誕生**：累計 `mined_amount_XMR` ≥ 1
90. **炭素ゼロの祈り**：累計 `power_usage_W` ≤ 0 over 1 day
91. **仮想世界への架け橋**：`advance_day` の `day_count` ≥ 50
92. **フィードバック・ループの魔術師**：`mine_log` の `power_usage_W`/`hashrate_khps` が3日連続で改善
93. **制御理論の錬金術師**：累計 `cea_run` 実行回数 ≥ 20
94. **システム同調の詩**：累計 `total_actions` ≥ 100
95. **安定化フィルタの守人**：`mine_log` の `hashrate_khps` が3日連続で50%以上維持
96. **ノイズ除去の狩人**：`observe_optics` の `error_rate` ≤ 2%
97. **レギュレータの彫刻家**：累計 `power_usage_W`/`expected_output_kwh_per_day` ≤ 0.2
98. **サイクルの鼓動を聴け**：`advance_day` の `day_count` ≥ 75
99. **同期回路の探検家**：`mine_log` と `design_plant` を同日に両方実行 ≥ 1
100. **終焉を告げるエンディング**：`advance_day` の `day_count` ≥ 100
"""
    
    print("🎯 GPTの条件テキストを変換中...")
    print("=" * 60)
    
    # 条件を解析
    missions = []
    titles = []
    parser = ConditionParser()
    
    # 行ごとに解析
    lines = gpt_conditions.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'):
            continue
            
        # ミッション番号と条件を抽出
        match = re.match(r'(\d+)\.\s*\*\*([^*]+)\*\*：(.+)', line)
        if match:
            mission_id, mission_name, condition_text = match.groups()
            
            print(f"📋 解析中: {mission_name.strip()}")
            
            # 条件を解析
            parsed_condition = parser.parse_condition_text(condition_text)
            
            # ミッションIDを生成
            mission_id_clean = f"mission_{int(mission_id):03d}"
            
            # ミッションデータを作成
            mission_data = {
                "id": mission_id_clean,
                "name": mission_name.strip(),
                "description": f"{mission_name.strip()}を達成する",
                "type": "main",  # メインミッションとして扱う
                "condition": parsed_condition,
                "reward": {
                    "xmr": 0.000001 * (100 - int(mission_id) + 1),  # 後半のミッションほど報酬が高い
                    "title": f"title_{mission_id_clean}"
                }
            }
            
            # 称号データを作成
            title_data = {
                "id": f"title_{mission_id_clean}",
                "name": mission_name.strip(),
                "description": f"{mission_name.strip()}を達成した",
                "condition": parsed_condition,
                "rarity": "common" if int(mission_id) <= 50 else "uncommon"
            }
            
            missions.append(mission_data)
            titles.append(title_data)
    
    print(f"\n✅ {len(missions)}個のミッションを解析")
    print(f"✅ {len(titles)}個の称号を解析")
    
    # ミッションシステムに追加
    mission_system = MissionSystem()
    
    print("\n📋 ミッションデータを追加中...")
    for mission in missions:
        mission_system.add_mission(mission, "main_missions")
        print(f"   ✅ {mission['name']} を追加")
    
    print("\n🏆 称号データを追加中...")
    for title in titles:
        mission_system.add_title(title)
        print(f"   ✅ {title['name']} を追加")
    
    print()
    print("🎉 変換と追加が完了しました！")
    
    # 現在の状況を表示
    available = mission_system.get_available_missions()
    unlocked = mission_system.get_unlocked_titles()
    
    print(f"\n📊 現在の状況:")
    print(f"   利用可能なメインミッション: {len(available['main_missions'])}")
    print(f"   利用可能なサブミッション: {len(available['sub_missions'])}")
    print(f"   獲得済み称号: {len(unlocked)}")
    
    # 変換結果をファイルに保存
    result_data = {
        "missions": missions,
        "titles": titles
    }
    
    with open('data/gpt_converted_missions.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 変換結果を data/gpt_converted_missions.json に保存しました")
    
    # サンプル条件の解析結果を表示
    print(f"\n🧪 サンプル条件解析結果:")
    sample_conditions = [
        "`design_plant` の `expected_output_kwh_per_day` ≥ 1.0",
        "`mine_log` 実行回数 ≥ 3",
        "1日内の `mine_log` 回数 ≥ 1 かつ `power_usage_W` ≤ 0",
        "3日連続で `advance_day` を実行"
    ]
    
    for condition in sample_conditions:
        result = parser.parse_condition_text(condition)
        print(f"   条件: {condition}")
        print(f"   解析結果: {result}")
        print()

if __name__ == "__main__":
    convert_gpt_conditions_direct() 