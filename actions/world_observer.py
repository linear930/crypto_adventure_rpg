#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界観測システム
現実のニュースから「世界のエネルギー」を計算し、ゲームに反映させる
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class WorldObserverSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('world_observation', {}).get('news_api_key', '')
        self.game_engine = None
        self.history_file = Path("data/activity_logs/world_observations.json")
        
        # 観測対象のキーワードとカテゴリ
        self.topics = {
            "war": ["war", "conflict", "military", "geopolitics"],
            "ai": ["AI", "artificial intelligence", "OpenAI", "singularity"],
            "crypto": ["crypto", "bitcoin", "ethereum", "web3"]
        }
        
        self.energy_state = {
            "total_energy": 0.0,
            "momentum": 0.0,
            "trends": {}
        }
        
        self._load_history()

    def set_game_engine(self, engine):
        self.game_engine = engine

    def _load_history(self):
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"observations": []}, f, ensure_ascii=False, indent=2)
            self.history = []
        else:
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get("observations", [])
            except:
                self.history = []

    def _save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({"observations": self.history}, f, ensure_ascii=False, indent=2)

    # ==========================================
    # ① 観測レイヤー（センサー）
    # ==========================================
    def fetch_news_counts(self, days_ago: int = 1) -> Dict[str, int]:
        """NewsAPIからトピックごとの記事数を取得"""
        counts = {}
        if not self.api_key or self.api_key == 'YOUR_WALLET_ADDRESS_HERE' or self.api_key == '':
            print("⚠️ NewsAPIキーが設定されていません。モックデータを使用します。")
            import random
            counts = {
                "war": random.randint(500, 2000),
                "ai": random.randint(800, 3000),
                "crypto": random.randint(1000, 4000)
            }
            return counts

        # 日付の計算
        target_date = datetime.now() - timedelta(days=days_ago)
        date_str = target_date.strftime("%Y-%m-%d")

        print(f"📡 観測衛星を起動中... 対象日: {date_str}")

        for category, keywords in self.topics.items():
            query = " OR ".join(f'"{k}"' for k in keywords)
            encoded_query = urllib.parse.quote(query)
            # URL構築
            url = f"https://newsapi.org/v2/everything?q={encoded_query}&from={date_str}&to={date_str}&language=en&sortBy=publishedAt&apiKey={self.api_key}"
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'CryptoAdventureRPG/2.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    counts[category] = data.get('totalResults', 0)
            except Exception as e:
                print(f"❌ 観測エラー ({category}): {e}")
                counts[category] = 0
            
            # API制限保護
            time.sleep(1)
            
        return counts

    # ==========================================
    # ② 圧縮レイヤー（理解・物理モデル化）
    # ==========================================
    def calculate_energy(self, current_counts: Dict[str, int], previous_counts: Dict[str, int]) -> Dict:
        """記事数を物理エネルギーに変換"""
        energy = 0.0
        momentum = 0.0
        trends = {}

        for category in self.topics.keys():
            current = current_counts.get(category, 0)
            previous = previous_counts.get(category, 0)
            
            # 記事数をエネルギー（活動量）とする。1000記事 = 100エネルギー
            cat_energy = current / 10.0
            
            # 運動量（変化率）の計算
            diff = current - previous
            cat_momentum = diff / 10.0
            
            # トレンドの判定（運動体・軌道モデル）
            trend_state = "停滞軌道（静止状態）"
            if cat_momentum > 30:
                trend_state = "急加速🚀（軌道離脱・ブレイクスルー）"
            elif cat_momentum > 10:
                trend_state = "上昇軌道📈（安定加速）"
            elif cat_momentum < -30:
                trend_state = "軌道崩壊📉（急速減衰）"
            elif cat_momentum < -10:
                trend_state = "下降軌道（エネルギー喪失）"
            elif abs(cat_momentum) <= 10 and cat_energy > 150:
                trend_state = "高エネルギー振動⚡（軌道維持・乱高下）"

            trends[category] = {
                "energy": round(cat_energy, 1),
                "momentum": round(cat_momentum, 1),
                "state": trend_state
            }
            
            energy += cat_energy
            momentum += cat_momentum

        self.energy_state = {
            "total_energy": round(energy, 1),
            "momentum": round(momentum, 1),
            "trends": trends,
            "date": datetime.now().isoformat()
        }
        
        return self.energy_state

    # ==========================================
    # ③ 表示レイヤー（UI）
    # ==========================================
    def display_world_state(self):
        """現在の世界状態をCLIで表示"""
        print("\n" + "="*50)
        print("🌍 世界線観測レポート")
        print("="*50)
        
        print(f"⚡ 総観測エネルギー: {self.energy_state['total_energy']} E")
        momentum_sign = "+" if self.energy_state['momentum'] >= 0 else ""
        print(f"🌪️  世界運動量 (1日の変動): {momentum_sign}{self.energy_state['momentum']} P")
        print("-" * 50)
        
        print("📊 セクター別 軌道状態:")
        for category, data in self.energy_state['trends'].items():
            cat_name = {"war": "紛争・地政学", "ai": "AI・技術特異点", "crypto": "仮想通貨・Web3"}.get(category, category)
            print(f"  [{cat_name}]")
            print(f"   現在位置 (Energy)  : {data['energy']} E")
            print(f"   現在速度 (Momentum): {momentum_sign if data['momentum'] >= 0 else ''}{data['momentum']} P")
            print(f"   軌道状態 (Orbit)   : {data['state']}")
            
            # 簡易グラフの描画
            bar_length = min(int(data['energy'] / 10), 30)
            bar = "█" * bar_length
            if data['momentum'] > 10:
                bar = "\033[91m" + bar + "\033[0m" # 赤色（上昇）
            elif data['momentum'] < -10:
                bar = "\033[94m" + bar + "\033[0m" # 青色（下降）
            print(f"   グラフ: |{bar}")
            print()
            
        # 全体評価
        print("-" * 50)
        print("🎯 観測結果のサマリー:")
        if self.energy_state['total_energy'] > 500:
            print("   ⚠️ 世界は極めて【騒がしい】状態です（ボラティリティ高）")
            print("   💡 ゲーム内ミッションの難易度と報酬が上昇します")
        elif self.energy_state['total_energy'] < 200:
            print("   🕊️ 世界は現在【平坦】で静かな状態です")
            print("   💡 基礎研究や安定した活動に向いています")
        else:
            print("   ⚖️ 世界は【安定振動】を続けています")
            print("   💡 通常の活動に最適な環境です")
        
        print("="*50)

    def observe_and_record(self):
        """観測から記録までの一連の処理を実行"""
        if self.game_engine:
            if not self.game_engine.use_action():
                print("❌ 行動回数が残っていません。次の日に進んでください。")
                return None

        print("\n📡 世界のニュースAPIへ接続を試みています...")
        
        # 今日と昨日のデータを取得して圧縮
        counts_today = self.fetch_news_counts(days_ago=1)
        
        # 履歴から昨日のデータを取得するか、新たに取得
        counts_yesterday = None
        if len(self.history) > 0:
            last_record = self.history[-1]
            counts_yesterday = last_record.get('raw_counts', {})
            
        if not counts_yesterday:
            counts_yesterday = self.fetch_news_counts(days_ago=2)
            
        energy_state = self.calculate_energy(counts_today, counts_yesterday)
        
        # UI表示
        self.display_world_state()
        
        # 記録
        record = {
            "date": datetime.now().isoformat(),
            "raw_counts": counts_today,
            "energy_state": energy_state
        }
        self.history.append(record)
        self.history = self.history[-30:] # 直近30件のみ保持
        self._save_history()
        
        # 経験値などの付与
        if self.game_engine:
            exp_reward = int(energy_state['total_energy'] / 10) + 20
            print(f"\n🎁 観測報酬獲得!")
            print(f"   💎 経験値: +{exp_reward}")
            self.game_engine.add_experience(exp_reward)
            
            # 世界のエネルギー状態をゲームエンジンに保存
            self.game_engine.save_state()
            
        return energy_state

    # ==========================================
    # ④ 高度なシミュレーション・理論システム
    # ==========================================
    def show_theoretical_simulation_menu(self):
        """世界線・トレンド理論シミュレーション"""
        while True:
            print("\n" + "="*40)
            print("🔬 世界線・歴史トレンド 理論シミュレーション")
            print("="*40)
            print("1. 情報・社会プラットフォームの静的解析 (シャノンエントロピー・情報量)")
            print("2. トレンド・パンデミック伝播の動的シミュレーション (SIRモデル・歴史ダイナミクス)")
            print("0. 戻る")
            
            choice = input("\n選択してください (1-2/0): ").strip()
            
            if choice == "1":
                self._simulate_static_information()
            elif choice == "2":
                self._simulate_dynamic_trends()
            elif choice == "0":
                break
            else:
                print("❌ 無効な選択です。")

    def _simulate_static_information(self):
        import math
        print("\n=== 情報の静的解析（シャノンエントロピー） ===")
        print("社会を飛び交う情報やニュースの確率分布から、システム全体が持つ「不確実性(エントロピー)」を計算します。")
        
        try:
            print("3つの独立したトピック（例: 戦争・AI・暗号資産）の発生確率 p1, p2, p3 を入力してください（合計1.0）")
            p1 = float(input("📰 トピックAの確率 (例: 0.5): ") or "0.5")
            p2 = float(input("📰 トピックBの確率 (例: 0.3): ") or "0.3")
            p3 = float(input("📰 トピックCの確率 (例: 0.2): ") or "0.2")
        except ValueError:
            print("❌ 無効な入力です。")
            return
            
        total_p = p1 + p2 + p3
        if total_p <= 0.0:
            print("❌ 確率は正の値である必要があります。")
            return
            
        # 正規化
        p1, p2, p3 = p1/total_p, p2/total_p, p3/total_p
        
        # シャノンエントロピー H = -Σ p_i log2(p_i)
        entropy = 0.0
        for p in [p1, p2, p3]:
            if p > 0:
                entropy -= p * math.log2(p)
                
        # 最大エントロピー（全て等確率の場合）
        max_entropy = math.log2(3)
        complexity_ratio = (entropy / max_entropy) * 100

        print("\n" + "="*40)
        print("📊 静的情報解析の結果")
        print("="*40)
        print(f"📌 正規化された確率分布: [A:{p1:.2f}, B:{p2:.2f}, C:{p3:.2f}]")
        print(f"📌 [使用方程式]: シャノンエントロピー H = -Σ p_i * log2(p_i)")
        print(f"   => 現在の世界の情報エントロピー: {entropy:.3f} bit")
        print(f"   => 世界の複雑度 (最大値に対する割合): {complexity_ratio:.1f} %")
        print(f"   ※ 注: 1つのトピックに情報が偏るほどエントロピーは低く(わかりやすく)なり、分散しているほど高くなります。")
        print("========================================")
        
        memo = input("\n📝 メモ・研究ノート (空白でスキップ): ").strip()
        self._save_simulation_record("情報理論解析", {"entropy": entropy, "complexity": complexity_ratio}, memo)
        
        if self.game_engine and self.game_engine.use_action():
            self.game_engine.add_experience(15)
            print(f"\n🎁 【情報理論解析】により経験値を獲得しました: +15 EXP")

    def _simulate_dynamic_trends(self):
        print("\n=== トレンド伝播の動的シミュレーション (SIR / 歴史モデル) ===")
        print("疫学のSIRモデルを応用し、新しい情報・イノベーション・歴史的事件が社会にどう伝播・忘却されるかを計算します。")
        
        try:
            total_pop = int(input("🌍 世界の総人口・対象規模 [万人] (例: 10000): ") or "10000")
            beta = float(input("🗣️ 感染(伝播)率 β (例: 0.3): ") or "0.3")
            gamma = float(input("📉 回復(忘却)率 γ (例: 0.1): ") or "0.1")
            max_days = int(input("⏱️ シミュレーション期間 [日] (例: 60): ") or "60")
        except ValueError:
            print("❌ 無効な入力です。")
            return
            
        # 初期状態:
        # S (Susceptible) = 未認知の層
        # I (Infected) = トレンドに乗っている層
        # R (Recovered) = 飽きて忘れた/関心を失った層
        I = 1.0 # 最初は1万人(少数)からスタート
        R = 0.0
        S = total_pop - I - R
        N = float(total_pop)
        
        print("\n⏳ 伝播シミュレーション開始！")
        print("-" * 65)
        print(f"{'Day':>4} | {'未認知 (S)':>12} | {'トレンド中 (I)':>14} | {'忘却済 (R)':>12}")
        print("-" * 65)

        for day in range(0, max_days + 1, 5):
            
            if day > 0:
                # 5日分時間を進める (オイラー法)
                dt = 1.0
                for _ in range(5):
                    new_infections = beta * S * I / N
                    new_recoveries = gamma * I
                    
                    S -= new_infections
                    I += new_infections - new_recoveries
                    R += new_recoveries

            # Iの状態でマーク
            trend_mark = ""
            if I > N * 0.3:
                trend_mark = "🔥(大流行)"
            elif I > N * 0.1:
                trend_mark = "📈(流行中)"
                
            print(f"{day:>4} | {S:>12.1f} | {I:>10.1f} {trend_mark:<3} | {R:>12.1f}")

        print("-" * 65)
        print(f"📌 [使用方程式]: SIRモデル (dS/dt = -βSI/N, dI/dt = βSI/N - γI, dR/dt = γI)")
        print(f"   => 情報が爆発的に広まった後、徐々に忘れ去られていく歴史的ダイナミクスが観測されました。")
        print("========================================")
        
        memo = input("\n📝 メモ・研究ノート (空白でスキップ): ").strip()
        self._save_simulation_record("動的歴史シミュレーション", {"total_pop": total_pop, "beta": beta, "gamma": gamma}, memo)
        
        if self.game_engine and self.game_engine.use_action():
            self.game_engine.add_experience(25)
            print(f"\n🎁 【動的歴史シミュレーション】により経験値を獲得しました: +25 EXP")

    def _save_simulation_record(self, sim_type, params, memo):
        """ シミュレーション結果を保存 """
        import time as _time
        from datetime import datetime as _dt
        record = {
            "timestamp": _dt.now().isoformat(),
            "type": sim_type,
            "params": params,
            "memo": memo
        }
        record_file = self.history_file.parent / f"sim_{int(_time.time())}.json"
        try:
            import json as _json
            with open(record_file, 'w', encoding='utf-8') as f:
                _json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        if self.game_engine:
            if 'world_simulations' not in self.game_engine.wallet:
                self.game_engine.wallet['world_simulations'] = []
            self.game_engine.wallet['world_simulations'].append(record)
            self.game_engine.save_wallet()
