<template>
  <nav class="top-nav">
    <div class="nav-left">
      <h1 class="software-title">⚡ 光伏热效应模拟器 - 仪表板</h1>

      <div class="nav-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-tab', { active: currentTab === tab.id }]"
          @click="switchTab(tab.id)"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <div class="nav-right">
      <!-- 浏览器地址栏模拟 -->
      <div class="browser-bar">
        <span>🌐</span>
        <input
          type="text"
          :value="browserUrl"
          readonly
          @click="copyUrl"
        />
        <button class="browser-action" @click="refreshPage" title="刷新页面">
          🔄
        </button>
      </div>

      <!-- 控制图标 -->
      <button class="nav-icon" @click="showNotifications" title="通知">
        <span>🔔</span>
        <span v-if="hasNotifications" class="notification-badge"></span>
      </button>

      <button class="nav-icon" @click="showSettings" title="设置">
        <span>⚙️</span>
      </button>

      <!-- 用户信息 -->
      <div class="user-info">
        <span class="user-avatar">👤</span>
        <span class="user-name">科研用户</span>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

// 定义props和emits
const props = defineProps({
  currentTab: {
    type: String,
    default: 'dashboard'
  }
})

const emit = defineEmits(['tabChange'])

// 导航标签
const tabs = [
  { id: 'dashboard', name: '仪表板' },
  { id: 'simulation', name: '模拟' },
  { id: 'history', name: '历史' },
  { id: 'settings', name: '设置' }
]

// 浏览器栏URL
const browserUrl = ref('doshaard dashboard.nci')

// 是否有未读通知
const hasNotifications = ref(true)

// 切换标签页
const switchTab = (tabId) => {
  emit('tabChange', tabId)
}

// 显示通知
const showNotifications = () => {
  console.log('显示通知面板')
  // 这里可以添加通知面板逻辑
  hasNotifications.value = false
}

// 显示设置
const showSettings = () => {
  emit('tabChange', 'settings')
}

// 复制URL
const copyUrl = () => {
  navigator.clipboard.writeText(browserUrl.value)
  console.log('URL已复制')
}

// 刷新页面
const refreshPage = () => {
  location.reload()
}
</script>

<style scoped>
/* 顶部导航栏样式 */
.top-nav {
  height: 60px;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  box-shadow: var(--shadow-md);
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.software-title {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-cyan), var(--color-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
  letter-spacing: 1px;
  white-space: nowrap;
}

.nav-tabs {
  display: flex;
  gap: var(--spacing-xs);
  background: var(--bg-primary);
  padding: var(--spacing-xs);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.nav-tab {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: 14px;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  white-space: nowrap;
}

.nav-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-tab.active {
  color: var(--color-cyan);
  background: var(--bg-tertiary);
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: var(--color-cyan);
  border-radius: 1px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.browser-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: var(--bg-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 12px;
  color: var(--text-tertiary);
}

.browser-bar input {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 12px;
  width: 180px;
  outline: none;
  cursor: pointer;
}

.browser-bar input:focus {
  color: var(--text-primary);
}

.browser-action {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.browser-action:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.nav-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.nav-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--color-blue);
  box-shadow: var(--shadow-glow-blue);
}

.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: var(--color-red);
  border-radius: 50%;
  border: 1px solid var(--bg-secondary);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-info:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.user-avatar {
  font-size: 16px;
}

.user-name {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}
</style>
