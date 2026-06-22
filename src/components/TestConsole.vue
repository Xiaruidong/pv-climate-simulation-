<template>
  <div class="test-console">
    <div class="console-header">
      <h2>🧪 参数测试控制台</h2>
      <div class="header-actions">
        <button @click="loadDefaultTests" class="btn btn-secondary">加载默认测试</button>
        <button @click="runAllTests" class="btn btn-primary">运行所有测试</button>
        <button @click="exportResults" class="btn btn-success">导出结果</button>
      </div>
    </div>

    <div class="console-layout">
      <!-- 测试场景列表 -->
      <div class="test-list">
        <h3>测试场景</h3>
        <div class="test-categories">
          <button
            v-for="category in categories"
            :key="category.key"
            :class="['category-btn', { active: selectedCategory === category.key }]"
            @click="selectedCategory = category.key"
          >
            {{ category.name }} ({{ category.count }})
          </button>
        </div>

        <div class="test-items">
          <div
            v-for="test in filteredTests"
            :key="test.id"
            :class="['test-item', { active: selectedTest === test.id, running: test.running, completed: test.completed }]"
            @click="selectTest(test)"
          >
            <div class="test-name">{{ test.name }}</div>
            <div class="test-status">
              <span v-if="test.running">⏳</span>
              <span v-else-if="test.completed">✅</span>
              <span v-else>⭕</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试参数面板 -->
      <div class="test-params">
        <h3>测试参数</h3>
        <div v-if="currentTest" class="params-grid">
          <div class="param-item">
            <label>光伏反照率</label>
            <input v-model.number="currentTest.params.albedo_pv" type="number" step="0.001" min="0" max="1">
          </div>
          <div class="param-item">
            <label>覆盖率</label>
            <input v-model.number="currentTest.params.coverage_ratio" type="number" step="1e-9">
            <span class="param-hint">{{ formatCoverage(currentTest.params.coverage_ratio) }}</span>
          </div>
          <div class="param-item">
            <label>光伏效率</label>
            <input v-model.number="currentTest.params.pv_efficiency" type="number" step="0.01" min="0" max="1">
          </div>
          <div class="param-item">
            <label>陆地反照率</label>
            <input v-model.number="currentTest.params.albedo_land" type="number" step="0.01" min="0" max="1">
          </div>
          <div class="param-item">
            <label>CO2浓度 (ppm)</label>
            <input v-model.number="currentTest.params.co2_current" type="number" step="10">
          </div>
          <div class="param-item">
            <label>初始温度 (°C)</label>
            <input v-model.number="currentTest.params.initial_temp" type="number" step="1">
          </div>
        </div>

        <div class="test-actions">
          <button @click="runCurrentTest" class="btn btn-primary" :disabled="!currentTest">
            🚀 运行当前测试
          </button>
          <button @click="applyToDashboard" class="btn btn-success" :disabled="!currentTest || !currentTest.completed">
            📊 应用到仪表板
          </button>
        </div>
      </div>

      <!-- 测试结果面板 -->
      <div class="test-results">
        <h3>测试结果</h3>
        <div v-if="currentTest && currentTest.result" class="results-content">
          <div class="result-card">
            <h4>温度变化</h4>
            <div :class="['result-value', getResultClass(currentTest.result.temp_change)]">
              {{ currentTest.result.temp_change.toFixed(6) }}°C
            </div>
            <div class="result-detail">
              基准: {{ currentTest.result.base_temp.toFixed(2) }}°C →
              光伏: {{ currentTest.result.pv_temp.toFixed(2) }}°C
            </div>
          </div>

          <div class="result-card">
            <h4>CO2减排</h4>
            <div class="result-value">
              {{ currentTest.result.co2_reduction.toFixed(4) }} ppm
            </div>
            <div class="result-detail">
              碳减排效果显著
            </div>
          </div>

          <div class="result-card">
            <h4>反照率变化</h4>
            <div class="result-value">
              {{ (currentTest.result.albedo_change * 10000).toFixed(6) }}
            </div>
            <div class="result-detail">
              行星反照率变化
            </div>
          </div>

          <div class="result-card">
            <h4>冷却效率</h4>
            <div class="result-value">
              {{ currentTest.result.cooling_efficiency.toFixed(2) }}%
            </div>
            <div class="result-detail">
              {{ currentTest.result.cooling_effect ? '✅ 降温生效' : '❌ 升温效应' }}
            </div>
          </div>
        </div>

        <div v-else class="no-results">
          选择一个测试并运行以查看结果
        </div>
      </div>
    </div>

    <!-- 批量测试进度 -->
    <div v-if="batchRunning" class="batch-progress">
      <h3>批量测试进度</h3>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: batchProgress + '%' }"></div>
      </div>
      <div class="progress-text">
        {{ batchCompleted }} / {{ batchTotal }} 测试完成
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getQuickTestData } from '@/utils/testDataGenerator'
import { useSimulation } from '@/composables/useSimulation'

