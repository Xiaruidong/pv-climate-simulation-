/**
 * 测试数据生成器
 * 为光伏热效应模拟器生成多组测试数据
 */

// 基础物理常数
const PHYSICAL_CONSTANTS = {
  SOLAR_CONSTANT: 1361.0,           // 太阳常数 W/m²
  LAND_FRACTION: 0.29,              // 陆地面积占比
  OCEAN_FRACTION: 0.71,             // 海洋面积占比
  BASE_LAND_ALBEDO: 0.3,            // 基准陆地反照率
  BASE_OCEAN_ALBEDO: 0.06,          // 基准海洋反照率
  PRE_INDUSTRIAL_CO2: 280.0,        // 前工业化CO2浓度 ppm
  GRID_EMISSION_FACTOR: 520         // 电网排放因子 gCO2/kWh
}

// 光伏面板类型
const PV_PANEL_TYPES = {
  traditional: {
    name: '传统光伏面板',
    albedo: 0.307,
    efficiency: 0.23,
    description: '标准反照率，中等效率'
  },
  new: {
    name: '新型选择性面板',
    albedo: 0.438,
    efficiency: 0.23,
    description: '高反照率，高效率'
  },
  mirror: {
    name: '镜面反射型面板',
    albedo: 0.95,
    efficiency: 0.23,
    description: '超高反照率，降温效果最强'
  },
  perovskite: {
    name: '钙钛矿面板',
    albedo: 0.35,
    efficiency: 0.25,
    description: '高效率新材料'
  },
  bifacial: {
    name: '双面发电面板',
    albedo: 0.28,
    efficiency: 0.24,
    description: '双面吸光，效率提升'
  }
}

// 地区特征数据
const REGION_DATA = {
  northwest_china: {
    name: '中国西北地区',
    latitude: 38.5,
    longitude: 105.0,
    land_albedo: 0.35,
    base_temp: 15.0,
    irradiance: 1650,
    description: '沙漠地区，太阳能资源丰富'
  },
  qinghai_tibet: {
    name: '青藏高原地区',
    latitude: 32.5,
    longitude: 95.0,
    land_albedo: 0.28,
    base_temp: 12.0,
    irradiance: 2130,
    description: '高海拔地区，辐射强度大'
  },
  coastal_area: {
    name: '沿海发达地区',
    latitude: 31.0,
    longitude: 121.0,
    land_albedo: 0.20,
    base_temp: 18.0,
    irradiance: 1260,
    description: '东部沿海，经济发达'
  },
  northeast_china: {
    name: '东北地区',
    latitude: 45.0,
    longitude: 126.0,
    land_albedo: 0.25,
    base_temp: 8.0,
    irradiance: 1270,
    description: '寒冷地区，冬季辐射强'
  },
  southwest_china: {
    name: '西南地区',
    latitude: 25.0,
    longitude: 102.0,
    land_albedo: 0.22,
    base_temp: 16.0,
    irradiance: 1100,
    description: '山区地形，辐射中等'
  }
}

// 计算函数（简化版）
function calculatePVEffect(params) {
  const { albedo_pv, coverage_ratio, pv_efficiency, albedo_land, co2_current, irradiance } = params

  // 计算反照率变化
  const surface_albedo = PHYSICAL_CONSTANTS.LAND_FRACTION * albedo_land +
                         PHYSICAL_CONSTANTS.OCEAN_FRACTION * PHYSICAL_CONSTANTS.BASE_OCEAN_ALBEDO
  const base_planetary_albedo = 0.248 + 0.425 * surface_albedo

  const new_surface_albedo = surface_albedo + (albedo_pv - albedo_land) * coverage_ratio * PHYSICAL_CONSTANTS.LAND_FRACTION
  const pv_planetary_albedo = 0.248 + 0.425 * new_surface_albedo

  // 计算CO2减排
  const effective_irradiance = irradiance || 1420
  const annual_generation = effective_irradiance * pv_efficiency * 0.8 * 0.8 * 0.96 // kWh/m²/year
  const land_area_m2 = 1.47921e14 * 1e6 // km² -> m²
  const total_pv_area = land_area_m2 * coverage_ratio
  const total_generation = annual_generation * total_pv_area
  const co2_reduction_kg = total_generation * PHYSICAL_CONSTANTS.GRID_EMISSION_FACTOR * 0.5 / 1000
  const co2_reduction_ppm = Math.max(0, co2_reduction_kg / 2.13e12)

  // 安全限制
  const safe_co2_reduction = Math.max(0, Math.min(co2_reduction_ppm, co2_current - PHYSICAL_CONSTANTS.PRE_INDUSTRIAL_CO2))

  // 计算温度效应
  const AREF = 210.2
  const B = 2.15
  const S0 = PHYSICAL_CONSTANTS.SOLAR_CONSTANT

  const base_flux_in = 0.25 * (1 - base_planetary_albedo) * S0
  const co2_forcing = 5.35 * Math.log(co2_current / PHYSICAL_CONSTANTS.PRE_INDUSTRIAL_CO2)
  const base_temp = (base_flux_in + co2_forcing - AREF) / B

  const pv_flux_in = 0.25 * (1 - pv_planetary_albedo) * S0
  const pv_co2_forcing = 5.35 * Math.log(Math.max(co2_current - safe_co2_reduction, PHYSICAL_CONSTANTS.PRE_INDUSTRIAL_CO2) / PHYSICAL_CONSTANTS.PRE_INDUSTRIAL_CO2)
  const pv_temp = (pv_flux_in + pv_co2_forcing - AREF) / B

  const temp_change = pv_temp - base_temp

  return {
    base_temp: base_temp,
    pv_temp: pv_temp,
    temp_change: temp_change,
    co2_reduction: co2_reduction_ppm,
    albedo_change: pv_planetary_albedo - base_planetary_albedo,
    cooling_effect: temp_change < 0,
    heat_island_effect: temp_change * 1.1,
    cooling_efficiency: Math.abs(temp_change) * 10
  }
}

