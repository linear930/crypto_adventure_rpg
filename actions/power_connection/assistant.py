import os
import uuid
import time
from pathlib import Path
from .device_registry import DeviceRegistry
from .power_grid import PowerGrid

class PowerConnectionAssistant:
    def __init__(self, config):
        self.config = config
        self.data_dir = Path("data/power_connection")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry = DeviceRegistry(self.data_dir)
        self.grid = PowerGrid(self.data_dir, self.registry)
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_status(self):
        print("\n" + "="*50)
        print("🤖 [電力管理アシスタント]")
        remaining = self.grid.get_remaining_power()
        consumption = self.grid.get_total_consumption()
        capacity = self.grid.capacity_w
        
        print(f"📊 現在の電力状況:")
        print(f"   最大発電量: {capacity} W")
        print(f"   消費電力  : {consumption} W")
        print(f"   残電力    : {remaining} W")
        print("="*50)
        
    def main_menu(self):
        self.clear_screen()
        print("🤖 「こんにちは！電力管理アシスタントです。2000Wの電源ネットワークへデバイスの接続をサポートしますね。」")
        
        while True:
            self.print_status()
            print("\n🤖 「どういたしましょうか？」")
            print("   1. 🔌 デバイスを接続する")
            print("   2. 🔌 デバイスを取り外す")
            print("   3. 📋 接続中のデバイスを確認する")
            print("   4. 🛠️ 新しい種類のデバイスを登録する")
            print("   5. 🔙 アシスタントを終了して戻る")
            
            choice = input("\n選択してください (1-5): ").strip()
            
            if choice == "1":
                self._menu_connect()
            elif choice == "2":
                self._menu_disconnect()
            elif choice == "3":
                self._menu_status()
            elif choice == "4":
                self._menu_register()
            elif choice == "5":
                print("\n🤖 「お疲れ様でした！またいつでも呼んでくださいね。」")
                time.sleep(1)
                break
            else:
                print("\n🤖 「すみません、よくわかりませんでした。1〜5の番号で教えてください。」")
                time.sleep(1)
                
    def _menu_connect(self):
        print("\n🤖 「どのデバイスを接続しますか？」")
        devices = self.registry.get_all_devices()
        
        device_keys = list(devices.keys())
        for i, key in enumerate(device_keys, 1):
            dev = devices[key]
            print(f"   {i}. {dev['name']} (消費電力: {dev['power_w']}W)")
        print(f"   0. やめる")
        
        choice = input("\n接続するデバイスの番号: ").strip()
        try:
            choice_idx = int(choice)
            if choice_idx == 0:
                print("🤖 「接続をやめますね。」")
                return
            if 1 <= choice_idx <= len(device_keys):
                selected_key = device_keys[choice_idx - 1]
                dev = devices[selected_key]
                if self.grid.get_remaining_power() >= dev['power_w']:
                    instance_id = str(uuid.uuid4())[:8]
                    self.grid.connect_device(instance_id, selected_key, dev['power_w'])
                    print(f"\n🤖 「{dev['name']} を接続しました！ (ID: {instance_id})」")
                else:
                    required_drop = dev['power_w'] - self.grid.get_remaining_power()
                    print(f"\n🤖 「ああっと！電力が足りません。あと {required_drop}W 減らさないと接続できません。」")
            else:
                print("🤖 「そのデバイスは見つかりませんでした。」")
        except ValueError:
            print("🤖 「番号を正しく入力してくださいね。」")
        time.sleep(1.5)
        
    def _menu_disconnect(self):
        connected = self.grid.connected_devices
        if not connected:
            print("\n🤖 「今は何も接続されていませんよ。」")
            time.sleep(1.5)
            return

        print("\n🤖 「取り外すデバイスを選んでください。」")
        for i, conn in enumerate(connected, 1):
            dev_info = self.registry.get_device(conn['device_id'])
            name = dev_info['name'] if dev_info else "不明なデバイス"
            print(f"   {i}. {name} (ID: {conn['instance_id']}, {conn['power_w']}W)")
        print(f"   0. やめる")
        
        choice = input("\n取り外すデバイスの番号: ").strip()
        try:
            choice_idx = int(choice)
            if choice_idx == 0:
                print("🤖 「取り外しをやめますね。」")
                return
            if 1 <= choice_idx <= len(connected):
                target = connected[choice_idx - 1]
                self.grid.disconnect_device(target['instance_id'])
                dev_info = self.registry.get_device(target['device_id'])
                name = dev_info['name'] if dev_info else "不明なデバイス"
                print(f"\n🤖 「{name} (ID: {target['instance_id']}) を取り外しました！」")
            else:
                print("🤖 「そのデバイスは見つかりませんでした。」")
        except ValueError:
            print("🤖 「番号を正しく入力してくださいね。」")
        time.sleep(1.5)
        
    def _menu_status(self):
        connected = self.grid.connected_devices
        print("\n🤖 「現在接続されているデバイスの一覧です。」")
        if not connected:
            print("   （何も接続されていません）")
        else:
            for conn in connected:
                dev_info = self.registry.get_device(conn['device_id'])
                name = dev_info['name'] if dev_info else "不明なデバイス"
                print(f"   - {name} [ID: {conn['instance_id']}] ({conn['power_w']}W)")
        input("\n[Enterキーで戻る]")
        
    def _menu_register(self):
        print("\n🤖 「新しい種類のデバイスですね！私に教えてください。」")
        device_id = input("デバイスの識別ID (半角英数, 例: tv_large): ").strip()
        if not device_id:
            print("🤖 「IDが入力されなかったのでキャンセルしますね。」")
            time.sleep(1)
            return
            
        if self.registry.get_device(device_id):
            print("🤖 「そのIDは既に登録されていますよ。」")
            time.sleep(1)
            return
            
        name = input("デバイスの表示名 (例: 大型テレビ): ").strip()
        power_w_str = input("消費電力(W) (例: 150): ").strip()
        
        try:
            power_w = int(power_w_str)
            if power_w <= 0:
                print("🤖 「消費電力は1以上にしてくださいね。」")
                time.sleep(1)
                return
                
            self.registry.register_device(device_id, name, power_w)
            print(f"\n🤖 「新しいデバイス『{name} ({power_w}W)』を覚えました！」")
            
        except ValueError:
            print("🤖 「消費電力は数字で入力してくださいね。」")
            
        time.sleep(1.5)
