/**
 * 计算结果存储管理
 * 支持本地存储、历史记录、导出和对比功能
 */

// 存储键名
const STORAGE_KEYS = {
  RESULTS: 'pv_simulation_results',
  CURRENT: 'pv_simulation_current',
  FAVORITES: 'pv_simulation_favorites',
  EXPORT_HISTORY: 'pv_simulation_export_history'
}

/**
 * 结果存储类
 */
class ResultStorage {
  constructor() {
    this.maxResults = 1000 // 最大存储结果数
    this.currentResult = null
    this.loadCurrent()
  }

  /**
   * 保存计算结果
   * @param {Object} params - 输入参数
   * @param {Object} results - 计算结果
   * @param {string} scenarioName - 场景名称
   * @returns {string} 结果ID
   */
  saveResult(params, results, scenarioName = null) {
    const resultId = this.generateId()
    const timestamp = new Date().toISOString()

    const resultRecord = {
      id: resultId,
      timestamp,
      scenarioName: scenarioName || this.generateScenarioName(params),
      params: { ...params },
      results: { ...results },
      metadata: {
        createdAt: timestamp,
        version: '2.0.0',
        tags: this.generateTags(params)
      }
    }

    // 保存到历史记录
    this.saveToHistory(resultRecord)

    // 保存为当前结果
    this.currentResult = resultRecord
    this.saveCurrent()

    return resultId
  }

  /**
   * 保存到历史记录
   * @private
   */
  saveToHistory(record) {
    let history = this.getHistory()

    // 添加新记录到开头
    history.unshift(record)

    // 限制历史记录数量
    if (history.length > this.maxResults) {
      history = history.slice(0, this.maxResults)
    }

    try {
      localStorage.setItem(STORAGE_KEYS.RESULTS, JSON.stringify(history))
    } catch (error) {
      console.error('保存历史记录失败:', error)
      // 如果存储空间不足，清理旧记录
      this.clearOldResults()
      localStorage.setItem(STORAGE_KEYS.RESULTS, JSON.stringify(history))
    }
  }

  /**
   * 获取历史记录
   * @param {Object} filters - 过滤条件
   * @returns {Array} 历史记录
   */
  getHistory(filters = {}) {
    try {
      const historyJson = localStorage.getItem(STORAGE_KEYS.RESULTS)
      if (!historyJson) return []

      let history = JSON.parse(historyJson)

      // 应用过滤条件
      if (filters.scenarioName) {
        history = history.filter(r =>
          r.scenarioName.includes(filters.scenarioName)
        )
      }

      if (filters.dateFrom) {
        history = history.filter(r =>
          new Date(r.timestamp) >= new Date(filters.dateFrom)
        )
      }

      if (filters.dateTo) {
        history = history.filter(r =>
          new Date(r.timestamp) <= new Date(filters.dateTo)
        )
      }

      if (filters.tags && filters.tags.length > 0) {
        history = history.filter(r =>
          filters.tags.some(tag => r.metadata.tags.includes(tag))
        )
      }

      return history
    } catch (error) {
      console.error('读取历史记录失败:', error)
      return []
    }
  }

  /**
   * 获取当前结果
   * @returns {Object|null} 当前结果
   */
  getCurrent() {
    return this.currentResult
  }

  /**
   * 保存当前结果
   * @private
   */
  saveCurrent() {
    try {
      localStorage.setItem(STORAGE_KEYS.CURRENT, JSON.stringify(this.currentResult))
    } catch (error) {
      console.error('保存当前结果失败:', error)
    }
  }

  /**
   * 加载当前结果
   * @private
   */
  loadCurrent() {
    try {
      const currentJson = localStorage.getItem(STORAGE_KEYS.CURRENT)
      if (currentJson) {
        this.currentResult = JSON.parse(currentJson)
      }
    } catch (error) {
      console.error('加载当前结果失败:', error)
    }
  }

