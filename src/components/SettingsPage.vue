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
        <!-- 通用设置 -->
        <div v-if="activeCategory === 'general'" class="setting-group">
          <h3 class="setting-group-title">🎛️ 通用设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">语言</label>
              <span class="setting-description">选择界面显示语言</span>
            </div>
            <select v-model="settings.language" class="setting-select">
              <option value="zh">简体中文</option>
              <option value="en">English</option>
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
        </div>

        <!-- 计算设置 -->
        <div v-if="activeCategory === 'calculation'" class="setting-group">
          <h3 class="setting-group-title">🔬 计算设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">默认模拟年数</label>
              <span class="setting-description">新模拟的默认时长</span>
            </div>
            <div class="number-input">
              <input
                v-model.number="calculationSettings.defaultYears"
                type="number"
                min="10"
                max="1000"
                class="tech-input"
              />
              <span class="input-unit">年</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">数值积分方法</label>
              <span class="setting-description">默认的数值计算方法</span>
            </div>
            <select v-model="calculationSettings.integrationMethod" class="setting-select">
              <option value="euler">欧拉法 (快速)</option>
              <option value="runge_kutta">龙格-库塔法 (精确)</option>
              <option value="adaptive">自适应步长 (平衡)</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">收敛容差</label>
              <span class="setting-description">数值计算的收敛精度</span>
            </div>
            <div class="number-input">
              <input
                v-model.number="calculationSettings.tolerance"
                type="number"
                step="0.0001"
                min="0.0001"
                max="0.1"
                class="tech-input"
              />
              <span class="input-unit">精度值</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">自动计算</label>
              <span class="setting-description">参数修改后自动重新计算</span>
            </div>
            <label class="toggle-switch">
              <input v-model="calculationSettings.autoCalculate" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
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
              <option value="csv">CSV (.csv)</option>
              <option value="json">JSON (.json)</option>
              <option value="excel">Excel (.xlsx)</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">清除历史数据</label>
              <span class="setting-description">删除所有历史模拟记录</span>
            </div>
            <button class="danger-button" @click="clearAllHistory">
              🗑️ 清除数据
            </button>
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
              <label class="setting-label">结果显示精度</label>
              <span class="setting-description">数值显示的小数位数</span>
            </div>
            <select v-model="displaySettings.decimalPlaces" class="setting-select">
              <option value="2">2位小数</option>
              <option value="4">4位小数</option>
              <option value="6">6位小数</option>
              <option value="8">8位小数</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">3D网格密度</label>
              <span class="setting-description">3D可视化的网格密度</span>
            </div>
            <select v-model="displaySettings.gridDensity" class="setting-select">
              <option value="low">低 (性能优先)</option>
              <option value="medium">中 (平衡)</option>
              <option value="high">高 (质量优先)</option>
            </select>
          </div>
        </div>

        <!-- 关于 -->
        <div v-if="activeCategory === 'about'" class="setting-group">
          <h3 class="setting-group-title">ℹ️ 关于系统</h3>

          <div class="about-info">
            <div class="about-item">
              <span class="about-label">系统名称:</span>
              <span class="about-value">光伏气候效应模拟系统</span>
            </div>
            <div class="about-item">
              <span class="about-label">系统版本:</span>
              <span class="about-value">v2.0.0</span>
            </div>
            <div class="about-item">
              <span class="about-label">物理模型:</span>
              <span class="about-value">零维能量平衡模型 (EBM)</span>
            </div>
            <div class="about-item">
              <span class="about-label">计算标准:</span>
              <span class="about-value">CODATA 2018 + IPCC AR5</span>
            </div>
            <div class="about-item">
              <span class="about-label">技术栈:</span>
              <span class="about-value">Vue.js 3 + Vite + Canvas API</span>
            </div>
            <div class="about-item">
              <span class="about-label">存储方案:</span>
              <span class="about-value">localStorage (可选MySQL)</span>
            </div>
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
            <button class="action-button" @click="goBack">
              ← 返回主界面
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 设置分类
const categories = [
  { id: 'general', name: '通用设置', icon: '🎛️' },
  { id: 'calculation', name: '计算设置', icon: '🔬' },
  { id: 'data', name: '数据管理', icon: '💾' },
  { id: 'display', name: '显示设置', icon: '🎨' },
  { id: 'about', name: '关于', icon: 'ℹ️' }
]

// 当前活动分类
const activeCategory = ref('general')

// 通用设置
const settings = reactive({
  language: 'zh',
  theme: 'dark',
  animations: true
})

// 计算设置
const calculationSettings = reactive({
  defaultYears: 100,
  integrationMethod: 'runge_kutta',
  tolerance: 0.001,
  autoCalculate: true
})

// 数据管理设置
const dataSettings = reactive({
  autoSave: true,
  historyLimit: 100,
  exportFormat: 'json'
})

// 显示设置
const displaySettings = reactive({
  temperatureUnit: 'celsius',
  decimalPlaces: 4,
  gridDensity: 'medium'
})

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})

// 加载设置
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (parsed.general) Object.assign(settings, parsed.general)
      if (parsed.calculation) Object.assign(calculationSettings, parsed.calculation)
      if (parsed.data) Object.assign(dataSettings, parsed.data)
      if (parsed.display) Object.assign(displaySettings, parsed.display)
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 获取语言名称
const getLanguageName = (code) => {
  const names = {
    zh: '简体中文',
    en: 'English'
  }
  return names[code] || code
}

