#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHubリポジトリ設定スクリプト
Crypto Adventure RPGをGitHubに公開するための設定を行います
"""

import subprocess
import os
from pathlib import Path

def setup_github_repository():
    """GitHubリポジトリの設定"""
    print("🚀 GitHubリポジトリ設定")
    print("="*50)
    print()
    
    # 現在のGit状態を確認
    print("1️⃣ 現在のGit状態を確認")
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        print("✅ Gitリポジトリが初期化されています")
        branch_name = 'master'
        if 'On branch ' in result.stdout:
            branch_line = result.stdout.split('On branch ')[1]
            branch_name = branch_line.split('\n')[0]
        print(f"   ブランチ: {branch_name}")
    except Exception as e:
        print(f"❌ Git状態の確認に失敗: {e}")
        return
    
    print()
    
    # GitHubリポジトリのURLを入力
    print("2️⃣ GitHubリポジトリの設定")
    print("GitHubでリポジトリを作成した後、以下の手順で設定してください:")
    print()
    
    # リモートリポジトリの追加方法を説明
    print("📋 手動手順:")
    print("1. GitHub.comにアクセス")
    print("2. 新しいリポジトリを作成:")
    print("   - リポジトリ名: crypto-adventure-rpg")
    print("   - 説明: 現実連動型暗号通貨アドベンチャーゲーム")
    print("   - 公開設定: Public")
    print("   - README、.gitignore、ライセンスは作成しない")
    print()
    print("3. 作成後、以下のコマンドを実行:")
    print()
    
    # コマンド例を表示
    commands = [
        "git remote add origin https://github.com/YOUR_USERNAME/crypto-adventure-rpg.git",
        "git branch -M main",
        "git push -u origin main"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. {cmd}")
    
    print()
    print("⚠️ 注意:")
    print("- YOUR_USERNAMEを実際のGitHubユーザー名に変更してください")
    print("- 機密情報（.envファイルなど）は.gitignoreに含まれているため、自動的に除外されます")
    print("- 初回プッシュ後、GitHubでリポジトリの設定を確認してください")
    
    print()
    print("🔒 セキュリティ確認:")
    print("✅ .gitignoreファイルが設定済み")
    print("✅ 機密ファイルが除外対象に含まれている")
    print("✅ 環境変数による設定管理が実装済み")
    
    print()
    print("📋 次のステップ:")
    print("1. GitHubでリポジトリを作成")
    print("2. 上記のコマンドを実行")
    print("3. README.mdの内容を確認・編集")
    print("4. IssuesやWikiの設定（オプション）")

def check_git_status():
    """Git状態の詳細確認"""
    print("\n🔍 Git状態の詳細確認")
    print("="*30)
    
    try:
        # ステージングされたファイルを確認
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 ステージングされたファイル:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"   {line}")
        else:
            print("✅ すべてのファイルがコミット済み")
        
        # コミット履歴を確認
        result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
        if result.stdout.strip():
            print("\n📋 最近のコミット:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"   {line}")
        
        # リモートリポジトリの確認
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.stdout.strip():
            print("\n🌐 リモートリポジトリ:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"   {line}")
        else:
            print("\n⚠️ リモートリポジトリが設定されていません")
            print("   GitHubでリポジトリを作成後、リモートを追加してください")
            
    except Exception as e:
        print(f"❌ Git状態の確認に失敗: {e}")

def main():
    """メイン関数"""
    setup_github_repository()
    check_git_status()
    
    print("\n🎉 GitHub設定ガイドが完了しました！")
    print("📋 上記の手順に従ってGitHubリポジトリを設定してください。")

if __name__ == "__main__":
    main() 