  /**
   * 根据ID获取结果
   * @param {string} resultId - 结果ID
   * @returns {Object|null} 结果记录
   */
  getResultById(resultId) {
    const history = this.getHistory()
    return history.find(r => r.id === resultId) || null
  }

  /**
   * 删除结果
   * @param {string} resultId - 结果ID
   * @returns {boolean} 是否成功
   */
  deleteResult(resultId) {
    try {
      let history = this.getHistory()
      history = history.filter(r => r.id !== resultId)
      localStorage.setItem(STORAGE_KEYS.RESULTS, JSON.stringify(history))
      return true
    } catch (error) {
      console.error('删除结果失败:', error)
      return false
    }
  }

  /**
   * 添加到收藏
   * @param {string} resultId - 结果ID
   * @param {string} note - 备注
   * @returns {boolean} 是否成功
   */
  addToFavorites(resultId, note = '') {
    try {
      let favorites = this.getFavorites()
      const result = this.getResultById(resultId)

      if (result && !favorites.find(f => f.id === resultId)) {
        favorites.push({
          ...result,
          note,
          favoriteAt: new Date().toISOString()
        })

        localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(favorites))
        return true
      }

      return false
    } catch (error) {
      console.error('添加收藏失败:', error)
      return false
    }
  }

  /**
   * 获取收藏列表
   * @returns {Array} 收藏列表
   */
  getFavorites() {
    try {
      const favoritesJson = localStorage.getItem(STORAGE_KEYS.FAVORITES)
      return favoritesJson ? JSON.parse(favoritesJson) : []
    } catch (error) {
      console.error('读取收藏失败:', error)
      return []
    }
  }

  /**
   * 从收藏中移除
   * @param {string} resultId - 结果ID
   * @returns {boolean} 是否成功
   */
  removeFromFavorites(resultId) {
    try {
      let favorites = this.getFavorites()
      favorites = favorites.filter(f => f.id !== resultId)
      localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(favorites))
      return true
    } catch (error) {
      console.error('移除收藏失败:', error)
      return false
    }
  }

  /**
   * 对比多个结果
   * @param {Array} resultIds - 结果ID数组
   * @returns {Object} 对比结果
   */
  compareResults(resultIds) {
    const results = resultIds.map(id => this.getResultById(id)).filter(r => r)

    if (results.length < 2) {
      throw new Error('需要至少2个结果进行对比')
    }

    const comparison = {
      results: results.map(r => ({
        id: r.id,
        scenarioName: r.scenarioName,
        timestamp: r.timestamp,
        temperatureChange: r.results.comparison?.temperature_change || 0,
        co2Reduction: r.results.pv_scenario?.co2_reduction || 0,
        coolingEfficiency: r.results.comparison?.cooling_efficiency || 0,
        albedoChange: r.results.comparison?.albedo_change || 0
      })),
      analysis: this.analyzeComparison(results)
    }

    return comparison
  }

  /**
   * 分析对比结果
   * @private
   */
  analyzeComparison(results) {
    const analysis = {
      bestCooling: null,
      bestCO2Reduction: null,
      bestEfficiency: null,
      parameterComparison: {}
    }

    let maxCooling = -Infinity
    let maxCO2 = -Infinity
    let maxEfficiency = -Infinity

    results.forEach(result => {
      const tempChange = result.results.comparison?.temperature_change || 0
      const co2Reduction = result.results.pv_scenario?.co2_reduction || 0
      const efficiency = result.results.comparison?.cooling_efficiency || 0

      if (tempChange < maxCooling) {
        maxCooling = tempChange
        analysis.bestCooling = result.id
      }

      if (co2Reduction > maxCO2) {
        maxCO2 = co2Reduction
        analysis.bestCO2Reduction = result.id
      }

      if (efficiency > maxEfficiency) {
        maxEfficiency = efficiency
        analysis.bestEfficiency = result.id
      }

      // 参数对比分析
      Object.keys(result.params).forEach(key => {
        if (!analysis.parameterComparison[key]) {
          analysis.parameterComparison[key] = {
            min: result.params[key],
            max: result.params[key],
            avg: result.params[key],
            values: []
          }
        }

        analysis.parameterComparison[key].values.push({
          id: result.id,
          value: result.params[key],
          scenarioName: result.scenarioName
        })
      })
    })

    // 计算参数统计
    Object.keys(analysis.parameterComparison).forEach(key => {
      const values = analysis.parameterComparison[key].values.map(v => v.value)
      analysis.parameterComparison[key].min = Math.min(...values)
      analysis.parameterComparison[key].max = Math.max(...values)
      analysis.parameterComparison[key].avg = values.reduce((a, b) => a + b, 0) / values.length
    })

    return analysis
  }

  /**
   * 导出结果
   * @param {string} resultId - 结果ID
   * @param {string} format - 导出格式 (json/csv/excel)
   * @returns {Blob} 导出文件
   */
  exportResult(resultId, format = 'json') {
    const result = this.getResultById(resultId)

    if (!result) {
      throw new Error('结果不存在')
    }

    let content, filename, mimeType

    switch (format) {
      case 'json':
        content = JSON.stringify(result, null, 2)
        filename = `pv-simulation-${result.id}.json`
        mimeType = 'application/json'
        break

      case 'csv':
        content = this.convertToCSV(result)
        filename = `pv-simulation-${result.id}.csv`
        mimeType = 'text/csv'
        break

      default:
        throw new Error('不支持的导出格式')
    }

    // 记录导出历史
    this.recordExport(resultId, format)

    return new Blob([content], { type: mimeType })
  }

  /**
   * 批量导出
   * @param {Array} resultIds - 结果ID数组
   * @param {string} format - 导出格式
   * @returns {Blob} 导出文件
   */
  exportBatch(resultIds, format = 'json') {
    const results = resultIds.map(id => this.getResultById(id)).filter(r => r)

    if (results.length === 0) {
      throw new Error('没有可导出的结果')
    }

    let content, filename, mimeType

    switch (format) {
      case 'json':
        content = JSON.stringify(results, null, 2)
        filename = `pv-simulation-batch-${Date.now()}.json`
        mimeType = 'application/json'
        break

      case 'csv':
        content = this.convertBatchToCSV(results)
        filename = `pv-simulation-batch-${Date.now()}.csv`
        mimeType = 'text/csv'
        break

      default:
        throw new Error('不支持的导出格式')
    }

    return new Blob([content], { type: mimeType })
  }

  /**
   * 转换为CSV格式
   * @private
   */
  convertToCSV(result) {
    const headers = [
      'ID',
      '场景名称',
      '时间戳',
      '反照率',
      '覆盖率',
      '光伏效率',
      '陆地反照率',
      '海洋反照率',
      'CO2浓度',
      '初始温度',
      '温度变化',
      'CO2减排',
      '冷却效率',
      '反照率变化'
    ]

    const row = [
      result.id,
      result.scenarioName,
      result.timestamp,
      result.params.albedo_pv || '',
      result.params.coverage_ratio || '',
      result.params.pv_efficiency || '',
      result.params.albedo_land || '',
      result.params.albedo_ocean || '',
      result.params.co2_current || '',
      result.params.initial_temp || '',
      result.results.comparison?.temperature_change || '',
      result.results.pv_scenario?.co2_reduction || '',
      result.results.comparison?.cooling_efficiency || '',
      result.results.comparison?.albedo_change || ''
    ]

    return [headers.join(','), row.join(',')].join('\n')
  }

  /**
   * 批量转换为CSV
   * @private
   */
  convertBatchToCSV(results) {
    const headers = [
      'ID',
      '场景名称',
      '时间戳',
      '反照率',
      '覆盖率',
      '光伏效率',
      '陆地反照率',
      '海洋反照率',
      'CO2浓度',
      '初始温度',
      '温度变化',
      'CO2减排',
      '冷却效率',
      '反照率变化'
    ]

    const rows = results.map(result => [
      result.id,
      result.scenarioName,
      result.timestamp,
      result.params.albedo_pv || '',
      result.params.coverage_ratio || '',
      result.params.pv_efficiency || '',
      result.params.albedo_land || '',
      result.params.albedo_ocean || '',
      result.params.co2_current || '',
      result.params.initial_temp || '',
      result.results.comparison?.temperature_change || '',
      result.results.pv_scenario?.co2_reduction || '',
      result.results.comparison?.cooling_efficiency || '',
      result.results.comparison?.albedo_change || ''
    ])

    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  }

  /**
   * 记录导出历史
   * @private
   */
  recordExport(resultId, format) {
    try {
      const history = JSON.parse(localStorage.getItem(STORAGE_KEYS.EXPORT_HISTORY) || '[]')
      history.unshift({
        resultId,
        format,
        timestamp: new Date().toISOString()
      })

      // 只保留最近100条导出记录
      if (history.length > 100) {
        history.pop()
      }

      localStorage.setItem(STORAGE_KEYS.EXPORT_HISTORY, JSON.stringify(history))
    } catch (error) {
      console.error('记录导出历史失败:', error)
    }
  }

  /**
   * 获取存储统计信息
   * @returns {Object} 统计信息
   */
  getStorageStats() {
    const history = this.getHistory()
    const favorites = this.getFavorites()

    return {
      totalResults: history.length,
      favoriteResults: favorites.length,
      storageUsed: this.getStorageUsed(),
      oldestResult: history.length > 0 ? history[history.length - 1].timestamp : null,
      newestResult: history.length > 0 ? history[0].timestamp : null
    }
  }

  /**
   * 获取存储使用情况
   * @private
   */
  getStorageUsed() {
    let totalSize = 0
    const keys = Object.values(STORAGE_KEYS)

    keys.forEach(key => {
      const value = localStorage.getItem(key)
      if (value) {
        totalSize += value.length
      }
    })

    return totalSize
  }

  /**
   * 清理旧结果
   * @private
   */
  clearOldResults() {
    try {
      let history = this.getHistory()
      const targetSize = Math.floor(this.maxResults * 0.8) // 保留80%

      if (history.length > targetSize) {
        history = history.slice(0, targetSize)
        localStorage.setItem(STORAGE_KEYS.RESULTS, JSON.stringify(history))
      }
    } catch (error) {
      console.error('清理旧结果失败:', error)
    }
  }

  /**
   * 清空所有数据
   */
  clearAll() {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
    this.currentResult = null
  }

  /**
   * 生成唯一ID
   * @private
   */
  generateId() {
    return `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 生成场景名称
   * @private
   */
  generateScenarioName(params) {
    const coverage = params.coverage_ratio || 0
    const albedo = params.albedo_pv || 0.438

    if (coverage >= 1e-7) {
      return `高覆盖率 (${albedo.toFixed(3)})`
    } else if (coverage >= 1e-8) {
      return `中等覆盖率 (${albedo.toFixed(3)})`
    } else {
      return `低覆盖率 (${albedo.toFixed(3)})`
    }
  }

  /**
   * 生成标签
   * @private
   */
  generateTags(params) {
    const tags = []

    // 覆盖率标签
    const coverage = params.coverage_ratio || 0
    if (coverage >= 1e-7) {
      tags.push('高覆盖率')
    } else if (coverage >= 1e-8) {
      tags.push('中等覆盖率')
    } else {
      tags.push('低覆盖率')
    }

    // 反照率标签
    const albedo = params.albedo_pv || 0.438
    if (albedo >= 0.9) {
      tags.push('镜面面板')
    } else if (albedo >= 0.4) {
      tags.push('新型面板')
    } else {
      tags.push('普通面板')
    }

    // CO2浓度标签
    const co2 = params.co2_current || 420
    if (co2 >= 800) {
      tags.push('高CO2')
    } else if (co2 <= 350) {
      tags.push('低CO2')
    }

    return tags
  }
}

// 导出单例实例
export const resultStorage = new ResultStorage()
export default resultStorage
