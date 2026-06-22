import { ref, reactive, watch, onMounted } from 'vue'

// 全局设置状态
const settings = reactive({
  language: 'zh',
  theme: 'dark',
  animations: true,
  autoSave: true
})

// 语言包
const languages = {
  zh: {
    // 顶部导航
    'nav.dashboard': '仪表板',
    'nav.simulation': '模拟',
    'nav.history': '历史',
    'nav.settings': '设置',

    // 参数面板
    'panel.title': '参数控制面板',
    'panel.pv_system': '⚡ 光伏系统参数',
    'panel.albedo_pv': '光伏反照率',
    'panel.coverage_ratio': '覆盖率',
    'panel.pv_efficiency': '光伏效率',
    'panel.surface': '🌍 地表反照率参数',
    'panel.albedo_land': '陆地反照率',
    'panel.albedo_ocean': '海洋反照率',
    'panel.climate': '🌡 气候参数',
    'panel.co2_current': 'CO2浓度',
    'panel.initial_temp': '初始温度',
    'panel.simulation': '模拟设置',
    'panel.simulation_years': '模拟年数',
    'panel.calculate': '开始计算',

    // 结果面板
    'results.title': '计算结果',
    'results.temp_change': '温度变化',
    'results.albedo_change': '反照率变化',
    'results.cooling_effect': '冷却效果',
    'results.co2_reduction': 'CO2减少量',

    // 3D可视化
    'visualization.title': '3D可视化',
    'visualization.input_params': '输入参数',
    'visualization.results': '计算结果',
    'visualization.earth_model': '地球模型',

    // 设置页面
    'settings.title': '系统设置',
    'settings.subtitle': '配置模拟器参数和系统偏好',
    'settings.general': '通用设置',
    'settings.calculation': '计算设置',
    'settings.data': '数据管理',
    'settings.display': '显示设置',
    'settings.storage': '存储管理',
    'settings.about': '关于',
    'settings.save': '保存设置',
    'settings.reset': '重置设置',
    'settings.language': '语言',
    'settings.theme': '主题',
    'settings.dark': '深色科技风',
    'settings.light': '浅色简约风'
  },
  en: {
    // Top Navigation
    'nav.dashboard': 'Dashboard',
    'nav.simulation': 'Simulation',
    'nav.history': 'History',
    'nav.settings': 'Settings',

    // Parameter Panel
    'panel.title': 'Control Panel',
    'panel.pv_system': '⚡ PV System Parameters',
    'panel.albedo_pv': 'PV Albedo',
    'panel.coverage_ratio': 'Coverage Ratio',
    'panel.pv_efficiency': 'PV Efficiency',
    'panel.surface': '🌍 Surface Albedo Parameters',
    'panel.albedo_land': 'Land Albedo',
    'panel.albedo_ocean': 'Ocean Albedo',
    'panel.climate': '🌡 Climate Parameters',
    'panel.co2_current': 'CO2 Concentration',
    'panel.initial_temp': 'Initial Temperature',
    'panel.simulation': 'Simulation Settings',
    'panel.simulation_years': 'Simulation Years',
    'panel.calculate': 'Start Calculation',

    // Results Panel
    'results.title': 'Calculation Results',
    'results.temp_change': 'Temperature Change',
    'results.albedo_change': 'Albedo Change',
    'results.cooling_effect': 'Cooling Effect',
    'results.co2_reduction': 'CO2 Reduction',

    // 3D Visualization
    'visualization.title': '3D Visualization',
    'visualization.input_params': 'Input Parameters',
    'visualization.results': 'Calculation Results',
    'visualization.earth_model': 'Earth Model',

    // Settings Page
    'settings.title': 'System Settings',
    'settings.subtitle': 'Configure simulator parameters and system preferences',
    'settings.general': 'General Settings',
    'settings.calculation': 'Calculation Settings',
    'settings.data': 'Data Management',
    'settings.display': 'Display Settings',
    'settings.storage': 'Storage Management',
    'settings.about': 'About',
    'settings.save': 'Save Settings',
    'settings.reset': 'Reset Settings',
    'settings.language': 'Language',
    'settings.theme': 'Theme',
    'settings.dark': 'Dark Tech',
    'settings.light': 'Light Minimal'
  }
}

// 加载保存的设置
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (parsed.general) {
        Object.assign(settings, parsed.general)
      }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存设置
const saveSettings = () => {
  try {
    // 这里只保存通用设置，其他设置在各自的页面处理
    const generalSettings = {
      language: settings.language,
      theme: settings.theme,
      animations: settings.animations,
      autoSave: settings.autoSave
    }
    localStorage.setItem('userSettings', JSON.stringify({ general: generalSettings }))
    console.log('设置已保存:', generalSettings)
  } catch (error) {
    console.error('保存设置失败:', error)
  }
}

// 应用主题
const applyTheme = (theme) => {
  const body = document.body
  const app = document.querySelector('#app')
  const topNav = document.querySelector('.top-nav')

  if (theme === 'light') {
    // 浅色主题
    if (body) {
      body.style.background = 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }
    if (app) {
      app.classList.add('light-theme')
      app.classList.remove('dark-theme')
    }
    if (topNav) {
      topNav.classList.add('light-theme')
    }
  } else {
    // 深色主题（默认）
    if (body) {
      body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }
    if (app) {
      app.classList.remove('light-theme')
      app.classList.add('dark-theme')
    }
    if (topNav) {
      topNav.classList.remove('light-theme')
    }
  }

  // 通知所有面板更新主题
  window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme }))
}

// 监听设置变化
watch(() => settings.language, (newLang) => {
  console.log('语言切换到:', newLang)
  saveSettings()
  // 触发语言更新事件
  window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: newLang } }))
})

watch(() => settings.theme, (newTheme) => {
  console.log('主题切换到:', newTheme)
  applyTheme(newTheme)
  saveSettings()
  // 触发主题更新事件
  window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }))
})

watch(() => settings.animations, (newAnimations) => {
  saveSettings()
  // 触发动画设置事件
  window.dispatchEvent(new CustomEvent('animationsChanged', { detail: { enabled: newAnimations } }))
})

watch(() => settings.autoSave, (newAutoSave) => {
  saveSettings()
})

// 初始化
onMounted(() => {
  loadSettings()
  applyTheme(settings.theme)
})

// 导出给其他组件使用
export function useSettings() {
  return {
    settings,
    languages,
    loadSettings,
    saveSettings,
    applyTheme
  }
}

// 导出响应式设置对象
export { settings as globalSettings }
