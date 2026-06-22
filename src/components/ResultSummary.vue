<template>
  <div class="result-summary">
    <div class="info-card">
      <div class="info-card-title">📈 模拟结果摘要</div>

      <div v-if="!data" class="no-result">
        <el-icon size="32"><Document /></el-icon>
        <p>暂无结果</p>
      </div>

      <div v-else class="result-content">
        <!-- 主要结果 -->
        <div class="main-result">
          <div class="result-title">温度变化</div>
          <div class="result-value" :class="tempChangeClass">
            {{ tempChangeText }}
          </div>
          <div class="result-description">
            {{ tempDescription }}
          </div>
        </div>

        <!-- 详细数据 -->
        <div class="detail-results">
          <div class="detail-item">
            <div class="detail-label">基准平衡温度</div>
            <div class="detail-value">{{ data.baseline.equilibrium_temp.toFixed(2) }}°C</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">光伏平衡温度</div>
            <div class="detail-value highlight">{{ data.pv_scenario.equilibrium_temp.toFixed(2) }}°C</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">平衡时间</div>
            <div class="detail-value">{{ data.pv_scenario.equilibrium_time }}年</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">CO2减排</div>
            <div class="detail-value success">{{ data.pv_scenario.co2_reduction.toFixed(2) }}ppm</div>
          </div>
        </div>

        <!-- 效果评级 -->
        <div class="effect-rating">
          <div class="rating-label">综合效果评级</div>
          <div class="rating-stars">
            <span
              v-for="i in 5"
              :key="i"
              class="star"
              :class="{ active: i <= ratingStars }"
            >★</span>
          </div>
          <div class="rating-text">{{ ratingText }}</div>
        </div>
      </div>
    </div>

    <!-- 科学意义 -->
    <div class="info-card">
      <div class="info-card-title">🔬 科学意义</div>

      <div class="science-points">
        <div class="point-item">
          <div class="point-icon">🌡️</div>
          <div class="point-text">
            <div class="point-title">气候调节</div>
            <div class="point-desc">反照率效应：高反照率面板可降低地表温度</div>
          </div>
        </div>

        <div class="point-item">
          <div class="point-icon">🌿</div>
          <div class="point-text">
            <div class="point-title">碳减排</div>
            <div class="point-desc">光伏发电替代化石燃料，减少温室气体排放</div>
          </div>
        </div>

        <div class="point-item">
          <div class="point-icon">⚖️</div>
          <div class="point-text">
            <div class="point-title">双重效应</div>
            <div class="point-desc">新型面板同时产生降温+减排双重气候效益</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出功能 -->
    <div class="info-card">
      <div class="info-card-title">📥 数据导出</div>

      <div class="export-buttons">
        <button class="export-button" @click="exportData('json')">
          📄 JSON格式
        </button>
        <button class="export-button" @click="exportData('csv')">
          📊 CSV格式
        </button>
        <button class="export-button" @click="exportData('pdf')">
          📑 PDF报告
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: Object
})

// 温度变化计算
const tempChange = computed(() => {
  if (!props.data) return 0
  return props.data.comparison.temperature_change
})

// 温度变化样式
const tempChangeClass = computed(() => {
  if (!props.data) return ''
  return props.data.comparison.cooling_effect ? 'cooling' : 'warming'
})

// 温度变化文本
const tempChangeText = computed(() => {
  if (!props.data) return '-'
  const change = tempChange.value
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}°C`
})

// 温度描述
const tempDescription = computed(() => {
  if (!props.data) return ''
  const change = Math.abs(tempChange.value)
  if (change < 0.1) return '变化很小'
  if (change < 0.5) return '轻微降温'
  if (change < 1.0) return '明显降温'
  if (change < 2.0) return '显著降温'
  return '大幅降温'
})

// 评级星级
const ratingStars = computed(() => {
  if (!props.data) return 0
  const change = Math.abs(tempChange.value)
  if (change >= 2.0) return 5
  if (change >= 1.0) return 4
  if (change >= 0.5) return 3
  if (change >= 0.1) return 2
  return 1
})

// 评级文本
const ratingText = computed(() => {
  const stars = ratingStars.value
  if (stars === 5) return '优秀'
  if (stars === 4) return '良好'
  if (stars === 3) return '中等'
  if (stars === 2) return '较弱'
  return '微弱'
})

// 导出数据
const exportData = (format) => {
  if (!props.data) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  // 模拟导出
  ElMessage.success(`正在导出${format.toUpperCase()}格式...`)

  // 实际应用中这里会调用API生成文件
  console.log(`Exporting as ${format}:`, props.data)
}
</script>

<style scoped>
.result-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.no-result {
  text-align: center;
  color: #a0aec0;
  padding: 20px 0;
}

.no-result p {
  margin: 10px 0 0 0;
  font-size: 14px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.main-result {
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 8px;
}

.result-title {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.result-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.result-value.cooling {
  background: linear-gradient(135deg, #10b981, #059669);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.result-value.warming {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.result-description {
  font-size: 14px;
  color: #475569;
}

.detail-results {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.detail-item {
  background: #f8fafc;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
}

.detail-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 5px;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.detail-value.highlight {
  color: #667eea;
}

.detail-value.success {
  color: #10b981;
}

.effect-rating {
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border-radius: 8px;
}

.rating-label {
  font-size: 12px;
  color: #92400e;
  margin-bottom: 8px;
}

.rating-stars {
  font-size: 20px;
  margin-bottom: 5px;
}

.star {
  color: #d1d5db;
  margin: 0 2px;
}

.star.active {
  color: #f59e0b;
}

.rating-text {
  font-size: 14px;
  font-weight: 600;
  color: #78350f;
}

.science-points {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.point-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.point-icon {
  font-size: 24px;
  line-height: 1;
}

.point-text {
  flex: 1;
}

.point-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 3px;
}

.point-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

.export-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.export-button {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  color: #475569;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.export-button:hover {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
  transform: translateY(-1px);
}
</style>
