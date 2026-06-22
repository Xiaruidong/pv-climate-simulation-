<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">⚙️ 系统设置</h1>
      <p class="page-subtitle">配置模拟器参数和系统偏好</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="settings-content">
      <!-- 左侧：设置分类 -->
      <div class="categories-panel">
        <div class="panel-section">
          <h3 class="section-title">📋 设置分类</h3>

          <div class="setting-categories">
            <button
              v-for="category in categories"
              :key="category.id"
              :class="['category-button', { active: activeCategory === category.id }]"
              @click="activeCategory = category.id"
            >
              <span class="category-icon">{{ category.icon }}</span>
              <span class="category-name">{{ category.name }}</span>
            </button>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="panel-section">
          <h3 class="section-title">⚡ 快速操作</h3>
          <div class="quick-actions">
            <button class="quick-action" @click="resetAllSettings">
              🔄 重置所有设置
            </button>
            <button class="quick-action" @click="exportSettings">
              📥 导出配置
            </button>
            <button class="quick-action" @click="importSettings">
              📤 导入配置
            </button>
            <button class="quick-action" @click="saveAllSettings">
              💾 保存所有更改
            </button>
          </div>
        </div>
      </div>

      <!-- 中间：设置内容 -->
      <div class="settings-panel">
        <!-- 常规设置 -->
        <div v-if="activeCategory === 'general'" class="setting-group">
          <h3 class="setting-group-title">🎛️ 常规设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">语言</label>
              <span class="setting-description">选择界面显示语言</span>
            </div>
            <select v-model="settings.language" class="setting-select">
              <option value="zh">简体中文</option>
              <option value="en">English</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">主题</label>
              <span class="setting-description">选择界面主题风格</span>
            </div>
            <select v-model="settings.theme" class="setting-select">
              <option value="dark">深色科技风</option>
              <option value="light">浅色简约风</option>
              <option value="auto">跟随系统</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">界面密度</label>
              <span class="setting-description">调整界面元素间距</span>
            </div>
            <select v-model="settings.density" class="setting-select">
              <option value="compact">紧凑</option>
              <option value="normal">正常</option>
              <option value="comfortable">舒适</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">动画效果</label>
              <span class="setting-description">启用界面动画和过渡效果</span>
            </div>
            <label class="toggle-switch">
              <input v-model="settings.animations" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">声音效果</label>
              <span class="setting-description">启用操作反馈声音</span>
            </div>
            <label class="toggle-switch">
              <input v-model="settings.sounds" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <!-- 模拟参数设置 -->
        <div v-if="activeCategory === 'simulation'" class="setting-group">
          <h3 class="setting-group-title">🔬 模拟参数设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">默认时间步长</label>
              <span class="setting-description">新模拟的默认时间分辨率</span>
            </div>
            <select v-model="simulationSettings.defaultTimeStep" class="setting-select">
              <option value="hourly">小时</option>
              <option value="daily">天</option>
              <option value="monthly">月</option>
              <option value="yearly">年</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">默认空间分辨率</label>
              <span class="setting-description">新模拟的默认空间分辨率</span>
            </div>
            <select v-model="simulationSettings.defaultResolution" class="setting-select">
              <option value="coarse">粗分辨率 (50km)</option>
              <option value="medium">中等分辨率 (10km)</option>
              <option value="fine">精细分辨率 (1km)</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">收敛容差</label>
              <span class="setting-description">数值计算的收敛精度</span>
            </div>
            <div class="number-input">
              <input
                v-model.number="simulationSettings.tolerance"
                type="number"
                step="0.0001"
                class="tech-input"
              />
              <span class="input-unit">精度值</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">最大迭代次数</label>
              <span class="setting-description">单次模拟的最大迭代次数</span>
            </div>
            <div class="number-input">
              <input
                v-model.number="simulationSettings.maxIterations"
                type="number"
                class="tech-input"
              />
              <span class="input-unit">次</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">并行计算</label>
              <span class="setting-description">启用多核并行计算</span>
            </div>
            <label class="toggle-switch">
              <input v-model="simulationSettings.parallelComputing" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div v-if="simulationSettings.parallelComputing" class="setting-item sub-setting">
            <div class="setting-info">
              <label class="setting-label">计算核心数</label>
              <span class="setting-description">使用的CPU核心数量 (0=自动)</span>
            </div>
            <input
              v-model.number="simulationSettings.parallelCores"
              type="number"
              min="0"
              max="16"
              class="tech-input"
            />
          </div>
        </div>

        <!-- 数据管理设置 -->
        <div v-if="activeCategory === 'data'" class="setting-group">
          <h3 class="setting-group-title">💾 数据管理设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">自动保存</label>
              <span class="setting-description">模拟完成后自动保存结果</span>
            </div>
            <label class="toggle-switch">
              <input v-model="dataSettings.autoSave" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">保存间隔</label>
              <span class="setting-description">自动保存的时间间隔</span>
            </div>
            <select v-model="dataSettings.saveInterval" class="setting-select">
              <option value="5">5分钟</option>
              <option value="10">10分钟</option>
              <option value="30">30分钟</option>
              <option value="60">1小时</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">数据缓存</label>
              <span class="setting-description">缓存模拟结果以提高性能</span>
            </div>
            <label class="toggle-switch">
              <input v-model="dataSettings.caching" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">历史记录限制</label>
              <span class="setting-description">保存的历史模拟记录最大数量</span>
            </div>
            <select v-model="dataSettings.historyLimit" class="setting-select">
              <option value="50">50条</option>
              <option value="100">100条</option>
              <option value="200">200条</option>
              <option value="unlimited">无限制</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">数据导出格式</label>
              <span class="setting-description">默认的数据导出文件格式</span>
            </div>
            <select v-model="dataSettings.exportFormat" class="setting-select">
              <option value="excel">Excel (.xlsx)</option>
              <option value="csv">CSV (.csv)</option>
              <option value="json">JSON (.json)</option>
              <option value="pdf">PDF (.pdf)</option>
            </select>
          </div>
        </div>

        <!-- 显示设置 -->
        <div v-if="activeCategory === 'display'" class="setting-group">
          <h3 class="setting-group-title">🎨 显示设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">温度单位</label>
              <span class="setting-description">温度显示的单位制</span>
            </div>
            <select v-model="displaySettings.temperatureUnit" class="setting-select">
              <option value="celsius">摄氏度 (°C)</option>
              <option value="fahrenheit">华氏度 (°F)</option>
              <option value="kelvin">开尔文 (K)</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">能量单位</label>
              <span class="setting-description">能量显示的单位制</span>
            </div>
            <select v-model="displaySettings.energyUnit" class="setting-select">
              <option value="kj">千焦 (kJ)</option>
              <option value="mj">兆焦 (MJ)</option>
              <option value="kwh">千瓦时 (kWh)</option>
              <option value="btu">英热单位 (BTU)</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">图表样式</label>
              <span class="setting-description">默认的图表显示样式</span>
            </div>
            <select v-model="displaySettings.chartStyle" class="setting-select">
              <option value="modern">现代风格</option>
              <option value="classic">经典风格</option>
              <option value="minimal">极简风格</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">颜色方案</label>
              <span class="setting-description">数据可视化的配色方案</span>
            </div>
            <div class="color-options">
              <button
                v-for="scheme in colorSchemes"
                :key="scheme.id"
                :class="['color-option', { active: displaySettings.colorScheme === scheme.id }]"
                :style="{ background: scheme.preview }"
                @click="displaySettings.colorScheme = scheme.id"
              >
                {{ scheme.name }}
              </button>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">网格密度</label>
              <span class="setting-description">3D可视化的网格密度</span>
            </div>
            <select v-model="displaySettings.gridDensity" class="setting-select">
              <option value="low">低 (性能优先)</option>
              <option value="medium">中 (平衡)</option>
              <option value="high">高 (质量优先)</option>
            </select>
          </div>
        </div>

        <!-- 通知设置 -->
        <div v-if="activeCategory === 'notifications'" class="setting-group">
          <h3 class="setting-group-title">🔔 通知设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">模拟完成通知</label>
              <span class="setting-description">模拟计算完成时发送通知</span>
            </div>
            <label class="toggle-switch">
              <input v-model="notificationSettings.simulationComplete" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">错误通知</label>
              <span class="setting-description">发生错误时立即通知</span>
            </div>
            <label class="toggle-switch">
              <input v-model="notificationSettings.errors" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">系统更新通知</label>
              <span class="setting-description">有新版本时通知用户</span>
            </div>
            <label class="toggle-switch">
              <input v-model="notificationSettings.updates" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">通知方式</label>
              <span class="setting-description">接收通知的方式</span>
            </div>
            <div class="notification-methods">
              <label class="method-checkbox">
                <input v-model="notificationSettings.methods" value="desktop" type="checkbox" />
                <span>桌面通知</span>
              </label>
              <label class="method-checkbox">
                <input v-model="notificationSettings.methods" value="sound" type="checkbox" />
                <span>声音提示</span>
              </label>
              <label class="method-checkbox">
                <input v-model="notificationSettings.methods" value="badge" type="checkbox" />
                <span>图标徽章</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 高级设置 -->
        <div v-if="activeCategory === 'advanced'" class="setting-group">
          <h3 class="setting-group-title">🔧 高级设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">开发者模式</label>
              <span class="setting-description">启用开发者工具和调试选项</span>
            </div>
            <label class="toggle-switch">
              <input v-model="advancedSettings.developerMode" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">调试日志</label>
              <span class="setting-description">记录详细的调试日志</span>
            </div>
            <label class="toggle-switch">
              <input v-model="advancedSettings.debugLogging" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">硬件加速</label>
              <span class="setting-description">使用GPU加速计算（如果可用）</span>
            </div>
            <label class="toggle-switch">
              <input v-model="advancedSettings.hardwareAcceleration" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">内存限制</label>
              <span class="setting-description">模拟可使用的最大内存 (GB)</span>
            </div>
            <input
              v-model.number="advancedSettings.memoryLimit"
              type="number"
              min="1"
              max="64"
              class="tech-input"
            />
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">API端点</label>
              <span class="setting-description">后端API服务地址</span>
            </div>
            <input
              v-model="advancedSettings.apiEndpoint"
              type="text"
              placeholder="http://localhost:8000"
              class="tech-input"
            />
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">代理设置</label>
              <span class="setting-description">网络代理配置</span>
            </div>
            <input
              v-model="advancedSettings.proxy"
              type="text"
              placeholder="http://proxy.example.com:8080"
              class="tech-input"
            />
          </div>
        </div>
      </div>

      <!-- 右侧：设置预览和说明 -->
      <div class="preview-panel">
        <div class="panel-section">
          <h3 class="section-title">👁️ 设置预览</h3>

          <!-- 当前设置摘要 -->
          <div class="settings-summary">
            <h4 class="summary-title">当前配置摘要</h4>
            <div class="summary-list">
              <div class="summary-item">
                <span class="summary-label">语言</span>
                <span class="summary-value">{{ getLanguageName(settings.language) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">主题</span>
                <span class="summary-value">{{ getThemeName(settings.theme) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">温度单位</span>
                <span class="summary-value">{{ getUnitName(displaySettings.temperatureUnit) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">自动保存</span>
                <span class="summary-value">{{ dataSettings.autoSave ? '开启' : '关闭' }}</span>
              </div>
            </div>
          </div>

          <!-- 配置文件信息 -->
          <div class="config-info">
            <h4 class="info-title">配置信息</h4>
            <div class="info-details">
              <div class="info-row">
                <span class="info-label">配置文件:</span>
                <span class="info-value">user_settings.json</span>
              </div>
              <div class="info-row">
                <span class="info-label">文件大小:</span>
                <span class="info-value">2.3 KB</span>
              </div>
              <div class="info-row">
                <span class="info-label">最后修改:</span>
                <span class="info-value">2024-01-20 10:30:15</span>
              </div>
              <div class="info-row">
                <span class="info-label">配置版本:</span>
                <span class="info-value">v2.1.0</span>
              </div>
            </div>
          </div>

          <!-- 重置警告 -->
          <div class="reset-warning">
            <h4 class="warning-title">⚠️ 注意事项</h4>
            <div class="warning-content">
              <p>修改高级设置可能影响系统稳定性</p>
              <p>建议仅在了解技术细节时进行调整</p>
              <p>重置设置将清除所有自定义配置</p>
            </div>
          </div>

          <!-- 快捷键提示 -->
          <div class="shortcuts-info">
            <h4 class="shortcuts-title">⌨️ 快捷键</h4>
            <div class="shortcuts-list">
              <div class="shortcut-item">
                <span class="shortcut-key">Ctrl+S</span>
                <span class="shortcut-desc">保存当前设置</span>
              </div>
              <div class="shortcut-item">
                <span class="shortcut-key">Ctrl+R</span>
                <span class="shortcut-desc">重置所有设置</span>
              </div>
              <div class="shortcut-item">
                <span class="shortcut-key">Ctrl+E</span>
                <span class="shortcut-desc">导出配置</span>
              </div>
              <div class="shortcut-item">
                <span class="shortcut-key">Ctrl+I</span>
                <span class="shortcut-desc">导入配置</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="panel-section">
          <div class="settings-actions">
            <button class="action-button primary" @click="saveAllSettings">
              💾 保存设置
            </button>
            <button class="action-button" @click="resetCurrentCategory">
              🔄 重置当前
            </button>
            <button class="action-button" @click="showHelp">
              ❓ 帮助
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// 设置分类
const categories = [
  { id: 'general', name: '常规设置', icon: '🎛️' },
  { id: 'simulation', name: '模拟参数', icon: '🔬' },
  { id: 'data', name: '数据管理', icon: '💾' },
  { id: 'display', name: '显示设置', icon: '🎨' },
  { id: 'notifications', name: '通知设置', icon: '🔔' },
  { id: 'advanced', name: '高级设置', icon: '🔧' }
]

// 当前活动分类
const activeCategory = ref('general')

// 常规设置
const settings = reactive({
  language: 'zh',
  theme: 'dark',
  density: 'normal',
  animations: true,
  sounds: false
})

// 模拟参数设置
const simulationSettings = reactive({
  defaultTimeStep: 'yearly',
  defaultResolution: 'medium',
  tolerance: 0.001,
  maxIterations: 1000,
  parallelComputing: true,
  parallelCores: 4
})

// 数据管理设置
const dataSettings = reactive({
  autoSave: true,
  saveInterval: 10,
  caching: true,
  historyLimit: 100,
  exportFormat: 'excel'
})

// 显示设置
const displaySettings = reactive({
  temperatureUnit: 'celsius',
  energyUnit: 'kwh',
  chartStyle: 'modern',
  colorScheme: 'tech',
  gridDensity: 'medium'
})

// 通知设置
const notificationSettings = reactive({
  simulationComplete: true,
  errors: true,
  updates: false,
  methods: ['desktop']
})

// 高级设置
const advancedSettings = reactive({
  developerMode: false,
  debugLogging: false,
  hardwareAcceleration: true,
  memoryLimit: 8,
  apiEndpoint: 'http://localhost:8000',
  proxy: ''
})

// 颜色方案
const colorSchemes = [
  { id: 'tech', name: '科技', preview: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { id: 'nature', name: '自然', preview: 'linear-gradient(135deg, #11998e, #38ef7d)' },
  { id: 'warm', name: '暖色', preview: 'linear-gradient(135deg, #f093fb, #f5576c)' },
  { id: 'cool', name: '冷色', preview: 'linear-gradient(135deg, #4facfe, #00f2fe)' }
]

// 获取语言名称
const getLanguageName = (code) => {
  const names = {
    zh: '简体中文',
    en: 'English',
    ja: '日本語'
  }
  return names[code] || code
}

// 获取主题名称
const getThemeName = (id) => {
  const names = {
    dark: '深色科技风',
    light: '浅色简约风',
    auto: '跟随系统'
  }
  return names[id] || id
}

// 获取单位名称
const getUnitName = (id) => {
  const names = {
    celsius: '摄氏度 (°C)',
    fahrenheit: '华氏度 (°F)',
    kelvin: '开尔文 (K)'
  }
  return names[id] || id
}

// 保存所有设置
const saveAllSettings = () => {
  const allSettings = {
    general: settings,
    simulation: simulationSettings,
    data: dataSettings,
    display: displaySettings,
    notifications: notificationSettings,
    advanced: advancedSettings
  }

  // 保存到本地存储
  localStorage.setItem('userSettings', JSON.stringify(allSettings))
  console.log('设置已保存:', allSettings)

  // 显示保存成功提示
  showNotification('设置已保存成功')
}

// 重置当前分类设置
const resetCurrentCategory = () => {
  switch (activeCategory.value) {
    case 'general':
      Object.assign(settings, {
        language: 'zh',
        theme: 'dark',
        density: 'normal',
        animations: true,
        sounds: false
      })
      break
    case 'simulation':
      Object.assign(simulationSettings, {
        defaultTimeStep: 'yearly',
        defaultResolution: 'medium',
        tolerance: 0.001,
        maxIterations: 1000,
        parallelComputing: true,
        parallelCores: 4
      })
      break
    // 其他分类...
  }
  showNotification('当前分类设置已重置')
}

// 重置所有设置
const resetAllSettings = () => {
  if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
    localStorage.removeItem('userSettings')
    location.reload()
  }
}

// 导出设置
const exportSettings = () => {
  const allSettings = {
    general: settings,
    simulation: simulationSettings,
    data: dataSettings,
    display: displaySettings,
    notifications: notificationSettings,
    advanced: advancedSettings
  }

  const dataStr = JSON.stringify(allSettings, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pv-simulator-settings-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)

  showNotification('设置配置已导出')
}

// 导入设置
const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const imported = JSON.parse(event.target.result)
        // 应用导入的设置
        if (imported.general) Object.assign(settings, imported.general)
        if (imported.simulation) Object.assign(simulationSettings, imported.simulation)
        if (imported.data) Object.assign(dataSettings, imported.data)
        if (imported.display) Object.assign(displaySettings, imported.display)
        if (imported.notifications) Object.assign(notificationSettings, imported.notifications)
        if (imported.advanced) Object.assign(advancedSettings, imported.advanced)

        showNotification('设置配置已导入')
      } catch (error) {
        showNotification('导入失败：配置文件格式错误')
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

// 显示帮助
const showHelp = () => {
  showNotification('帮助文档正在准备中...')
}

// 显示通知
const showNotification = (message) => {
  // 这里可以集成通知系统
  console.log('通知:', message)
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  height: 100%;
  overflow-y: auto;
}

.page-header {
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-cyan), var(--color-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
}

.settings-content {
  display: grid;
  grid-template-columns: 240px 1fr 320px;
  gap: var(--spacing-md);
  flex: 1;
  min-height: 0;
}

.panel-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.setting-categories {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.category-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.category-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.category-button.active {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: white;
}

.category-icon {
  font-size: 16px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.quick-action {
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
  color: var(--text-primary);
}

.setting-group {
  margin-bottom: var(--spacing-lg);
}

.setting-group-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--border-primary);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
}

.setting-item.sub-setting {
  margin-left: var(--spacing-lg);
  border-left: 2px solid var(--border-secondary);
}

.setting-info {
  flex: 1;
}

.setting-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.setting-description {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
}

.setting-select,
.tech-input {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  min-width: 150px;
}

.number-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.input-unit {
  font-size: 11px;
  color: var(--text-tertiary);
  min-width: 40px;
}

/* 开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  transition: all var(--transition-fast);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: var(--text-tertiary);
  border-radius: 50%;
  transition: all var(--transition-fast);
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--color-cyan);
  border-color: var(--color-cyan);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(20px);
  background-color: white;
}

.color-options {
  display: flex;
  gap: var(--spacing-sm);
}

.color-option {
  flex: 1;
  height: 32px;
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-md);
  font-size: 11px;
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.color-option:hover {
  border-color: var(--color-blue);
}

.color-option.active {
  border-color: white;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.notification-methods {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.method-checkbox {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  color: var(--text-secondary);
}

.settings-summary {
  margin-bottom: var(--spacing-lg);
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  font-size: 12px;
}

.summary-label {
  color: var(--text-tertiary);
}

.summary-value {
  color: var(--color-cyan);
  font-weight: 600;
}

.config-info {
  margin-bottom: var(--spacing-lg);
}

.info-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
}

.info-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.info-label {
  color: var(--text-tertiary);
}

.info-value {
  color: var(--text-secondary);
}

.reset-warning {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: rgba(255, 157, 0, 0.1);
  border: 1px solid var(--color-orange);
  border-radius: var(--radius-md);
}

.warning-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-orange);
  margin-bottom: var(--spacing-md);
}

.warning-content {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.warning-content p {
  margin-bottom: var(--spacing-xs);
}

.shortcuts-info {
  margin-bottom: var(--spacing-lg);
}

.shortcuts-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-cyan);
  margin-bottom: var(--spacing-md);
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: 12px;
}

.shortcut-key {
  padding: 2px 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--color-cyan);
  font-family: monospace;
  font-weight: 600;
}

.shortcut-desc {
  color: var(--text-secondary);
}

.settings-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.action-button {
  padding: var(--spacing-sm);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-button:hover {
  background: var(--bg-hover);
  border-color: var(--color-blue);
}

.action-button.primary {
  background: linear-gradient(135deg, var(--color-blue), var(--color-cyan));
  border-color: transparent;
  color: var(--bg-primary);
}
</style>
