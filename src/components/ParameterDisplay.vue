<template>
  <div class="parameter-display">
    <div class="info-card">
      <div class="info-card-title">🔧 当前参数</div>

      <div class="parameter-item">
        <span class="parameter-label">面板类型</span>
        <span class="parameter-value">{{ panelTypeNames[params.panelType] }}</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">面板反照率</span>
        <span class="parameter-value">{{ params.albedo_pv?.toFixed(3) || '-' }}</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">覆盖比例</span>
        <span class="parameter-value">{{ (params.coverage_ratio * 100).toFixed(2) }}%</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">CO2浓度</span>
        <span class="parameter-value">{{ params.co2_current }} ppm</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">模拟时长</span>
        <span class="parameter-value">{{ params.simulation_years }}年</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">光电效率</span>
        <span class="parameter-value">{{ (params.pv_efficiency * 100).toFixed(1) }}%</span>
      </div>
    </div>

    <div class="info-card">
      <div class="info-card-title">📐 物理参数</div>

      <div class="parameter-item">
        <span class="parameter-label">陆地反照率</span>
        <span class="parameter-value">0.300</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">海洋反照率</span>
        <span class="parameter-value">0.150</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">太阳常数</span>
        <span class="parameter-value">1361 W/m²</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">初始温度</span>
        <span class="parameter-value">8.00°C</span>
      </div>

      <div class="parameter-item">
        <span class="parameter-label">热容量</span>
        <span class="parameter-value">2.08×10⁸ J/°C</span>
      </div>
    </div>

    <div class="info-card">
      <div class="info-card-title">🌏 覆盖面积估算</div>

      <div class="area-calculation">
        <div class="area-value">
          <span class="number">{{ (params.coverage_ratio * 5.1).toFixed(3) }}</span>
          <span class="unit">亿km²</span>
        </div>
        <div class="area-breakdown">
          <div class="breakdown-item">
            <span class="label">陆地:</span>
            <span class="value">{{ (params.coverage_ratio * 1.48).toFixed(3) }}亿km²</span>
          </div>
          <div class="breakdown-item">
            <span class="label">海洋:</span>
            <span class="value">{{ (params.coverage_ratio * 3.62).toFixed(3) }}亿km²</span>
          </div>
        </div>
        <div class="area-comparison">
          相当于{{ areaComparison }}面积
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  params: {
    type: Object,
    default: () => ({})
  }
})

const panelTypeNames = {
  new: '新型透过+反射选择性',
  traditional: '传统光伏面板',
  mirror: '镜面反射型'
}

// 面积对比
const areaComparison = computed(() => {
  const ratio = props.params.coverage_ratio || 0
  const areaMillionKm2 = ratio * 510

  if (areaMillionKm2 < 1) {
    return `${(areaMillionKm2).toFixed(1)}个中国`
  } else if (areaMillionKm2 < 10) {
    return `${(areaMillionKm2 / 9.6).toFixed(1)}个中国`
  } else if (areaMillionKm2 < 50) {
    return `${(areaMillionKm2 / 9.6).toFixed(0)}个中国`
  } else {
    return `${(areaMillionKm2 / 510).toFixed(2)}个地球`
  }
})
</script>

<style scoped>
.parameter-display {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.parameter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.parameter-item:last-child {
  border-bottom: none;
}

.parameter-label {
  font-size: 13px;
  color: #718096;
}

.parameter-value {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.area-calculation {
  text-align: center;
}

.area-value {
  margin-bottom: 15px;
}

.area-value .number {
  font-size: 28px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.area-value .unit {
  font-size: 14px;
  color: #718096;
  margin-left: 5px;
}

.area-breakdown {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.breakdown-item .label {
  font-size: 12px;
  color: #a0aec0;
}

.breakdown-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.area-comparison {
  font-size: 12px;
  color: #718096;
  font-style: italic;
}
</style>
