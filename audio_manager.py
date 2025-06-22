#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声管理モジュール
pygameを使用した効果音とBGMの管理
"""

import pygame
import os
import random
import threading
import time
from pathlib import Path
from typing import Optional, List

class AudioManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.sounds_dir = data_dir / "sounds"
        
        # pygame初期化
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # 音量設定
        self.effect_volume = 0.7
        self.bgm_volume = 0.5
        
        # BGM関連
        self.current_bgm = None
        self.bgm_thread = None
        self.bgm_playing = False
        self.bgm_files = []
        
        # 効果音の読み込み
        self.sounds = {}
        self.load_sounds()
        
        # BGMファイルの検索
        self.find_bgm_files()
    
    def load_sounds(self):
        """効果音の読み込み"""
        sound_files = {
            'action_select': 'action_select.mp3',
            'next_day': 'next_day.mp3',
            'title_earned': 'title_earned.mp3',
            'error': 'error.mp3'
        }
        
        for sound_name, filename in sound_files.items():
            file_path = self.sounds_dir / filename
            if file_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    sound.set_volume(self.effect_volume)
                    self.sounds[sound_name] = sound
                    print(f"✅ 効果音読み込み成功: {filename}")
                except Exception as e:
                    print(f"❌ 効果音読み込み失敗: {filename} - {e}")
            else:
                print(f"⚠️ 効果音ファイルが見つかりません: {filename}")
    
    def find_bgm_files(self):
        """BGMファイルの検索"""
        if not self.sounds_dir.exists():
            print("⚠️ soundsディレクトリが存在しません")
            self.bgm_playing = False
            return
        
        # BGMファイルを検索
        for file in self.sounds_dir.glob("bgm_*.mp3"):
            self.bgm_files.append(file)
        
        # エンディングBGMも追加
        ending_bgm = self.sounds_dir / "ending_bgm.mp3"
        if ending_bgm.exists():
            self.bgm_files.append(ending_bgm)
        
        if self.bgm_files:
            print(f"✅ BGMファイル {len(self.bgm_files)}個 を発見")
        else:
            print("⚠️ BGMファイルが見つかりません")
            self.bgm_playing = False
    
    def play_effect(self, sound_name: str):
        """効果音の再生"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                print(f"🔊 効果音再生: {sound_name}")
            except Exception as e:
                print(f"❌ 効果音再生失敗: {sound_name} - {e}")
        else:
            print(f"⚠️ 効果音が見つかりません: {sound_name}")
    
    def play_bgm(self, bgm_file: Optional[Path] = None):
        """BGMの再生開始"""
        # 既存のBGMを停止
        if self.bgm_playing:
            self.stop_bgm()
        
        if bgm_file is None:
            if not self.bgm_files:
                print("⚠️ BGMファイルが見つかりません")
                return
            bgm_file = random.choice(self.bgm_files)
        
        if not bgm_file.exists():
            print(f"⚠️ BGMファイルが見つかりません: {bgm_file.name}")
            return
        
        try:
            # pygameの音楽を直接再生
            pygame.mixer.music.load(str(bgm_file))
            pygame.mixer.music.set_volume(self.bgm_volume)
            pygame.mixer.music.play(-1)  # -1でループ再生
            
            # 状態を更新
            self.bgm_playing = True
            self.current_bgm = bgm_file
            print(f"🎵 BGM再生開始: {bgm_file.name}")
        except Exception as e:
            print(f"❌ BGM再生失敗: {bgm_file.name} - {e}")
            self.bgm_playing = False
            self.current_bgm = None
    
    def stop_bgm(self):
        """BGMの停止"""
        try:
            pygame.mixer.music.stop()
            self.bgm_playing = False
            self.current_bgm = None
            print("🔇 BGM停止")
        except Exception as e:
            print(f"❌ BGM停止エラー: {e}")
            self.bgm_playing = False
            self.current_bgm = None
    
    def pause_bgm(self):
        """BGMの一時停止"""
        if self.bgm_playing and pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.pause()
                print("⏸️ BGM一時停止")
            except Exception as e:
                print(f"❌ BGM一時停止エラー: {e}")
        else:
            print("⚠️ BGMが再生されていません")
    
    def unpause_bgm(self):
        """BGMの再開"""
        if self.bgm_playing:
            try:
                pygame.mixer.music.unpause()
                print("▶️ BGM再開")
            except Exception as e:
                print(f"❌ BGM再開エラー: {e}")
        else:
            print("⚠️ BGMが再生されていません")
    
    def set_effect_volume(self, volume: float):
        """効果音の音量設定 (0.0 - 1.0)"""
        self.effect_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.effect_volume)
        print(f"🔊 効果音音量設定: {self.effect_volume:.1f}")
    
    def set_bgm_volume(self, volume: float):
        """BGMの音量設定 (0.0 - 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.bgm_volume)
            print(f"🎵 BGM音量設定: {self.bgm_volume:.1f}")
        except Exception as e:
            print(f"❌ BGM音量設定エラー: {e}")
    
    def play_ending_bgm(self):
        """エンディングBGMの再生"""
        # 既存のBGMを停止
        if self.bgm_playing:
            self.stop_bgm()
        
        ending_bgm = self.sounds_dir / "ending_bgm.mp3"
        if ending_bgm.exists():
            try:
                pygame.mixer.music.load(str(ending_bgm))
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(0)  # 1回だけ再生
                print("🎵 エンディングBGM再生開始")
            except Exception as e:
                print(f"❌ エンディングBGM再生失敗: {e}")
        else:
            print("⚠️ エンディングBGMファイルが見つかりません")
    
    def cleanup(self):
        """音声システムのクリーンアップ"""
        self.stop_bgm()
        pygame.mixer.quit()
        print("🔇 音声システム終了")
    
    def get_volume_info(self) -> dict:
        """音量情報の取得"""
        # pygameの実際の再生状態を確認
        actual_bgm_playing = pygame.mixer.music.get_busy() if self.bgm_playing else False
        
        return {
            'effect_volume': self.effect_volume,
            'bgm_volume': self.bgm_volume,
            'bgm_playing': actual_bgm_playing,
            'current_bgm': self.current_bgm.name if self.current_bgm else None,
            'available_bgm_count': len(self.bgm_files)
        }
    
    def change_bgm(self, bgm_file: Path):
        """BGMの変更"""
        if not bgm_file.exists():
            print(f"⚠️ BGMファイルが見つかりません: {bgm_file.name}")
            return False
        
        try:
            # 既存のBGMを停止
            if self.bgm_playing:
                pygame.mixer.music.stop()
            
            # 新しいBGMを再生
            pygame.mixer.music.load(str(bgm_file))
            pygame.mixer.music.set_volume(self.bgm_volume)
            pygame.mixer.music.play(-1)  # -1でループ再生
            
            # 状態を更新
            self.bgm_playing = True
            self.current_bgm = bgm_file
            print(f"🎵 BGM変更: {bgm_file.name}")
            return True
        except Exception as e:
            print(f"❌ BGM変更失敗: {bgm_file.name} - {e}")
            self.bgm_playing = False
            self.current_bgm = None
            return False 