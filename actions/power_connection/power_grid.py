import json
from pathlib import Path
from typing import Dict, List

class PowerGrid:
    def __init__(self, data_dir: Path, registry):
        self.capacity_w = 2000
        self.registry = registry
        self.connections_file = data_dir / "connections.json"
        
        # 接続中デバイスのインスタンス管理 [{"instance_id": str, "device_id": str, "power_w": int}]
        self.connected_devices = self._load_connections()
        
    def _load_connections(self) -> List[Dict]:
        if self.connections_file.exists():
            try:
                with open(self.connections_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
        
    def _save_connections(self):
        try:
            with open(self.connections_file, 'w', encoding='utf-8') as f:
                json.dump(self.connected_devices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 接続状態の保存エラー: {e}")
            
    def get_total_consumption(self) -> int:
        return sum(d.get("power_w", 0) for d in self.connected_devices)
        
    def get_remaining_power(self) -> int:
        return self.capacity_w - self.get_total_consumption()
        
    def connect_device(self, instance_id: str, device_id: str, power_w: int) -> bool:
        if self.get_remaining_power() < power_w:
            return False
            
        self.connected_devices.append({
            "instance_id": instance_id,
            "device_id": device_id,
            "power_w": power_w
        })
        self._save_connections()
        return True
        
    def disconnect_device(self, instance_id: str) -> bool:
        initial_len = len(self.connected_devices)
        self.connected_devices = [d for d in self.connected_devices if d["instance_id"] != instance_id]
        if len(self.connected_devices) < initial_len:
            self._save_connections()
            return True
        return False
