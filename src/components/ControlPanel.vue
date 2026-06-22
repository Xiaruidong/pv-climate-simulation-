<template>
  <div class="control-panel">
    <div class="info-card">
      <div class="info-card-title">⚙️ 参数配置</div>

      <!-- 面板类型选择 -->
      <div class="form-item">
        <label class="form-item-label">光伏面板类型</label>
        <el-select v-model="params.panelType" @change="updateParams">
          <el-option
            v-for="(panel, key) in panelTypes"
            :key="key"
            :label="panel.name"
            :value="key"
          >
            <div>
              <div>{{ panel.name }}</div>
              <div style="font-size: 12px; color: #999">{{ panel.description }}</div>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- 覆盖面积比例 -->
      <div class="form-item">
        <label class="form-item-label">覆盖面积比例: {{ formatCoverage(params.coverageRatio) }}</label>
        <el-slider
          v-model="params.coverageRatio"
          :marks="coverageMarks"
          :step="1e-8"
          :max="1e-6"
          @change="updateParams"
        />
        <div style="font-size: 12px; color: #888; margin-top: 4px;">
          当前值: {{ (params.coverageRatio * 100).toFixed(6) }}%
        </div>
      </div>

      <!-- CO2浓度 -->
      <div class="form-item">
        <label class="form-item-label">CO2浓度 (ppm)</label>
        <el-input-number
          v-model="params.co2Current"
          :min="280"
          :max="1000"
          :step="10"
          @change="updateParams"
        />
      </div>

      <!-- 模拟时长 -->
      <div class="form-item">
        <label class="form-item-label">模拟时长 (年)</label>
        <el-select v-model="params.simulationYears" @change="updateParams">
          <el-option label="50年" :value="50" />
          <el-option label="100年" :value="100" />
          <el-option label="200年" :value="200" />
          <el-option label="500年" :value="500" />
        </el-select>
      </div>
    </div>

    <!-- 预设场景 -->
    <div class="info-card">
      <div class="info-card-title">📋 预设场景</div>
      <el-button
        v-for="(scenario, index) in scenarios"
        :key="index"
        size="small"
        @click="applyScenario(scenario)"
        style="margin-bottom: 8px; width: 100%"
      >
        {{ scenario.name }}
      </el-button>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="action-button primary-button" @click="startSimulation">
        🚀 开始模拟
      </button>
      <button class="action-button secondary-button" @click="resetParams">
        🔄 重置参数
      </button>
      <button class="action-button secondary-button" @click="exportConfig">
        📥 导出配置
      </button>
    </div>

    <!-- 计算进度 -->
    <div v-if="isCalculating" class="progress-display">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="progress-text">{{ progressText }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['simulationStart'])

// 光伏面板类型
const panelTypes = {
  new: {
    name: '新型透过+反射选择性面板',
    albedo: 0.438,
    efficiency: 0.23,
    description: '高反照率+高转化效率'
  },
  traditional: {
    name: '传统光伏面板',
    albedo: 0.307,
    efficiency: 0.23,
    description: '中等反照率+标准效率'
  },
  mirror: {
    name: '镜面反射型面板',
    albedo: 0.95,
    efficiency: 0.23,
    description: '超高反照率，降温最强'
  }
}

// 覆盖面积标记
const coverageMarks = {
  1e-8: '0.000001%',
  1e-7: '0.00001%',
  5e-7: '0.00005%',
  1e-6: '0.0001%'
}

// 格式化覆盖率显示
const formatCoverage = (value) => {
  if (value >= 0.01) return `${(value * 100).toFixed(1)}%`
  if (value >= 0.001) return `${(value * 100).toFixed(2)}%`
  if (value >= 0.0001) return `${(value * 100).toFixed(3)}%`
  return `${(value * 100).toFixed(6)}%`
}

// 预设场景
const scenarios = [
  {
    name: '🌱 环保方案',
    panelType: 'new',
    coverageRatio: 1e-8,
    co2Current: 420,
    simulationYears: 100
  },
  {
    name: '🔥 激进方案',
    panelType: 'new',
    coverageRatio: 1e-7,
    co2Current: 420,
    simulationYears: 100
  },
  {
    name: '⚖️ 对比基准',
    panelType: 'traditional',
    coverageRatio: 5e-8,
    co2Current: 420,
    simulationYears: 100
  }
]

// 当前参数
const params = reactive({
  panelType: 'new',
  coverageRatio: 1e-8,
  co2Current: 420,
  simulationYears: 100
})

// 计算状态
const isCalculating = ref(false)
const progress = ref(0)
const progressText = ref('')

// 更新参数
const updateParams = () => {
  // 实时更新参数并触发计算
  const requestData = {
    albedo_land: 0.3,
    albedo_ocean: 0.15,
    albedo_pv: panelTypes[params.panelType].albedo,
    coverage_ratio: params.coverageRatio,
    co2_current: params.co2Current,
    initial_temp: 15.0,
    simulation_years: params.simulationYears,
    pv_efficiency: panelTypes[params.panelType].efficiency
  }

  // 实时触发计算（不显示进度条）
  emit('simulationStart', requestData)
}

// 应用预设场景
const applyScenario = (scenario) => {
  Object.assign(params, scenario)
  // 应用场景后立即触发计算
  updateParams()
}

// 开始模拟
const startSimulation = () => {
  isCalculating.value = true
  progress.value = 0
  progressText.value = '正在初始化...'

  const requestData = {
    albedo_land: 0.3,
    albedo_ocean: 0.15,
    albedo_pv: panelTypes[params.panelType].albedo,
    coverage_ratio: params.coverageRatio,
    co2_current: params.co2Current,
    initial_temp: 8.0,
    simulation_years: params.simulationYears,
    pv_efficiency: panelTypes[params.panelType].efficiency
  }

  emit('simulationStart', requestData)
}

// 重置参数
const resetParams = () => {
  Object.assign(params, {
    panelType: 'new',
    coverageRatio: 1e-8,
    co2Current: 420,
    simulationYears: 100
  })
}

// 导出配置
const exportConfig = () => {
  const config = {
    ...params,
    albedo_pv: panelTypes[params.panelType].albedo,
    efficiency: panelTypes[params.panelType].efficiency
  }
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pv-climate-config-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.control-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-item {
  margin-bottom: 15px;
}

.form-item-label {
  display: block;
  font-size: 14px;
  color: #4a5568;
  margin-bottom: 8px;
  font-weight: 500;
}

.action-buttons {
  margin-top: auto;
}

.progress-display {
  margin-top: 15px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