const { updateParams, triggerCalculation } = useSimulation()

// 测试状态
const tests = ref([])
const selectedCategory = ref('all')
const selectedTest = ref(null)
const batchRunning = ref(false)
const batchProgress = ref(0)
const batchCompleted = ref(0)
const batchTotal = ref(0)

// 计算属性
const categories = computed(() => {
  const cats = [
    { key: 'all', name: '全部', count: tests.value.length }
  ]

  const categoryMap = {}
  tests.value.forEach(test => {
    const category = test.category || 'other'
    if (!categoryMap[category]) {
      categoryMap[category] = 0
    }
    categoryMap[category]++
  })

  Object.entries(categoryMap).forEach(([key, count]) => {
    cats.push({ key, name: key, count })
  })

  return cats
})

const filteredTests = computed(() => {
  if (selectedCategory.value === 'all') {
    return tests.value
  }
  return tests.value.filter(test => test.category === selectedCategory.value)
})

const currentTest = computed(() => {
  return tests.value.find(test => test.id === selectedTest.value)
})

// 方法
const formatCoverage = (value) => {
  if (!value) return '0%'
  return `${(value * 100).toFixed(6)}%`
}

const getResultClass = (value) => {
  if (value < -0.01) return 'cooling'
  if (value > 0.01) return 'warming'
  return 'neutral'
}

const loadDefaultTests = () => {
  const quickTests = getQuickTestData()
  tests.value = Object.entries(quickTests).map(([key, test]) => ({
    id: key,
    name: test.name,
    category: 'quick',
    params: { ...test.params },
    expected_results: test.expected_results,
    result: null,
    completed: false,
    running: false
  }))
}

const selectTest = (test) => {
  selectedTest.value = test.id
}

const runCurrentTest = async () => {
  if (!currentTest.value) return

  currentTest.value.running = true
  currentTest.value.completed = false

  try {
    // 使用真实计算
    const result = await calculateTest(currentTest.value.params)
    currentTest.value.result = result
    currentTest.value.completed = true
  } catch (error) {
    console.error('测试运行错误:', error)
  } finally {
    currentTest.value.running = false
  }
}

