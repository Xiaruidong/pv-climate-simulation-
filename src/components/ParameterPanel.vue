<template>
  <aside class="side-panel">
    <div class="side-panel-header">
      <h2 class="side-panel-title">📊 物理计算参数</h2>
      <button class="tech-button" @click="toggleCollapse">
        {{ isCollapsed ? '◀' : '▶' }}
      </button>
    </div>

    <div v-if="!isCollapsed" class="side-panel-content">
      <!-- 核心计算参数 -->
      <div class="param-section">
        <h3 class="param-section-title">⚡ 光伏系统参数</h3>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">光伏面板反照率</span>
            <span class="param-label-info" title="直接影响降温效果的主要参数">⭐</span>
          </div>
          <input
            v-model.number="params.albedo_pv"
            type="number"
            step="0.001"
            min="0"
            max="1"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ params.albedo_pv.toFixed(3) }} |
            推荐: 0.438 (新型) / 0.95 (镜面)
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">光伏覆盖率</span>
            <span class="param-label-info" title="光伏部署面积占总陆地面积的比例">⭐</span>
          </div>
          <input
            v-model.number="params.coverage_ratio"
            type="number"
            step="1e-9"
            min="1e-10"
            max="1e-5"
            class="tech-input"
            placeholder="1e-8"
          />
          <div class="param-hint">
            当前: {{ formatCoverage(params.coverage_ratio) }}
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">光伏转化效率</span>
            <span class="param-label-info" title="影响发电量和CO2减排量">⭐</span>
          </div>
          <input
            v-model.number="params.pv_efficiency"
            type="number"
            step="0.01"
            min="0.15"
            max="0.30"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ (params.pv_efficiency * 100).toFixed(1) }}% |
            范围: 15-30%
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">光伏面板类型</span>
            <span class="param-label-info" title="快速设置典型面板参数">⚡</span>
          </div>
          <select v-model="params.panel_type" class="tech-select" @change="applyPanelType">
            <option value="mono">单晶硅 (效率23%, 反照率0.307)</option>
            <option value="poly">多晶硅 (效率16%, 反照率0.307)</option>
            <option value="thin_film">薄膜 (效率12%, 反照率0.25)</option>
            <option value="perovskite">钙钛矿 (效率25%, 反照率0.35)</option>
            <option value="mirror">镜面反射型 (效率23%, 反照率0.95)</option>
          </select>
        </div>
      </div>

      <!-- 地表反照率参数 -->
      <div class="param-section">
        <h3 class="param-section-title">🌍 地表反照率参数</h3>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">陆地反照率</span>
            <span class="param-label-info" title="计算地表反照率的基准值">⭐</span>
          </div>
          <input
            v-model.number="params.albedo_land"
            type="number"
            step="0.01"
            min="0"
            max="1"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ params.albedo_land.toFixed(2) }} |
            范围: 0.15-0.40
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">海洋反照率</span>
            <span class="param-label-info" title="海洋表面的反射率">💧</span>
          </div>
          <input
            v-model.number="params.albedo_ocean"
            type="number"
            step="0.01"
            min="0"
            max="1"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ params.albedo_ocean.toFixed(2) }} |
            通常固定为 0.06
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">地表类型预设</span>
            <span class="param-label-info" title="快速设置地表反照率组合">⚡</span>
          </div>
          <select v-model="params.surface_type" class="tech-select" @change="applySurfaceType">
            <option value="desert">沙漠地区 (陆地表0.35)</option>
            <option value="grassland">草原地区 (陆地表0.25)</option>
            <option value="forest">森林地区 (陆地表0.15)</option>
            <option value="urban">城市地区 (陆地表0.18)</option>
            <option value="custom">自定义</option>
          </select>
        </div>
      </div>

      <!-- 气候参数 -->
      <div class="param-section">
        <h3 class="param-section-title">🌡 气候参数</h3>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">CO₂浓度</span>
            <span class="param-label-info" title="大气CO₂浓度影响温室效应">⭐</span>
          </div>
          <input
            v-model.number="params.co2_current"
            type="number"
            step="10"
            min="280"
            max="1000"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ params.co2_current }} ppm |
            预设: 280(前工业化) / 420(当前) / 450(巴黎目标)
          </div>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">气候情景预设</span>
            <span class="param-label-info" title="快速设置不同气候情景">⚡</span>
          </div>
          <select v-model="params.climate_scenario" class="tech-select" @change="applyClimateScenario">
            <option value="pre_industrial">前工业化 (280ppm)</option>
            <option value="current">当前水平 (420ppm)</option>
            <option value="rcp26">RCP2.6 (450ppm)</option>
            <option value="rcp45">RCP4.5 (650ppm)</option>
            <option value="rcp85">RCP8.5 (1000ppm)</option>
          </select>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">初始地表温度</span>
            <span class="param-label-info" title="计算起始的温度基准">⭐</span>
          </div>
          <input
            v-model.number="params.initial_temp"
            type="number"
            step="1"
            min="-20"
            max="50"
            class="tech-input"
          />
          <div class="param-hint">
            当前: {{ params.initial_temp }}°C |
            通常在 -10 到 35°C 范围内
          </div>
        </div>
      </div>

      <!-- 模拟控制参数 -->
      <div class="param-section">
        <h3 class="param-section-title">⚙️ 模拟控制</h3>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">模拟时长</span>
            <span class="param-label-info">影响计算精度和收敛时间</span>
          </div>
          <select v-model="params.simulation_years" class="tech-select">
            <option value="50">50年 (快速评估)</option>
            <option value="100">100年 (标准)</option>
            <option value="200">200年 (长期)</option>
            <option value="500">500年 (超长期)</option>
          </select>
        </div>

        <div class="param-group">
          <div class="param-label">
            <span class="param-label-text">计算方法</span>
            <span class="param-label-info">选择计算精度模式</span>
          </div>
          <select v-model="params.calculation_method" class="tech-select">
            <option value="simplified">简化计算 (快速响应)</option>
            <option value="numerical">数值积分 (精确计算)</option>
          </select>
        </div>
      </div>

      <!-- 参数预设 -->
      <div class="param-section">
        <h3 class="param-section-title">🎯 快速预设</h3>

        <div class="preset-buttons">
          <button @click="applyPreset('low_coverage')" class="preset-btn">
            低覆盖率
            <small>1e-9</small>
          </button>
          <button @click="applyPreset('medium_coverage')" class="preset-btn">
            中等覆盖率
            <small>1e-8</small>
          </button>
          <button @click="applyPreset('high_coverage')" class="preset-btn">
            高覆盖率
            <small>1e-7</small>
          </button>
          <button @click="applyPreset('mirror_panel')" class="preset-btn">
            镜面面板
            <small>强降温</small>
          </button>
        </div>
      </div>

      <!-- 计算控制 -->
      <div class="param-actions">
        <button class="tech-button primary" @click="runSimulation" style="width: 100%;">
          🚀 运行计算
        </button>
        <button class="tech-button secondary" @click="resetParams" style="width: 100%; margin-top: 8px;">
          🔄 重置参数
        </button>
        <button class="tech-button" @click="exportParams" style="width: 100%; margin-top: 8px;">
          📥 导出配置
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const emit = defineEmits(['simulate'])

