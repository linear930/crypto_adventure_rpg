import json
import time
import math
from datetime import datetime
from pathlib import Path

class RocketResearchSystem:
    """
    ロケット研究および軌道力学の学習システム
    静的な理論計算（ツィオルコフスキーの式等）と
    時間発展を伴う動的シミュレーションの両方を扱う。
    """
    
    # 物理定数
    G = 6.67430e-11      # 万有引力定数 (m^3/kg/s^2)
    M_EARTH = 5.972e24   # 地球質量 (kg)
    R_EARTH = 6371000    # 地球半径 (m)
    g0 = 9.80665         # 標準重力加速度 (m/s^2)
    
    def __init__(self, config):
        self.config = config
        self.history_file = Path("data/activity_logs/rocket_research.json")
        self.game_engine = None
        self._load_history()

    def set_game_engine(self, engine):
        self.game_engine = engine

    def _load_history(self):
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({"experiments": []}, f, ensure_ascii=False, indent=2)
            self.history = []
        else:
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f).get("experiments", [])
            except:
                self.history = []

    def _save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({"experiments": self.history}, f, ensure_ascii=False, indent=2)

    # ==========================================
    # ① 静的モデル（理論計算）
    # ==========================================
    def calculate_static_orbit(self):
        print("\n=== ロケット静的性能・軌道計算 ===")
        print("ロケットの重量や推進剤から、到達可能な理論上の速度増分(ΔV)や軌道速度を計算します。")
        
        try:
            dry_mass = float(input("🚀 機体乾燥質量(ペイロード含む) [kg]: "))
            prop_mass = float(input("⛽ 推進剤質量 [kg]: "))
            isp = float(input("🔥 エンジン比推力(Isp) [s]: "))
            target_alt = float(input("🌍 目標軌道高度 [km]: ")) * 1000
        except ValueError:
            print("❌ 無効な入力です。処理を中断します。")
            return
            
        m0 = dry_mass + prop_mass
        mf = dry_mass
        
        # ツィオルコフスキーのロケット方程式 (ΔV)
        delta_v = isp * self.g0 * math.log(m0 / mf)
        
        # 第一宇宙速度 (軌道速度)
        r = self.R_EARTH + target_alt
        v_orbit = math.sqrt((self.G * self.M_EARTH) / r)
        
        # ホーマン遷移軌道の速度増分 (LEO 200km から target_alt への遷移を仮定)
        r_leo = self.R_EARTH + 200000
        if r > r_leo:
            dv_hohmann = math.sqrt(self.G * self.M_EARTH / r_leo) * (math.sqrt((2 * r) / (r_leo + r)) - 1)
        else:
            dv_hohmann = 0.0

        print("\n" + "="*40)
        print("📊 静的シミュレーション解析結果")
        print("="*40)
        print(f"📌 [使用方程式]: ツィオルコフスキーのロケット方程式 (ΔV = Isp * g0 * ln(m0/mf))")
        print(f"   => 獲得可能 ΔV   : {delta_v:,.1f} m/s")
        print(f"📌 [使用方程式]: 第一宇宙速度・軌道速度 (v = √(GM/r))")
        print(f"   => 目標軌道速度  : {v_orbit:,.1f} m/s (高度 {target_alt/1000:,.1f} km)")
        if r > r_leo:
            print(f"📌 [使用方程式]: ホーマン遷移軌道の速度増分 (Δv1 = √(GM/r1) * (√(2r2/(r1+r2)) - 1))")
            print(f"   => 200kmからの遷移ΔV: {dv_hohmann:,.1f} m/s")
        
        print("\n💡 軌道投入評価:")
        if delta_v >= v_orbit + dv_hohmann + 1500: # 空気抵抗・重力ロスとして適当に1500をブレンド
            print("🟢 軌道到達は理論上【可能】です！十分なΔVがあります。")
            success = True
        else:
            print("🔴 軌道到達にはΔVが【不足】しています。機体軽量化か推力向上が必要です。")
            success = False

        # 記録の保存
        record = {
            "date": datetime.now().isoformat(),
            "type": "static_calculation",
            "m0": m0, "mf": mf, "isp": isp, "target_alt": target_alt,
            "results": {
                "delta_v": delta_v, "v_orbit": v_orbit, "dv_hohmann": dv_hohmann, "success": success
            }
        }
        self.history.append(record)
        self._save_history()

        self._grant_rewards(success, "静的軌道計算")

    # ==========================================
    # ② 動的モデル（時間積分シミュレーション）
    # ==========================================
    def get_atmospheric_density(self, altitude):
        """簡易的な大気密度モデル (指数関数的減衰)"""
        # 海面基準 1.225 kg/m^3, スケールハイト 約8500m
        if altitude > 100000: # カーマンライン以上はほぼ0
            return 0.0
        return 1.225 * math.exp(-altitude / 8500.0)

    def simulate_launch_dynamic(self):
        print("\n=== ロケット動的打ち上げシミュレーション ===")
        print("ニュートンの運動方程式と空気抵抗を用いて、時間軸に沿ったロケットの打ち上げをシミュレートします。")
        
        try:
            m_empty = float(input("🚀 機体乾燥質量(ペイロード含む) [kg]: "))
            m_prop = float(input("⛽ 推進剤質量 [kg]: "))
            thrust = float(input("💨 エンジン総推力 [N] (例: 1000000): "))
            isp = float(input("🔥 エンジン比推力(Isp) [s]: "))
            burn_time_input = float(input("⏱️ 予定燃焼時間 [s]: "))
            print("※シミュレーションは真上(鉛直方向)への打ち上げを想定しています。")
        except ValueError:
            print("❌ 無効な入力です。")
            return

        # 初期条件
        m = m_empty + m_prop
        alt = 0.0          # 高度(m)
        v = 0.0            # 速度(m/s)
        t = 0.0            # 時間(s)
        dt = 0.1           # 時間刻み幅(s)
        
        Cd = 0.5           # 抗力係数
        A = 10.0           # 前面投影面積(m^2) 適当なロケットサイズ
        
        # 推進剤消費率 (dm/dt = -F / (Isp * g0))
        mass_flow_rate = thrust / (isp * self.g0)
        
        print("\n🚀 打ち上げ開始！ (10秒ごとの推移を表示)")
        print("-" * 60)
        print(f"{'Time(s)':>8} | {'Alt(km)':>10} | {'Vel(m/s)':>10} | {'Mass(kg)':>10} | {'Status':>10}")
        print("-" * 60)

        max_alt = 0.0
        max_v = 0.0
        is_apogee = False

        # シミュレーションループ (最高到達点まで、または墜落まで)
        while alt >= 0 and t < 1000: # 最大1000秒でストップ
            # 1. 大気密度と空気抵抗
            rho = self.get_atmospheric_density(alt)
            # 空気抵抗 F_drag = 1/2 * rho * v^2 * Cd * A
            f_drag = 0.5 * rho * (v**2) * Cd * A * (1 if v > 0 else -1) # 速度の逆向き
            
            # 2. 重力
            r = self.R_EARTH + alt
            gravity = self.G * self.M_EARTH / (r**2)
            f_gravity = m * gravity
            
            # 3. 推力と質量の更新
            current_thrust = 0.0
            if t <= burn_time_input and m > m_empty:
                current_thrust = thrust
                m -= mass_flow_rate * dt
                if m < m_empty:
                    m = m_empty
            else:
                current_thrust = 0.0
                
            # 4. ニュートンの運動方程式 (加速度 a = F_net / m)
            f_net = current_thrust - f_gravity - f_drag
            a = f_net / m
            
            # 5. 速度と位置の更新 (オイラー法)
            v += a * dt
            alt += v * dt
            t += dt
            
            # 記録用
            if alt > max_alt:
                max_alt = alt
            if v > max_v:
                max_v = v
            
            # 頂点到達判定
            if v < 0 and not is_apogee and alt > 100:
                is_apogee = True
                print(f"{t:>8.1f} | {alt/1000:>10.2f} | {v:>10.1f} | {m:>10.1f} | 🔴 最高到達点(Apogee)!")
                
            # 10秒ごとにログ出力
            if math.isclose(t % 10.0, 0, abs_tol=dt/2):
                status = "🔥 燃焼中" if current_thrust > 0 else ("🌍 落下中" if v < 0 else "☁️ 慣性飛行")
                print(f"{t:>8.1f} | {alt/1000:>10.2f} | {v:>10.1f} | {m:>10.1f} | {status}")

        print("-" * 60)
        print("🛬 シミュレーション終了")
        
        print("\n" + "="*40)
        print("📊 動的シミュレーション解析結果")
        print("="*40)
        print(f"📌 [使用方程式]: ニュートンの運動方程式 (d^2r/dt^2 = -GM/r^3 + F_thrust/m + F_drag/m)")
        print(f"📌 [使用方程式]: 大気抵抗方程式 (F_drag = 1/2 * ρ * v^2 * Cd * A)")
        print(f"📌 [使用方程式]: 推力・質量変化方程式 (dm/dt = -F / (Isp * g0))")
        print(f"   => 最高高度 : {max_alt/1000:,.1f} km")
        print(f"   => 最大速度 : {max_v:,.1f} m/s")
        
        success = max_alt > 100000 # カーマンライン越えを成功とする
        if success:
            print("\n🟢 宇宙空間(高度100km以上)に到達しました！")
        else:
            print("\n🔴 宇宙空間には到達できませんでした。")

        # 記録の保存
        record = {
            "date": datetime.now().isoformat(),
            "type": "dynamic_simulation",
            "thrust": thrust, "isp": isp, "m_prop": m_prop,
            "results": {
                "max_altitude_km": max_alt/1000, "max_velocity": max_v, "success": success
            }
        }
        self.history.append(record)
        self._save_history()
        
        self._grant_rewards(success, "動的打ち上げシミュレーション")

    # ==========================================
    # 報酬・ゲームエンジン連動
    # ==========================================
    def _grant_rewards(self, success, exp_type):
        if self.game_engine:
            if not self.game_engine.use_action():
                print("⚠️ 行動回数が残っていませんが、研究室での解析は完了しました。")
                return

            exp = 50 if success else 20
            print(f"\n🎁 【{exp_type}】により経験値を獲得しました: +{exp} EXP")
            self.game_engine.add_experience(exp)

    # ==========================================
    # UI メニュー
    # ==========================================
    def main_menu(self):
        while True:
            print("\n" + "="*40)
            print("🚀 ロケット研究制御センター")
            print("="*40)
            print("1. 静的性能・軌道計算 (ツィオルコフスキーの式等)")
            print("2. 動的打ち上げシミュレーション (ニュートンの運動方程式等)")
            print("3. 研究履歴の確認")
            print("0. 戻る")
            
            choice = input("\n実行するコマンドを選択してください: ")
            
            if choice == '1':
                self.calculate_static_orbit()
            elif choice == '2':
                self.simulate_launch_dynamic()
            elif choice == '3':
                self._show_history()
            elif choice == '0':
                break
            else:
                print("❌ 無効な選択です。")

    def _show_history(self):
        if not self.history:
            print("\n📚 研究履歴がありません。")
            return
            
        print("\n=== ロケット研究履歴 (直近5件) ===")
        for i, rec in enumerate(reversed(self.history[-5:])):
            date_str = rec.get("date", "")[:19].replace("T", " ")
            rtype = rec.get("type", "unknown")
            print(f"[{i+1}] {date_str} - {rtype}")
            if rtype == "static_calculation":
                res = rec.get("results", {})
                print(f"    ΔV: {res.get('delta_v', 0):.1f} m/s, 軌道速度: {res.get('v_orbit', 0):.1f} m/s")
            elif rtype == "dynamic_simulation":
                res = rec.get("results", {})
                print(f"    最高高度: {res.get('max_altitude_km', 0):.1f} km, 最大速度: {res.get('max_velocity', 0):.1f} m/s")