const calculateTest = async (params) => {
  // 这里可以调用后端API或前端计算
  // 暂时使用简化的前端计算
  const { albedo_pv, coverage_ratio, pv_efficiency, albedo_land, co2_current } = params

  // 简化计算逻辑
  const S0 = 1361.0
  const land_fraction = 0.29
  const ocean_fraction = 0.71

  const surface_albedo = land_fraction * albedo_land + ocean_fraction * 0.06
  const base_planetary_albedo = 0.248 + 0.425 * surface_albedo

  const new_surface_albedo = surface_albedo + (albedo_pv - albedo_land) * coverage_ratio * land_fraction
  const pv_planetary_albedo = 0.248 + 0.425 * new_surface_albedo

  // CO2减排计算
  const irradiance = 1420
  const annual_generation = irradiance * pv_efficiency * 0.8 * 0.8 * 0.96
  const land_area_m2 = 1.47921e14 * 1e6
  const total_pv_area = land_area_m2 * coverage_ratio
  const total_generation = annual_generation * total_pv_area
  const co2_reduction_kg = total_generation * 520 * 0.5 / 1000
  const co2_reduction_ppm = Math.max(0, co2_reduction_kg / 2.13e12)

  // 温度计算
  const AREF = 210.2
  const B = 2.15

  const base_flux_in = 0.25 * (1 - base_planetary_albedo) * S0
  const co2_forcing = 5.35 * Math.log(co2_current / 280.0)
  const base_temp = (base_flux_in + co2_forcing - AREF) / B

  const safe_co2_reduction = Math.max(0, Math.min(co2_reduction_ppm, co2_current - 280))
  const pv_flux_in = 0.25 * (1 - pv_planetary_albedo) * S0
  const pv_co2_forcing = 5.35 * Math.log(Math.max(co2_current - safe_co2_reduction, 280) / 280.0)
  const pv_temp = (pv_flux_in + pv_co2_forcing - AREF) / B

  const temp_change = pv_temp - base_temp

  return {
    base_temp,
    pv_temp,
    temp_change,
    co2_reduction: co2_reduction_ppm,
    albedo_change: pv_planetary_albedo - base_planetary_albedo,
    cooling_effect: temp_change < 0,
    heat_island_effect: temp_change * 1.1,
    cooling_efficiency: Math.abs(temp_change) * 10
  }
}

const runAllTests = async () => {
  batchRunning.value = true
  batchCompleted.value = 0
  batchTotal.value = tests.value.length

  for (const test of tests.value) {
    selectedTest.value = test.id
    await runCurrentTest()
    batchCompleted.value++
    batchProgress.value = (batchCompleted.value / batchTotal.value) * 100
  }

  batchRunning.value = false
}

const applyToDashboard = () => {
  if (!currentTest.value || !currentTest.value.completed) return

  // 应用参数到仪表板
  updateParams(currentTest.value.params)

  // 通知用户
  alert('参数已应用到仪表板，请切换到仪表板查看结果！')
}

const exportResults = () => {
  const results = tests.value
    .filter(test => test.completed)
    .map(test => ({
      name: test.name,
      params: test.params,
      result: test.result
    }))

  const dataStr = JSON.stringify(results, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test-results-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadDefaultTests()
})
</script>

<style scoped>
.test-console {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  min-height: 100vh;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-primary);
}

.console-header h2 {
  margin: 0;
  color: var(--color-cyan);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.console-layout {
  display: grid;
  grid-template-columns: 300px 1fr 1fr;
  gap: 20px;
  flex: 1;
}

.test-list,
.test-params,
.test-results {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.test-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
}

.category-btn {
  padding: 5px 10px;
  font-size: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-btn.active {
  background: var(--color-cyan);
  color: white;
  border-color: var(--color-cyan);
}

.test-items {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  overflow-y: auto;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.test-item:hover {
  border-color: var(--color-blue);
}

.test-item.active {
  border-color: var(--color-cyan);
  background: rgba(74, 158, 255, 0.1);
}

.test-item.running {
  border-color: var(--color-yellow);
}

.test-item.completed {
  border-color: var(--color-green);
}

.test-name {
  font-size: 13px;
  color: var(--text-primary);
}

.test-params h3,
.test-results h3 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: var(--color-cyan);
}

.params-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-item label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.param-item input {
  padding: 5px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
}

.param-hint {
  font-size: 10px;
  color: var(--text-tertiary);
}

.test-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--color-cyan);
  color: white;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.btn-success {
  background: var(--color-green);
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.result-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: 12px;
}

.result-card h4 {
  margin: 0 0 8px 0;
  font-size: 11px;
  color: var(--text-tertiary);
  text-transform: uppercase;
}

.result-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-cyan);
}

.result-value.cooling {
  color: var(--color-cyan);
}

.result-value.warming {
  color: var(--color-red);
}

.result-value.neutral {
  color: var(--text-secondary);
}

.result-detail {
  margin-top: 5px;
  font-size: 10px;
  color: var(--text-tertiary);
}

.no-results {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-tertiary);
  font-size: 13px;
}

.batch-progress {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: 15px 20px;
}

.batch-progress h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: var(--color-cyan);
}

.progress-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-cyan);
  transition: width var(--transition-fast);
}

.progress-text {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
}
</style>
