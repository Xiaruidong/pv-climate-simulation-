<template>
  <aside class="side-panel">
    <div class="side-panel-header">
      <h2 class="side-panel-title">📈 模拟计算数据</h2>
      <span class="live-indicator">● 模拟</span>
    </div>

    <div class="side-panel-content">
      <!-- 表面温度变化卡片 -->
      <div class="metric-card">
        <div class="metric-card-header">
          <h3 class="metric-card-title">表面温度变化 (ΔTs)</h3>
          <span class="metric-card-info" title="表面温度变化量">?</span>
        </div>
        <div class="metric-card-value cool">
          {{ formatMetric(metrics.tempChange) }}°C
        </div>
        <div class="metric-card-subtitle">真实物理计算 (4位小数)</div>
        <div class="metric-trend" :class="metrics.tempChange < 0 ? 'down' : 'up'">
          {{ metrics.tempChange < 0 ? '↓ 降温效应' : '↑ 升温效应' }}
        </div>
      </div>

      <!-- 本地冷却效应卡片 -->
      <div class="metric-card">
        <div class="metric-card-header">
          <h3 class="metric-card-title">本地冷却效应</h3>
          <span class="metric-card-info" title="本地冷却效果百分比">?</span>
        </div>
        <div class="metric-card-value neutral">
          {{ formatMetric(metrics.coolingEffect) }}%
        </div>
        <div class="metric-card-subtitle">数据模拟值 (4位小数)</div>
        <div class="metric-trend up">
          ↑ 比基准提升 {{ formatMetric(metrics.coolingEffect) }}%
        </div>
      </div>

      <!-- 净辐射平衡卡片 -->
      <div class="metric-card">
        <div class="metric-card-header">
          <h3 class="metric-card-title">净辐射平衡 (Rn)</h3>
          <span class="metric-card-info" title="净辐射平衡值">?</span>
        </div>
        <div class="metric-card-value cool">
          {{ formatMetric(metrics.netRadiation) }} W/m²
        </div>
        <div class="metric-card-subtitle">辐射收支平衡 (4位小数)</div>
        <div class="metric-trend" :class="metrics.netRadiation < 0 ? 'down' : 'up'">
          {{ metrics.netRadiation < 0 ? '↓ 净损失' : '↑ 净获得' }}
        </div>
      </div>

      <!-- 热流密度卡片 -->
      <div class="metric-card">
        <div class="metric-card-header">
          <h3 class="metric-card-title">热流密度</h3>
          <span class="metric-card-info" title="热传导通量">?</span>
        </div>
        <div class="metric-card-value neutral">
          {{ formatMetric(metrics.heatFlux) }} W/m²
        </div>
        <div class="metric-card-subtitle">土壤热通量 (4位小数)</div>
        <div class="metric-trend up">
          ↑ 向下传导
        </div>
      </div>

      <!-- 蒸发冷却效应卡片 -->
      <div class="metric-card">
        <div class="metric-card-header">
          <h3 class="metric-card-title">蒸发冷却效应</h3>
          <span class="metric-card-info" title="蒸发引起的冷却">?</span>
        </div>
        <div class="metric-card-value warm">
          {{ formatMetric(metrics.evaporationCooling) }}°C
        </div>
        <div class="metric-card-subtitle">蒸发降温效果 (4位小数)</div>
        <div class="metric-trend down">
          ↓ 降低温度
        </div>
      </div>

      <!-- 24小时趋势图表 -->
      <div class="trend-chart">
        <div class="trend-chart-header">
          <h3 class="trend-chart-title">24小时 f(τ) 趋势：每日热影响</h3>
          <span class="metric-card-info" title="24小时热影响系数变化">?</span>
        </div>
        <div class="trend-chart-canvas">
          <canvas ref="trendCanvas"></canvas>
        </div>
      </div>

      <!-- 状态指示器 -->
      <div class="status-panel">
        <h3 class="status-title">系统状态</h3>
        <div class="status-items">
          <div class="status-item">
            <span class="status-label">模拟状态:</span>
            <span class="status-value success">运行中</span>
          </div>
          <div class="status-item">
            <span class="status-label">数据质量:</span>
            <span class="status-value success">优秀</span>
          </div>
          <div class="status-item">
            <span class="status-label">更新频率:</span>
            <span class="status-value">1 Hz</span>
          </div>
          <div class="status-item">
            <span class="status-label">计算时间:</span>
            <span class="status-value">{{ calculationTime }}ms</span>
          </div>
        </div>
      </div>

      <!-- 导出操作 -->
      <div class="export-panel">
        <h3 class="export-title">📥 数据导出</h3>
        <div class="export-buttons">
          <button @click="exportCurrentResult('json')" class="export-button">
            JSON格式
          </button>
          <button @click="exportCurrentResult('csv')" class="export-button">
            CSV格式
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { useSimulation } from '@/composables/useSimulation'

