<template>
  <nav class="top-nav">
    <div class="nav-left">
      <h1 class="software-title">{{ softwareTitle }}</h1>

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
import { ref, computed, onMounted } from 'vue'
import { useSettings } from '../composables/useSettings'

// 使用设置composable
const { settings, languages } = useSettings()

// 定义props和emits
const props = defineProps({
  currentTab: {
    type: String,
    default: 'dashboard'
  }
})

const emit = defineEmits(['tabChange'])

// 导航标签 - 使用计算属性根据语言设置动态生成
const tabs = computed(() => [
  { id: 'dashboard', name: languages[settings.language]['nav.dashboard'] },
  { id: 'simulation', name: languages[settings.language]['nav.simulation'] },
  { id: 'history', name: languages[settings.language]['nav.history'] },
  { id: 'settings', name: languages[settings.language]['nav.settings'] }
])

// 软件标题 - 根据语言动态变化
const softwareTitle = computed(() => {
  if (settings.language === 'en') {
    return '⚡ PV Climate Effect Simulator - Dashboard'
  }
  return '⚡ 光伏热效应模拟器 - 仪表板'
})

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
  hasNotifications.value = false
}

// 显示设置
const showSettings = () => {
  emit('tabChange', 'settings')
}

// 复制URL
const copyUrl = () => {
  navigator.clipboard.writeText(browserUrl.value)
}

// 刷新页面
const refreshPage = () => {
  location.reload()
}

// 监听语言变化事件
onMounted(() => {
  window.addEventListener('languageChanged', (event) => {
    console.log('TopNav收到语言变化事件:', event.detail.language)
  })
})
</script>

<style scoped>
/* 顶部导航栏样式 */
.top-nav {
  height: 60px;
  background: #131829;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  z-index: 100;
  transition: background 0.3s ease;
}

.top-nav.light-theme {
  background: linear-gradient(135deg, rgba(245, 247, 250, 0.9), rgba(195, 207, 226, 0.9));
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.software-title {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #00d9ff, #4a9eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
  letter-spacing: 1px;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.nav-tabs {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-tab {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-tab.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.browser-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.browser-bar input {
  background: transparent;
  border: none;
  color: white;
  font-size: 12px;
  width: 180px;
  outline: none;
}

.browser-bar input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.browser-action {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.browser-action:hover {
  opacity: 1;
}

.nav-icon {
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background: #ff5747;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-avatar {
  font-size: 16px;
}

.user-name {
  color: white;
  font-size: 13px;
  font-weight: 500;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .software-title {
    display: none;
  }

  .browser-bar {
    display: none;
  }
}
</style>