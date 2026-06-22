<template>
  <div class="history-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">📋 历史记录管理</h1>
      <p class="page-subtitle">查看和管理所有模拟计算的历史记录</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="history-content">
      <!-- 左侧：筛选和搜索 -->
      <div class="filter-panel">
        <div class="panel-section">
          <h3 class="section-title">🔍 筛选条件</h3>

          <!-- 搜索框 -->
          <div class="filter-group">
            <label class="filter-label">搜索记录</label>
            <div class="search-box">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="输入关键词..."
                class="search-input"
              />
              <span class="search-icon">🔍</span>
            </div>
          </div>

          <!-- 时间范围 -->
          <div class="filter-group">
            <label class="filter-label">时间范围</label>
            <select v-model="timeRange" class="filter-select">
              <option value="all">全部时间</option>
              <option value="today">今天</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="year">今年</option>
            </select>
          </div>

          <!-- 模拟类型 -->
          <div class="filter-group">
            <label class="filter-label">模拟类型</label>
            <select v-model="selectedType" class="filter-select">
              <option value="all">全部类型</option>
              <option value="thermal">热效应模拟</option>
              <option value="electrical">电力模拟</option>
              <option value="combined">综合模拟</option>
              <option value="scenario">情景分析</option>
            </select>
          </div>

          <!-- 状态筛选 -->
          <div class="filter-group">
            <label class="filter-label">状态</label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input v-model="statusFilter" value="completed" type="checkbox" />
                <span>已完成</span>
              </label>
              <label class="checkbox-item">
                <input v-model="statusFilter" value="running" type="checkbox" />
                <span>运行中</span>
              </label>
              <label class="checkbox-item">
                <input v-model="statusFilter" value="failed" type="checkbox" />
                <span>失败</span>
              </label>
            </div>
          </div>

          <!-- 排序方式 -->
          <div class="filter-group">
            <label class="filter-label">排序方式</label>
            <select v-model="sortBy" class="filter-select">
              <option value="date_desc">时间 (新→旧)</option>
              <option value="date_asc">时间 (旧→新)</option>
              <option value="name_asc">名称 (A→Z)</option>
              <option value="name_desc">名称 (Z→A)</option>
              <option value="duration_desc">耗时 (长→短)</option>
            </select>
          </div>

          <!-- 操作按钮 -->
          <div class="filter-actions">
            <button class="action-button primary" @click="applyFilters">
              🔄 应用筛选
            </button>
            <button class="action-button" @click="resetFilters">
              🗑️ 清空筛选
            </button>
            <button class="action-button" @click="exportHistory">
              📥 导出记录
            </button>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="panel-section">
          <h3 class="section-title">📊 统计信息</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ historyStats.total }}</span>
              <span class="stat-label">总记录</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ historyStats.completed }}</span>
              <span class="stat-label">已完成</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ historyStats.running }}</span>
              <span class="stat-label">运行中</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ historyStats.failed }}</span>
              <span class="stat-label">失败</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：历史记录列表 -->
      <div class="records-panel">
        <div class="panel-section">
          <div class="records-header">
            <h3 class="section-title">🗂️ 模拟记录</h3>
            <div class="records-actions">
              <span class="records-count">共 {{ filteredRecords.length }} 条记录</span>
              <button
                :class="['icon-button', { active: comparisonMode }]"
                @click="toggleComparisonMode"
                title="对比模式"
              >
                📊
              </button>
              <button class="icon-button" @click="toggleViewMode">
                {{ viewMode === 'grid' ? '☰' : '▦' }}
              </button>
            </div>
          </div>

          <!-- 对比控制条 -->
          <div v-if="comparisonMode" class="comparison-bar">
            <div class="comparison-info">
              <span class="comparison-label">已选择:</span>
              <span class="comparison-count">{{ selectedForComparison.length }}/5</span>
              <div class="comparison-tags">
                <span
                  v-for="item in selectedForComparison"
                  :key="item.id"
                  class="comparison-tag"
                >
                  {{ item.name }}
                  <button @click="toggleComparisonSelection(item)" class="tag-close">×</button>
                </span>
              </div>
            </div>
            <div class="comparison-actions">
              <button
                class="comparison-button"
                :disabled="selectedForComparison.length < 2"
                @click="runComparison"
              >
                📊 开始对比
              </button>
              <button class="comparison-button secondary" @click="toggleComparisonMode">
                取消
              </button>
            </div>
          </div>

          <!-- 对比结果面板 -->
          <div v-if="comparisonResult" class="comparison-result-panel">
            <h4 class="comparison-result-title">📊 对比分析结果</h4>
            <div class="comparison-results-grid">
              <div class="comparison-result-item">
                <span class="comparison-result-label">最佳降温效果</span>
                <span class="comparison-result-value success">
                  {{ getResultName(comparisonResult.analysis.bestCooling) }}
                </span>
              </div>
              <div class="comparison-result-item">
                <span class="comparison-result-label">最大CO₂减排</span>
                <span class="comparison-result-value success">
                  {{ getResultName(comparisonResult.analysis.bestCO2Reduction) }}
                </span>
              </div>
              <div class="comparison-result-item">
                <span class="comparison-result-label">最高冷却效率</span>
                <span class="comparison-result-value success">
                  {{ getResultName(comparisonResult.analysis.bestEfficiency) }}
                </span>
              </div>
            </div>

            <div class="comparison-table">
              <table>
                <thead>
                  <tr>
                    <th>场景名称</th>
                    <th>温度变化</th>
                    <th>CO₂减排</th>
                    <th>冷却效率</th>
                    <th>反照率</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="result in comparisonResult.results" :key="result.id">
                    <td>{{ result.scenarioName }}</td>
                    <td :class="{ 'text-cyan': result.temperatureChange < 0 }">
                      {{ result.temperatureChange?.toFixed(4) }}°C
                    </td>
                    <td class="text-green">{{ result.co2Reduction?.toFixed(4) }} ppm</td>
                    <td>{{ result.coolingEfficiency?.toFixed(4) }}%</td>
                    <td>{{ result.albedoChange?.toFixed(4) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 网格视图 -->
          <div v-if="viewMode === 'grid'" class="records-grid">
            <div
              v-for="record in filteredRecords"
              :key="record.id"
              :class="['record-card', record.status]"
              @click="selectRecord(record)"
            >
              <!-- 对比模式选择框 -->
              <div v-if="comparisonMode" class="record-checkbox">
                <input
                  type="checkbox"
                  :checked="isSelectedForComparison(record)"
                  @click.stop="toggleComparisonSelection(record)"
                />
              </div>

              <div class="record-header">
                <div class="record-title">{{ record.name }}</div>
                <div :class="['record-status', record.status]">
                  {{ getStatusText(record.status) }}
                </div>
              </div>

              <div class="record-info">
                <div class="info-item">
                  <span class="info-icon">📅</span>
                  <span class="info-text">{{ record.date }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">⏱️</span>
                  <span class="info-text">{{ record.duration }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">🎯</span>
                  <span class="info-text">{{ record.type }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">📍</span>
                  <span class="info-text">{{ record.location }}</span>
                </div>
              </div>

              <div v-if="record.status === 'completed'" class="record-results">
                <div class="result-item">
                  <span class="result-label">温度变化</span>
                  <span :class="['result-value', record.tempChange >= 0 ? 'warm' : 'cool']">
                    {{ record.tempChange >= 0 ? '+' : '' }}{{ record.tempChange }}°C
                  </span>
                </div>
                <div class="result-item">
                  <span class="result-label">热岛强度</span>
                  <span class="result-value neutral">{{ record.heatIntensity }}°C</span>
                </div>
              </div>

              <div class="record-actions">
                <button class="record-action" @click.stop="viewDetails(record)">
                  👁️ 详情
                </button>
                <button class="record-action" @click.stop="duplicateRecord(record)">
                  📋 复制
                </button>
                <button class="record-action danger" @click.stop="deleteRecord(record)">
                  🗑️ 删除
                </button>
              </div>
            </div>
          </div>

          <!-- 列表视图 -->
          <div v-else class="records-list">
            <div
              v-for="record in filteredRecords"
              :key="record.id"
              :class="['record-row', record.status]"
              @click="selectRecord(record)"
            >
              <div class="row-main">
                <div class="row-title">{{ record.name }}</div>
                <div class="row-meta">
                  <span>{{ record.date }}</span>
                  <span>{{ record.duration }}</span>
                  <span>{{ record.type }}</span>
                </div>
              </div>
              <div :class="['row-status', record.status]">
                {{ getStatusText(record.status) }}
              </div>
              <div class="row-results">
                <span v-if="record.status === 'completed'" class="row-result">
                  ΔT: {{ record.tempChange }}°C
                </span>
                <span v-if="record.status === 'completed'" class="row-result">
                  热岛: {{ record.heatIntensity }}°C
                </span>
              </div>
              <div class="row-actions">
                <button class="row-action" @click.stop="viewDetails(record)">详情</button>
                <button class="row-action" @click.stop="duplicateRecord(record)">复制</button>
                <button class="row-action danger" @click.stop="deleteRecord(record)">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页控制 -->
        <div class="pagination">
          <button class="page-button" :disabled="currentPage === 1" @click="currentPage--">
            ◀ 上一页
          </button>
          <div class="page-numbers">
            <button
              v-for="page in visiblePages"
              :key="page"
              :class="['page-number', { active: page === currentPage }]"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
          </div>
          <button class="page-button" :disabled="currentPage === totalPages" @click="currentPage++">
            下一页 ▶
          </button>
          <div class="page-info">
            第 {{ currentPage }} / {{ totalPages }} 页
          </div>
        </div>
      </div>

      <!-- 右侧：详情面板 -->
      <div class="details-panel">
        <div v-if="selectedRecord" class="panel-section">
          <h3 class="section-title">📄 模拟详情</h3>

          <!-- 基本信息 -->
          <div class="detail-group">
            <h4 class="detail-subtitle">基本信息</h4>
            <div class="detail-info">
              <div class="detail-item">
                <span class="detail-label">模拟名称</span>
                <span class="detail-value">{{ selectedRecord.name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ selectedRecord.createdAt }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">执行时间</span>
                <span class="detail-value">{{ selectedRecord.duration }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">模拟类型</span>
                <span class="detail-value">{{ selectedRecord.type }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">地理位置</span>
                <span class="detail-value">{{ selectedRecord.location }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">状态</span>
                <span :class="['detail-value', 'status-' + selectedRecord.status]">
                  {{ getStatusText(selectedRecord.status) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 参数配置 -->
          <div class="detail-group">
            <h4 class="detail-subtitle">参数配置</h4>
            <div class="params-grid">
              <div class="param-item">
                <span class="param-label">反照率</span>
                <span class="param-value">{{ selectedRecord.params.albedo }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">覆盖面积</span>
                <span class="param-value">{{ selectedRecord.params.coverage }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">CO2浓度</span>
                <span class="param-value">{{ selectedRecord.params.co2 }} ppm</span>
              </div>
              <div class="param-item">
                <span class="param-label">模拟年份</span>
                <span class="param-value">{{ selectedRecord.params.years }}年</span>
              </div>
            </div>
          </div>

          <!-- 结果数据 -->
          <div v-if="selectedRecord.status === 'completed'" class="detail-group">
            <h4 class="detail-subtitle">模拟结果</h4>
            <div class="results-grid">
              <div class="result-card">
                <span class="result-card-title">温度变化</span>
                <span :class="['result-card-value', selectedRecord.tempChange >= 0 ? 'warm' : 'cool']">
                  {{ selectedRecord.tempChange >= 0 ? '+' : '' }}{{ selectedRecord.tempChange }}°C
                </span>
              </div>
              <div class="result-card">
                <span class="result-card-title">热岛强度</span>
                <span class="result-card-value neutral">{{ selectedRecord.heatIntensity }}°C</span>
              </div>
              <div class="result-card">
                <span class="result-card-title">冷却效率</span>
                <span class="result-card-value good">{{ selectedRecord.coolingEff }}%</span>
              </div>
              <div class="result-card">
                <span class="result-card-title">碳减排</span>
                <span class="result-card-value good">{{ selectedRecord.carbonRed }}Mt</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <button class="detail-button primary" @click="rerunSimulation">
              🔄 重新运行
            </button>
            <button class="detail-button" @click="exportRecord">
              📥 导出结果
            </button>
            <button class="detail-button" @click="shareRecord">
              🔗 分享记录
            </button>
            <button class="detail-button danger" @click="deleteSelectedRecord">
              🗑️ 删除记录
            </button>
          </div>
        </div>

        <div v-else class="no-selection">
          <div class="no-selection-content">
            <span class="no-selection-icon">📋</span>
            <p>选择一条记录查看详情</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useSimulation } from '@/composables/useSimulation'

// 使用模拟状态和存储功能
const {
  getResultHistory,
  addToFavorites,
  getFavorites,
  exportResult,
  compareResults,
  deleteResult
} = useSimulation()

// 筛选条件
const searchQuery = ref('')
const timeRange = ref('all')
const selectedType = ref('all')
const statusFilter = ref(['completed', 'running'])
const sortBy = ref('date_desc')
const viewMode = ref('grid')

// 分页
const currentPage = ref(1)
const pageSize = 12

// 选中的记录
const selectedRecord = ref(null)
const selectedForComparison = ref([])
const comparisonMode = ref(false)
const comparisonResult = ref(null)

// 从存储加载历史记录
const historyRecords = ref([])
const loadingHistory = ref(false)

// 加载历史记录
const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const rawHistory = getResultHistory()
    historyRecords.value = rawHistory.map(record => ({
      id: record.id,
      name: record.scenarioName,
      date: new Date(record.timestamp).toLocaleDateString('zh-CN'),
      createdAt: new Date(record.timestamp).toLocaleString('zh-CN'),
      duration: '< 1秒',
      type: 'thermal',
      location: '光伏部署区',
      status: 'completed',
      tempChange: record.results.comparison?.temperature_change || 0,
      heatIntensity: record.results.comparison?.heat_island_effect || 0,
      coolingEff: record.results.comparison?.cooling_efficiency || 0,
      carbonRed: record.results.pv_scenario?.co2_reduction || 0,
      params: record.params,
      metadata: record.metadata,
      rawRecord: record
    }))
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// 组件挂载时加载历史
onMounted(() => {
  loadHistory()
})

// 统计信息
const historyStats = computed(() => {
  const total = historyRecords.value.length
  const completed = historyRecords.value.filter(r => r.status === 'completed').length
  const running = historyRecords.value.filter(r => r.status === 'running').length
  const failed = historyRecords.value.filter(r => r.status === 'failed').length

  return { total, completed, running, failed }
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let records = [...historyRecords.value]

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    records = records.filter(r =>
      r.name.toLowerCase().includes(query) ||
      r.location.toLowerCase().includes(query) ||
      r.type.toLowerCase().includes(query)
    )
  }

  // 类型筛选
  if (selectedType.value !== 'all') {
    records = records.filter(r => r.type === selectedType.value)
  }

  // 状态筛选
  if (statusFilter.value.length > 0) {
    records = records.filter(r => statusFilter.value.includes(r.status))
  }

  // 排序
  records.sort((a, b) => {
    switch (sortBy.value) {
      case 'date_desc':
        return new Date(b.createdAt) - new Date(a.createdAt)
      case 'date_asc':
        return new Date(a.createdAt) - new Date(b.createdAt)
      case 'name_asc':
        return a.name.localeCompare(b.name, 'zh-CN')
      case 'name_desc':
        return b.name.localeCompare(a.name, 'zh-CN')
      default:
        return 0
    }
  })

  return records
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / pageSize)
})

// 可见页码
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    pending: '等待中'
  }
  return statusMap[status] || status
}

// 应用筛选
const applyFilters = () => {
  currentPage.value = 1
  console.log('应用筛选条件')
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  timeRange.value = 'all'
  selectedType.value = 'all'
  statusFilter.value = ['completed', 'running']
  sortBy.value = 'date_desc'
  currentPage.value = 1
}

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

// 选择记录
const selectRecord = (record) => {
  selectedRecord.value = record
}

// 查看详情
const viewDetails = (record) => {
  selectedRecord.value = record
  // 可以添加打开详情模态框的逻辑
}

// 复制记录
const duplicateRecord = (record) => {
  const newRecord = {
    ...record,
    id: Date.now(),
    name: `${record.name} (副本)`,
    date: new Date().toISOString().split('T')[0],
    createdAt: new Date().toLocaleString('zh-CN'),
    status: 'pending'
  }
  historyRecords.value.unshift(newRecord)
  console.log('复制记录:', record.name)
}

// 删除记录
const deleteRecord = async (record) => {
  if (!confirm(`确定要删除记录 "${record.name}" 吗？`)) {
    return
  }

  try {
    const success = deleteResult(record.id)
    if (success) {
      // 从本地列表中移除
      const index = historyRecords.value.findIndex(r => r.id === record.id)
      if (index > -1) {
        historyRecords.value.splice(index, 1)
      }
      // 清除选中状态
      if (selectedRecord.value?.id === record.id) {
        selectedRecord.value = null
      }
      console.log('删除成功:', record.name)
    } else {
      alert('删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败: ' + error.message)
  }
}

// 删除选中的记录
const deleteSelectedRecord = () => {
  if (selectedRecord.value) {
    deleteRecord(selectedRecord.value)
  }
}

// 重新运行模拟
const rerunSimulation = () => {
  if (selectedRecord.value) {
    console.log('重新运行模拟:', selectedRecord.value.name)
    // 这里可以添加重新运行模拟的逻辑
  }
}

// 导出记录
const exportRecord = () => {
  if (selectedRecord.value) {
    try {
      // 导出为JSON格式
      const blob = exportResult(selectedRecord.value.id, 'json')
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `simulation-${selectedRecord.value.id}.json`
      a.click()
      URL.revokeObjectURL(url)
      console.log('导出成功:', selectedRecord.value.name)
    } catch (error) {
      console.error('导出失败:', error)
      alert('导出失败: ' + error.message)
    }
  }
}

// 导出历史记录
const exportHistory = () => {
  try {
    // 批量导出当前筛选的记录
    const selectedIds = filteredRecords.value.map(r => r.id)
    if (selectedIds.length === 0) {
      alert('没有可导出的记录')
      return
    }

    // 创建CSV格式导出
    const headers = ['ID', '场景名称', '时间', '温度变化', 'CO2减排', '冷却效率', '反照率', '覆盖率', '光伏效率']
    const rows = filteredRecords.value.map(r => [
      r.id,
      r.name,
      r.date,
      r.tempChange?.toFixed(4) || '0',
      r.carbonRed?.toFixed(4) || '0',
      r.coolingEff?.toFixed(4) || '0',
      r.params.albedo_pv?.toFixed(4) || '0',
      r.params.coverage_ratio || '0',
      r.params.pv_efficiency?.toFixed(4) || '0'
    ])

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `simulation-history-${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
    console.log('批量导出成功')
  } catch (error) {
    console.error('批量导出失败:', error)
    alert('批量导出失败: ' + error.message)
  }
}

// 分享记录
const shareRecord = () => {
  if (selectedRecord.value) {
    // 复制记录信息到剪贴板
    const shareText = `
光伏气候效应模拟结果
场景: ${selectedRecord.value.name}
时间: ${selectedRecord.value.createdAt}
温度变化: ${selectedRecord.value.tempChange?.toFixed(4)}°C
CO2减排: ${selectedRecord.value.carbonRed?.toFixed(4)} ppm
冷却效率: ${selectedRecord.value.coolingEff?.toFixed(4)}%
    `.trim()

    navigator.clipboard.writeText(shareText).then(() => {
      alert('记录信息已复制到剪贴板')
    }).catch(err => {
      console.error('复制失败:', err)
      alert('复制失败')
    })
  }
}

// 切换对比模式
const toggleComparisonMode = () => {
  comparisonMode.value = !comparisonMode.value
  selectedForComparison.value = []
  comparisonResult.value = null
}

// 选择/取消选择对比记录
const toggleComparisonSelection = (record) => {
  const index = selectedForComparison.value.findIndex(r => r.id === record.id)
  if (index > -1) {
    selectedForComparison.value.splice(index, 1)
  } else {
    if (selectedForComparison.value.length >= 5) {
      alert('最多只能选择5条记录进行对比')
      return
    }
    selectedForComparison.value.push(record)
  }
}

// 执行对比
const runComparison = () => {
  if (selectedForComparison.value.length < 2) {
    alert('请至少选择2条记录进行对比')
    return
  }

  try {
    const result = compareResults(selectedForComparison.value.map(r => r.id))
    comparisonResult.value = result
    console.log('对比结果:', result)
  } catch (error) {
    console.error('对比失败:', error)
    alert('对比失败: ' + error.message)
  }
}

// 检查记录是否被选中用于对比
const isSelectedForComparison = (record) => {
  return selectedForComparison.value.some(r => r.id === record.id)
}

// 根据ID获取结果名称
const getResultName = (id) => {
  const result = comparisonResult.value?.results.find(r => r.id === id)
  return result?.scenarioName || '未知'
}
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  height: 100%;
  overflow-y: auto;
}

.page-header {
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-cyan), var(--color-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
}

.history-content {
  display: grid;
  grid-template-columns: 280px 1fr 360px;
  gap: var(--spacing-md);
  flex: 1;
  min-height: 0;
}

.panel-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-group {
  margin-bottom: var(--spacing-md);
}

.filter-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
}

.search-box {
  position: relative;
}

.search-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  padding-right: 32px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
}

.search-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.filter-select {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.action-button {
  padding: var(--spacing-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.action-button.primary {
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-color: transparent;
  color: var(--bg-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.stat-item {
  text-align: center;
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.records-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.records-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

.icon-button {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

.record-card {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.record-card:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-blue);
}

.record-card.completed {
  border-left: 3px solid var(--color-green);
}

.record-card.running {
  border-left: 3px solid var(--color-blue);
}

.record-card.failed {
  border-left: 3px solid var(--color-red);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.record-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.record-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  white-space: nowrap;
}

.record-status.completed {
  background: rgba(0, 255, 157, 0.2);
  color: var(--color-green);
}

.record-status.running {
  background: rgba(74, 158, 255, 0.2);
  color: var(--color-blue);
}

.record-status.failed {
  background: rgba(255, 71, 87, 0.2);
  color: var(--color-red);
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 12px;
}

.info-icon {
  color: var(--text-tertiary);
}

.info-text {
  color: var(--text-secondary);
}

.record-results {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.result-label {
  color: var(--text-tertiary);
}

.result-value {
  font-weight: 600;
  color: var(--color-cyan);
}

.result-value.cool {
  color: var(--color-blue);
}

.result-value.warm {
  color: var(--color-red);
}

.record-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.record-action {
  flex: 1;
  padding: var(--spacing-xs);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.record-action:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.record-action.danger:hover {
  border-color: var(--color-red);
  color: var(--color-red);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.record-row {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr auto;
  gap: var(--spacing-md);
  align-items: center;
  padding: var(--spacing-md);
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.record-row:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.record-row.completed {
  border-left: 3px solid var(--color-green);
}

.record-row.running {
  border-left: 3px solid var(--color-blue);
}

.record-row.failed {
  border-left: 3px solid var(--color-red);
}

.row-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.row-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.row-meta {
  display: flex;
  gap: var(--spacing-md);
  font-size: 12px;
  color: var(--text-tertiary);
}

.row-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  text-align: center;
}

.row-status.completed {
  background: rgba(0, 255, 157, 0.2);
  color: var(--color-green);
}

.row-status.running {
  background: rgba(74, 158, 255, 0.2);
  color: var(--color-blue);
}

.row-status.failed {
  background: rgba(255, 71, 87, 0.2);
  color: var(--color-red);
}

.row-results {
  display: flex;
  gap: var(--spacing-md);
  font-size: 12px;
}

.row-result {
  color: var(--text-secondary);
}

.row-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.row-action {
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
}

.row-action:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.row-action.danger:hover {
  border-color: var(--color-red);
  color: var(--color-red);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.page-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: var(--spacing-xs);
}

.page-number {
  min-width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-number:hover {
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.page-number.active {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: var(--bg-primary);
}

.page-info {
  font-size: 12px;
  color: var(--text-tertiary);
}

.detail-group {
  margin-bottom: var(--spacing-lg);
}

.detail-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-primary);
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.detail-label {
  color: var(--text-tertiary);
}

.detail-value {
  color: var(--text-primary);
  font-weight: 500;
}

.detail-value.status-completed {
  color: var(--color-green);
}

.detail-value.status-running {
  color: var(--color-blue);
}

.detail-value.status-failed {
  color: var(--color-red);
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  font-size: 12px;
}

.param-label {
  color: var(--text-tertiary);
}

.param-value {
  color: var(--color-cyan);
  font-weight: 600;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}

.result-card {
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  text-align: center;
}

.result-card-title {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-xs);
}

.result-card-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-cyan);
}

.result-card-value.cool {
  color: var(--color-blue);
}

.result-card-value.warm {
  color: var(--color-red);
}

.result-card-value.neutral {
  color: var(--color-green);
}

.result-card-value.good {
  color: var(--color-green);
}

.detail-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.detail-button {
  padding: var(--spacing-sm);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.detail-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.detail-button.primary {
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-color: transparent;
  color: var(--bg-primary);
}

.detail-button.danger:hover {
  border-color: var(--color-red);
  color: var(--color-red);
}

.no-selection {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
}

.no-selection-content {
  text-align: center;
  color: var(--text-tertiary);
}

.no-selection-icon {
  font-size: 48px;
  display: block;
  margin-bottom: var(--spacing-md);
}

.no-selection-content p {
  font-size: 14px;
  margin: 0;
}

/* 对比模式样式 */
.icon-button.active {
  background: var(--color-cyan);
  border-color: var(--color-cyan);
  color: var(--bg-primary);
}

.comparison-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--bg-tertiary);
  border: 1px solid var(--color-cyan);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
}

.comparison-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
}

.comparison-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

.comparison-count {
  font-size: 13px;
  color: var(--color-cyan);
  font-weight: 700;
}

.comparison-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
  max-width: 600px;
}

.comparison-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: rgba(74, 158, 255, 0.2);
  border: 1px solid var(--color-cyan);
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--color-cyan);
}

.tag-close {
  background: none;
  border: none;
  color: var(--color-cyan);
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.tag-close:hover {
  color: var(--color-red);
}

.comparison-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.comparison-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-cyan);
  border: none;
  border-radius: var(--radius-md);
  color: var(--bg-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.comparison-button:hover:not(:disabled) {
  background: var(--color-blue);
}

.comparison-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comparison-button.secondary {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  color: var(--text-primary);
}

.comparison-button.secondary:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.comparison-result-panel {
  background: var(--bg-tertiary);
  border: 1px solid var(--color-cyan);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.comparison-result-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
}

.comparison-results-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.comparison-result-item {
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  text-align: center;
}

.comparison-result-label {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-xs);
}

.comparison-result-value {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-cyan);
}

.comparison-result-value.success {
  color: var(--color-green);
}

.comparison-table {
  margin-top: var(--spacing-md);
  overflow-x: auto;
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.comparison-table th {
  background: var(--bg-tertiary);
  color: var(--color-cyan);
  font-weight: 600;
  text-align: left;
  padding: var(--spacing-sm);
  border-bottom: 2px solid var(--border-primary);
}

.comparison-table td {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
}

.comparison-table tr:hover {
  background: var(--bg-hover);
}

.text-cyan {
  color: var(--color-cyan);
}

.text-green {
  color: var(--color-green);
}

.record-checkbox {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  z-index: 2;
}

.record-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-cyan);
}
</style>
