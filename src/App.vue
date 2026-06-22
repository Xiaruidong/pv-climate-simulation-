<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <TopNav
      :current-tab="currentPage"
      @tab-change="handleTabChange"
    />

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 仪表板页面 (默认页面) -->
      <div v-show="currentPage === 'dashboard'" class="page-container dashboard-page">
        <main class="dashboard-main">
          <!-- 左侧参数控制面板 -->
          <ParameterPanel @simulate="handleSimulation" />

          <!-- 中央3D可视化主视图区 -->
          <Visualization3D ref="visualization" />

          <!-- 右侧指标与趋势面板 -->
          <MetricsPanel />
        </main>
      </div>

      <!-- 模拟页面 -->
      <div v-show="currentPage === 'simulation'" class="page-container">
        <SimulationPage />
      </div>

      <!-- 历史页面 -->
      <div v-show="currentPage === 'history'" class="page-container">
        <HistoryPage />
      </div>

      <!-- 设置页面 -->
      <div v-show="currentPage === 'settings'" class="page-container">
        <SettingsPage />
      </div>
    </main>

    <!-- 全局通知/Toast -->
    <transition name="slide-fade">
      <div v-if="notification.show" :class="['global-notification', notification.type]">
        <div class="notification-content">
          <span class="notification-icon">{{ notification.icon }}</span>
          <span class="notification-message">{{ notification.message }}</span>
        </div>
        <button class="notification-close" @click="dismissNotification">✕</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopNav from './components/TopNav.vue'
import ParameterPanel from './components/ParameterPanel.vue'
import Visualization3D from './components/Visualization3D.vue'
import MetricsPanel from './components/MetricsPanel.vue'
import SimulationPage from './components/SimulationPage.vue'
import HistoryPage from './components/HistoryPage.vue'
import SettingsPage from './components/SettingsPage.vue'
import { useSimulation } from './composables/useSimulation'

// 初始化模拟状态
const {
  triggerCalculation,
  setScenario,
  simulationState
} = useSimulation()

// 当前页面状态
const currentPage = ref('dashboard')
const visualization = ref(null)

// 通知系统
const notification = ref({
  show: false,
  type: 'info',
  icon: 'ℹ️',
  message: '',
  duration: 3000
})

// 页面切换处理
const handleTabChange = (tabId) => {
  currentPage.value = tabId
  console.log('页面切换到:', tabId)

  // 显示切换提示
  const pageNames = {
    dashboard: '仪表板',
    simulation: '模拟',
    history: '历史',
    settings: '设置'
  }

  showNotification('info', `已切换到${pageNames[tabId]}页面`, '📄')
}

// 处理模拟启动
const handleSimulation = async (params) => {
  console.log('参数更新触发:', params)

  // 验证参数（使用新参数名）
  if (params.albedo_pv > 1 || params.albedo_pv < 0) {
    showNotification('error', '光伏反照率值无效，必须在0-1之间', '⚠️')
    return
  }

  // 验证覆盖率
  if (params.coverage_ratio < 0 || params.coverage_ratio > 0.01) {
    showNotification('warning', '覆盖率超出建议范围 (0-0.01%)', '⚠️')
  }

  try {
    // 直接传递参数（新ParameterPanel已经使用与后端一致的参数名）
    const backendParams = {
      albedo_pv: params.albedo_pv ?? 0.438,
      coverage_ratio: params.coverage_ratio ?? 1e-8,
      pv_efficiency: params.pv_efficiency ?? 0.23,
      albedo_land: params.albedo_land ?? 0.35,
      albedo_ocean: params.albedo_ocean ?? 0.06,
      co2_current: params.co2_current ?? 420.0,
      initial_temp: params.initial_temp ?? 15.0,
      simulation_years: params.simulation_years ?? 100
    }

    console.log('传递给计算的参数:', backendParams)

    // 更新模拟状态
    simulationState.params = backendParams

    // 触发计算
    await triggerCalculation()

    // 显示成功通知
    showNotification('success', '真实物理计算完成！3D可视化已更新', '✅')

  } catch (error) {
    console.error('Simulation error:', error)
    showNotification('error', `计算失败: ${error.message}`, '❌')
  }
}

// 显示通知
const showNotification = (type, message, icon = 'ℹ️') => {
  notification.value.type = type
  notification.value.message = message
  notification.value.icon = icon
  notification.value.show = true

  setTimeout(() => {
    notification.value.show = false
  }, notification.value.duration)
}

// 关闭通知
const dismissNotification = () => {
  notification.value.show = false
}

// 组件挂载完成
onMounted(() => {
  // 初始化模拟计算
  triggerCalculation()

  // 欢迎消息
  setTimeout(() => {
    showNotification('info', '欢迎使用光伏热效应模拟器 - 已加载真实物理常数', '👋')
  }, 1000)

  // 监听设置页面的导航事件
  window.addEventListener('navigateToDashboard', () => {
    currentPage.value = 'dashboard'
    showNotification('info', '已返回主界面', '🏠')
  })

  // 监听设置更新事件
  window.addEventListener('settingsUpdated', (event) => {
    console.log('设置已更新:', event.detail)
    showNotification('success', '系统设置已更新', '✨')
  })
})
</script>

<style>
/* 导入深色科技风样式 */
@import './styles/dashboard.css';

/* 页面容器样式 */
.page-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-page {
  padding: var(--spacing-md);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 动画效果 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* 全局通知样式 */
.global-notification {
  position: fixed;
  top: 80px;
  right: 20px;
  min-width: 300px;
  max-width: 400px;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.global-notification.info {
  background: rgba(74, 158, 255, 0.15);
  border: 1px solid rgba(74, 158, 255, 0.5);
}

.global-notification.success {
  background: rgba(0, 255, 157, 0.15);
  border: 1px solid rgba(0, 255, 157, 0.5);
}

.global-notification.error {
  background: rgba(255, 71, 87, 0.15);
  border: 1px solid rgba(255, 71, 87, 0.5);
}

.global-notification.warning {
  background: rgba(255, 157, 0, 0.15);
  border: 1px solid rgba(255, 157, 0, 0.5);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-icon {
  font-size: 20px;
}

.notification-message {
  font-size: 14px;
  color: var(--text-primary);
}

.notification-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.notification-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

/* 确保页面填满容器 */
.app-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-content > div {
  flex: 1;
  overflow: hidden;
}
</style>