const isCollapsed = ref(false)

// 核心计算参数 - 与实际EBM模型一一对应
const params = reactive({
  // 光伏系统参数 ⭐⭐⭐⭐⭐
  albedo_pv: 0.438,           // 光伏面板反照率
  coverage_ratio: 1e-8,       // 覆盖率比例
  pv_efficiency: 0.23,        // 光伏转化效率

  // 地表反照率参数 ⭐⭐⭐⭐
  albedo_land: 0.35,          // 陆地反照率
  albedo_ocean: 0.06,         // 海洋反照率

  // 气候参数 ⭐⭐⭐⭐⭐
  co2_current: 420.0,         // CO2浓度 (ppm)
  initial_temp: 15.0,         // 初始地表温度 (°C)

  // 模拟控制参数
  simulation_years: 100,     // 模拟年数
  calculation_method: 'simplified', // 计算方法

  // 辅助参数
  panel_type: 'mono',          // 面板类型
  surface_type: 'desert',      // 地表类型
  climate_scenario: 'current'  // 气候情景
})

// 光伏面板类型预设
const panelTypes = {
  mono: { albedo: 0.307, efficiency: 0.23 },
  poly: { albedo: 0.307, efficiency: 0.16 },
  thin_film: { albedo: 0.25, efficiency: 0.12 },
  perovskite: { albedo: 0.35, efficiency: 0.25 },
  mirror: { albedo: 0.95, efficiency: 0.23 }
}

// 地表类型预设 (对应真实反照率值)
const surfaceTypes = {
  desert: { albedo_land: 0.35, name: '沙漠地区' },
  grassland: { albedo_land: 0.25, name: '草原地区' },
  forest: { albedo_land: 0.15, name: '森林地区' },
  urban: { albedo_land: 0.18, name: '城市地区' }
}

// 气候情景预设
const climateScenarios = {
  pre_industrial: { co2_current: 280, name: '前工业化' },
  current: { co2_current: 420, name: '当前水平' },
  rcp26: { co2_current: 450, name: '巴黎目标' },
  rcp45: { co2_current: 650, name: 'RCP4.5' },
  rcp85: { co2_current: 1000, name: 'RCP8.5' }
}

// 格式化覆盖率显示
const formatCoverage = (value) => {
  if (!value && value !== 0) return '---'
  const num = parseFloat(value)
  if (num >= 0.01) return `${(num * 100).toFixed(1)}%`
  if (num >= 0.001) return `${(num * 100).toFixed(2)}%`
  if (num >= 0.0001) return `${(num * 100).toFixed(3)}%`
  if (num >= 0.00001) return `${(num * 100).toFixed(4)}%`
  return `${(num * 100).toFixed(6)}%`
}

