/**
 * 模拟状态管理
 * 提供全局状态和方法给所有组件使用
 */

import { ref, reactive, computed } from 'vue'
import { quickCalculate, defaultParams } from '@/services/realApi'
import resultStorage from '@/utils/resultStorage'

// 全局模拟状态
const simulationState = reactive({
  // 当前参数
  params: { ...defaultParams },

  // 计算结果
  results: null,

  // 计算状态
  isCalculating: false,

  // 错误信息
  error: null,

  // 当前场景
  currentScenario: null,

  // 3D可视化数据
  visualizationData: {
    temperatureField: [],
    heatIslandIntensity: 0,
    coolingEfficiency: 0,
    albedoChange: 0,
    co2Reduction: 0
  }
})

// 计算队列（用于批量计算）
const calculationQueue = []

/**
 * 模拟状态管理Composable
 */
export function useSimulation() {
  // 更新参数
  const updateParams = (newParams) => {
    simulationState.params = {
      ...simulationState.params,
      ...newParams
    }
    // 触发重新计算
    triggerCalculation()
  }

  // 设置场景
  const setScenario = (scenario) => {
    simulationState.currentScenario = scenario.name
    updateParams(scenario.params)
  }

  // 触发计算
  const triggerCalculation = async (saveResult = true) => {
    simulationState.isCalculating = true
    simulationState.error = null

    try {
      // 使用快速计算（前端实时计算）
      const result = quickCalculate(simulationState.params)

      if (result.success) {
        simulationState.results = result.data

        // 更新可视化数据
        updateVisualizationData(result.data)

        // 自动保存结果
        if (saveResult) {
          const resultId = resultStorage.saveResult(
            simulationState.params,
            result.data,
            simulationState.currentScenario
          )
          console.log('计算结果已保存:', resultId)
        }

        // 触发事件通知其他组件
        window.dispatchEvent(new CustomEvent('simulation-updated', {
          detail: result.data
        }))
      }
    } catch (error) {
      simulationState.error = error.message
      console.error('计算错误:', error)
    } finally {
      simulationState.isCalculating = false
    }
  }

  // 更新可视化数据
  const updateVisualizationData = (data) => {
    if (!data) return

    const comparison = data.comparison || {}
    const pvScenario = data.pv_scenario || {}

    simulationState.visualizationData = {
      temperatureField: generateTemperatureField(data),
      heatIslandIntensity: comparison.heat_island_effect || 0,
      coolingEfficiency: comparison.cooling_efficiency || 0,
      albedoChange: comparison.albedo_change || 0,
      co2Reduction: pvScenario.co2_reduction || 0
    }
  }

  // 生成温度场数据
  const generateTemperatureField = (data) => {
    const baselineTemp = data.baseline?.equilibrium_temp || 15.0
    const pvTemp = data.pv_scenario?.equilibrium_temp || 15.0
    const tempChange = data.comparison?.temperature_change || 0

    // 生成20x20温度场网格
    const field = []
    const gridSize = 20

    for (let x = 0; x < gridSize; x++) {
      for (let z = 0; z < gridSize; z++) {
        // 添加空间变化和噪声
        const centerX = gridSize / 2
        const centerZ = gridSize / 2
        const distance = Math.sqrt((x - centerX) ** 2 + (z - centerZ) ** 2)
        const maxDistance = Math.sqrt(centerX ** 2 + centerZ ** 2)

        // 距离中心的归一化距离
        const normalizedDistance = distance / maxDistance

        // 温度变化受距离影响（中心效应更强）
        const localTempChange = tempChange * (1 - normalizedDistance * 0.5)

        // 添加随机变化
        const randomVariation = (Math.random() - 0.5) * 2

        field.push({
          x,
          z,
          temperature: baselineTemp + localTempChange + randomVariation,
          temperatureChange: localTempChange + randomVariation
        })
      }
    }

    return field
  }

  // 计算属性
  const temperatureChange = computed(() => {
    return simulationState.results?.comparison?.temperature_change || 0
  })

  const albedoChange = computed(() => {
    return simulationState.results?.comparison?.albedo_change || 0
  })

  const co2Reduction = computed(() => {
    return simulationState.results?.pv_scenario?.co2_reduction || 0
  })

  const coolingEffect = computed(() => {
    return simulationState.results?.comparison?.cooling_effect || false
  })

  const heatIslandEffect = computed(() => {
    return simulationState.results?.comparison?.heat_island_effect || 0
  })

  const coolingEfficiency = computed(() => {
    return simulationState.results?.comparison?.cooling_efficiency || 0
  })

  // 获取温度颜色
  const getTemperatureColor = (temp) => {
    const normalizedTemp = (temp + 32) / 77 // -32 to +45 -> 0 to 1

    if (normalizedTemp < 0.2) {
      // 冷色：蓝色到青色
      const t = normalizedTemp / 0.2
      return `rgb(${Math.round(74 * t)}, ${Math.round(158 * (1 - t) + 217 * t)}, ${255})`
    } else if (normalizedTemp < 0.5) {
      // 中等：青色到绿色
      const t = (normalizedTemp - 0.2) / 0.3
      return `rgb(${Math.round(74 * (1 - t))}, ${255}, ${Math.round(217 * (1 - t) + 157 * t)})`
    } else if (normalizedTemp < 0.8) {
      // 暖色：绿色到橙色
      const t = (normalizedTemp - 0.5) / 0.3
      return `rgb(${Math.round(255 * t)}, ${Math.round(217 * (1 - t) + 157 * t)}, ${Math.round(89 * t)})`
    } else {
      // 热色：橙色到红色
      const t = (normalizedTemp - 0.8) / 0.2
      return `rgb(255, ${Math.round(157 * (1 - t) + 87 * t)}, ${Math.round(87 * t)})`
    }
  }

  // 重置状态
  const resetState = () => {
    simulationState.params = { ...defaultParams }
    simulationState.results = null
    simulationState.error = null
    simulationState.currentScenario = null
    simulationState.visualizationData = {
      temperatureField: [],
      heatIslandIntensity: 0,
      coolingEfficiency: 0,
      albedoChange: 0,
      co2Reduction: 0
    }
  }

  return {
    // 状态
    simulationState,
    params: simulationState.params,
    results: simulationState.results,
    isCalculating: simulationState.isCalculating,
    error: simulationState.error,
    currentScenario: simulationState.currentScenario,
    visualizationData: simulationState.visualizationData,

    // 计算属性
    temperatureChange,
    albedoChange,
    co2Reduction,
    coolingEffect,
    heatIslandEffect,
    coolingEfficiency,

    // 方法
    updateParams,
    setScenario,
    triggerCalculation,
    getTemperatureColor,
    resetState,

    // 存储相关方法
    resultStorage,
    getResultHistory: (filters) => resultStorage.getHistory(filters),
    getResultById: (id) => resultStorage.getResultById(id),
    deleteResult: (id) => resultStorage.deleteResult(id),
    addToFavorites: (id, note) => resultStorage.addToFavorites(id, note),
    getFavorites: () => resultStorage.getFavorites(),
    compareResults: (ids) => resultStorage.compareResults(ids),
    exportResult: (id, format) => resultStorage.exportResult(id, format),
    getStorageStats: () => resultStorage.getStorageStats()
  }
}

// 导出单例实例
export const simulation = useSimulation()
