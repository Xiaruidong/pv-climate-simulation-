<template>
  <div class="visualization-area">
    <canvas
      ref="canvas"
      class="visualization-canvas"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @wheel="onZoom"
    ></canvas>

    <!-- 视图控制按钮 -->
    <div class="view-controls">
      <button
        v-for="view in viewModes"
        :key="view.id"
        :class="['view-button', { active: currentView === view.id }]"
        @click="setView(view.id)"
      >
        {{ view.label }}
      </button>
    </div>

    <!-- 垂直颜色标尺 -->
    <div class="color-scale"></div>
    <div class="color-scale-labels">
      <span>+45°C</span>
      <span>+30°C</span>
      <span>+15°C</span>
      <span>0°C</span>
      <span>-15°C</span>
      <span>-32°C</span>
    </div>

    <!-- 底部说明文字 -->
    <div class="visualization-caption">
      <span>🎯</span>
      <span>3D 实时可视化</span>
      <span v-if="showRealData" class="live-indicator">● 实时计算</span>
      <span v-else class="demo-indicator">○ 演示模式</span>
      <span style="margin-left: auto;">FPS: {{ fps }}</span>
    </div>

    <!-- 数据控制面板 -->
    <div class="data-controls">
      <button
        :class="['control-btn', { active: showRealData }]"
        @click="showRealData = !showRealData"
      >
        {{ showRealData ? '🔬 真实数据' : '🎭 演示模式' }}
      </button>
      <div v-if="showRealData" class="data-summary">
        <div class="data-item">
          <span>温度变化:</span>
          <span :class="{ cooling: temperatureChange < 0, warming: temperatureChange > 0 }">
            {{ temperatureChange !== undefined ? temperatureChange.toFixed(4) : '---' }}°C
          </span>
        </div>
        <div class="data-item">
          <span>CO₂减排:</span>
          <span>{{ co2Reduction !== undefined ? co2Reduction.toFixed(4) : '---' }} ppm</span>
        </div>
        <div class="data-item">
          <span>冷却效率:</span>
          <span>{{ coolingEfficiency !== undefined ? coolingEfficiency.toFixed(4) : '---' }}%</span>
        </div>
      </div>
    </div>

    <!-- 参数信息面板 -->
    <div class="params-panel">
      <div class="panel-title">📊 输入参数</div>
      <div class="params-grid">
        <div class="param-item">
          <span class="param-label">反照率:</span>
          <span class="param-value">{{ (simulationState.params?.albedo_pv || 0.438).toFixed(3) }}</span>
        </div>
        <div class="param-item">
          <span class="param-label">覆盖率:</span>
          <span class="param-value">{{ formatCoverage(simulationState.params?.coverage_ratio || 1e-8) }}</span>
        </div>
        <div class="param-item">
          <span class="param-label">效率:</span>
          <span class="param-value">{{ ((simulationState.params?.pv_efficiency || 0.23) * 100).toFixed(1) }}%</span>
        </div>
        <div class="param-item">
          <span class="param-label">CO₂:</span>
          <span class="param-value">{{ (simulationState.params?.co2_current || 420).toFixed(0) }} ppm</span>
        </div>
      </div>
    </div>

    <!-- 计算结果面板 -->
    <div class="results-panel">
      <div class="panel-title">📈 计算结果</div>
      <div class="results-grid">
        <div class="result-item">
          <span class="result-label">温度变化:</span>
          <span :class="['result-value', temperatureChange < 0 ? 'cooling' : 'warming']">
            {{ (temperatureChange || 0).toFixed(4) }}°C
          </span>
        </div>
        <div class="result-item">
          <span class="result-label">CO₂减排:</span>
          <span class="result-value success">
            {{ (co2Reduction || 0).toFixed(4) }} ppm
          </span>
        </div>
        <div class="result-item">
          <span class="result-label">反照率变化:</span>
          <span class="result-value">
            {{ ((albedoChange || 0) * 10000).toFixed(4) }}
          </span>
        </div>
        <div class="result-item">
          <span class="result-label">冷却效率:</span>
          <span class="result-value success">
            {{ (coolingEfficiency || 0).toFixed(4) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="legend-panel">
      <div class="legend-title">图例</div>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-color" style="background: #1a1f38;"></div>
          <span>光伏面板</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background: #c2b280;"></div>
          <span>沙漠地表</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background: linear-gradient(90deg, #4a9eff, #ff4757);"></div>
          <span>温度热图</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useSimulation } from '@/composables/useSimulation'

// 使用模拟状态
const {
  visualizationData,
  temperatureChange,
  albedoChange,
  co2Reduction,
  coolingEffect,
  coolingEfficiency,
  simulationState
} = useSimulation()

const canvas = ref(null)
let ctx = null
let animationId = null

const currentView = ref('3D')
const fps = ref(60)
const showRealData = ref(true)

const viewModes = [
  { id: '3D', label: '3D' },
  { id: 'RD', label: 'RD' },
  { id: 'Haan', label: 'Haan' }
]

// 3D 场景参数
const scene = {
  rotation: { x: 30, y: 45 },
  zoom: 1,
  pan: { x: 0, y: 0 },
  isDragging: false,
  lastMouse: { x: 0, y: 0 }
}

// 光伏面板数据
const solarPanels = []
const gridSize = 20

// 初始化光伏面板位置
const initSolarPanels = () => {
  for (let x = 0; x < gridSize; x++) {
    for (let z = 0; z < gridSize; z++) {
      solarPanels.push({
        x: (x - gridSize / 2) * 15,
        y: 0,
        z: (z - gridSize / 2) * 15,
        width: 12,
        height: 8,
        temperature: 25, // 初始温度
        temperatureChange: 0,
        baseTemperature: 25
      })
    }
  }
}

// 根据计算结果更新温度场
const updateTemperatureField = () => {
  if (!showRealData.value || !visualizationData.temperatureField.length) {
    // 使用随机温度
    solarPanels.forEach(panel => {
      panel.temperature = panel.baseTemperature + Math.random() * 20
      panel.temperatureChange = 0
    })
    return
  }

  // 使用真实计算结果
  const tempField = visualizationData.temperatureField
  const baselineTemp = simulationState.results?.baseline?.equilibrium_temp || 15.0

  solarPanels.forEach((panel, index) => {
    if (index < tempField.length) {
      const fieldData = tempField[index]
      panel.temperature = baselineTemp + fieldData.temperature
      panel.temperatureChange = fieldData.temperatureChange
    }
  })
}

// 监听计算结果变化
watch(() => visualizationData.temperatureField, () => {
  updateTemperatureField()
}, { deep: true })

// 监听温度变化
watch(temperatureChange, (newChange) => {
  if (showRealData.value) {
    updateTemperatureField()
  }
})

// 3D 投影函数
const project3D = (x, y, z) => {
  const radX = (scene.rotation.x * Math.PI) / 180
  const radY = (scene.rotation.y * Math.PI) / 180

  // 旋转 Y 轴
  const x1 = x * Math.cos(radY) - z * Math.sin(radY)
  const z1 = x * Math.sin(radY) + z * Math.cos(radY)

  // 旋转 X 轴
  const y1 = y * Math.cos(radX) - z1 * Math.sin(radX)
  const z2 = y * Math.sin(radX) + z1 * Math.cos(radX)

  // 透视投影
  const scale = 600 / (z2 + 500) * scene.zoom

  return {
    x: x1 * scale + scene.pan.x + canvas.value.width / 2,
    y: y1 * scale + scene.pan.y + canvas.value.height / 2,
    scale: scale,
    z: z2
  }
}

// 获取温度颜色
const getTemperatureColor = (temp) => {
  const normalizedTemp = (temp + 32) / 77 // -32 to +45 -> 0 to 1

  if (normalizedTemp < 0.2) {
    // 冷色：蓝色到青色
    const t = normalizedTemp / 0.2
    return `rgb(${74 * t}, ${158 * (1 - t) + 217 * t}, ${255})`
  } else if (normalizedTemp < 0.5) {
    // 中等：青色到绿色
    const t = (normalizedTemp - 0.2) / 0.3
    return `rgb(${74 * (1 - t)}, ${255}, ${217 * (1 - t) + 157 * t})`
  } else if (normalizedTemp < 0.8) {
    // 暖色：绿色到橙色
    const t = (normalizedTemp - 0.5) / 0.3
    return `rgb(${255 * t}, ${217 * (1 - t) + 157 * t}, ${89 * t})`
  } else {
    // 热色：橙色到红色
    const t = (normalizedTemp - 0.8) / 0.2
    return `rgb(${255}, ${157 * (1 - t) + 87 * t}, ${87 * t})`
  }
}

// 格式化覆盖率显示
const formatCoverage = (value) => {
  if (!value && value !== 0) return '---'
  const num = parseFloat(value)
  if (num >= 0.01) return `${(num * 100).toFixed(4)}%`
  if (num >= 0.001) return `${(num * 100).toFixed(5)}%`
  return `${(num * 100).toExponential(2)}`
}

// 绘制沙漠地表
const drawGround = () => {
  const groundColor = '#c2b280'
  const gridColor = '#a89868'

  // 绘制网格地面
  const gridSize = 300
  const divisions = 20

  ctx.strokeStyle = gridColor
  ctx.lineWidth = 1

  for (let i = 0; i <= divisions; i++) {
    const pos1 = project3D(-gridSize / 2, 20, -gridSize / 2 + (i * gridSize) / divisions)
    const pos2 = project3D(gridSize / 2, 20, -gridSize / 2 + (i * gridSize) / divisions)

    ctx.beginPath()
    ctx.moveTo(pos1.x, pos1.y)
    ctx.lineTo(pos2.x, pos2.y)
    ctx.stroke()

    const pos3 = project3D(-gridSize / 2 + (i * gridSize) / divisions, 20, -gridSize / 2)
    const pos4 = project3D(-gridSize / 2 + (i * gridSize) / divisions, 20, gridSize / 2)

    ctx.beginPath()
    ctx.moveTo(pos3.x, pos3.y)
    ctx.lineTo(pos4.x, pos4.y)
    ctx.stroke()
  }
}

// 绘制光伏面板
const drawSolarPanels = () => {
  // 按 Z 坐标排序以正确处理遮挡
  const sortedPanels = [...solarPanels].sort((a, b) => {
    const posA = project3D(a.x, a.y, a.z)
    const posB = project3D(b.x, b.y, b.z)
    return posB.z - posA.z
  })

  sortedPanels.forEach(panel => {
    const pos = project3D(panel.x, panel.y, panel.z)
    const size = panel.width * pos.scale

    // 面板阴影
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'
    ctx.fillRect(
      pos.x + size * 0.1,
      pos.y + size * 0.1,
      size,
      size * 0.6
    )

    // 面板主体
    const gradient = ctx.createLinearGradient(
      pos.x, pos.y,
      pos.x, pos.y + size * 0.6
    )
    gradient.addColorStop(0, '#1a1f38')
    gradient.addColorStop(1, '#2a3a5c')

    ctx.fillStyle = gradient
    ctx.fillRect(
      pos.x,
      pos.y,
      size,
      size * 0.6
    )

    // 面板边框
    ctx.strokeStyle = '#4a9eff'
    ctx.lineWidth = 1
    ctx.strokeRect(
      pos.x,
      pos.y,
      size,
      size * 0.6
    )

    // 温度热图叠加
    const tempColor = getTemperatureColor(panel.temperature)
    ctx.fillStyle = tempColor.replace('rgb', 'rgba').replace(')', ', 0.3)')
    ctx.fillRect(
      pos.x,
      pos.y,
      size,
      size * 0.6
    )

    // 面板高光
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.fillRect(
      pos.x,
      pos.y,
      size,
      size * 0.1
    )
  })
}

// 绘制信息指示器
const drawInfoIndicators = () => {
  // 绘制实时计算数据指示器
  const tempChange = temperatureChange.value || 0
  const albChange = albedoChange.value || 0
  const co2Red = co2Reduction.value || 0
  const coolEffect = coolingEffect.value || false
  const coolEff = coolingEfficiency.value || 0

  const positions = [
    { x: -100, z: -100, label: '温度变化', value: `${tempChange.toFixed(4)}°C` },
    { x: 100, z: -100, label: '反照率变化', value: `${(albChange * 10000).toFixed(4)}` },
    { x: 0, z: -120, label: 'CO₂减排', value: `${co2Red.toFixed(4)} ppm` },
    { x: 0, z: 100, label: '冷却效率', value: `${coolEff.toFixed(4)}%` }
  ]

  positions.forEach(pos => {
    const projected = project3D(pos.x, 30, pos.z)
    const color = '#4a9eff'

    // 绘制标签背景
    ctx.fillStyle = 'rgba(10, 14, 39, 0.8)'
    ctx.fillRect(projected.x - 40, projected.y - 10, 80, 25)

    // 绘制边框
    ctx.strokeStyle = color
    ctx.lineWidth = 1
    ctx.strokeRect(projected.x - 40, projected.y - 10, 80, 25)

    // 绘制标签文字
    ctx.fillStyle = '#aaaaaa'
    ctx.font = '10px Arial'
    ctx.fillText(pos.label, projected.x - 35, projected.y + 2)

    // 绘制数值
    ctx.fillStyle = color
    ctx.font = 'bold 11px Arial'
    ctx.fillText(pos.value, projected.x - 35, projected.y + 12)
  })
}

// 主渲染循环
const render = () => {
  if (!canvas.value || !ctx) return

  // 清除画布
  ctx.fillStyle = '#0a0e27'
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)

  // 绘制背景渐变
  const bgGradient = ctx.createRadialGradient(
    canvas.value.width / 2, canvas.value.height / 2, 0,
    canvas.value.width / 2, canvas.value.height / 2, canvas.value.width / 2
  )
  bgGradient.addColorStop(0, '#1a1f38')
  bgGradient.addColorStop(1, '#0a0e27')
  ctx.fillStyle = bgGradient
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)

  // 绘制3D场景
  drawGround()
  drawSolarPanels()
  drawInfoIndicators()

  // 更新FPS
  fps.value = Math.round(1000 / 16.67) // 假设60fps

  animationId = requestAnimationFrame(render)
}