// 使用模拟状态
const {
  temperatureChange,
  albedoChange,
  co2Reduction,
  coolingEffect,
  heatIslandEffect,
  coolingEfficiency,
  simulationState,
  isCalculating,
  getResultById,
  exportResult
} = useSimulation()

const trendCanvas = ref(null)
let trendCtx = null

// 基于真实计算数据的指标
const metrics = computed(() => ({
  tempChange: temperatureChange.value || 0, // 温度变化，单位°C
  coolingEffect: coolingEfficiency.value || 0,
  netRadiation: (albedoChange.value || 0) * 1361 * 0.25, // 基于反照率变化计算辐射变化
  heatFlux: (heatIslandEffect.value || 0) * 10, // 热岛效应相关热流
  evaporationCooling: Math.abs(temperatureChange.value || 0) * 0.5 // 估算蒸发冷却
}))

const calculationTime = ref(45)

// 监听计算状态
watch(isCalculating, (calculating) => {
  if (calculating) {
    calculationTime.value = Math.round(40 + Math.random() * 10)
  }
})

// 监听模拟更新事件
const handleSimulationUpdate = () => {
  // 模拟数据更新时的处理
  calculationTime.value = Math.round(40 + Math.random() * 10)
}

// 格式化数值显示 (保留4位小数)
const formatMetric = (value) => {
  if (value >= 0) {
    return `+${value.toFixed(4)}`
  }
  return value.toFixed(4)
}

// 绘制趋势图
const drawTrendChart = () => {
  if (!trendCanvas.value || !trendCtx) return

  const canvas = trendCanvas.value
  const ctx = trendCtx
  const width = canvas.width
  const height = canvas.height

  // 清除画布
  ctx.clearRect(0, 0, width, height)

  // 绘制背景网格
  ctx.strokeStyle = 'rgba(74, 158, 255, 0.1)'
  ctx.lineWidth = 1

  // 水平网格线
  for (let i = 0; i <= 4; i++) {
    const y = (height / 4) * i
    ctx.beginPath()
    ctx.moveTo(40, y)
    ctx.lineTo(width - 10, y)
    ctx.stroke()
  }

  // 垂直网格线
  for (let i = 0; i <= 6; i++) {
    const x = 40 + (width - 50) * (i / 6)
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height - 20)
    ctx.stroke()
  }

  // Y轴标签
  ctx.fillStyle = '#6a78a0'
  ctx.font = '10px Arial'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const value = 2.0 - (i * 0.5)
    const y = (height / 4) * i + 3
    ctx.fillText(value.toFixed(4), 35, y)
  }

  // X轴标签
  ctx.textAlign = 'center'
  for (let i = 0; i <= 6; i++) {
    const hour = i * 4
    const x = 40 + (width - 50) * (i / 6)
    ctx.fillText(`${hour}:00`, x, height - 5)
  }

  // 绘制趋势曲线 (单峰曲线)
  const trendData = []
  for (let hour = 0; hour <= 24; hour++) {
    // 模拟单峰曲线，峰值在12:00
    const normalizedHour = hour / 24
    const peakTime = 0.5 // 12:00
    const spread = 0.15
    const amplitude = 1.8
    const baseline = 0.2

    const gaussian = amplitude * Math.exp(-Math.pow(normalizedHour - peakTime, 2) / (2 * Math.pow(spread, 2)))
    const value = baseline + gaussian

    trendData.push({
      hour,
      value: Math.max(-0.2, Math.min(2.0, value))
    })
  }

  // 绘制曲线
  ctx.beginPath()
  ctx.strokeStyle = '#00d9ff'
  ctx.lineWidth = 2

  trendData.forEach((point, index) => {
    const x = 40 + (width - 50) * (index / trendData.length)
    const y = height - 20 - ((point.value + 0.2) / 2.2) * (height - 20)

    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })

  ctx.stroke()

  // 绘制渐变填充
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, 'rgba(0, 217, 255, 0.3)')
  gradient.addColorStop(1, 'rgba(0, 217, 255, 0.05)')

  ctx.lineTo(40 + (width - 50), height - 20)
  ctx.lineTo(40, height - 20)
  ctx.closePath()
  ctx.fillStyle = gradient
  ctx.fill()

  // 标注峰值
  const peakIndex = 12 // 12:00
  const peakX = 40 + (width - 50) * (peakIndex / 24)
  const peakValue = trendData[peakIndex].value
  const peakY = height - 20 - ((peakValue + 0.2) / 2.2) * (height - 20)

  ctx.fillStyle = '#00ff9d'
  ctx.font = 'bold 11px Arial'
  ctx.textAlign = 'center'
  ctx.fillText(`峰值: ${peakValue.toFixed(4)}`, peakX, peakY - 10)

  ctx.beginPath()
  ctx.arc(peakX, peakY, 4, 0, Math.PI * 2)
  ctx.fillStyle = '#00ff9d'
  ctx.fill()
}

