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
            <button class="quick-action primary" @click="saveAllSettings">
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

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">自动保存</label>
              <span class="setting-description">设置修改后自动保存</span>
            </div>
            <label class="toggle-switch">
              <input v-model="settings.autoSave" type="checkbox" />
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

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">显示收敛信息</label>
              <span class="setting-description">计算完成后显示收敛分析</span>
            </div>
            <label class="toggle-switch">
              <input v-model="calculationSettings.showConvergence" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">结果缓存</label>
              <span class="setting-description">缓存计算结果以提高性能</span>
            </div>
            <label class="toggle-switch">
              <input v-model="calculationSettings.cacheResults" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <!-- 数据管理设置 -->
        <div v-if="activeCategory === 'data'" class="setting-group">
          <h3 class="setting-group-title">💾 数据管理设置</h3>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">自动保存模拟结果</label>
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
              <option value="500">500条</option>
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
              <label class="setting-label">包含元数据</label>
              <span class="setting-description">导出时包含时间戳和参数信息</span>
            </div>
            <label class="toggle-switch">
              <input v-model="dataSettings.includeMetadata" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
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

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">实时显示</label>
              <span class="setting-description">参数修改时实时更新显示</span>
            </div>
            <label class="toggle-switch">
              <input v-model="displaySettings.showRealTime" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <label class="setting-label">图表样式</label>
              <span class="setting-description">图表显示的视觉风格</span>
            </div>
            <select v-model="displaySettings.chartStyle" class="setting-select">
              <option value="modern">现代风格</option>
              <option value="classic">经典风格</option>
              <option value="minimal">极简风格</option>
            </select>
          </div>
        </div>

        <!-- 存储管理 -->
        <div v-if="activeCategory === 'storage'" class="setting-group">
          <h3 class="setting-group-title">📊 存储管理</h3>

          <!-- 存储统计信息 -->
          <div class="storage-stats">
            <div class="stat-item">
              <span class="stat-label">历史记录数</span>
              <span class="stat-value">{{ storageStats.totalRecords }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">存储使用</span>
              <span class="stat-value">{{ storageStats.storageUsed }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">存储状态</span>
              <span
                class="stat-value"
                :style="{ color: getStorageHealthColor(storageStats.storageHealth) }"
              >
                {{ getStorageHealthText(storageStats.storageHealth) }}
              </span>
            </div>
            <div class="stat-item" v-if="storageStats.oldestRecord">
              <span class="stat-label">最早记录</span>
              <span class="stat-value">{{ storageStats.oldestRecord }}</span>
            </div>
            <div class="stat-item" v-if="storageStats.newestRecord">
              <span class="stat-label">最新记录</span>
              <span class="stat-value">{{ storageStats.newestRecord }}</span>
            </div>
          </div>

          <!-- 数据管理操作 -->
          <div class="data-operations">
            <h4 class="operation-title">数据管理操作</h4>

            <button class="operation-button" @click="calculateStorageStats">
              🔄 刷新统计
            </button>

            <button class="operation-button" @click="batchDeleteHistory">
              🗑️ 批量删除（按天数）
            </button>

            <button class="operation-button" @click="deleteByDateRange">
              📅 按日期范围删除
            </button>

            <button class="operation-button primary" @click="exportAllData">
              📦 导出所有数据
            </button>
          </div>

          <!-- 存储优化建议 -->
          <div class="storage-tips" v-if="storageStats.storageHealth !== 'good'">
            <h4 class="tips-title">💡 存储优化建议</h4>
            <ul class="tips-list">
              <li v-if="storageStats.storageHealth === 'critical'">
                存储空间紧张，建议删除部分历史记录
              </li>
              <li v-if="storageStats.storageHealth === 'warning'">
                存储使用较多，建议定期清理不需要的数据
              </li>
              <li>
                导出重要数据进行备份，然后清除本地记录
              </li>
              <li>
                考虑调整历史记录限制设置
              </li>
            </ul>
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
              <span class="about-value">v2.0.0 (Real Physics Edition)</span>
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
            <div class="about-item">
              <span class="about-label">部署平台:</span>
              <span class="about-value">GitHub Pages / Vercel</span>
            </div>
            <div class="about-item">
              <span class="about-label">开源地址:</span>
              <a href="https://github.com/Xiaruidong/pv-climate-simulation-" class="about-link" target="_blank">
                GitHub Repository
              </a>
            </div>
          </div>

          <!-- 系统特性 -->
          <div class="system-features">
            <h4 class="features-title">✨ 系统特性</h4>
            <div class="features-list">
              <div class="feature-item">
                <span class="feature-icon">🔬</span>
                <span class="feature-text">真实物理计算</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <span class="feature-text">高精度结果显示</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🌍</span>
                <span class="feature-text">实时3D可视化</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">💾</span>
                <span class="feature-text">本地数据存储</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">📊</span>
                <span class="feature-text">历史记录管理</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🔄</span>
                <span class="feature-text">数据对比功能</span>
              </div>
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
                <span class="summary-label">显示精度</span>
                <span class="summary-value">{{ displaySettings.decimalPlaces }}位小数</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">自动保存</span>
                <span class="summary-value">{{ dataSettings.autoSave ? '开启' : '关闭' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">积分方法</span>
                <span class="summary-value">{{ getMethodDisplayName(calculationSettings.integrationMethod) }}</span>
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
                <span class="shortcut-desc">重置当前分类</span>
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
            <button class="action-button" @click="applySettings">
              ✨ 应用设置
            </button>
          </div>
        </div>

        <!-- 设置提示 -->
        <div class="settings-tips">
          <h4 class="tips-title">💡 使用提示</h4>
          <ul class="tips-list">
            <li>设置修改后会自动保存到浏览器</li>
            <li>可以导出设置进行备份</li>
            <li>支持导入配置文件快速部署</li>
            <li>存储管理功能帮助优化性能</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useSettings } from '../composables/useSettings'

// 使用全局设置composable
const { settings: globalSettings, languages, applyTheme } = useSettings()

// 设置分类
const categories = [
  { id: 'general', name: '通用设置', icon: '🎛️' },
  { id: 'calculation', name: '计算设置', icon: '🔬' },
  { id: 'data', name: '数据管理', icon: '💾' },
  { id: 'display', name: '显示设置', icon: '🎨' },
  { id: 'storage', name: '存储管理', icon: '📊' },
  { id: 'about', name: '关于', icon: 'ℹ️' }
]

// 当前活动分类
const activeCategory = ref('general')

// 存储统计信息
const storageStats = ref({
  totalRecords: 0,
  storageUsed: '0 KB',
  oldestRecord: null,
  newestRecord: null,
  storageHealth: 'good'
})

// 通用设置 - 使用全局设置
const settings = globalSettings

// 计算设置
const calculationSettings = reactive({
  defaultYears: 100,
  integrationMethod: 'runge_kutta',
  tolerance: 0.001,
  autoCalculate: true,
  showConvergence: true,
  cacheResults: true
})

// 数据管理设置
const dataSettings = reactive({
  autoSave: true,
  historyLimit: 100,
  exportFormat: 'json',
  includeMetadata: true,
  compressData: false
})

// 显示设置
const displaySettings = reactive({
  temperatureUnit: 'celsius',
  decimalPlaces: 4,
  gridDensity: 'medium',
  showRealTime: true,
  chartStyle: 'modern'
})

// 计算存储统计
const calculateStorageStats = () => {
  try {
    // 获取历史记录
    const historyKey = 'calculation_results'
    const historyData = localStorage.getItem(historyKey)

    if (historyData) {
      const history = JSON.parse(historyData)
      const records = Array.isArray(history) ? history : []

      storageStats.value.totalRecords = records.length

      // 计算存储大小
      const storageSize = new Blob([historyData]).size
      storageStats.value.storageUsed = formatBytes(storageSize)

      // 获取最旧和最新记录
      if (records.length > 0) {
        const timestamps = records
          .map(r => new Date(r.timestamp || r.created_at))
          .filter(date => !isNaN(date.getTime()))

        if (timestamps.length > 0) {
          storageStats.value.oldestRecord = new Date(Math.min(...timestamps)).toLocaleDateString('zh-CN')
          storageStats.value.newestRecord = new Date(Math.max(...timestamps)).toLocaleDateString('zh-CN')
        }
      }

      // 存储健康状况
      const storagePercentage = (storageSize / (5 * 1024 * 1024)) * 100 // 假设5MB限制
      if (storagePercentage > 80) {
        storageStats.value.storageHealth = 'critical'
      } else if (storagePercentage > 60) {
        storageStats.value.storageHealth = 'warning'
      } else {
        storageStats.value.storageHealth = 'good'
      }
    } else {
      storageStats.value.totalRecords = 0
      storageStats.value.storageUsed = '0 B'
      storageStats.value.storageHealth = 'good'
    }
  } catch (error) {
    console.error('计算存储统计失败:', error)
  }
}

// 格式化字节大小
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取存储健康状态文本
const getStorageHealthText = (health) => {
  const texts = {
    good: '存储充足',
    warning: '存储较多',
    critical: '存储紧张'
  }
  return texts[health] || health
}

// 获取存储健康状态颜色
const getStorageHealthColor = (health) => {
  const colors = {
    good: '#4ad97f',
    warning: '#ffa947',
    critical: '#ff5747'
  }
  return colors[health] || '#4a5568'
}

// 批量删除历史记录
const batchDeleteHistory = () => {
  const days = prompt('删除多少天前的记录？（输入天数，如：30）')
  if (days && !isNaN(days)) {
    try {
      const historyKey = 'calculation_results'
      const historyData = localStorage.getItem(historyKey)

      if (historyData) {
        const history = JSON.parse(historyData)
        const records = Array.isArray(history) ? history : []

        const cutoffDate = new Date()
        cutoffDate.setDate(cutoffDate.getDate() - parseInt(days))

        const filteredRecords = records.filter(record => {
          const recordDate = new Date(record.timestamp || record.created_at)
          return recordDate > cutoffDate
        })

        localStorage.setItem(historyKey, JSON.stringify(filteredRecords))

        const deletedCount = records.length - filteredRecords.length
        showNotification(`已删除 ${deletedCount} 条历史记录`, 'success')

        calculateStorageStats()
      } else {
        showNotification('没有找到历史记录', 'info')
      }
    } catch (error) {
      showNotification('删除失败：' + error.message, 'error')
    }
  }
}

// 按日期范围删除
const deleteByDateRange = () => {
  const startDate = prompt('开始日期 (格式: YYYY-MM-DD)')
  const endDate = prompt('结束日期 (格式: YYYY-MM-DD)')

  if (startDate && endDate) {
    try {
      const historyKey = 'calculation_results'
      const historyData = localStorage.getItem(historyKey)

      if (historyData) {
        const history = JSON.parse(historyData)
        const records = Array.isArray(history) ? history : []

        const start = new Date(startDate)
        const end = new Date(endDate)
        end.setHours(23, 59, 59)

        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
          showNotification('日期格式错误，请使用 YYYY-MM-DD 格式', 'error')
          return
        }

        const filteredRecords = records.filter(record => {
          const recordDate = new Date(record.timestamp || record.created_at)
          return recordDate < start || recordDate > end
        })

        localStorage.setItem(historyKey, JSON.stringify(filteredRecords))

        const deletedCount = records.length - filteredRecords.length
        showNotification(`已删除 ${deletedCount} 条记录`, 'success')

        calculateStorageStats()
      }
    } catch (error) {
      showNotification('删除失败：' + error.message, 'error')
    }
  }
}

// 导出所有数据
const exportAllData = () => {
  try {
    // 导出历史记录
    const historyKey = 'calculation_results'
    const historyData = localStorage.getItem(historyKey)

    // 导出用户设置
    const settingsData = localStorage.getItem('userSettings')

    // 创建完整备份
    const backup = {
      version: '2.0.0',
      exportDate: new Date().toISOString(),
      settings: settingsData ? JSON.parse(settingsData) : null,
      history: historyData ? JSON.parse(historyData) : [],
      metadata: {
        totalRecords: historyData ? JSON.parse(historyData).length : 0,
        exportFormat: 'full_backup'
      }
    }

    const dataStr = JSON.stringify(backup, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pv-simulator-backup-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)

    showNotification(`已导出 ${backup.metadata.totalRecords} 条记录和完整设置`, 'success')
  } catch (error) {
    showNotification('导出失败：' + error.message, 'error')
  }
}

// 应用设置到当前系统
const applySettings = () => {
  // 应用主题
  applyTheme(settings.theme)

  // 触发事件通知其他组件设置已更新
  window.dispatchEvent(new CustomEvent('settingsUpdated', {
    detail: {
      display: displaySettings,
      calculation: calculationSettings,
      general: settings
    }
  }))

  showNotification('设置已应用到当前系统', 'success')
}

// 获取积分方法显示名称
const getMethodDisplayName = (method) => {
  const names = {
    euler: '欧拉法',
    runge_kutta: '龙格-库塔法',
    adaptive: '自适应步长'
  }
  return names[method] || method
}

// 监听设置变化，自动应用
watch([displaySettings, calculationSettings], () => {
  if (settings.autoSave) {
    applySettings()
  }
}, { deep: true })

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
  calculateStorageStats()
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

// 显示通知
const showNotification = (message, type = 'info') => {
  // 创建通知元素
  const notification = document.createElement('div')
  notification.className = `settings-notification ${type}`
  notification.textContent = message
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#4ad97f' : type === 'error' ? '#ff5747' : '#4a9eff'};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    font-size: 14px;
    font-weight: 600;
    animation: slideIn 0.3s ease;
  `

  document.body.appendChild(notification)

  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease'
    setTimeout(() => document.body.removeChild(notification), 300)
  }, 3000)
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
  applySettings()
  showNotification('设置已保存成功', 'success')
}

// 重置当前分类设置
const resetCurrentCategory = () => {
  if (!confirm('确定要重置当前分类的设置吗？')) return

  switch (activeCategory.value) {
    case 'general':
      Object.assign(settings, {
        language: 'zh',
        theme: 'dark',
        animations: true,
        autoSave: true
      })
      break
    case 'calculation':
      Object.assign(calculationSettings, {
        defaultYears: 100,
        integrationMethod: 'runge_kutta',
        tolerance: 0.001,
        autoCalculate: true,
        showConvergence: true,
        cacheResults: true
      })
      break
    case 'data':
      Object.assign(dataSettings, {
        autoSave: true,
        historyLimit: 100,
        exportFormat: 'json',
        includeMetadata: true,
        compressData: false
      })
      break
    case 'display':
      Object.assign(displaySettings, {
        temperatureUnit: 'celsius',
        decimalPlaces: 4,
        gridDensity: 'medium',
        showRealTime: true,
        chartStyle: 'modern'
      })
      break
  }
  showNotification('当前分类设置已重置', 'info')
}

// 重置所有设置
const resetAllSettings = () => {
  if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
    localStorage.removeItem('userSettings')
    loadSettings()
    showNotification('所有设置已重置', 'info')
  }
}

// 清除所有历史数据
const clearAllHistory = () => {
  if (confirm('确定要删除所有历史模拟记录吗？此操作不可撤销。')) {
    const keysToDelete = ['calculation_results', 'simulation_history']
    let deletedCount = 0

    keysToDelete.forEach(key => {
      const data = localStorage.getItem(key)
      if (data) {
        const parsed = JSON.parse(data)
        deletedCount += Array.isArray(parsed) ? parsed.length : 0
        localStorage.removeItem(key)
      }
    })

    calculateStorageStats()
    showNotification(`已清除 ${deletedCount} 条历史数据`, 'success')
  }
}

// 导出设置
const exportSettings = () => {
  const allSettings = {
    version: '2.0.0',
    exportDate: new Date().toISOString(),
    settings: {
      general: settings,
      calculation: calculationSettings,
      data: dataSettings,
      display: displaySettings
    }
  }

  const dataStr = JSON.stringify(allSettings, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pv-simulator-settings-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)

  showNotification('设置配置已导出', 'success')
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

        // 兼容不同的导入格式
        const settingsToImport = imported.settings || imported

        if (settingsToImport.general) Object.assign(settings, settingsToImport.general)
        if (settingsToImport.calculation) Object.assign(calculationSettings, settingsToImport.calculation)
        if (settingsToImport.data) Object.assign(dataSettings, settingsToImport.data)
        if (settingsToImport.display) Object.assign(displaySettings, settingsToImport.display)

        saveAllSettings()
        showNotification('设置配置已导入', 'success')
      } catch (error) {
        showNotification('导入失败：配置文件格式错误', 'error')
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

// 返回主界面
const goBack = () => {
  // 触发返回主界面事件
  window.dispatchEvent(new CustomEvent('navigateToDashboard'))
  showNotification('正在返回主界面...', 'info')
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

.quick-action.primary {
  background: linear-gradient(135deg, #4a9eff, #00d9ff);
  border-color: transparent;
  color: white;
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

/* 存储管理样式 */
.storage-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(245, 247, 250, 0.8);
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 11px;
  color: #718096;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #00d9ff;
}

.data-operations {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.operation-title {
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
}

.operation-button {
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  color: #4a5568;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.operation-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #4a9eff;
}

.operation-button.primary {
  background: linear-gradient(135deg, #4a9eff, #00d9ff);
  border-color: transparent;
  color: white;
}

.storage-tips {
  padding: 12px;
  background: rgba(255, 157, 0, 0.1);
  border: 1px solid #ffa947;
  border-radius: 8px;
}

.tips-title {
  font-size: 12px;
  font-weight: 600;
  color: #ffa947;
  margin-bottom: 8px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  font-size: 11px;
  color: #4a5568;
  margin-bottom: 4px;
  padding-left: 12px;
  position: relative;
}

.tips-list li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #ffa947;
}

/* 关于页面样式 */
.about-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
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

.about-link {
  color: #4a9eff;
  text-decoration: none;
  font-weight: 600;
}

.about-link:hover {
  text-decoration: underline;
}

.system-features {
  margin-top: 20px;
}

.features-title {
  font-size: 14px;
  font-weight: 600;
  color: #00d9ff;
  margin-bottom: 12px;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  font-size: 12px;
}

.feature-icon {
  font-size: 14px;
}

.feature-text {
  color: #4a5568;
}

/* 设置摘要 */
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

.settings-tips {
  padding: 12px;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid #4ad97f;
  border-radius: 8px;
}

.tips-title {
  font-size: 12px;
  font-weight: 600;
  color: #4ad97f;
  margin-bottom: 8px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  font-size: 11px;
  color: #4a5568;
  margin-bottom: 4px;
  padding-left: 12px;
  position: relative;
}

.tips-list li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #4ad97f;
  font-weight: 600;
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

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
</style>