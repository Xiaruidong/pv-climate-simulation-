"""
零维EBM模型核心计算模块
基于Mann et al. (2014)的能量平衡模型
"""

import numpy as np
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZeroDimensionEBM:
    """零维能量平衡模型"""

    def __init__(self):
        # 物理常数
        self.CE = 2.08e8  # 地球系统平均热容量 J℃⁻¹m⁻²
        self.S0 = 1361    # 太阳辐射常数 Wm⁻²
        self.Aref = 210.2 # 向外长波辐射拟合系数 Wm⁻²
        self.B = 2.15     # 向外长波辐射拟合系数 Wm⁻²℃⁻¹
        self.Cref = 315   # 参考二氧化碳浓度 ppm

        # 地表参数
        self.land_ratio = 0.29  # 陆地面积占比
        self.ocean_ratio = 0.71 # 海洋面积占比

    def calc_surface_albedo(self, albedo_land: float, albedo_ocean: float) -> float:
        """计算地表反照率"""
        return self.land_ratio * albedo_land + self.ocean_ratio * albedo_ocean

    def calc_planetary_albedo(self, surface_albedo: float) -> float:
        """计算行星反照率（基于Hyde et al. 1989）"""
        return 0.248 + 0.425 * surface_albedo

    def pv_induce_palbedo_change(self, albedo_land: float, ratio1: float,
                                 albedo_ocean: float, ratio2: float,
                                 albedo_pv: float) -> float:
        """光伏建设引起的行星反照率变化"""
        # 计算光伏部署后的地表反照率
        albedo_surface_pv = (
            self.land_ratio * albedo_land * (1 - ratio1) +
            albedo_pv * ratio1 +
            self.ocean_ratio * albedo_ocean * (1 - ratio2) +
            albedo_pv * ratio2
        )

        # 计算对应的行星反照率
        return self.calc_planetary_albedo(albedo_surface_pv)

    def pv_induce_CO2(self, ratio: float, albedo_pv: float,
                      efficiency: float = 0.23) -> float:
        """光伏发电引起的CO2浓度修正量"""
        # 光伏发电参数
        Is = 1050        # 单位面积年吸收太阳能 kWh m⁻² yr⁻¹
        PR = 0.8         # 系统表现效率
        Fs = 0.05        # 遮蔽系数
        EF = 0.91        # 火电CO2排放系数 kgCO2/kWh
        S = 5e14         # 地球面积 km²
        Mair = 5.15e18   # 地球大气总质量 kg

        # 计算单位面积光伏年发电量
        Epv = efficiency * Is * PR * (1 - Fs)  # kWh m⁻² yr⁻¹

        # 计算CO2减排量（转换为ppm）
        cpv = (0.5 * Epv * ratio * S * EF) / (Mair * 1e6)  # ppm

        return cpv

    def calcu_EBM_ts(self, TS0: float, palbedo: float, CO2_now: float,
                    nt: int, dt: float = 1.0, cpv: float = 0.0) -> np.ndarray:
        """计算地表温度演变

        Args:
            TS0: 初始地表温度 ℃
            palbedo: 行星反照率
            CO2_now: 当前CO2浓度 ppm
            nt: 积分时间步数
            dt: 时间步长（年）
            cpv: 光伏减排的CO2修正量 ppm

        Returns:
            温度时间序列
        """
        # 初始化温度数组
        ts = np.zeros(nt + 1)
        ts[0] = TS0

        # CO2温室效应修正
        co2_effect = 5.35 * np.log((CO2_now - cpv) / self.Cref)

        # 时间积分
        for i in range(nt):
            T = ts[i]

            # 计算能量收支
            solar_input = 0.25 * (1 - palbedo) * self.S0  # 太阳辐射收入
            thermal_output = self.Aref + self.B * T       # 长波辐射支出

            # 温度变化率
            dTdt = (solar_input - thermal_output + co2_effect) / self.CE * 31536000  # 转换为年尺度

            # 更新温度（欧拉前向差分）
            ts[i + 1] = T + dTdt * dt

        return ts

    def Equil_time(self, ts: np.ndarray, Rerror: float = 2e-5) -> int:
        """计算温度平衡时间"""
        for i in range(1, len(ts)):
            if abs(ts[i] - ts[i-1]) < Rerror:
                return i
        return len(ts) - 1

    def run_simulation(self, params: Dict) -> Dict:
        """运行完整模拟

        Args:
            params: 模拟参数字典

        Returns:
            模拟结果字典
        """
        try:
            # 提取参数
            albedo_land = params.get('albedo_land', 0.3)
            albedo_ocean = params.get('albedo_ocean', 0.15)
            albedo_pv = params.get('albedo_pv', 0.438)
            coverage_ratio = params.get('coverage_ratio', 0.01)
            co2_current = params.get('co2_current', 420)
            initial_temp = params.get('initial_temp', 8.0)
            simulation_years = params.get('simulation_years', 100)
            pv_efficiency = params.get('pv_efficiency', 0.23)

            # 计算反照率变化
            palbedo_base = self.calc_planetary_albedo(
                self.calc_surface_albedo(albedo_land, albedo_ocean)
            )
            palbedo_pv = self.pv_induce_palbedo_change(
                albedo_land, coverage_ratio, albedo_ocean, coverage_ratio, albedo_pv
            )

            # 计算CO2减排效应
            cpv = self.pv_induce_CO2(coverage_ratio, albedo_pv, pv_efficiency)

            # 运行基准实验
            ts_base = self.calcu_EBM_ts(initial_temp, palbedo_base, co2_current,
                                       simulation_years, cpv=0.0)
            equil_time_base = self.Equil_time(ts_base)
            equil_temp_base = ts_base[equil_time_base]

            # 运行光伏实验
            ts_pv = self.calcu_EBM_ts(initial_temp, palbedo_pv, co2_current,
                                     simulation_years, cpv=cpv)
            equil_time_pv = self.Equil_time(ts_pv)
            equil_temp_pv = ts_pv[equil_time_pv]

            # 计算差异
            temp_change = equil_temp_pv - equil_temp_base

            logger.info(f"模拟完成: 基准温度={equil_temp_base:.2f}°C, "
                       f"光伏温度={equil_temp_pv:.2f}°C, 变化={temp_change:.2f}°C")

            return {
                'success': True,
                'data': {
                    'baseline': {
                        'temperature_series': ts_base.tolist(),
                        'equilibrium_time': equil_time_base,
                        'equilibrium_temp': float(equil_temp_base),
                        'planetary_albedo': float(palbedo_base)
                    },
                    'pv_scenario': {
                        'temperature_series': ts_pv.tolist(),
                        'equilibrium_time': equil_time_pv,
                        'equilibrium_temp': float(equil_temp_pv),
                        'planetary_albedo': float(palbedo_pv),
                        'co2_reduction': float(cpv)
                    },
                    'comparison': {
                        'temperature_change': float(temp_change),
                        'albedo_change': float(palbedo_pv - palbedo_base),
                        'cooling_effect': temp_change < 0
                    }
                }
            }

        except Exception as e:
            logger.error(f"模拟失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# 创建全局实例
ebm_model = ZeroDimensionEBM()
