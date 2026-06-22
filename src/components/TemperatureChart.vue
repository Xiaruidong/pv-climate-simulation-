<template>
  <div class="temperature-chart">
    <div class="info-card-title">🌡️ 地表温度演变</div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>计算中，请稍候...</p>
    </div>

    <div v-else-if="data" class="chart-container">
      <div ref="chartRef" style="width: 100%; height: 100%; min-height: 300px;"></div>
    </div>

    <div v-else class="empty-state">
      <el-icon size="48"><DataAnalysis /></el-icon>
      <p>请配置参数并开始模拟</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Loading, DataAnalysis } from '@element-plus/icons-vue'

const props = defineProps({
  data: Object,
  loading: Boolean
})

const chartRef = ref(null)
let chartInstance = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
}

// 更新图表
const updateChart = () => {
  if (!props.data || !chartInstance) return

  const baseline = props.data.baseline
  const pv = props.data.pv_scenario

  const years = Array.from({ length: baseline.temperature_series.length }, (_, i) => i)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let result = `第 ${params[0].axisValue} 年<br/>`
        params.forEach(param => {
          result += `${param.marker}${param.seriesName}: ${param.value.toFixed(2)}°C<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['基准情景', '光伏建设情景'],
      textStyle: { color: '#4a5568' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      name: '年份',
      nameTextStyle: { color: '#718096' },
      data: years,
      axisLine: { lineStyle: { color: '#cbd5e0' } },
      axisLabel: { color: '#718096' }
    },
    yAxis: {
      type: 'value',
      name: '温度 (°C)',
      nameTextStyle: { color: '#718096' },
      axisLine: { lineStyle: { color: '#cbd5e0' } },
      axisLabel: { color: '#718096' },
      splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
    },
    series: [
      {
        name: '基准情景',
        type: 'line',
        data: baseline.temperature_series,
        smooth: true,
        lineStyle: { color: '#f59e0b', width: 2 },
        itemStyle: { color: '#f59e0b' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
          ])
        }
      },
      {
        name: '光伏建设情景',
        type: 'line',
        data: pv.temperature_series,
        smooth: true,
        lineStyle: { color: '#667eea', width: 2 },
        itemStyle: { color: '#667eea' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 监听数据变化
watch(() => props.data, (newData) => {
  if (newData) {
    nextTick(() => {
      updateChart()
    })
  }
}, { deep: true })

// 监听加载状态
watch(() => props.loading, (loading) => {
  if (!loading && props.data) {
    nextTick(() => {
      if (!chartInstance) {
        initChart()
      }
      updateChart()
    })
  }
})

// 组件挂载
import { onMounted } from 'vue'
onMounted(() => {
  initChart()
})
</script>

<style scoped>
.temperature-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
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

.loading-state .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
  color: #667eea;
}

.empty-state .el-icon {
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.chart-container {
  flex: 1;
  min-height: 0;
}
</style>