// 鼠标交互
const startDrag = (e) => {
  scene.isDragging = true
  scene.lastMouse = { x: e.clientX, y: e.clientY }
}

const onDrag = (e) => {
  if (!scene.isDragging) return

  const deltaX = e.clientX - scene.lastMouse.x
  const deltaY = e.clientY - scene.lastMouse.y

  scene.rotation.y += deltaX * 0.5
  scene.rotation.x += deltaY * 0.5

  // 限制 X 轴旋转角度
  scene.rotation.x = Math.max(-60, Math.min(60, scene.rotation.x))

  scene.lastMouse = { x: e.clientX, y: e.clientY }
}

const endDrag = () => {
  scene.isDragging = false
}

const onZoom = (e) => {
  e.preventDefault()
  const zoomSpeed = 0.1
  scene.zoom += e.deltaY > 0 ? -zoomSpeed : zoomSpeed
  scene.zoom = Math.max(0.5, Math.min(3, scene.zoom))
}

const setView = (viewId) => {
  currentView.value = viewId

  switch (viewId) {
    case '3D':
      scene.rotation = { x: 30, y: 45 }
      break
    case 'RD':
      scene.rotation = { x: 0, y: 0 }
      break
    case 'Haan':
      scene.rotation = { x: 60, y: 30 }
      break
  }
}
onMounted(() => {
  if (canvas.value) {
    ctx = canvas.value.getContext('2d')
    initSolarPanels()
    updateTemperatureField()

    // 设置画布尺寸
    const resizeCanvas = () => {
      const rect = canvas.value.parentElement.getBoundingClientRect()
      canvas.value.width = rect.width
      canvas.value.height = rect.height
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // 开始渲染循环
    render()

    // 监听模拟更新事件
    window.addEventListener('simulation-updated', handleSimulationUpdate)
  }
})

// 处理模拟更新
const handleSimulationUpdate = (event) => {
  // 计算结果更新时重新计算温度场
  if (showRealData.value) {
    updateTemperatureField()
  }
}

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener('simulation-updated', handleSimulationUpdate)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  window.removeEventListener('resize', resizeCanvas)
})
</script>

