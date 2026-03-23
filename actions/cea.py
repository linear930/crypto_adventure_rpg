#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEA計算記録・学習モジュール

プレイヤーが実際に実行したCEA（Chemical Equilibrium Analysis）計算の結果を記録し、
学習目標の達成を管理するシステムです。

データ保存先:
    data/cea_calculation/cea_calculations.json  - 全計算履歴
    data/cea_calculation/cea_calculation_xxx.json - 個別計算ファイル

新しい学習カテゴリを追加する場合:
    1. _initialize_learning_goals() に新カテゴリキーと _make_goal() のリストを追加する
    2. _update_learning_progress() に達成判定ロジックを追加する
    3. _show_category_goals() に elif を追加して表示に対応する
    4. check_goal_completion() のカテゴリリストに新キーを追加する
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CEALearningSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.cea_dir = Path("data/cea_calculation")
        self.cea_dir.mkdir(exist_ok=True)
        
        # 履歴ファイルの初期化
        self.history_file = self.cea_dir / "cea_calculations.json"
        self.calculation_history = self._load_calculation_history()
        
        # 学習目標の初期化
        self.learning_goals = self._initialize_learning_goals()
        
        # GameEngineへの参照を追加
        self.game_engine = None
        
        # 推進剤リストの初期化
        self.propellants = self._initialize_propellants()
        
    def set_game_engine(self, game_engine):
        """GameEngineへの参照を設定"""
        self.game_engine = game_engine
        
    def _initialize_learning_goals(self) -> Dict:
        """
        学習目標を初期化して返します。

        新しい目標を追加する場合:
            - 既存のカテゴリリストに _make_goal() を追加することで対応できます。
            - 新カテゴリの場合はインデックスに新キーを追加し、
              _show_category_goals() と check_goal_completion() も更新してください。
        """
        return {
            'basic_goals': [
                self._make_goal('first_cea',         '初めてのCEA計算',         '初めてCEA計算を実行した',
                    'achievement', target=1,  experience=100, crypto=0.001, status='locked'),
                self._make_goal('basic_propellants', '基本推進劑マスター', 'LOX/LH2、LOX/RP-1、N2O4/UDMHの計算を実行',
                    'collection', target=3,  experience=200, crypto=0.002),
            ],
            # ---- 推進剤カテゴリ: どんな推進剤の組み合わせを試したか ----
            'propellant_goals': [
                self._make_goal('propellant_alchemist',             '推進剤の錬金術師',           '未体験の推進剤組み合わせを1つ発見し計算',
                    'achievement', target=1,  experience=150,  crypto=0.0015),
                self._make_goal('propellant_polyhedron',            '推進剤の多面体',             '10種類以上の推進剤組み合わせを試行',
                    'collection',  target=10, experience=400,  crypto=0.004),
                self._make_goal('oxidizer_alchemy',                 '酸化剤の錬金術',             '新規酸化剤を組み合わせて実験計算',
                    'achievement', target=1,  experience=300,  crypto=0.003),
                self._make_goal('fuel_symphony',                    '燃料の交響曲',               '多様な燃料で燃焼特性を比較',
                    'collection',  target=5,  experience=280,  crypto=0.0028),
                self._make_goal('propellant_composition_alchemy',   '推進剤組成の錬金術',         '新規組成比率で実験計算成功',
                    'achievement', target=1,  experience=280,  crypto=0.0028),
                self._make_goal('propellant_stability_evaluator',   '推進剤安定性評価',           '推進剤の安定性試験を計算で模擬',
                    'achievement', target=1,  experience=320,  crypto=0.0032),
                self._make_goal('udmh_master',                      'UDMHマスター',              'UDMHを使用した計算を実行',
                    'achievement', target=1,  experience=350,  crypto=0.0035),
                self._make_goal('fluorine_explorer',                'フッ素の探求者',             'F2を使用した超高エネルギー計算を実行',
                    'achievement', target=1,  experience=500,  crypto=0.005),
                self._make_goal('high_energy_propellant_expert',    '高エネルギー推進剤エキスパート', 'F2、ClF3、ClF5などの高エネルギー酸化剤を使用',
                    'collection',  target=3,  experience=600,  crypto=0.006),
                self._make_goal('hydrazine_family_explorer',        'ヒドラジン族の探求者',       'UDMH、MMH、N2H4の計算を実行',
                    'collection',  target=3,  experience=450,  crypto=0.0045),
                self._make_goal('hydrocarbon_master',               '炭化水素マスター',           'C2H6からC50H102までの炭化水素燃料を試行',
                    'collection',  target=10, experience=400,  crypto=0.004),
                self._make_goal('concentrated_oxidizer_expert',     '高濃度酸化剤エキスパート',   '90%以上の高濃度酸化剤を使用',
                    'collection',  target=5,  experience=350,  crypto=0.0035),
                self._make_goal('dangerous_propellant_researcher',  '危険推進剤研究者',           'F2、ClF3、ClF5などの危険な推進剤を研究',
                    'collection',  target=3,  experience=700,  crypto=0.007),
            ],

            # ---- 性能カテゴリ: 比推力・排気速度・燃焼効率 ----
            'performance_goals': [
                self._make_goal('specific_impulse_heights',         '比推力の高みへ',             '比推力350秒以上の計算結果達成',
                    'achievement', target=1,  experience=300,  crypto=0.003),
                self._make_goal('high_specific_impulse_legend',     '高比推力伝説',               '400秒以上の比推力を目指せ',
                    'achievement', target=1,  experience=400,  crypto=0.004),
                self._make_goal('exhaust_velocity_traveler',        '排気速度の旅人',             '理論排気速度4000m/s超を達成',
                    'achievement', target=1,  experience=320,  crypto=0.0032),
                self._make_goal('combustion_efficiency_conductor',  '燃焼効率の調律者',           '燃焼効率95%以上の計算に成功',
                    'achievement', target=1,  experience=280,  crypto=0.0028),
                self._make_goal('energy_density_explorer',         'エネルギー密度の探求',        '高エネルギー密度燃料の評価計算',
                    'achievement', target=1,  experience=320,  crypto=0.0032),
            ],

            # ---- 圧力カテゴリ: 燃焼室圧力・混合比 ----
            'pressure_goals': [
                self._make_goal('combustion_chamber_abyss',         '燃焼室の深淵',               '200bar以上の燃焼室圧力で計算成功',
                    'achievement', target=1,  experience=250,  crypto=0.0025),
                self._make_goal('combustion_pressure_master',       '燃焼室圧力マスター',         '圧力変動を考慮した複数計算成功',
                    'collection',  target=5,  experience=350,  crypto=0.0035),
                self._make_goal('mixture_ratio_magician',           '混合比の魔術師',             '最適混合比を見つけて計算',
                    'achievement', target=1,  experience=200,  crypto=0.002),
                self._make_goal('mixture_ratio_variation_explorer', '混合比変動の探査',           '連続的に混合比を変えた計算実施',
                    'collection',  target=10, experience=320,  crypto=0.0032),
            ],

            # ---- 温度カテゴリ: 燃焼室温度・冷却設計 ----
            'temperature_goals': [
                self._make_goal('combustion_temperature_explorer',  '燃焼温度の探求者',           '3000K以上の燃焼温度を計算で確認',
                    'achievement', target=1,  experience=270,  crypto=0.0027),
                self._make_goal('propellant_cooling_researcher',    '推進剤冷却技術研究',         '燃焼温度低減技術を理論計算',
                    'achievement', target=1,  experience=270,  crypto=0.0027),
                self._make_goal('heat_exchange_efficiency_explorer','熱交換効率の探査',           '冷却系統の熱交換効率計算',
                    'achievement', target=1,  experience=270,  crypto=0.0027),
            ],

            # ---- 設計カテゴリ: ノズル・燃焼室形状 ----
            'design_goals': [
                self._make_goal('expansion_ratio_poet',             '膨張比の詩人',               '膨張比15以上のノズル計算を実施',
                    'achievement', target=1,  experience=220,  crypto=0.0022),
                self._make_goal('nozzle_design_master',             'ノズル設計の匠',             '拡大膨張ノズル設計と計算成功',
                    'achievement', target=1,  experience=300,  crypto=0.003),
                self._make_goal('combustion_chamber_shape_revolution','燃焼室形状の革命',         '複雑な燃焼室設計で性能向上計算',
                    'achievement', target=1,  experience=350,  crypto=0.0035),
            ],

            # ---- 高度解析カテゴリ: 精度・多段式・安定性・流体力学 ----
            'advanced_analysis_goals': [
                self._make_goal('calculation_accuracy_explorer',    '計算精度の探求者',           '誤差1%以下の再現性ある計算を実施',
                    'achievement', target=1,  experience=350,  crypto=0.0035),
                self._make_goal('multi_stage_propulsion_simulator', '多段階推進シミュレータ',     '多段式ロケットの燃焼計算を模擬',
                    'achievement', target=1,  experience=380,  crypto=0.0038),
                self._make_goal('combustion_stability_guardian',    '燃焼安定性の守護者',         '不安定燃焼を解析し回避計算',
                    'achievement', target=1,  experience=400,  crypto=0.004),
                self._make_goal('reaction_rate_analyzer',           '反応速度の解析者',           '燃焼反応速度の最適化計算',
                    'achievement', target=1,  experience=300,  crypto=0.003),
                self._make_goal('combustion_gas_dynamics',          '燃焼ガスの動力学',           '燃焼ガスの流体力学計算を実施',
                    'achievement', target=1,  experience=350,  crypto=0.0035),
                self._make_goal('extreme_combustion_challenger',    '極限燃焼条件への挑戦',       '極高圧・高温条件での計算成功',
                    'achievement', target=1,  experience=400,  crypto=0.004),
            ],

            # ---- ドキュメントカテゴリ: レポート・研究発表 ----
        'documentation_goals': [
                self._make_goal('engineering_document_master',      'エンジニアリング文書の達人',   'CEA計算結果を技術報告書にまとめる',
                    'achievement', target=1,  experience=300,  crypto=0.003),
                self._make_goal('propulsion_research_conference_participant', '燃焼推進研究会議参加', '専門家とのオンライン討論に参加（報告提出）',
                    'achievement', target=1,  experience=350,  crypto=0.0035),
                self._make_goal('future_rocket_bridge',             '未来ロケットへの架け橋',     '新技術を取り入れたCEA計算成功',
                    'achievement', target=1,  experience=400,  crypto=0.004),
            ]
        }
    
    def _initialize_propellants(self) -> Dict:
        """推進剤リストの初期化"""
        return {
            'fuels': {
                'LH2': {'name': '液体水素', 'description': '高比推力、低密度'},
                'RP-1': {'name': 'ケロシン', 'description': '高密度、安定性良好'},
                'CH4': {'name': 'メタン', 'description': '再利用可能ロケット向け'},
                'C2H6': {'name': 'エタン', 'description': 'メタンより高密度'},
                'UDMH': {'name': '非対称ジメチルヒドラジン', 'description': '高エネルギー密度、自己着火性'},
                'MMH': {'name': 'モノメチルヒドラジン', 'description': '自己着火性、高信頼性'},
                'N2H4': {'name': 'ヒドラジン', 'description': '単推進剤としても使用可能'},
                'JP-8': {'name': 'ジェット燃料', 'description': '軍用燃料、高密度'},
                'JP-10': {'name': '高密度燃料', 'description': '高密度、高エネルギー'},
                'C2H4': {'name': 'エチレン', 'description': '高エネルギー密度'},
                'C3H8': {'name': 'プロパン', 'description': 'LPG燃料'},
                'C4H10': {'name': 'ブタン', 'description': '高密度炭化水素'},
                'C2H5OH': {'name': 'エタノール', 'description': '再生可能燃料'},
                'C3H6O': {'name': 'アセトン', 'description': '高エネルギー密度'},
                'C6H6': {'name': 'ベンゼン', 'description': '芳香族炭化水素'},
                'C8H18': {'name': 'オクタン', 'description': '高密度燃料'},
                'C10H22': {'name': 'デカン', 'description': '高密度炭化水素'},
                'C12H26': {'name': 'ドデカン', 'description': '高密度燃料'},
                'C14H30': {'name': 'テトラデカン', 'description': '高密度炭化水素'},
                'C16H34': {'name': 'ヘキサデカン', 'description': '高密度燃料'},
                'C18H38': {'name': 'オクタデカン', 'description': '高密度炭化水素'},
                'C20H42': {'name': 'エイコサン', 'description': '高密度燃料'},
                'C22H46': {'name': 'ドコサン', 'description': '高密度炭化水素'},
                'C24H50': {'name': 'テトラコサン', 'description': '高密度燃料'},
                'C26H54': {'name': 'ヘキサコサン', 'description': '高密度炭化水素'},
                'C28H58': {'name': 'オクタコサン', 'description': '高密度燃料'},
                'C30H62': {'name': 'トリアコンタン', 'description': '高密度炭化水素'},
                'C32H66': {'name': 'ドトリアコンタン', 'description': '高密度燃料'},
                'C34H70': {'name': 'テトラトリアコンタン', 'description': '高密度炭化水素'},
                'C36H74': {'name': 'ヘキサトリアコンタン', 'description': '高密度燃料'},
                'C38H78': {'name': 'オクタトリアコンタン', 'description': '高密度炭化水素'},
                'C40H82': {'name': 'テトラコンタン', 'description': '高密度燃料'},
                'C42H86': {'name': 'ドテトラコンタン', 'description': '高密度炭化水素'},
                'C44H90': {'name': 'テトラテトラコンタン', 'description': '高密度燃料'},
                'C46H94': {'name': 'ヘキサテトラコンタン', 'description': '高密度炭化水素'},
                'C48H98': {'name': 'オクタテトラコンタン', 'description': '高密度燃料'},
                'C50H102': {'name': 'ペンタコンタン', 'description': '高密度炭化水素'}
            },
            'oxidizers': {
                'LOX': {'name': '液体酸素', 'description': '標準的酸化剤、高効率'},
                'N2O4': {'name': '四酸化二窒素', 'description': '自己着火性、高密度'},
                'H2O2': {'name': '過酸化水素', 'description': '単推進剤としても使用可能'},
                'N2O': {'name': '亜酸化窒素', 'description': 'ハイブリッドロケット向け'},
                'F2': {'name': 'フッ素', 'description': '最高性能、極めて危険'},
                'ClF3': {'name': '三フッ化塩素', 'description': '高エネルギー、腐食性'},
                'ClF5': {'name': '五フッ化塩素', 'description': '高エネルギー、腐食性'},
                'OF2': {'name': '二フッ化酸素', 'description': '高エネルギー、危険'},
                'N2F4': {'name': '四フッ化二窒素', 'description': '高エネルギー、自己着火性'},
                'CIF3': {'name': '三フッ化塩素', 'description': '高エネルギー、腐食性'},
                'CIF5': {'name': '五フッ化塩素', 'description': '高エネルギー、腐食性'},
                'NF3': {'name': '三フッ化窒素', 'description': '高エネルギー、危険'},
                'N2O3': {'name': '三酸化二窒素', 'description': '高エネルギー、不安定'},
                'N2O5': {'name': '五酸化二窒素', 'description': '高エネルギー、不安定'},
                'HNO3': {'name': '硝酸', 'description': '高密度、腐食性'},
                'N2H4': {'name': 'ヒドラジン', 'description': '単推進剤としても使用可能'},
                'H2O2_90': {'name': '90%過酸化水素', 'description': '高濃度、高エネルギー'},
                'H2O2_98': {'name': '98%過酸化水素', 'description': '超高濃度、高エネルギー'},
                'H2O2_99': {'name': '99%過酸化水素', 'description': '超高濃度、高エネルギー'},
                'H2O2_100': {'name': '100%過酸化水素', 'description': '純粋、高エネルギー'},
                'N2O4_90': {'name': '90%四酸化二窒素', 'description': '高濃度、高エネルギー'},
                'N2O4_95': {'name': '95%四酸化二窒素', 'description': '超高濃度、高エネルギー'},
                'N2O4_98': {'name': '98%四酸化二窒素', 'description': '超高濃度、高エネルギー'},
                'N2O4_99': {'name': '99%四酸化二窒素', 'description': '純粋、高エネルギー'},
                'N2O4_100': {'name': '100%四酸化二窒素', 'description': '純粋、高エネルギー'},
                'LOX_90': {'name': '90%液体酸素', 'description': '高濃度、高エネルギー'},
                'LOX_95': {'name': '95%液体酸素', 'description': '超高濃度、高エネルギー'},
                'LOX_98': {'name': '98%液体酸素', 'description': '超高濃度、高エネルギー'},
                'LOX_99': {'name': '99%液体酸素', 'description': '純粋、高エネルギー'},
                'LOX_100': {'name': '100%液体酸素', 'description': '純粋、高エネルギー'}
            }
        }
    
    def show_propellant_list(self, propellant_type: str = "all"):
        """推進剤リストを表示"""
        print(f"\n🚀 推進剤リスト")
        print("="*50)
        
        if propellant_type in ["all", "fuels"]:
            print("\n🔥 燃料:")
            print("-" * 30)
            for i, (key, info) in enumerate(self.propellants['fuels'].items(), 1):
                print(f"{i:2d}. {key:12} - {info['name']:15} ({info['description']})")
        
        if propellant_type in ["all", "oxidizers"]:
            print("\n💨 酸化剤:")
            print("-" * 30)
            for i, (key, info) in enumerate(self.propellants['oxidizers'].items(), 1):
                print(f"{i:2d}. {key:12} - {info['name']:15} ({info['description']})")
        
        print("\n💡 ヒント: 番号を入力するか、直接化学式を入力してください")
        print("💡 例: 1 または LH2 または custom")
    
    def select_propellant(self, propellant_type: str, prev_prompt: str = "", prev_default: str = "") -> str:
        """推進剤を選択"""
        propellants = self.propellants['fuels'] if propellant_type == 'fuel' else self.propellants['oxidizers']
        prompt_str = f"{'燃料' if propellant_type == 'fuel' else '酸化剤'}を選択してください (list/番号/化学式/custom) [{'LH2' if propellant_type == 'fuel' else 'LOX'}]: "
        default_val = "LH2" if propellant_type == 'fuel' else "LOX"
        
        while True:
            choice, sig = self._prompt_input(prompt_str, default_val, prev_prompt=prev_prompt, prev_default=prev_default)
            
            if sig == "abort": return None
            if sig == "back": return "back"
            
            if choice.lower() == "list":
                self.show_propellant_list(propellant_type + "s")
                continue
            
            # 番号で選択
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(propellants):
                    return list(propellants.keys())[index]
                else:
                    print("❌ 無効な番号です")
                    continue
            
            # 直接化学式入力
            if choice.upper() in propellants:
                return choice.upper()
            
            # カスタム入力
            if choice.lower() == "custom":
                custom, csig = self._prompt_input(f"カスタム{'燃料' if propellant_type == 'fuel' else '酸化剤'}の化学式を入力: ")
                if csig == "abort": return None
                if csig == "back": continue
                return custom.upper()
            
            print("❌ 無効な選択です。番号、化学式、または 'custom' を入力してください")
    
    def record_cea_calculation(self) -> Dict:
        """CEA計算結果を記録"""
        print(f"\n🚀 CEA計算結果記録")
        print("="*40)
        print("💡 入力中に「abort」と入力すると記録を中断できます")
        print("💡 入力中に「back」と入力すると一つ前の入力に戻れます")
        print("💡 入力中に「list」と入力すると推進剤リストを表示します")
        print("-" * 40)
        
        # 基本パラメータ入力
        print("📊 計算パラメータを入力してください:")
        
        try:
            # 燃料・酸化剤選択
            fuel = None
            oxidizer = None
            
            while True:
                if fuel is None:
                    fuel = self.select_propellant('fuel')
                    if fuel is None: return None
                    if fuel == "back":
                        print("🔄 最初の入力なので戻る場所がありません。")
                        fuel = None
                        continue
                
                oxidizer = self.select_propellant('oxidizer', prev_prompt="燃料を選択してください (list/番号/化学式/custom) [LH2]: ", prev_default="LH2")
                if oxidizer is None: return None
                if oxidizer == "back":
                    fuel = None
                    continue
                break
            
            val, sig = self._prompt_input("燃焼室圧力 (bar) [50]: ", "50")
            if sig == "abort": return None
            Pc = float(val)

            val, sig = self._prompt_input("混合比 [6.0]: ", "6.0", prev_prompt="燃焼室圧力 (bar) [50]: ", prev_default="50")
            if sig == "abort": return None
            if sig == "back": Pc = float(val)
            else: MR = float(val)
            if sig == "back":
                val, sig = self._prompt_input("混合比 [6.0]: ", "6.0")
                if sig == "abort": return None
                MR = float(val)

            val, sig = self._prompt_input("排気圧力 (bar) [1.0]: ", "1.0", prev_prompt="混合比 [6.0]: ", prev_default="6.0")
            if sig == "abort": return None
            if sig == "back": MR = float(val)
            else: Pe = float(val)
            if sig == "back":
                val, sig = self._prompt_input("排気圧力 (bar) [1.0]: ", "1.0")
                if sig == "abort": return None
                Pe = float(val)

        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            fuel, oxidizer, Pc, MR, Pe = fuel or "LH2", oxidizer or "LOX", 50.0, 6.0, 1.0
        
        # 計算結果入力
        print(f"\n📈 計算結果を入力してください:")
        
        try:
            val, sig = self._prompt_input("真空中比推力 (s) [400]: ", "400")
            if sig == "abort": return None
            isp_vacuum = float(val)

            val, sig = self._prompt_input("海面比推力 (s) [350]: ", "350", prev_prompt="真空中比推力 (s) [400]: ", prev_default="400")
            if sig == "abort": return None
            if sig == "back": isp_vacuum = float(val)
            else: isp_sea_level = float(val)
            if sig == "back":
                val, sig = self._prompt_input("海面比推力 (s) [350]: ", "350")
                if sig == "abort": return None
                isp_sea_level = float(val)

            val, sig = self._prompt_input("燃焼室温度 (K) [3500]: ", "3500", prev_prompt="海面比推力 (s) [350]: ", prev_default="350")
            if sig == "abort": return None
            if sig == "back": isp_sea_level = float(val)
            else: Tc = float(val)
            if sig == "back":
                val, sig = self._prompt_input("燃焼室温度 (K) [3500]: ", "3500")
                if sig == "abort": return None
                Tc = float(val)

            val, sig = self._prompt_input("比熱比 [1.2]: ", "1.2", prev_prompt="燃焼室温度 (K) [3500]: ", prev_default="3500")
            if sig == "abort": return None
            if sig == "back": Tc = float(val)
            else: gamma = float(val)
            if sig == "back":
                val, sig = self._prompt_input("比熱比 [1.2]: ", "1.2")
                if sig == "abort": return None
                gamma = float(val)

            val, sig = self._prompt_input("推力係数 [1.8]: ", "1.8", prev_prompt="比熱比 [1.2]: ", prev_default="1.2")
            if sig == "abort": return None
            if sig == "back": gamma = float(val)
            else: Cf = float(val)
            if sig == "back":
                val, sig = self._prompt_input("推力係数 [1.8]: ", "1.8")
                if sig == "abort": return None
                Cf = float(val)

        except ValueError:
            print("❌ 無効な値です。デフォルト値を使用します。")
            isp_vacuum, isp_sea_level, Tc, gamma, Cf = 400.0, 350.0, 3500.0, 1.2, 1.8
        
        # 学習メモ入力
        print(f"\n📝 学習メモを入力してください:")
        notes, sig = self._prompt_input("計算の目的、発見、学んだこと: ")
        if sig == "abort": return None
        
        # 使用ツール入力
        print(f"\n🛠️ 使用ツール:")
        tools, sig = self._prompt_input("使用したソフトウェア/ツール (例: CEA, RPA, 自作プログラム): ", prev_prompt="計算の目的、発見、学んだこと: ")
        if sig == "abort": return None
        if sig == "back":
            notes = tools  # back entered into tools gives back the notes
            tools, sig = self._prompt_input("使用したソフトウェア/ツール (例: CEA, RPA, 自作プログラム): ")
            if sig == "abort": return None

        # 結果をまとめる
        result = {
            'timestamp': datetime.now().isoformat(),
            'fuel': fuel,
            'oxidizer': oxidizer,
            'Pc': Pc,
            'MR': MR,
            'Pe': Pe,
            'isp_vacuum': isp_vacuum,
            'isp_sea_level': isp_sea_level,
            'Tc': Tc,
            'gamma': gamma,
            'Cf': Cf,
            'notes': notes,
            'tools': tools,
            'status': 'recorded'
        }
        
        # 履歴に追加
        self.calculation_history.append(result)
        
        # 学習目標の進捗を更新
        self._update_learning_progress(result)
        
        # ファイルに保存
        self._save_calculation(result)
        self._save_calculation_history()
        
        print(f"\n✅ CEA計算結果を記録しました!")
        print(f"   🔥 燃料: {fuel}")
        print(f"   💨 酸化剤: {oxidizer}")
        print(f"   📊 燃焼室圧力: {Pc} bar")
        print(f"   ⚖️ 混合比: {MR}")
        print(f"   ⚡ 真空中比推力: {isp_vacuum} s")
        print(f"   🌡️ 燃焼室温度: {Tc} K")
        
        return result
    
    def _update_learning_progress(self, result: Dict):
        """学習目標の進捗を更新"""
        fuel_oxidizer = f"{result['fuel']}/{result['oxidizer']}"
        basic_combinations = ['LH2/LOX', 'RP-1/LOX', 'UDMH/N2O4']
        
        # 基本目標の更新
        for goal in self.learning_goals['basic_goals']:
            if goal['id'] == 'first_cea':
                goal['current'] = 1
                goal['status'] = 'active'
            elif goal['id'] == 'basic_propellants':
                # 基本推進剤の組み合わせをチェック
                if fuel_oxidizer in basic_combinations:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 推進剤目標の更新
        for goal in self.learning_goals['propellant_goals']:
            if goal['id'] == 'propellant_alchemist' and fuel_oxidizer not in basic_combinations:
                goal['current'] = 1
            elif goal['id'] == 'propellant_polyhedron':
                # ユニークな推進剤組み合わせをカウント
                unique_combinations = set()
                for calc in self.calculation_history:
                    unique_combinations.add(f"{calc['fuel']}/{calc['oxidizer']}")
                goal['current'] = len(unique_combinations)
            elif goal['id'] == 'oxidizer_alchemy' and result['oxidizer'] not in ['LOX', 'N2O4', 'H2O2']:
                goal['current'] = 1
            elif goal['id'] == 'fuel_symphony':
                # ユニークな燃料をカウント
                unique_fuels = set()
                for calc in self.calculation_history:
                    unique_fuels.add(calc['fuel'])
                goal['current'] = len(unique_fuels)
            elif goal['id'] == 'propellant_composition_alchemy' and '新規組成' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'propellant_stability_evaluator' and '安定性' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'udmh_master' and 'UDMH' in result['fuel']:
                goal['current'] = 1
            elif goal['id'] == 'fluorine_explorer' and 'F2' in result['oxidizer']:
                goal['current'] = 1
            elif goal['id'] == 'high_energy_propellant_expert':
                # F2、ClF3、ClF5などの高エネルギー酸化剤をチェック
                high_energy_oxidizers = ['F2', 'ClF3', 'ClF5', 'OF2', 'N2F4']
                if result['oxidizer'] in high_energy_oxidizers:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'hydrazine_family_explorer':
                # UDMH、MMH、N2H4のヒドラジン族をチェック
                hydrazine_fuels = ['UDMH', 'MMH', 'N2H4']
                if result['fuel'] in hydrazine_fuels:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'hydrocarbon_master':
                # C2H6からC50H102までの炭化水素燃料をチェック
                hydrocarbon_fuels = [key for key in self.propellants['fuels'].keys() 
                                   if key.startswith('C') and 'H' in key and key not in ['CH4']]
                if result['fuel'] in hydrocarbon_fuels:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'concentrated_oxidizer_expert':
                # 90%以上の高濃度酸化剤をチェック
                concentrated_oxidizers = [key for key in self.propellants['oxidizers'].keys() 
                                        if any(suffix in key for suffix in ['_90', '_95', '_98', '_99', '_100'])]
                if result['oxidizer'] in concentrated_oxidizers:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
            elif goal['id'] == 'dangerous_propellant_researcher':
                # F2、ClF3、ClF5などの危険な推進剤をチェック
                dangerous_propellants = ['F2', 'ClF3', 'ClF5', 'OF2', 'N2F4', 'NF3']
                if result['oxidizer'] in dangerous_propellants:
                    goal['current'] = min(goal['current'] + 1, goal['target'])
        
        # 性能目標の更新
        for goal in self.learning_goals['performance_goals']:
            if goal['id'] == 'specific_impulse_heights' and result['isp_vacuum'] >= 350:
                goal['current'] = 1
            elif goal['id'] == 'high_specific_impulse_legend' and result['isp_vacuum'] >= 400:
                goal['current'] = 1
            elif goal['id'] == 'exhaust_velocity_traveler':
                # 理論排気速度 = 比推力 × 重力加速度
                exhaust_velocity = result['isp_vacuum'] * 9.81
                if exhaust_velocity >= 4000:
                    goal['current'] = 1
            elif goal['id'] == 'combustion_efficiency_conductor' and '効率95%' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'energy_density_explorer' and 'エネルギー密度' in result['notes']:
                goal['current'] = 1
        
        # 圧力目標の更新
        for goal in self.learning_goals['pressure_goals']:
            if goal['id'] == 'combustion_chamber_abyss' and result['Pc'] >= 200:
                goal['current'] = 1
            elif goal['id'] == 'combustion_pressure_master':
                # 圧力変動を考慮した計算をカウント
                pressure_variations = 0
                for calc in self.calculation_history:
                    if calc['Pc'] != result['Pc']:
                        pressure_variations += 1
                goal['current'] = min(pressure_variations, goal['target'])
            elif goal['id'] == 'mixture_ratio_magician' and '最適混合比' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'mixture_ratio_variation_explorer':
                # 混合比変動の計算をカウント
                mr_variations = 0
                for calc in self.calculation_history:
                    if calc['MR'] != result['MR']:
                        mr_variations += 1
                goal['current'] = min(mr_variations, goal['target'])
        
        # 温度目標の更新
        for goal in self.learning_goals['temperature_goals']:
            if goal['id'] == 'combustion_temperature_explorer' and result['Tc'] >= 3000:
                goal['current'] = 1
            elif goal['id'] == 'propellant_cooling_researcher' and '冷却技術' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'heat_exchange_efficiency_explorer' and '熱交換' in result['notes']:
                goal['current'] = 1
        
        # 設計目標の更新
        for goal in self.learning_goals['design_goals']:
            # 膨張比 = 燃焼室圧力 / 排気圧力
            expansion_ratio = result['Pc'] / result['Pe']
            if goal['id'] == 'expansion_ratio_poet' and expansion_ratio >= 15:
                goal['current'] = 1
            elif goal['id'] == 'nozzle_design_master' and 'ノズル設計' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_chamber_shape_revolution' and '燃焼室形状' in result['notes']:
                goal['current'] = 1
        
        # 高度解析目標の更新
        for goal in self.learning_goals['advanced_analysis_goals']:
            if goal['id'] == 'calculation_accuracy_explorer' and '精度1%' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'multi_stage_propulsion_simulator' and '多段式' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_stability_guardian' and '燃焼安定性' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'reaction_rate_analyzer' and '反応速度' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'combustion_gas_dynamics' and '流体力学' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'extreme_combustion_challenger' and (result['Pc'] >= 300 or result['Tc'] >= 4000):
                goal['current'] = 1
        
        # ドキュメント目標の更新
        for goal in self.learning_goals['documentation_goals']:
            if goal['id'] == 'engineering_document_master' and '技術報告書' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'propulsion_research_conference_participant' and '研究会議' in result['notes']:
                goal['current'] = 1
            elif goal['id'] == 'future_rocket_bridge' and '新技術' in result['notes']:
                goal['current'] = 1
    
    def _load_calculation_history(self) -> List[Dict]:
        """計算履歴を読み込み"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('calculations', [])
            except Exception as e:
                print(f"⚠️ CEA履歴読み込みエラー: {e}")
        return []
    
    def _save_calculation_history(self):
        """計算履歴をファイルに保存"""
        try:
            data = {'calculations': self.calculation_history}
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ CEA履歴保存エラー: {e}")
    
    def _save_calculation(self, result: Dict):
        """計算結果をファイルに保存"""
        timestamp = int(time.time())
        filename = f"cea_calculation_{timestamp}.json"
        filepath = self.cea_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 計算結果を保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
        
        # GameEngineのウォレットにも保存
        if self.game_engine:
            if 'cea_calculations' not in self.game_engine.wallet:
                self.game_engine.wallet['cea_calculations'] = []
            self.game_engine.wallet['cea_calculations'].append(result)
            self.game_engine.save_wallet()
            print("💾 GameEngineウォレットに保存しました")
    
    def show_learning_goals(self, selected_category: str = "all"):
        """学習目標を表示"""
        print(f"\n🎯 CEA学習目標")
        print("="*50)
        
        categories = {
            'basic': '📚 基本目標',
            'propellant': '🚀 推進剤目標',
            'performance': '🔬 性能目標',
            'pressure': '🌡️ 圧力目標',
            'temperature': '🌡️ 温度目標',
            'design': '🛠️ 設計目標',
            'advanced': '🚀 高度目標',
            'documentation': '📋 ドキュメント目標',
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
        elif category == "propellant":
            goals = self.learning_goals['propellant_goals']
        elif category == "performance":
            goals = self.learning_goals['performance_goals']
        elif category == "pressure":
            goals = self.learning_goals['pressure_goals']
        elif category == "temperature":
            goals = self.learning_goals['temperature_goals']
        elif category == "design":
            goals = self.learning_goals['design_goals']
        elif category == "advanced":
            goals = self.learning_goals['advanced_analysis_goals']
        elif category == "documentation":
            goals = self.learning_goals['documentation_goals']
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
        
        for category in ['basic_goals', 'propellant_goals', 'performance_goals', 'pressure_goals', 'temperature_goals', 'design_goals', 'advanced_analysis_goals', 'documentation_goals']:
            for goal in self.learning_goals[category]:
                if goal['status'] == 'active' and goal['current'] >= goal['target']:
                    goal['status'] = 'completed'
                    goal['completion_time'] = datetime.now().isoformat()
                    completed_goals.append(goal)
        
        return completed_goals
    
    def get_calculation_statistics(self) -> Dict:
        """計算統計を取得"""
        if not self.calculation_history:
            return {'status': 'no_data'}
        
        # 統計計算
        total_calculations = len(self.calculation_history)
        unique_propellants = set()
        max_isp = 0
        max_pressure = 0
        
        # 新しい推進剤統計
        udmh_usage = 0
        fluorine_usage = 0
        high_energy_oxidizer_usage = 0
        hydrazine_family_usage = 0
        hydrocarbon_usage = 0
        concentrated_oxidizer_usage = 0
        dangerous_propellant_usage = 0
        
        for calc in self.calculation_history:
            unique_propellants.add(f"{calc['fuel']}/{calc['oxidizer']}")
            max_isp = max(max_isp, calc['isp_vacuum'])
            max_pressure = max(max_pressure, calc['Pc'])
            
            # UDMH使用統計
            if 'UDMH' in calc['fuel']:
                udmh_usage += 1
            
            # フッ素使用統計
            if 'F2' in calc['oxidizer']:
                fluorine_usage += 1
            
            # 高エネルギー酸化剤統計
            high_energy_oxidizers = ['F2', 'ClF3', 'ClF5', 'OF2', 'N2F4']
            if calc['oxidizer'] in high_energy_oxidizers:
                high_energy_oxidizer_usage += 1
            
            # ヒドラジン族統計
            hydrazine_fuels = ['UDMH', 'MMH', 'N2H4']
            if calc['fuel'] in hydrazine_fuels:
                hydrazine_family_usage += 1
            
            # 炭化水素統計
            hydrocarbon_fuels = [key for key in self.propellants['fuels'].keys() 
                               if key.startswith('C') and 'H' in key and key not in ['CH4']]
            if calc['fuel'] in hydrocarbon_fuels:
                hydrocarbon_usage += 1
            
            # 高濃度酸化剤統計
            concentrated_oxidizers = [key for key in self.propellants['oxidizers'].keys() 
                                    if any(suffix in key for suffix in ['_90', '_95', '_98', '_99', '_100'])]
            if calc['oxidizer'] in concentrated_oxidizers:
                concentrated_oxidizer_usage += 1
            
            # 危険推進剤統計
            dangerous_propellants = ['F2', 'ClF3', 'ClF5', 'OF2', 'N2F4', 'NF3']
            if calc['oxidizer'] in dangerous_propellants:
                dangerous_propellant_usage += 1
        
        return {
            'status': 'success',
            'total_calculations': total_calculations,
            'unique_propellants': len(unique_propellants),
            'max_isp': max_isp,
            'max_pressure': max_pressure,
            'propellant_combinations': list(unique_propellants),
            'udmh_usage': udmh_usage,
            'fluorine_usage': fluorine_usage,
            'high_energy_oxidizer_usage': high_energy_oxidizer_usage,
            'hydrazine_family_usage': hydrazine_family_usage,
            'hydrocarbon_usage': hydrocarbon_usage,
            'concentrated_oxidizer_usage': concentrated_oxidizer_usage,
            'dangerous_propellant_usage': dangerous_propellant_usage
        }
    
    def show_calculation_history(self):
        """計算履歴を表示"""
        print(f"\n📚 CEA計算履歴")
        print("="*50)
        
        if not self.calculation_history:
            print("📝 計算履歴がありません")
            return
        
        for i, calc in enumerate(self.calculation_history[-5:], 1):  # 最新5件
            print(f"\n{i}. {calc['fuel']}/{calc['oxidizer']} (Pc={calc['Pc']}bar, MR={calc['MR']})")
            print(f"   ⚡ 比推力: {calc['isp_vacuum']}s (真空), {calc['isp_sea_level']}s (海面)")
            print(f"   🌡️ 燃焼室温度: {calc['Tc']}K")
            print(f"   🛠️ ツール: {calc['tools']}")
            if calc['notes']:
                print(f"   📝 メモ: {calc['notes'][:50]}...") 