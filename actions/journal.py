#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雑記記録モジュール
テキストベースの自由な雑記を記録・閲覧・保存するシステム
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class JournalSystem:
    """テキスト雑記記録システム"""

    def __init__(self, config: Dict):
        self.config = config
        self.journal_dir = Path("data/journal")
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.journal_dir / "journal_entries.json"
        self.entries: List[Dict] = []
        self._load_entries()
        self.game_engine = None

    def set_game_engine(self, engine):
        self.game_engine = engine

    # ------ 永続化 ------
    def _load_entries(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f).get("entries", [])
            except Exception:
                self.entries = []
        else:
            self.entries = []

    def _save_entries(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({"entries": self.entries}, f, ensure_ascii=False, indent=2)

    # ------ メインメニュー ------
    def main_menu(self):
        while True:
            print("\n" + "=" * 40)
            print("📝 雑記記録システム")
            print("=" * 40)
            print("1. ✏️  新しい雑記を書く")
            print("2. 📚 雑記一覧を見る")
            print("3. 🔍 雑記を検索する")
            print("0. 🔙 戻る")

            choice = input("\n選択してください (0-3): ").strip()

            if choice == "1":
                self.write_entry()
            elif choice == "2":
                self.list_entries()
            elif choice == "3":
                self.search_entries()
            elif choice == "0":
                break
            else:
                print("❌ 無効な選択です。")

    # ------ エントリ記録 ------
    def write_entry(self):
        print("\n--- ✏️ 新しい雑記を作成 ---")
        print("💡 「abort」と入力すると記録を中断します")

        title = input("📌 タイトル: ").strip()
        if title.lower() == "abort":
            print("❌ 記録を中断しました")
            return

        # タグ (カンマ区切り)
        tags_input = input("🏷️  タグ (カンマ区切り / 空欄OK): ").strip()
        if tags_input.lower() == "abort":
            print("❌ 記録を中断しました")
            return
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

        print("📝 本文を入力してください（空行を2回連続で入力すると終了）:")
        lines = []
        blank_count = 0
        while True:
            line = input()
            if line.lower() == "abort":
                print("❌ 記録を中断しました")
                return
            if line == "":
                blank_count += 1
                if blank_count >= 2:
                    break
                lines.append("")
            else:
                blank_count = 0
                lines.append(line)

        body = "\n".join(lines).rstrip("\n")

        if not body:
            print("⚠️ 本文が空のため記録しませんでした。")
            return

        entry = {
            "id": int(time.time() * 1000),
            "timestamp": datetime.now().isoformat(),
            "title": title or "(無題)",
            "tags": tags,
            "body": body,
        }

        self.entries.append(entry)
        self._save_entries()

        # GameEngine のウォレットにも保存
        if self.game_engine:
            if "journal_entries" not in self.game_engine.wallet:
                self.game_engine.wallet["journal_entries"] = []
            self.game_engine.wallet["journal_entries"].append(entry)
            self.game_engine.save_wallet()

        print(f"\n✅ 雑記を保存しました！")
        print(f"   📌 タイトル: {entry['title']}")
        print(f"   🏷️  タグ: {', '.join(tags) if tags else 'なし'}")
        print(f"   📄 本文: {len(body)} 文字")

        # 報酬
        if self.game_engine:
            if self.game_engine.use_action():
                exp = 10
                self.game_engine.add_experience(exp)
                print(f"   🎁 経験値を獲得しました: +{exp} EXP")

    # ------ 一覧表示 ------
    def list_entries(self):
        if not self.entries:
            print("\n📚 雑記はまだありません。")
            return

        print(f"\n📚 雑記一覧 (全{len(self.entries)}件)")
        print("=" * 50)

        # 直近10件を新しい順に表示
        recent = list(reversed(self.entries[-10:]))
        for i, e in enumerate(recent, 1):
            date_str = e["timestamp"][:16].replace("T", " ")
            tags_str = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
            print(f"  {i}. 📌 {e['title']}{tags_str}  — {date_str}")

        # 詳細を見る
        print("\n番号を入力すると詳細を表示します (0で戻る):")
        try:
            num = int(input("番号: ").strip())
            if 1 <= num <= len(recent):
                self._show_entry_detail(recent[num - 1])
        except (ValueError, IndexError):
            pass

    def _show_entry_detail(self, entry: Dict):
        print("\n" + "-" * 50)
        print(f"📌 {entry['title']}")
        date_str = entry["timestamp"][:19].replace("T", " ")
        print(f"📅 {date_str}")
        if entry.get("tags"):
            print(f"🏷️  {', '.join(entry['tags'])}")
        print("-" * 50)
        print(entry["body"])
        print("-" * 50)

    # ------ 検索 ------
    def search_entries(self):
        keyword = input("\n🔍 検索キーワード: ").strip()
        if not keyword:
            return

        results = [
            e for e in self.entries
            if keyword.lower() in e["title"].lower()
            or keyword.lower() in e["body"].lower()
            or any(keyword.lower() in t.lower() for t in e.get("tags", []))
        ]

        if not results:
            print(f"📝 「{keyword}」に一致する雑記はありません。")
            return

        print(f"\n🔍 「{keyword}」の検索結果: {len(results)}件")
        for i, e in enumerate(results[-10:], 1):
            date_str = e["timestamp"][:16].replace("T", " ")
            print(f"  {i}. 📌 {e['title']}  — {date_str}")

        print("\n番号を入力すると詳細を表示します (0で戻る):")
        try:
            num = int(input("番号: ").strip())
            display = results[-10:]
            if 1 <= num <= len(display):
                self._show_entry_detail(display[num - 1])
        except (ValueError, IndexError):
            pass