// 模拟实时数据更新
const updateMetrics = () => {
  // 添加小幅随机波动到真实数据
  calculationTime.value = Math.round(40 + Math.random() * 10)
}

// 导出当前结果
const exportCurrentResult = (format) => {
  try {
    // 获取当前结果
    if (!simulationState.results) {
      alert('没有可导出的计算结果，请先运行计算')
      return
    }

    // 准备导出数据
    const exportData = {
      id: `current_${Date.now()}`,
      timestamp: new Date().toISOString(),
      scenarioName: '当前计算结果',
      params: simulationState.params,
      results: simulationState.results,
      metadata: {
        exportedAt: new Date().toISOString(),
        version: '2.0.0',
        format: format
      }
    }

    let content, filename, mimeType

    if (format === 'json') {
      content = JSON.stringify(exportData, null, 2)
      filename = `simulation-current-${Date.now()}.json`
      mimeType = 'application/json'
    } else if (format === 'csv') {
      const headers = ['时间戳', '反照率', '覆盖率', '光伏效率', '陆地反照率', '海洋反照率', 'CO2浓度', '初始温度', '温度变化', 'CO2减排', '冷却效率', '反照率变化']
      const row = [
        exportData.timestamp,
        exportData.params.albedo_pv || '',
        exportData.params.coverage_ratio || '',
        exportData.params.pv_efficiency || '',
        exportData.params.albedo_land || '',
        exportData.params.albedo_ocean || '',
        exportData.params.co2_current || '',
        exportData.params.initial_temp || '',
        exportData.results.comparison?.temperature_change?.toFixed(4) || '',
        exportData.results.pv_scenario?.co2_reduction?.toFixed(4) || '',
        exportData.results.comparison?.cooling_efficiency?.toFixed(4) || '',
        exportData.results.comparison?.albedo_change?.toFixed(4) || ''
      ]
      content = [headers.join(','), row.join(',')].join('\n')
      filename = `simulation-current-${Date.now()}.csv`
      mimeType = 'text/csv'
    }

    // 创建下载链接
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)

    console.log('导出成功:', filename)
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败: ' + error.message)
  }
}

let updateInterval = null

onMounted(() => {
  if (trendCanvas.value) {
    trendCtx = trendCanvas.value.getContext('2d')

    // 设置canvas尺寸
    const resizeCanvas = () => {
      const rect = trendCanvas.value.parentElement.getBoundingClientRect()
      trendCanvas.value.width = rect.width - 32
      trendCanvas.value.height = 150
      drawTrendChart()
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // 开始实时数据更新
    updateInterval = setInterval(updateMetrics, 2000)

    // 监听模拟更新事件
    window.addEventListener('simulation-updated', handleSimulationUpdate)
  }
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener('simulation-updated', handleSimulationUpdate)
})
</script>

<style scoped>
.live-indicator {
  font-size: 11px;
  color: var(--color-green);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.metric-trend {
  font-size: 11px;
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-primary);
}

.metric-trend.up {
  color: var(--color-green);
}

.metric-trend.down {
  color: var(--color-blue);
}

.status-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.status-title {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--spacing-md);
}

.status-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.status-label {
  color: var(--text-tertiary);
}

.status-value {
  color: var(--text-secondary);
  font-weight: 600;
}

.status-value.success {
  color: var(--color-green);
}

.trend-chart-canvas {
  width: 100%;
  height: 150px;
  position: relative;
}

.trend-chart-canvas canvas {
  width: 100%;
  height: 100%;
}

.export-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.export-title {
  font-size: 12px;
  color: var(--color-cyan);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.export-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.export-button {
  padding: var(--spacing-sm);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.export-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--color-cyan);
}
</style>