/**
 * 生成测试场景数据
 */
export function generateTestScenarios() {
  const scenarios = []

  // 覆盖率测试序列
  const coverage_ratios = [1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7]

  coverage_ratios.forEach(ratio => {
    const params = {
      albedo_pv: 0.438,
      coverage_ratio: ratio,
      pv_efficiency: 0.23,
      albedo_land: 0.3,
      albedo_ocean: 0.06,
      co2_current: 420.0,
      initial_temp: 15.0,
      simulation_years: 100,
      irradiance: 1420
    }

    const result = calculatePVEffect(params)

    scenarios.push({
      name: `覆盖率测试 - ${ratio.toExponential(1)}`,
      category: 'coverage_test',
      params: params,
      result: result,
      description: `测试覆盖率 ${ratio.toExponential(1)} 对温度的影响`
    })
  })

  // 光伏面板类型对比
  Object.entries(PV_PANEL_TYPES).forEach(([type, panel]) => {
    const params = {
      albedo_pv: panel.albedo,
      coverage_ratio: 1e-8,
      pv_efficiency: panel.efficiency,
      albedo_land: 0.3,
      albedo_ocean: 0.06,
      co2_current: 420.0,
      initial_temp: 15.0,
      simulation_years: 100,
      irradiance: 1420
    }

    const result = calculatePVEffect(params)

    scenarios.push({
      name: `面板类型 - ${panel.name}`,
      category: 'panel_type',
      params: params,
      result: result,
      description: panel.description
    })
  })

  // 地区对比测试
  Object.entries(REGION_DATA).forEach(([region, data]) => {
    const params = {
      albedo_pv: 0.438,
      coverage_ratio: 1e-8,
      pv_efficiency: 0.23,
      albedo_land: data.land_albedo,
      albedo_ocean: 0.06,
      co2_current: 420.0,
      initial_temp: data.base_temp,
      simulation_years: 100,
      irradiance: data.irradiance,
      latitude: data.latitude,
      longitude: data.longitude
    }

    const result = calculatePVEffect(params)

    scenarios.push({
      name: `地区测试 - ${data.name}`,
      category: 'region_test',
      params: params,
      result: result,
      description: data.description
    })
  })

  // CO2浓度影响测试
  const co2_levels = [350, 380, 420, 450, 500, 600]

  co2_levels.forEach(co2 => {
    const params = {
      albedo_pv: 0.438,
      coverage_ratio: 1e-8,
      pv_efficiency: 0.23,
      albedo_land: 0.3,
      albedo_ocean: 0.06,
      co2_current: co2,
      initial_temp: 15.0,
      simulation_years: 100,
      irradiance: 1420
    }

    const result = calculatePVEffect(params)

    scenarios.push({
      name: `CO2浓度测试 - ${co2} ppm`,
      category: 'co2_test',
      params: params,
      result: result,
      description: `测试不同CO2浓度下的光伏效应`
    })
  })

  return scenarios
}

/**
 * 生成对比报告
 */