<style scoped>
.visualization-area {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.visualization-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.visualization-canvas:active {
  cursor: grabbing;
}

.legend-panel {
  position: absolute;
  top: var(--spacing-md);
  left: var(--spacing-md);
  background: rgba(10, 14, 39, 0.8);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  backdrop-filter: blur(10px);
}

.legend-title {
  font-size: 12px;
  color: var(--color-cyan);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 11px;
  color: var(--text-secondary);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-primary);
}

.visualization-caption {
  position: absolute;
  bottom: var(--spacing-md);
  left: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 11px;
  color: var(--text-secondary);
  background: rgba(10, 14, 39, 0.6);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  backdrop-filter: blur(10px);
}

.live-indicator {
  color: var(--color-green);
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

.demo-indicator {
  color: var(--text-tertiary);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.data-controls {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  align-items: flex-end;
}

.control-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(10, 14, 39, 0.8);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all var(--transition-fast);
  backdrop-filter: blur(10px);
}

.control-btn:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.control-btn.active {
  background: rgba(74, 158, 255, 0.2);
  border-color: var(--color-cyan);
  color: var(--color-cyan);
}

.data-summary {
  background: rgba(10, 14, 39, 0.8);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  backdrop-filter: blur(10px);
  min-width: 150px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-md);
  font-size: 10px;
  padding: var(--spacing-xs) 0;
  border-bottom: 1px solid var(--border-secondary);
}

