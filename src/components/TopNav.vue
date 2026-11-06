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
        <svg class="bar-icon" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        <input
          type="text"
          :value="browserUrl"
          readonly
          @click="copyUrl"
        />
        <button class="browser-action" @click="refreshPage" title="刷新页面">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
        </button>
      </div>

      <!-- 语言快捷切换 -->
      <button class="nav-icon lang-toggle" @click="toggleLanguage" :title="settings.language === 'zh' ? '切换到英文' : '切换到中文'">
        {{ settings.language === 'zh' ? 'EN' : '中' }}
      </button>

      <!-- 控制图标 -->
      <button class="nav-icon" @click="showNotifications" title="通知">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <span v-if="hasNotifications" class="notification-badge"></span>
      </button>

      <button class="nav-icon" @click="showSettings" title="设置">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="4" y1="21" x2="4" y2="14"></line>
          <line x1="4" y1="10" x2="4" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12" y2="3"></line>
          <line x1="20" y1="21" x2="20" y2="16"></line>
          <line x1="20" y1="12" x2="20" y2="3"></line>
          <line x1="1" y1="14" x2="7" y2="14"></line>
          <line x1="9" y1="8" x2="15" y2="8"></line>
          <line x1="17" y1="16" x2="23" y2="16"></line>
        </svg>
      </button>

      <!-- 用户信息 -->
      <div class="user-info">
        <svg class="user-avatar" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
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
    return ' PV Climate Effect Simulator - Dashboard'
  }
  return ' 光伏热效应模拟器 - 仪表板'
})

// 浏览器栏URL（装饰性展示文案）
const browserUrl = ref('光伏气候效应模拟系统 v2.0')

// 快捷切换中英文
const toggleLanguage = () => {
  settings.language = settings.language === 'zh' ? 'en' : 'zh'
}

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

.nav-icon svg,
.user-avatar,
.bar-icon,
.browser-action svg {
  display: block;
  color: rgba(255, 255, 255, 0.85);
}

.lang-toggle {
  font-size: 12px;
  font-weight: 600;
  color: #00d9ff;
  width: 34px;
  padding: 8px 0;
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
  color: rgba(255, 255, 255, 0.85);
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