export function generateComparisonReport(scenarios) {
  const report = {
    summary: {
      total_scenarios: scenarios.length,
      categories: {},
      temp_range: { min: Infinity, max: -Infinity },
      co2_range: { min: Infinity, max: -Infinity }
    },
    scenarios: scenarios,
    insights: []
  }

  scenarios.forEach(scenario => {
    // 统计分类
    if (!report.summary.categories[scenario.category]) {
      report.summary.categories[scenario.category] = 0
    }
    report.summary.categories[scenario.category]++

    // 温度范围
    if (scenario.result.temp_change < report.summary.temp_range.min) {
      report.summary.temp_range.min = scenario.result.temp_change
    }
    if (scenario.result.temp_change > report.summary.temp_range.max) {
      report.summary.temp_range.max = scenario.result.temp_change
    }

    // CO2范围
    if (scenario.result.co2_reduction < report.summary.co2_range.min) {
      report.summary.co2_range.min = scenario.result.co2_reduction
    }
    if (scenario.result.co2_reduction > report.summary.co2_range.max) {
      report.summary.co2_range.max = scenario.result.co2_reduction
    }
  })

  // 生成洞察
  const coverage_scenarios = scenarios.filter(s => s.category === 'coverage_test')
  if (coverage_scenarios.length >= 2) {
    const min_coverage = coverage_scenarios[0]
    const max_coverage = coverage_scenarios[coverage_scenarios.length - 1]

    report.insights.push({
      type: 'coverage_impact',
      title: '覆盖率影响分析',
      content: `覆盖率从 ${min_coverage.params.coverage_ratio.toExponential(1)} 增加到 ${max_coverage.params.coverage_ratio.toExponential(1)} 时，CO2减排量从 ${min_coverage.result.co2_reduction.toFixed(2)} ppm 增加到 ${max_coverage.result.co2_reduction.toFixed(2)} ppm`
    })
  }

  const panel_scenarios = scenarios.filter(s => s.category === 'panel_type')
  if (panel_scenarios.length > 0) {
    const best_cooling = panel_scenarios.reduce((best, current) =>
      current.result.temp_change < best.result.temp_change ? current : best
    )

    report.insights.push({
      type: 'panel_performance',
      title: '最佳面板性能',
      content: `${best_cooling.name} 在相同覆盖率下产生最大的降温效果：${best_cooling.result.temp_change.toFixed(6)}°C`
    })
  }

  return report
}

/**
 * 获取快速测试数据
 */
export function getQuickTestData() {
  return {
    low_coverage: {
      name: '低覆盖率场景',
      params: {
        albedo_pv: 0.438,
        coverage_ratio: 1e-9,
        pv_efficiency: 0.23,
        albedo_land: 0.3,
        co2_current: 420.0
      },
      expected_results: {
        temp_change_range: '-0.02 to -0.01°C',
        co2_reduction_range: '2-5 ppm'
      }
    },
    medium_coverage: {
      name: '中等覆盖率场景',
      params: {
        albedo_pv: 0.438,
        coverage_ratio: 1e-8,
        pv_efficiency: 0.23,
        albedo_land: 0.3,
        co2_current: 420.0
      },
      expected_results: {
        temp_change_range: '-0.2 to -0.1°C',
        co2_reduction_range: '20-30 ppm'
      }
    },
    high_coverage: {
      name: '高覆盖率场景',
      params: {
        albedo_pv: 0.438,
        coverage_ratio: 1e-7,
        pv_efficiency: 0.23,
        albedo_land: 0.3,
        co2_current: 420.0
      },
      expected_results: {
        temp_change_range: '-1.5 to -0.5°C',
        co2_reduction_range: '200-300 ppm'
      }
    },
    high_albedo: {
      name: '高反照率面板',
      params: {
        albedo_pv: 0.95,
        coverage_ratio: 1e-8,
        pv_efficiency: 0.23,
        albedo_land: 0.3,
        co2_current: 420.0
      },
      expected_results: {
        temp_change_range: '-0.5 to -0.3°C',
        co2_reduction_range: '20-30 ppm',
        note: '主要降温来自反照率效应'
      }
    },
    high_efficiency: {
      name: '高效率面板',
      params: {
        albedo_pv: 0.438,
        coverage_ratio: 1e-8,
        pv_efficiency: 0.25,
        albedo_land: 0.3,
        co2_current: 420.0
      },
      expected_results: {
        temp_change_range: '-0.2 to -0.1°C',
        co2_reduction_range: '25-35 ppm',
        note: '主要降温来自CO2减排'
      }
    }
  }
}

export default {
  generateTestScenarios,
  generateComparisonReport,
  getQuickTestData,
  PV_PANEL_TYPES,
  REGION_DATA,
  PHYSICAL_CONSTANTS
}