.data-item:last-child {
  border-bottom: none;
}

.data-item span:first-child {
  color: var(--text-tertiary);
}

.data-item span:last-child {
  color: var(--text-primary);
  font-weight: 600;
}

.data-item .cooling {
  color: var(--color-cyan);
}

.data-item .warming {
  color: var(--color-red);
}

.view-controls {
  position: absolute;
  bottom: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  gap: var(--spacing-xs);
}

.view-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(10, 14, 39, 0.8);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all var(--transition-fast);
  backdrop-filter: blur(10px);
}

.view-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.view-button.active {
  background: rgba(74, 158, 255, 0.2);
  border-color: var(--color-cyan);
  color: var(--color-cyan);
}

.color-scale {
  position: absolute;
  right: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 150px;
  background: linear-gradient(
    to bottom,
    #ff5747 0%,
    #ff9d47 25%,
    #d9a728 50%,
    #4ad97f 75%,
    #4a9eff 100%
  );
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-primary);
}

.color-scale-labels {
  position: absolute;
  right: calc(var(--spacing-md) + 12px);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  height: 150px;
  justify-content: space-between;
  font-size: 9px;
  color: var(--text-tertiary);
}

.params-panel {
  position: absolute;
  top: var(--spacing-md);
  left: var(--spacing-md);
  background: rgba(10, 14, 39, 0.9);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  backdrop-filter: blur(10px);
  min-width: 180px;
  z-index: 10;
}

.panel-title {
  font-size: 11px;
  color: var(--color-cyan);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid var(--border-secondary);
}

.params-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-xs);
}

.param-item {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  padding: 2px 0;
}

.param-label {
  color: var(--text-tertiary);
}

.param-value {
  color: var(--text-primary);
  font-weight: 600;
}

.results-panel {
  position: absolute;
  top: 160px;
  left: var(--spacing-md);
  background: rgba(10, 14, 39, 0.9);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  backdrop-filter: blur(10px);
  min-width: 180px;
  z-index: 10;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-xs);
}

.result-item {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  padding: 2px 0;
}

.result-label {
  color: var(--text-tertiary);
}

.result-value {
  color: var(--text-primary);
  font-weight: 600;
}

.result-value.cooling {
  color: var(--color-cyan);
}

.result-value.warming {
  color: var(--color-red);
}

.result-value.success {
  color: var(--color-green);
}
</style>
