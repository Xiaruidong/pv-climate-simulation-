<template>
  <div class="comparison-chart">
    <div class="info-card-title">📊 平衡状态对比</div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>计算中，请稍候...</p>
    </div>

    <div v-else-if="data" class="comparison-content">
      <div class="metrics-grid">
        <!-- 平衡温度对比 -->
        <div class="metric-card">
          <div class="metric-label">平衡温度</div>
          <div class="metric-value">
            <span class="baseline">{{ data.baseline.equilibrium_temp.toFixed(2) }}°C</span>
            <span class="arrow">→</span>
            <span :class="['pv', data.comparison.cooling_effect ? 'cooling' : 'warming']">
              {{ data.pv_scenario.equilibrium_temp.toFixed(2) }}°C
            </span>
          </div>
          <div class="metric-change">
            {{ data.comparison.temperature_change > 0 ? '+' : '' }}
            {{ data.comparison.temperature_change.toFixed(2) }}°C
            <el-tag :type="data.comparison.cooling_effect ? 'success' : 'danger'" size="small">
              {{ data.comparison.cooling_effect ? '降温' : '升温' }}
            </el-tag>
          </div>
        </div>

        <!-- 平衡时间对比 -->
        <div class="metric-card">
          <div class="metric-label">平衡时间</div>
          <div class="metric-value">
            <span class="baseline">{{ data.baseline.equilibrium_time }}年</span>
            <span class="arrow">→</span>
            <span class="pv">{{ data.pv_scenario.equilibrium_time }}年</span>
          </div>
          <div class="metric-change">
            差值: {{ data.pv_scenario.equilibrium_time - data.baseline.equilibrium_time }}年
          </div>
        </div>

        <!-- 反照率变化 -->
        <div class="metric-card">
          <div class="metric-label">行星反照率</div>
          <div class="metric-value">
            <span class="baseline">{{ data.baseline.planetary_albedo.toFixed(3) }}</span>
            <span class="arrow">→</span>
            <span class="pv">{{ data.pv_scenario.planetary_albedo.toFixed(3) }}</span>
          </div>
          <div class="metric-change">
            +{{ data.comparison.albedo_change.toFixed(3) }}
          </div>
        </div>

        <!-- CO2减排 -->
        <div class="metric-card highlight">
          <div class="metric-label">CO2减排效果</div>
          <div class="metric-value large">
            {{ data.pv_scenario.co2_reduction.toFixed(2) }} ppm
          </div>
          <div class="metric-description">
            相当于减少{{ (data.pv_scenario.co2_reduction * 7.82).toFixed(0) }}亿吨CO2排放
          </div>
        </div>
      </div>

      <!-- 效果评估 -->
      <div class="assessment-panel">
        <div class="assessment-title">🎯 综合效果评估</div>
        <div class="assessment-content">
          <div class="assessment-item">
            <div class="assessment-label">气候效应</div>
            <el-progress
              :percentage="effectPercentage"
              :color="effectColor"
              :show-text="false"
            />
            <div class="assessment-value" :style="{ color: effectColor }">
              {{ data.comparison.cooling_effect ? '降温效应' : '升温效应' }}
            </div>
          </div>

          <div class="assessment-item">
            <div class="assessment-label">可行性评估</div>
            <el-progress
              :percentage="feasibilityPercentage"
              :show-text="false"
              color="#67c23a"
            />
            <div class="assessment-value" style="color: #67c23a">
              {{ feasibilityLevel }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-icon size="48"><DataBoard /></el-icon>
      <p>暂无对比数据</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading, DataBoard } from '@element-plus/icons-vue'

const props = defineProps({
  data: Object,
  loading: Boolean
})

// 计算效果百分比
const effectPercentage = computed(() => {
  if (!props.data) return 0
  const change = Math.abs(props.data.comparison.temperature_change)
  return Math.min(change * 50, 100) // 假设2°C变化为100%
})

// 效果颜色
const effectColor = computed(() => {
  if (!props.data) return '#667eea'
  return props.data.comparison.cooling_effect ? '#67c23a' : '#f56c6c'
})

// 可行性百分比（基于覆盖面积）
const feasibilityPercentage = computed(() => {
  if (!props.data) return 0
  // 假设覆盖面积越小可行性越高
  const ratio = props.data.pv_scenario.co2_reduction // 作为代理指标
  return Math.max(0, 100 - ratio * 10)
})

// 可行性等级
const feasibilityLevel = computed(() => {
  const pct = feasibilityPercentage.value
  if (pct >= 80) return '高度可行'
  if (pct >= 60) return '基本可行'
  if (pct >= 40) return '需要规划'
  return '挑战较大'
})
</script>

<style scoped>
.comparison-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.comparison-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric-card {
  background: linear-gradient(135deg, #f5f7fa, #e4e7eb);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e2e8f0;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-card.highlight {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  grid-column: span 2;
}

.metric-label {
  font-size: 12px;
  color: #718096;
  margin-bottom: 8px;
}

.metric-card.highlight .metric-label {
  color: rgba(255, 255, 255, 0.8);
}

.metric-value {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.metric-value.large {
  font-size: 24px;
}

.metric-value .baseline {
  color: #f59e0b;
}

.metric-value .pv {
  color: #667eea;
}

.metric-value .pv.cooling {
  color: #67c23a;
}

.metric-value .pv.warming {
  color: #f56c6c;
}

.metric-value .arrow {
  color: #a0aec0;
  font-size: 14px;
}

.metric-change {
  font-size: 12px;
  color: #718096;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.metric-card.highlight .metric-change {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.metric-description {
  font-size: 12px;
  opacity: 0.9;
  text-align: center;
  margin-top: 5px;
}

.assessment-panel {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #bae6fd;
}

.assessment-title {
  font-size: 14px;
  font-weight: bold;
  color: #0369a1;
  margin-bottom: 12px;
}

.assessment-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assessment-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.assessment-label {
  font-size: 12px;
  color: #475569;
}

.assessment-value {
  font-size: 12px;
  font-weight: bold;
  text-align: right;
}

.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #a0aec0;
}

.empty-state p {
  font-size: 14px;
  margin: 10px 0 0 0;
}
</style>
