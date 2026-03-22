import json
from pathlib import Path
from typing import Dict, Optional

class DeviceRegistry:
    def __init__(self, data_dir: Path):
        self.devices_file = data_dir / "devices.json"
        self.devices = self._load_devices()
        
    def _load_devices(self) -> Dict[str, Dict]:
        if self.devices_file.exists():
            try:
                with open(self.devices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ デバイス定義ファイルの読み込みエラー: {e}")
        return self._get_default_devices()
        
    def _get_default_devices(self) -> Dict[str, Dict]:
        defaults = {
            "pc": {"name": "PC", "power_w": 50},
            "fridge": {"name": "冷蔵庫", "power_w": 300},
            "light": {"name": "照明", "power_w": 30},
            "miner": {"name": "マイニングリグ", "power_w": 1000}
        }
        self.devices = defaults
        self._save_devices()
        return defaults
        
    def _save_devices(self):
        try:
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ デバイス定義ファイルの保存エラー: {e}")
            
    def get_all_devices(self) -> Dict[str, Dict]:
        return self.devices
        
    def get_device(self, device_id: str) -> Optional[Dict]:
        return self.devices.get(device_id)
        
    def register_device(self, device_id: str, name: str, power_w: int) -> bool:
        if device_id in self.devices:
            return False
        self.devices[device_id] = {"name": name, "power_w": power_w}
        self._save_devices()
        return True
