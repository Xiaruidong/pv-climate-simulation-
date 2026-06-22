/**
 * 真实物理计算API服务
 * 连接后端EBM模型计算服务
 */

const API_BASE_URL = 'http://localhost:8000'

// 获取物理常数
export async function getPhysicalConstants() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/constants`)
    if (!response.ok) throw new Error('获取物理常数失败')
    return await response.json()
  } catch (error) {
    console.error('获取物理常数错误:', error)
    return null
  }
}

// 获取真实场景配置
export async function getRealScenarios() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scenarios`)
    if (!response.ok) throw new Error('获取场景配置失败')
    return await response.json()
  } catch (error) {
    console.error('获取场景配置错误:', error)
    return null
  }
}

// 验证模拟参数
export async function validateSimulationParams(params) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
    if (!response.ok) throw new Error('参数验证失败')
    return await response.json()
  } catch (error) {
    console.error('参数验证错误:', error)
    return null
  }
}

// 运行真实模拟计算
export async function runRealSimulation(params) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/simulate/real`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '模拟计算失败')
    }
    return await response.json()
  } catch (error) {
    console.error('模拟计算错误:', error)
    throw error
  }
}

// 获取计算结果
export async function getSimulationResult(taskId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/simulate/real/${taskId}`)
    if (!response.ok) throw new Error('获取结果失败')
    return await response.json()
  } catch (error) {
    console.error('获取结果错误:', error)
    return null
  }
}

// 轮询任务状态
export async function pollTaskStatus(taskId, onUpdate, onComplete, onError) {
  const pollInterval = 1000 // 1秒
  const maxAttempts = 300 // 最多5分钟

  let attempts = 0

  const poll = async () => {
    attempts++

    try {
      const result = await getSimulationResult(taskId)

      if (!result) {
        if (onError) onError('获取结果失败')
        return
      }

      if (onUpdate) onUpdate(result)

      // 检查任务状态
      if (result.status === 'completed') {
        if (onComplete) onComplete(result.data)
        return
      } else if (result.status === 'failed') {
        if (onError) onError(result.error || '计算失败')
        return
      } else if (attempts >= maxAttempts) {
        if (onError) onError('计算超时')
        return
      } else {
        // 继续轮询
        setTimeout(poll, pollInterval)
      }
    } catch (error) {
      if (onError) onError(error.message)
    }
  }

  poll()
}

// 与文献数据对比
export async function compareWithLiterature() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/compare/with-literature`)
    if (!response.ok) throw new Error('获取文献数据失败')
    return await response.json()
  } catch (error) {
    console.error('获取文献数据错误:', error)
    return null
  }
}

// 快速计算（简化版，用于实时更新）
export function quickCalculate(params) {
  // 基于真实常数的简化计算
  const S0 = 1361.0 // 太阳常数 W/m²
  const albedo_land = params.albedo_land || 0.3
  const albedo_pv = params.albedo_pv || 0.438
  const coverage_ratio = params.coverage_ratio || 1e-8
  const co2_current = params.co2_current || 420.0
  const initial_temp = params.initial_temp || 15.0

  // 计算有效反照率
  const land_fraction = 0.29
  const ocean_fraction = 0.71
  const surface_albedo = land_fraction * albedo_land + ocean_fraction * 0.06
  const base_planetary_albedo = 0.248 + 0.425 * surface_albedo

  // 光伏部署后的反照率
  const new_surface_albedo = surface_albedo + (albedo_pv - albedo_land) * coverage_ratio * land_fraction
  const pv_planetary_albedo = 0.248 + 0.425 * new_surface_albedo

  // CO2减排效应（简化）
  const irradiance = 1050 // kWh/m²/year
  const pv_efficiency = params.pv_efficiency || 0.23
  const grid_emission_factor = 520 // gCO2/kWh

  const annual_generation = irradiance * pv_efficiency * 0.8 * 0.8 * 0.96 // kWh/m²/year
  const land_area_m2 = 1.47921e14 * 1e6 // km² -> m²
  const total_pv_area = land_area_m2 * coverage_ratio
  const total_generation = annual_generation * total_pv_area
  const co2_reduction_kg = total_generation * grid_emission_factor * 0.5 / 1000
  const co2_reduction_ppm = co2_reduction_kg / 2.13e12

  // 限制CO2减排量，防止负数或异常值
  const safe_co2_reduction = Math.max(0, Math.min(co2_reduction_ppm, co2_current - 280))

  // 温度效应（简化平衡温度计算）
  const AREF = 210.2
  const B = 2.15

  // 基准温度 - 使用简化的能量平衡模型
  const base_flux_in = 0.25 * (1 - base_planetary_albedo) * S0
  const co2_forcing = 5.35 * Math.log(co2_current / 280.0)
  const base_temp = (base_flux_in + co2_forcing - AREF) / B

  // 光伏情景温度
  const pv_flux_in = 0.25 * (1 - pv_planetary_albedo) * S0
  const pv_co2_forcing = 5.35 * Math.log(Math.max(co2_current - safe_co2_reduction, 280) / 280.0)
  const pv_temp = (pv_flux_in + pv_co2_forcing - AREF) / B

  const temp_change = pv_temp - base_temp

  return {
    success: true,
    data: {
      baseline: {
        equilibrium_temp: base_temp,
        planetary_albedo: base_planetary_albedo
      },
      pv_scenario: {
        equilibrium_temp: pv_temp,
        planetary_albedo: pv_planetary_albedo,
        co2_reduction: co2_reduction_ppm
      },
      comparison: {
        temperature_change: temp_change,
        albedo_change: pv_planetary_albedo - base_planetary_albedo,
        cooling_effect: temp_change < 0,
        heat_island_effect: temp_change * 1.1,
        cooling_efficiency: Math.abs(temp_change) * 10
      }
    }
  }
}

// 默认参数
export const defaultParams = {
  latitude: 38.5,
  longitude: 105.0,
  albedo_pv: 0.438,
  coverage_ratio: 1e-8,        // 0.000001% - 现实的全球光伏覆盖率
  pv_efficiency: 0.23,
  albedo_land: 0.3,
  albedo_ocean: 0.06,
  co2_current: 420.0,
  initial_temp: 15.0,
  simulation_years: 100,
  time_step: 1.0
}

// 场景预设
export const scenarioPresets = {
  northwest_china: {
    name: '中国西北地区',
    description: '西北沙漠地区，太阳能资源丰富',
    params: {
      ...defaultParams,
      latitude: 38.5,
      longitude: 105.0,
      albedo_pv: 0.438,
      coverage_ratio: 1e-8,    // 0.000001% - 现实的覆盖率
      albedo_land: 0.35,
      initial_temp: 15.0
    }
  },
  qinghai_tibet: {
    name: '青藏高原地区',
    description: '高海拔地区，辐射强度大',
    params: {
      ...defaultParams,
      latitude: 32.5,
      longitude: 95.0,
      albedo_pv: 0.28,
      coverage_ratio: 5e-9,    // 0.0000005% - 适中的覆盖率
      pv_efficiency: 0.24,
      albedo_land: 0.28,
      initial_temp: 12.0
    }
  },
  coastal_area: {
    name: '沿海发达地区',
    description: '东部沿海，经济发达',
    params: {
      ...defaultParams,
      latitude: 31.0,
      longitude: 121.0,
      albedo_pv: 0.25,
      coverage_ratio: 1e-8,    // 0.000001% - 适中的覆盖率
      pv_efficiency: 0.22,
      albedo_land: 0.20,
      initial_temp: 18.0
    }
  }
}
