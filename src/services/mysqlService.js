/**
 * MySQL数据库服务
 * 用于连接后端MySQL API
 */

class MySQLDatabaseService {
  constructor() {
    this.apiBaseURL = 'http://localhost:5000/api'
    this.isConnected = false
  }

  /**
   * 测试数据库连接
   */
  async testConnection() {
    try {
      const response = await fetch(`${this.apiBaseURL}/health`)
      const result = await response.json()

      this.isConnected = result.success
      return result
    } catch (error) {
      console.error('数据库连接测试失败:', error)
      return {
        success: false,
        status: 'disconnected',
        error: error.message
      }
    }
  }

  /**
   * 保存计算结果到MySQL数据库
   */
  async saveSimulation(params, results, metadata = {}) {
    try {
      const payload = {
        scenario_name: this.generateScenarioName(params),
        description: metadata.description || '',
        calculation_time_ms: metadata.calculationTimeMs || 0,
        params: params,
        results: results
      }

      const response = await fetch(`${this.apiBaseURL}/simulations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      const result = await response.json()

      if (result.success) {
        console.log('✅ 模拟结果已保存到MySQL:', result.data.record_id)
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('保存模拟结果失败:', error)
      throw error
    }
  }

  /**
   * 获取模拟记录列表
   */
  async getSimulations(filters = {}) {
    try {
      const queryParams = new URLSearchParams()

      if (filters.page) queryParams.append('page', filters.page)
      if (filters.perPage) queryParams.append('per_page', filters.perPage)
      if (filters.status) queryParams.append('status', filters.status)
      if (filters.search) queryParams.append('search', filters.search)
      if (filters.sortBy) queryParams.append('sort_by', filters.sortBy)
      if (filters.sortOrder) queryParams.append('sort_order', filters.sortOrder)

      const url = `${this.apiBaseURL}/simulations${queryParams.toString() ? '?' + queryParams.toString() : ''}`
      const response = await fetch(url)
      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('获取模拟记录失败:', error)
      throw error
    }
  }

  /**
   * 获取单个模拟记录详情
   */
  async getSimulation(recordId) {
    try {
      const response = await fetch(`${this.apiBaseURL}/simulations/${recordId}`)
      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('获取模拟记录详情失败:', error)
      throw error
    }
  }

  /**
   * 删除模拟记录
   */
  async deleteSimulation(recordId) {
    try {
      const response = await fetch(`${this.apiBaseURL}/simulations/${recordId}`, {
        method: 'DELETE'
      })
      const result = await response.json()

      if (result.success) {
        console.log('✅ 模拟记录已删除:', recordId)
        return true
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('删除模拟记录失败:', error)
      throw error
    }
  }

  /**
   * 对比多个模拟记录
   */
  async compareSimulations(recordIds) {
    try {
      if (recordIds.length < 2) {
        throw new Error('至少需要2条记录进行对比')
      }

      const response = await fetch(`${this.apiBaseURL}/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ record_ids: recordIds })
      })

      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('对比模拟记录失败:', error)
      throw error
    }
  }

  /**
   * 获取统计信息
   */
  async getStatistics() {
    try {
      const response = await fetch(`${this.apiBaseURL}/statistics`)
      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('获取统计信息失败:', error)
      throw error
    }
  }

  /**
   * 获取所有标签
   */
  async getTags() {
    try {
      const response = await fetch(`${this.apiBaseURL}/tags`)
      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('获取标签失败:', error)
      throw error
    }
  }

  /**
   * 根据标签获取模拟记录
   */
  async getSimulationsByTag(tagId) {
    try {
      const response = await fetch(`${this.apiBaseURL}/tags/${tagId}/simulations`)
      const result = await response.json()

      if (result.success) {
        return result.data
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('获取标签模拟记录失败:', error)
      throw error
    }
  }

  /**
   * 生成场景名称
   */
  generateScenarioName(params) {
    const coverage = params.coverage_ratio || 0
    const albedo = params.albedo_pv || 0.438

    // 覆盖率描述
    let coverageDesc = '未知覆盖率'
    if (coverage >= 1e-7) {
      coverageDesc = '高覆盖率'
    } else if (coverage >= 1e-8) {
      coverageDesc = '中等覆盖率'
    } else {
      coverageDesc = '低覆盖率'
    }

    // 面板类型描述
    let panelDesc = ''
    if (albedo >= 0.9) {
      panelDesc = '镜面面板'
    } else if (albedo >= 0.4) {
      panelDesc = '新型面板'
    } else {
      panelDesc = '普通面板'
    }

    return `${coverageDesc} - ${panelDesc} (${albedo.toFixed(3)})`
  }

  /**
   * 批量导入数据
   */
  async batchImport(records) {
    const results = {
      success: 0,
      failed: 0,
      errors: []
    }

    for (const record of records) {
      try {
        await this.saveSimulation(
          record.params,
          record.results,
          record.metadata || {}
        )
        results.success++
      } catch (error) {
        results.failed++
        results.errors.push({
          record: record.scenario_name,
          error: error.message
        })
      }
    }

    return results
  }

  /**
   * 导出数据为JSON
   */
  async exportToJson(recordIds) {
    try {
      const records = await Promise.all(
        recordIds.map(id => this.getSimulation(id))
      )

      const exportData = {
        export_date: new Date().toISOString(),
        total_records: records.length,
        records: records
      }

      return JSON.stringify(exportData, null, 2)
    } catch (error) {
      console.error('导出JSON失败:', error)
      throw error
    }
  }

  /**
   * 导出数据为CSV
   */
  async exportToCsv(recordIds) {
    try {
      const records = await Promise.all(
        recordIds.map(id => this.getSimulation(id))
      )

      // CSV表头
      const headers = [
        'record_id',
        'scenario_name',
        'created_at',
        'albedo_pv',
        'coverage_ratio',
        'pv_efficiency',
        'co2_current',
        'temperature_change',
        'pv_co2_reduction',
        'cooling_efficiency',
        'albedo_change'
      ]

      // CSV数据行
      const rows = records.map(record => [
        record.record_id || '',
        record.scenario_name || '',
        record.created_at || '',
        record.albedo_pv || '',
        record.coverage_ratio || '',
        record.pv_efficiency || '',
        record.co2_current || '',
        record.temperature_change || '',
        record.pv_co2_reduction || '',
        record.cooling_efficiency || '',
        record.albedo_change || ''
      ])

      // 组合CSV内容
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n')

      return csvContent
    } catch (error) {
      console.error('导出CSV失败:', error)
      throw error
    }
  }
}

// 创建全局实例
const mysqlDB = new MySQLDatabaseService()

export default mysqlDB