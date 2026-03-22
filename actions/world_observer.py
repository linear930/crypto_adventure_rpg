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
            "war": ["war", "conflict", "military"],
            "ai": ["AI", "artificial intelligence", "OpenAI"],
            "economy": ["economy", "inflation", "market"]
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
                "economy": random.randint(1000, 2500)
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
            
            # トレンドの判定
            trend_state = "平坦"
            if cat_momentum > 30:
                trend_state = "急加速🚀"
            elif cat_momentum > 10:
                trend_state = "上昇軌道📈"
            elif cat_momentum < -30:
                trend_state = "急速減衰📉"
            elif cat_momentum < -10:
                trend_state = "下降軌道"
            elif abs(cat_momentum) < 5 and cat_energy > 150:
                trend_state = "高エネルギー振動⚡"

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
        
        print("📊 セクター別トレンド:")
        for category, data in self.energy_state['trends'].items():
            cat_name = {"war": "紛争・地政学", "ai": "人工知能・技術", "economy": "経済・市場"}.get(category, category)
            print(f"  [{cat_name}]")
            print(f"   活動量: {data['energy']} E")
            print(f"   勢い　: {momentum_sign if data['momentum'] >= 0 else ''}{data['momentum']} P")
            print(f"   状態　: {data['state']}")
            
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
            self.game_engine.state['world_energy'] = energy_state['total_energy']
            self.game_engine.state['world_momentum'] = energy_state['momentum']
            self.game_engine.save_state()
            
        return energy_state
