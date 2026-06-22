<template>
  <div class="simulation-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">🔬 高级模拟控制台</h1>
      <p class="page-subtitle">配置和运行详细的光伏热效应模拟</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="simulation-content">
      <!-- 左侧：模拟配置面板 -->
      <div class="config-panel">
        <div class="panel-section">
          <h3 class="section-title">⚙️ 模拟配置</h3>

          <!-- 模拟类型选择 -->
          <div class="config-group">
            <label class="config-label">模拟类型</label>
            <div class="button-group">
              <button
                v-for="type in simulationTypes"
                :key="type.id"
                :class="['type-button', { active: simulationConfig.type === type.id }]"
                @click="simulationConfig.type = type.id"
              >
                {{ type.name }}
              </button>
            </div>
          </div>

          <!-- 时间范围设置 -->
          <div class="config-group">
            <label class="config-label">模拟时间范围</label>
            <div class="time-range">
              <div class="time-input">
                <label>开始年份</label>
                <input v-model.number="simulationConfig.startYear" type="number" class="tech-input" />
              </div>
              <div class="time-input">
                <label>结束年份</label>
                <input v-model.number="simulationConfig.endYear" type="number" class="tech-input" />
              </div>
              <div class="time-input">
                <label>时间步长</label>
                <select v-model="simulationConfig.timeStep" class="tech-select">
                  <option value="hourly">小时</option>
                  <option value="daily">天</option>
                  <option value="monthly">月</option>
                  <option value="yearly">年</option>
                </select>
              </div>
            </div>
          </div>

          <!-- 空间分辨率 -->
          <div class="config-group">
            <label class="config-label">空间分辨率</label>
            <select v-model="simulationConfig.resolution" class="tech-select">
              <option value="coarse">粗分辨率 (50km)</option>
              <option value="medium">中等分辨率 (10km)</option>
              <option value="fine">精细分辨率 (1km)</option>
              <option value="ultra">超高分辨率 (100m)</option>
            </select>
          </div>

          <!-- 输出选项 -->
          <div class="config-group">
            <label class="config-label">输出数据选项</label>
            <div class="checkbox-group">
              <label v-for="option in outputOptions" :key="option.id" class="checkbox-item">
                <input
                  v-model="simulationConfig.outputs"
                  :value="option.id"
                  type="checkbox"
                />
                <span>{{ option.name }}</span>
              </label>
            </div>
          </div>

          <!-- 高级设置 -->
          <div class="config-group">
            <details class="advanced-settings">
              <summary>🔧 高级设置</summary>
              <div class="advanced-content">
                <div class="advanced-item">
                  <label>收敛容差</label>
                  <input v-model.number="simulationConfig.tolerance" type="number" step="0.0001" class="tech-input" />
                </div>
                <div class="advanced-item">
                  <label>最大迭代次数</label>
                  <input v-model.number="simulationConfig.maxIterations" type="number" class="tech-input" />
                </div>
                <div class="advanced-item">
                  <label>并行计算核心数</label>
                  <input v-model.number="simulationConfig.parallelCores" type="number" min="1" max="16" class="tech-input" />
                </div>
              </div>
            </details>
          </div>
        </div>

        <!-- 模拟控制按钮 -->
        <div class="simulation-controls">
          <button class="control-button primary" @click="startSimulation" :disabled="isRunning">
            {{ isRunning ? '⏳ 模拟运行中...' : '🚀 开始模拟' }}
          </button>
          <button class="control-button" @click="pauseSimulation" :disabled="!isRunning">
            ⏸️ 暂停
          </button>
          <button class="control-button" @click="stopSimulation" :disabled="!isRunning && !simulationResults">
            ⏹️ 停止
          </button>
          <button class="control-button" @click="resetSimulation">
            🔄 重置
          </button>
        </div>
      </div>

      <!-- 中间：模拟状态和进度 -->
      <div class="status-panel">
        <div class="panel-section">
          <h3 class="section-title">📊 模拟状态</h3>

          <!-- 状态指示器 -->
          <div class="status-indicators">
            <div class="status-item">
              <span class="status-label">模拟状态</span>
              <span :class="['status-value', simulationStatus.class]">{{ simulationStatus.text }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">当前进度</span>
              <span class="status-value">{{ simulationProgress }}%</span>
            </div>
            <div class="status-item">
              <span class="status-label">已用时间</span>
              <span class="status-value">{{ formatTime(elapsedTime) }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">预计剩余</span>
              <span class="status-value">{{ formatTime(estimatedTime) }}</span>
            </div>
          </div>

          <!-- 进度条 -->
          <div class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: simulationProgress + '%' }"></div>
            </div>
            <div class="progress-info">
              <span>步骤: {{ currentStep }}/{{ totalSteps }}</span>
              <span>{{ currentStepName }}</span>
            </div>
          </div>

          <!-- 实时数据预览 -->
          <div v-if="simulationResults" class="realtime-preview">
            <h4 class="preview-title">📈 实时结果预览</h4>
            <div class="preview-grid">
              <div class="preview-item">
                <span class="preview-label">当前年份</span>
                <span class="preview-value">{{ simulationResults.currentYear }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">平均温度</span>
                <span class="preview-value">{{ simulationResults.avgTemp }}°C</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">热岛强度</span>
                <span class="preview-value">{{ simulationResults.heatIntensity }}°C</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">冷却效率</span>
                <span class="preview-value">{{ simulationResults.coolingEff }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 模拟日志 -->
        <div class="panel-section">
          <h3 class="section-title">📋 模拟日志</h3>
          <div class="log-container">
            <div
              v-for="(log, index) in simulationLogs"
              :key="index"
              :class="['log-entry', log.type]"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：结果预览和导出 -->
      <div class="results-panel">
        <div class="panel-section">
          <h3 class="section-title">📊 结果分析</h3>

          <!-- 结果摘要 -->
          <div v-if="simulationResults" class="results-summary">
            <div class="summary-cards">
              <div class="summary-card">
                <div class="card-title">温度变化</div>
                <div class="card-value :class="simulationResults.tempChange >= 0 ? 'warm' : 'cool'">
                  {{ simulationResults.tempChange >= 0 ? '+' : '' }}{{ simulationResults.tempChange }}°C
                </div>
              </div>
              <div class="summary-card">
                <div class="card-title">热岛效应</div>
                <div class="card-value neutral">
                  {{ simulationResults.heatIslandEffect }}°C
                </div>
              </div>
              <div class="summary-card">
                <div class="card-title">能源效率</div>
                <div class="card-value good">
                  {{ simulationResults.energyEfficiency }}%
                </div>
              </div>
              <div class="summary-card">
                <div class="card-title">碳减排</div>
                <div class="card-value good">
                  {{ simulationResults.carbonReduction }}Mt
                </div>
              </div>
            </div>
          </div>

          <!-- 图表预览 -->
          <div class="charts-preview">
            <div class="chart-placeholder">
              <canvas ref="tempChart" class="mini-chart"></canvas>
            </div>
            <div class="chart-placeholder">
              <canvas ref="energyChart" class="mini-chart"></canvas>
            </div>
          </div>

          <!-- 导出选项 -->
          <div class="export-options">
            <h4 class="export-title">📥 导出结果</h4>
            <div class="export-buttons">
              <button class="export-button" @click="exportResults('excel')">
                📊 Excel格式
              </button>
              <button class="export-button" @click="exportResults('csv')">
                📄 CSV数据
              </button>
              <button class="export-button" @click="exportResults('pdf')">
                📑 PDF报告
              </button>
              <button class="export-button" @click="exportResults('json')">
                🔧 JSON格式
              </button>
            </div>
          </div>
        </div>

        <!-- 历史模拟记录 -->
        <div class="panel-section">
          <h3 class="section-title">🗂️ 历史模拟</h3>
          <div class="history-list">
            <div
              v-for="record in simulationHistory"
              :key="record.id"
              class="history-item"
              @click="loadSimulation(record.id)"
            >
              <div class="history-info">
                <div class="history-name">{{ record.name }}</div>
                <div class="history-date">{{ record.date }}</div>
              </div>
              <div class="history-status" :class="record.status">
                {{ record.statusText }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

// 模拟类型
const simulationTypes = [
  { id: 'thermal', name: '热效应模拟' },
  { id: 'electrical', name: '电力模拟' },
  { id: 'combined', name: '综合模拟' },
  { id: 'scenario', name: '情景分析' }
]

// 输出选项
const outputOptions = [
  { id: 'temperature', name: '温度场' },
  { id: 'radiation', name: '辐射通量' },
  { id: 'energy', name: '能量平衡' },
  { id: 'carbon', name: '碳排放' },
  { id: 'economic', name: '经济分析' }
]

// 模拟配置
const simulationConfig = reactive({
  type: 'thermal',
  startYear: 2020,
  endYear: 2030,
  timeStep: 'yearly',
  resolution: 'medium',
  tolerance: 0.001,
  maxIterations: 1000,
  parallelCores: 4,
  outputs: ['temperature', 'radiation', 'energy']
})

// 状态变量
const isRunning = ref(false)
const simulationProgress = ref(0)
const elapsedTime = ref(0)
const estimatedTime = ref(0)
const currentStep = ref(0)
const totalSteps = ref(100)
const currentStepName = ref('初始化')
const simulationResults = ref(null)
const simulationLogs = ref([])

// 模拟状态
const simulationStatus = computed(() => {
  if (!simulationResults.value) {
    return { text: '未开始', class: 'idle' }
  } else if (isRunning.value) {
    return { text: '运行中', class: 'running' }
  } else {
    return { text: '已完成', class: 'completed' }
  }
})

// 模拟历史
const simulationHistory = ref([
  { id: 1, name: '西北沙漠热效应', date: '2024-01-15', status: 'completed', statusText: '已完成' },
  { id: 2, name: '沿海地区对比', date: '2024-01-10', status: 'completed', statusText: '已完成' },
  { id: 3, name: '青藏高原测试', date: '2024-01-05', status: 'failed', statusText: '失败' }
])

// 时间格式化
const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

// 开始模拟
const startSimulation = () => {
  isRunning.value = true
  simulationProgress.value = 0
  elapsedTime.value = 0
  currentStep.value = 0
  simulationLogs.value = []
  simulationResults.value = null

  addLog('info', '模拟任务启动')
  addLog('info', `模拟类型: ${simulationConfig.type}`)
  addLog('info', `时间范围: ${simulationConfig.startYear}-${simulationConfig.endYear}`)

  runSimulation()
}

// 运行模拟（模拟计算过程）
const runSimulation = () => {
  const steps = [
    { name: '初始化参数', duration: 2 },
    { name: '加载地理数据', duration: 5 },
    { name: '计算辐射场', duration: 8 },
    { name: '求解温度分布', duration: 15 },
    { name: '计算能量平衡', duration: 10 },
    { name: '评估热效应', duration: 7 },
    { name: '生成结果报告', duration: 3 }
  ]

  let currentStepIndex = 0
  totalSteps.value = steps.length

  const processStep = () => {
    if (currentStepIndex >= steps.length || !isRunning.value) {
      if (isRunning.value) {
        completeSimulation()
      }
      return
    }

    const step = steps[currentStepIndex]
    currentStepName.value = step.name
    currentStep.value = currentStepIndex + 1

    addLog('info', `正在执行: ${step.name}`)

    // 模拟计算进度
    let progress = 0
    const stepDuration = step.duration * 1000 // 转换为毫秒
    const stepInterval = stepDuration / 20 // 20个更新点

    const stepTimer = setInterval(() => {
      progress += 5
      simulationProgress.value = ((currentStepIndex * 100) + progress) / steps.length
      elapsedTime.value += stepInterval / 1000

      if (progress >= 100) {
        clearInterval(stepTimer)
        addLog('success', `${step.name} 完成`)
        currentStepIndex++
        setTimeout(processStep, 500)
      }
    }, stepInterval)
  }

  processStep()
}

// 完成模拟
const completeSimulation = () => {
  isRunning.value = false
  simulationProgress.value = 100
  currentStepName.value = '模拟完成'

  // 生成模拟结果
  simulationResults.value = {
    currentYear: simulationConfig.endYear,
    avgTemp: 28.5,
    heatIntensity: -1.8,
    coolingEff: 12.5,
    tempChange: -1.2,
    heatIslandEffect: -2.3,
    energyEfficiency: 18.7,
    carbonReduction: 45.6
  }

  addLog('success', '模拟计算完成!')
  addLog('info', '结果已生成，可以查看和导出')
}

// 暂停模拟
const pauseSimulation = () => {
  isRunning.value = false
  addLog('warning', '模拟已暂停')
}

// 停止模拟
const stopSimulation = () => {
  isRunning.value = false
  simulationProgress.value = 0
  currentStepName.value = '已停止'
  addLog('error', '模拟已停止')
}

// 重置模拟
const resetSimulation = () => {
  isRunning.value = false
  simulationProgress.value = 0
  elapsedTime.value = 0
  currentStep.value = 0
  simulationResults.value = null
  simulationLogs.value = []
  currentStepName.value = '就绪'

  addLog('info', '模拟已重置')
}

// 加载历史模拟
const loadSimulation = (id) => {
  const record = simulationHistory.value.find(r => r.id === id)
  if (record && record.status === 'completed') {
    addLog('info', `加载历史模拟: ${record.name}`)
    // 这里可以添加加载历史数据的逻辑
  }
}

// 导出结果
const exportResults = (format) => {
  if (!simulationResults.value) {
    addLog('error', '没有可导出的结果')
    return
  }

  addLog('info', `导出结果为${format.toUpperCase()}格式...`)

  // 模拟导出过程
  setTimeout(() => {
    addLog('success', `${format.toUpperCase()}文件导出成功`)
  }, 1000)
}

// 添加日志
const addLog = (type, message) => {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN')

  simulationLogs.value.unshift({
    type,
    time,
    message
  })

  // 限制日志数量
  if (simulationLogs.value.length > 50) {
    simulationLogs.value = simulationLogs.value.slice(0, 50)
  }
}

// 组件挂载时
onMounted(() => {
  addLog('info', '模拟控制台已就绪')
})
</script>

<style scoped>
.simulation-page {
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

.simulation-content {
  display: grid;
  grid-template-columns: 320px 1fr 360px;
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

.config-group {
  margin-bottom: var(--spacing-lg);
}

.config-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
}

.button-group {
  display: flex;
  gap: var(--spacing-sm);
}

.type-button {
  flex: 1;
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-button:hover {
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.type-button.active {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: white;
}

.time-range {
  display: flex;
  gap: var(--spacing-sm);
}

.time-input {
  flex: 1;
}

.time-input label {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.tech-select,
.tech-input {
  width: 100%;
  padding: var(--spacing-sm);
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

.advanced-settings {
  margin-top: var(--spacing-md);
}

.advanced-settings summary {
  cursor: pointer;
  font-size: 12px;
  color: var(--color-cyan);
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.advanced-content {
  margin-top: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.advanced-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.advanced-item label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.simulation-controls {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.control-button {
  padding: var(--spacing-md);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.control-button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.control-button.primary:not(:disabled) {
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-color: transparent;
  color: var(--bg-primary);
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.status-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.status-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-value.idle { color: var(--text-tertiary); }
.status-value.running { color: var(--color-cyan); }
.status-value.completed { color: var(--color-green); }

.progress-section {
  margin-bottom: var(--spacing-lg);
}

.progress-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-blue), var(--color-cyan));
  transition: width 0.3s ease;
  border-radius: 4px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-tertiary);
}

.realtime-preview {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.preview-title {
  font-size: 12px;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
  font-weight: 600;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.preview-item {
  text-align: center;
  padding: var(--spacing-sm);
}

.preview-label {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.preview-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-cyan);
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-entry {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: 11px;
}

.log-entry.info { background: rgba(74, 158, 255, 0.1); }
.log-entry.success { background: rgba(0, 255, 157, 0.1); }
.log-entry.warning { background: rgba(255, 157, 0, 0.1); }
.log-entry.error { background: rgba(255, 71, 87, 0.1); }

.log-time {
  color: var(--text-tertiary);
  min-width: 70px;
}

.log-message {
  color: var(--text-secondary);
  flex: 1;
}

.results-summary {
  margin-bottom: var(--spacing-md);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}

.summary-card {
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  text-align: center;
}

.card-title {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-xs);
}

.card-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-cyan);
}

.card-value.cool { color: var(--color-blue); }
.card-value.warm { color: var(--color-red); }
.card-value.neutral { color: var(--color-green); }
.card-value.good { color: var(--color-green); }

.charts-preview {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.chart-placeholder {
  height: 120px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

.export-options {
  margin-bottom: var(--spacing-md);
}

.export-title {
  font-size: 12px;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
  font-weight: 600;
}

.export-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.export-button {
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.export-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.history-item:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-name {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 600;
}

.history-date {
  font-size: 11px;
  color: var(--text-tertiary);
}

.history-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.history-status.completed {
  background: rgba(0, 255, 157, 0.2);
  color: var(--color-green);
}

.history-status.failed {
  background: rgba(255, 71, 87, 0.2);
  color: var(--color-red);
}

.history-status.running {
  background: rgba(74, 158, 255, 0.2);
  color: var(--color-blue);
}
</style>