// 获取主题名称
const getThemeName = (id) => {
  const names = {
    dark: '深色科技风',
    light: '浅色简约风'
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
    calculation: calculationSettings,
    data: dataSettings,
    display: displaySettings
  }

  localStorage.setItem('userSettings', JSON.stringify(allSettings))
  alert('设置已保存成功！')
}

// 重置当前分类设置
const resetCurrentCategory = () => {
  switch (activeCategory.value) {
    case 'general':
      Object.assign(settings, {
        language: 'zh',
        theme: 'dark',
        animations: true
      })
      break
    case 'calculation':
      Object.assign(calculationSettings, {
        defaultYears: 100,
        integrationMethod: 'runge_kutta',
        tolerance: 0.001,
        autoCalculate: true
      })
      break
    case 'data':
      Object.assign(dataSettings, {
        autoSave: true,
        historyLimit: 100,
        exportFormat: 'json'
      })
      break
    case 'display':
      Object.assign(displaySettings, {
        temperatureUnit: 'celsius',
        decimalPlaces: 4,
        gridDensity: 'medium'
      })
      break
  }
  alert('当前分类设置已重置！')
}

// 重置所有设置
const resetAllSettings = () => {
  if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
    localStorage.removeItem('userSettings')
    loadSettings()
    alert('所有设置已重置！')
  }
}

// 清除所有历史数据
const clearAllHistory = () => {
  if (confirm('确定要删除所有历史模拟记录吗？此操作不可撤销。')) {
    localStorage.removeItem('calculation_results')
    localStorage.removeItem('simulation_history')
    alert('所有历史数据已清除！')
  }
}

// 导出设置
const exportSettings = () => {
  const allSettings = {
    general: settings,
    calculation: calculationSettings,
    data: dataSettings,
    display: displaySettings
  }

  const dataStr = JSON.stringify(allSettings, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pv-simulator-settings-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)

  alert('设置配置已导出！')
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
        if (imported.general) Object.assign(settings, imported.general)
        if (imported.calculation) Object.assign(calculationSettings, imported.calculation)
        if (imported.data) Object.assign(dataSettings, imported.data)
        if (imported.display) Object.assign(displaySettings, imported.display)

        saveAllSettings()
        alert('设置配置已导入！')
      } catch (error) {
        alert('导入失败：配置文件格式错误')
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

// 返回主界面
const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  height: 100%;
  overflow-y: auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d9ff, #4a9eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  color: white;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.settings-content {
  display: grid;
  grid-template-columns: 240px 1fr 320px;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.panel-section {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #4a9eff;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  color: #4a5568;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.category-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #4a9eff;
}

.category-button.active {
  background: linear-gradient(135deg, #4a9eff, #00d9ff);
  border-color: transparent;
  color: white;
}

.category-icon {
  font-size: 16px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action {
  padding: 8px;
  background: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  color: #4a5568;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-action:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #4a9eff;
  color: #2d3748;
}

.setting-group {
  margin-bottom: 24px;
}

.setting-group-title {
  font-size: 16px;
  font-weight: 600;
  color: #00d9ff;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  margin-bottom: 8px;
}

.setting-info {
  flex: 1;
}

.setting-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.setting-description {
  display: block;
  font-size: 11px;
  color: #718096;
}

.setting-select,
.tech-input {
  padding: 6px 12px;
  background: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  color: #2d3748;
  font-size: 13px;
  min-width: 120px;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-unit {
  font-size: 11px;
  color: #718096;
  min-width: 30px;
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
  background-color: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: #718096;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #00d9ff;
  border-color: #00d9ff;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(20px);
  background-color: white;
}

.danger-button {
  padding: 6px 12px;
  background: linear-gradient(135deg, #ff5747, #ffa947);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.danger-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 87, 71, 0.3);
}

.about-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.about-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  font-size: 13px;
}

.about-label {
  color: #718096;
  font-weight: 600;
}

.about-value {
  color: #00d9ff;
  font-weight: 600;
}

.settings-summary {
  margin-bottom: 16px;
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: #00d9ff;
  margin-bottom: 12px;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
}

.summary-label {
  color: #718096;
}

.summary-value {
  color: #00d9ff;
  font-weight: 600;
}

.shortcuts-info {
  margin-bottom: 16px;
}

.shortcuts-title {
  font-size: 13px;
  font-weight: 600;
  color: #00d9ff;
  margin-bottom: 12px;
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.shortcut-key {
  padding: 2px 8px;
  background: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  color: #00d9ff;
  font-family: monospace;
  font-weight: 600;
}

.shortcut-desc {
  color: #4a5568;
}

.settings-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button {
  padding: 8px;
  background: rgba(245, 247, 250, 0.8);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  color: #2d3748;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #4a9eff;
}

.action-button.primary {
  background: linear-gradient(135deg, #4a9eff, #00d9ff);
  border-color: transparent;
  color: white;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .settings-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .categories-panel {
    order: 1;
  }

  .settings-panel {
    order: 2;
  }

  .preview-panel {
    order: 3;
  }
}
</style>