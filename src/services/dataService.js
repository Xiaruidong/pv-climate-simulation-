/**
 * 统一数据服务
 * MySQL数据库为首选存储，localStorage为兜底：
 * - 保存：先写localStorage（保证离线可用），数据库在线时异步同步到MySQL并回填record_id
 * - 读取：数据库在线时合并MySQL记录与本地记录，离线时只读本地
 * - 删除：本地与数据库两侧同步删除
 */
import mysqlDB from '@/services/mysqlService'
import resultStorage from '@/utils/resultStorage'

// 连接状态缓存（避免每次操作都做健康检查）
let connectionChecked = false
let dbOnline = false
let connectionPromise = null
const CONNECTION_TTL = 30 * 1000
let lastCheckTime = 0

class DataService {
  /**
   * 检查MySQL后端是否可用（带缓存）
   * @param {boolean} force - 强制重新检查
   * @returns {Promise<boolean>}
   */
  async isDbOnline(force = false) {
    const now = Date.now()
    if (!force && connectionChecked && now - lastCheckTime < CONNECTION_TTL) {
      return dbOnline
    }
    if (connectionPromise) return connectionPromise

    connectionPromise = (async () => {
      try {
        const result = await mysqlDB.testConnection()
        dbOnline = !!(result && result.success)
      } catch {
        dbOnline = false
      } finally {
        connectionChecked = true
        lastCheckTime = Date.now()
        connectionPromise = null
      }
      return dbOnline
    })()

    return connectionPromise
  }

  /** 数据源描述，用于界面显示 */
  async getDataSourceLabel() {
    const online = await this.isDbOnline()
    return online ? 'MySQL数据库' : '本地存储（数据库离线）'
  }

  /**
   * 保存计算结果
   * 始终写入localStorage，数据库在线时同步写MySQL
   * @returns {Promise<{localId: string, dbRecordId: string|null, dbOnline: boolean}>}
   */
  async saveSimulation(params, results, scenarioName = null, metadata = {}) {
    const localId = resultStorage.saveResult(params, results, scenarioName)
    let dbRecordId = null
    const online = await this.isDbOnline()

    if (online) {
      try {
        const start = Date.now()
        // 将计算来源等元数据随结果一并入库（写入calculation_metadata JSON字段）
        const resultsWithMeta = {
          ...results,
          metadata: {
            ...(results.metadata || {}),
            calculation_source: metadata.calculationSource || null,
            saved_at: new Date().toISOString()
          }
        }
        const data = await mysqlDB.saveSimulation(params, resultsWithMeta, {
          description: scenarioName || metadata.description || '',
          calculationTimeMs: metadata.calculationTimeMs || (Date.now() - start)
        })
        dbRecordId = data?.record_id || null
        if (dbRecordId) {
          resultStorage.updateResultMeta(localId, { syncedToDb: true }, { dbRecordId })
        }
      } catch (error) {
        console.warn('同步到MySQL失败（结果已保留在本地）:', error.message)
        await this.isDbOnline(true)
      }
    }

    return { localId, dbRecordId, dbOnline: online }
  }

  /**
   * 将MySQL扁平行记录转换为前端统一的记录结构
   */
  mapDbRecord(row) {
    return {
      id: row.record_id,
      dbRecordId: row.record_id,
      timestamp: row.created_at || new Date().toISOString(),
      scenarioName: row.scenario_name || '未命名场景',
      source: 'mysql',
      params: {
        albedo_pv: Number(row.albedo_pv),
        coverage_ratio: Number(row.coverage_ratio),
        pv_efficiency: Number(row.pv_efficiency),
        albedo_land: Number(row.albedo_land),
        albedo_ocean: Number(row.albedo_ocean),
        co2_current: Number(row.co2_current),
        initial_temp: Number(row.initial_temp),
        simulation_years: Number(row.simulation_years)
      },
      results: {
        baseline: {
          equilibrium_temp: Number(row.baseline_equilibrium_temp),
          planetary_albedo: Number(row.baseline_planetary_albedo)
        },
        pv_scenario: {
          equilibrium_temp: Number(row.pv_equilibrium_temp),
          planetary_albedo: Number(row.pv_planetary_albedo),
          co2_reduction: Number(row.pv_co2_reduction)
        },
        comparison: {
          temperature_change: Number(row.temperature_change),
          albedo_change: Number(row.albedo_change),
          cooling_effect: !!row.cooling_effect,
          heat_island_effect: Number(row.heat_island_effect),
          cooling_efficiency: Number(row.cooling_efficiency)
        }
      },
      metadata: {
        createdAt: row.created_at,
        tags: row.tags ? String(row.tags).split(',') : []
      }
    }
  }

  /**
   * 获取历史记录（数据库在线时合并MySQL与本地记录）
   * 合并规则：本地已同步的记录（有dbRecordId且在库中）以本地为准（含完整时间序列），
   * 数据库独有的记录补充进来，本地未同步的记录保留
   * @returns {Promise<Array>}
   */
  async getHistory(filters = {}) {
    const localHistory = resultStorage.getHistory(filters)
    const online = await this.isDbOnline()
    if (!online) {
      return localHistory.map(r => ({ ...r, source: 'local' }))
    }

    try {
      const data = await mysqlDB.getSimulations({ page: 1, perPage: 500 })
      const dbRecords = (data?.simulations || data || []).map(row => this.mapDbRecord(row))
      const dbIds = new Set(dbRecords.map(r => r.dbRecordId))

      // 本地已同步且库中存在的记录：以本地为准
      const syncedLocal = localHistory.filter(r => r.dbRecordId && dbIds.has(r.dbRecordId))
      const localOnly = localHistory.filter(r => !r.dbRecordId)
      const localDbIds = new Set(localHistory.map(r => r.dbRecordId).filter(Boolean))
      const dbOnly = dbRecords.filter(r => !localDbIds.has(r.dbRecordId))

      const merged = [...syncedLocal, ...localOnly, ...dbOnly]
      merged.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      return merged
    } catch (error) {
      console.warn('读取MySQL历史记录失败，回退到本地存储:', error.message)
      await this.isDbOnline(true)
      return localHistory.map(r => ({ ...r, source: 'local' }))
    }
  }

  /**
   * 删除记录（本地与数据库同步删除）
   * @param {string} id - 记录ID（本地ID或数据库record_id）
   * @returns {Promise<boolean>}
   */
  async deleteRecord(id) {
    const record = resultStorage.getResultById(id)
    const dbRecordId = record?.dbRecordId || (String(id).startsWith('sim_') ? id : null)

    // 本地删除（id可能是数据库记录ID，本地没有对应记录时忽略）
    resultStorage.deleteResult(id)

    if (dbRecordId) {
      const online = await this.isDbOnline()
      if (online) {
        try {
          await mysqlDB.deleteSimulation(dbRecordId)
        } catch (error) {
          console.warn('从MySQL删除记录失败:', error.message)
          return false
        }
      }
    }
    return true
  }

  /**
   * 获取数据库统计信息（离线时返回null）
   */
  async getDbStatistics() {
    const online = await this.isDbOnline()
    if (!online) return null
    try {
      return await mysqlDB.getStatistics()
    } catch {
      return null
    }
  }
}

export default new DataService()