// 验证参数合理性
const hasErrors = computed(() => {
  if (params.albedo_pv > 1 || params.albedo_pv < 0) return true
  if (params.coverage_ratio < 0 || params.coverage_ratio > 0.01) return true
  if (params.pv_efficiency < 0 || params.pv_efficiency > 1) return true
  if (params.co2_current < 280 || params.co2_current > 1000) return true
  if (params.initial_temp < -50 || params.initial_temp > 50) return true
  return false
})

const validationMessage = computed(() => {
  if (params.albedo_pv > 1 || params.albedo_pv < 0) {
    return "光伏反照率必须在0-1之间"
  }
  if (params.coverage_ratio < 0 || params.coverage_ratio > 0.01) {
    return "覆盖率必须在0-0.01之间"
  }
  if (params.pv_efficiency < 0 || params.pv_efficiency > 1) {
    return "光伏效率必须在0-1之间"
  }
  if (params.co2_current < 280 || params.co2_current > 1000) {
    return "CO2浓度必须在280-1000ppm之间"
  }
  return null
})

// 应用面板类型预设
const applyPanelType = () => {
  const panel = panelTypes[params.panel_type]
  if (panel) {
    params.albedo_pv = panel.albedo
    params.pv_efficiency = panel.efficiency
  }
}

// 应用地表类型预设
const applySurfaceType = () => {
  const surface = surfaceTypes[params.surface_type]
  if (surface) {
    params.albedo_land = surface.albedo_land
  }
}

// 应用气候情景预设
const applyClimateScenario = () => {
  const scenario = climateScenarios[params.climate_scenario]
  if (scenario) {
    params.co2_current = scenario.co2_current
  }
}

// 快速预设
const applyPreset = (preset) => {
  switch(preset) {
    case 'low_coverage':
      params.coverage_ratio = 1e-9
      break
    case 'medium_coverage':
      params.coverage_ratio = 1e-8
      break
    case 'high_coverage':
      params.coverage_ratio = 1e-7
      break
    case 'mirror_panel':
      params.albedo_pv = 0.95
      params.coverage_ratio = 1e-8
      break
  }
}

// 重置参数
const resetParams = () => {
  Object.assign(params, {
    albedo_pv: 0.438,
    coverage_ratio: 1e-8,
    pv_efficiency: 0.23,
    albedo_land: 0.35,
    albedo_ocean: 0.06,
    co2_current: 420.0,
    initial_temp: 15.0,
    simulation_years: 100,
    panel_type: 'mono',
    surface_type: 'desert',
    climate_scenario: 'current'
  })
}

// 导出参数
const exportParams = () => {
  const config = {
    ...params,
    export_time: new Date().toISOString(),
    version: '2.0.0'
  }
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pv-climate-config-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 运行模拟
const runSimulation = () => {
  if (hasErrors.value) {
    alert('参数错误: ' + validationMessage.value)
    return
  }

  console.log('运行计算，参数:', params)

  // 直接触发计算（不需要点击按钮）
  emit('simulate', { ...params })
}

// 折叠控制
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 暴露所有方法供外部调用
defineExpose({
  resetParams,
  runSimulation,
  exportParams
})
</script>

<style scoped>
.side-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  overflow-y: auto;
}

.side-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-primary);
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
}

.side-panel-title {
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-cyan), var(--color-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.tech-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tech-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  box-shadow: var(--shadow-glow-blue);
}

.tech-button.primary {
  background: var(--color-cyan);
  color: white;
  border-color: var(--color-cyan);
}

.tech-button.secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.side-panel-content {
  padding: var(--spacing-md);
  flex: 1;
}

.param-section {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.param-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-cyan);
  margin: 0 0 var(--spacing-md) 0;
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-secondary);
}

.param-group {
  margin-bottom: var(--spacing-md);
}

.param-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.param-label-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.param-label-info {
  font-size: 16px;
  color: var(--color-yellow);
  cursor: help;
}

.tech-input {
  width: 100%;
  padding: var(--spacing-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 14px;
  transition: all var(--transition-fast);
}

.tech-input:focus {
  outline: none;
  border-color: var(--color-cyan);
  box-shadow: var(--shadow-glow-cyan);
}

.tech-input.error {
  border-color: var(--color-red);
}

.input-unit {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: var(--spacing-xs);
}

.param-hint {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: var(--spacing-xs);
  line-height: 1.4;
}

.tech-select {
  width: 100%;
  padding: var(--spacing-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 14px;
}

.tech-select:focus {
  outline: none;
  border-color: var(--color-cyan);
}

.param-actions {
  padding: var(--spacing-md) 0;
  margin-top: var(--spacing-lg);
  border-top: 1px solid var(--border-primary);
}

.preset-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.preset-btn {
  padding: var(--spacing-sm);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preset-btn:hover {
  background: var(--color-cyan);
  border-color: var(--color-cyan);
  color: white;
}

.preset-btn small {
  display: block;
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 2px;
}
</style>
