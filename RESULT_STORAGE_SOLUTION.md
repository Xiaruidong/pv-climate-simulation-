# 💾 计算结果存储方案

## 🎯 存储解决方案概述

为您的光伏气候效应模拟系统提供了完整的本地存储方案，支持：
- ✅ 自动保存每次计算结果
- ✅ 历史记录管理
- ✅ 收藏功能
- ✅ 多结果对比
- ✅ 导出功能 (JSON/CSV)
- ✅ 智能标签分类

## 📦 存储架构

### 1. 存储层级

```
localStorage (浏览器本地存储)
├── pv_simulation_results       # 历史计算记录 (最多1000条)
├── pv_simulation_current       # 当前计算结果
├── pv_simulation_favorites     # 收藏的结果
└── pv_simulation_export_history  # 导出历史记录
```

### 2. 数据结构

**单条记录结构**:
```javascript
{
  id: "result_1234567890_abc123xyz",
  timestamp: "2026-06-11T10:30:00.000Z",
  scenarioName: "高覆盖率 (0.950)",
  params: {
    albedo_pv: 0.95,
    coverage_ratio: 1e-7,
    pv_efficiency: 0.23,
    albedo_land: 0.35,
    albedo_ocean: 0.06,
    co2_current: 420.0,
    initial_temp: 15.0,
    simulation_years: 100
  },
  results: {
    comparison: {
      temperature_change: -2.5024,
      albedo_change: 0.4380,
      cooling_efficiency: 15.2345
    },
    pv_scenario: {
      co2_reduction: 270.1234,
      equilibrium_temp: 12.4976
    }
  },
  metadata: {
    createdAt: "2026-06-11T10:30:00.000Z",
    version: "2.0.0",
    tags: ["高覆盖率", "镜面面板"]
  }
}
```

## 🔧 功能特性

### 1. 自动保存

**计算时自动保存**:
```javascript
// 在 useSimulation.js 中
const triggerCalculation = async (saveResult = true) => {
  // ... 计算逻辑 ...

  // 自动保存结果
  if (saveResult) {
    const resultId = resultStorage.saveResult(
      simulationState.params,
      result.data,
      simulationState.currentScenario
    )
  }
}
```

### 2. 历史记录管理

**获取历史记录**:
```javascript
// 获取所有历史
const history = resultStorage.getHistory()

// 带过滤条件
const filtered = resultStorage.getHistory({
  scenarioName: '高覆盖率',
  dateFrom: '2026-06-01',
  dateTo: '2026-06-30',
  tags: ['镜面面板', '高CO2']
})
```

**删除记录**:
```javascript
resultStorage.deleteResult('result_1234567890_abc123xyz')
```

### 3. 收藏功能

**添加到收藏**:
```javascript
resultStorage.addToFavorites(
  'result_1234567890_abc123xyz',
  '这是一个很好的高覆盖率场景'
)
```

**获取收藏列表**:
```javascript
const favorites = resultStorage.getFavorites()
```

### 4. 多结果对比

**对比多个场景**:
```javascript
const comparison = resultStorage.compareResults([
  'result_id_1',
  'result_id_2',
  'result_id_3'
])

// 返回结果:
{
  results: [
    {
      id: 'result_id_1',
      scenarioName: '高覆盖率 (0.950)',
      temperatureChange: -2.5024,
      co2Reduction: 270.1234,
      coolingEfficiency: 15.2345,
      // ...
    },
    // ... 其他结果
  ],
  analysis: {
    bestCooling: 'result_id_1',        // 最佳降温效果
    bestCO2Reduction: 'result_id_1',   // 最大CO2减排
    bestEfficiency: 'result_id_2',     // 最高效率
    parameterComparison: {
      // 各参数的统计分析
    }
  }
}
```

### 5. 导出功能

**导出单个结果**:
```javascript
// JSON格式
const jsonBlob = resultStorage.exportResult('result_id', 'json')
// 下载文件: pv-simulation-result_id.json

// CSV格式
const csvBlob = resultStorage.exportResult('result_id', 'csv')
// 下载文件: pv-simulation-result_id.csv
```

**批量导出**:
```javascript
const batchBlob = resultStorage.exportBatch(
  ['result_id_1', 'result_id_2', 'result_id_3'],
  'json'
)
```

**在组件中使用**:
```vue
<script setup>
import { useSimulation } from '@/composables/useSimulation'

const { exportResult } = useSimulation()

const handleExport = (resultId) => {
  const blob = exportResult(resultId, 'json')
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `simulation-${resultId}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
```

### 6. 存储统计

**获取存储信息**:
```javascript
const stats = resultStorage.getStorageStats()

// 返回:
{
  totalResults: 150,           // 总结果数
  favoriteResults: 25,        // 收藏数
  storageUsed: 2048576,       // 使用字节 (约2MB)
  oldestResult: "2026-06-01T...",  // 最旧记录
  newestResult: "2026-06-11T..."   // 最新记录
}
```

## 🎨 智能标签系统

系统会自动为每次计算生成标签：

### 覆盖率标签
- `高覆盖率`: coverage_ratio ≥ 1e-7
- `中等覆盖率`: 1e-8 ≤ coverage_ratio < 1e-7
- `低覆盖率`: coverage_ratio < 1e-8

### 面板类型标签
- `镜面面板`: albedo_pv ≥ 0.9
- `新型面板`: 0.4 ≤ albedo_pv < 0.9
- `普通面板`: albedo_pv < 0.4

### CO2浓度标签
- `高CO2`: co2_current ≥ 800
- `低CO2`: co2_current ≤ 350

## 📊 在组件中使用

### 在 App.vue 中集成

```vue
<script setup>
import { useSimulation } from '@/composables/useSimulation'

const {
  // 现有功能
  triggerCalculation,
  temperatureChange,

  // 新增存储功能
  getResultHistory,
  addToFavorites,
  exportResult
} = useSimulation()

// 获取历史记录
const history = getResultHistory()

// 添加到收藏
const handleFavorite = (resultId) => {
  addToFavorites(resultId, '重要场景')
}

// 导出结果
const handleExport = (resultId) => {
  const blob = exportResult(resultId, 'json')
  // 触发下载...
}
</script>
```

## 🚀 推荐的UI增强

### 1. 历史记录页面

在现有的 HistoryPage.vue 中添加：
- 历史记录列表
- 过滤和搜索功能
- 标签筛选
- 对比选择

### 2. 收藏管理

- 收藏列表显示
- 备注编辑
- 快速访问

### 3. 导出按钮

在 ParameterPanel.vue 或 MetricsPanel.vue 中添加：
```vue
<button @click="handleExportCurrent" class="tech-button">
  📥 导出当前结果
</button>
```

## 💡 使用建议

### 存储策略

1. **自动保存**: 每次计算自动保存（默认开启）
2. **定期清理**: 系统自动保留最近1000条记录
3. **重要标记**: 将重要场景添加到收藏

### 数据管理

1. **命名规范**: 使用描述性的场景名称
2. **标签分类**: 利用标签快速筛选
3. **定期备份**: 定期导出重要数据

### 性能优化

1. **按需加载**: 大量历史记录时分页加载
2. **索引优化**: 使用ID快速查找
3. **存储限制**: 监控存储使用情况

## 🔮 扩展建议

### 远程存储 (未来)

如果需要云存储或多设备同步，可以添加：
- 后端API存储
- 数据库支持 (MongoDB/PostgreSQL)
- 用户账户系统
- 跨设备同步

### 数据分析 (未来)

- 参数敏感性分析
- 趋势预测
- 优化建议生成
- 报告自动生成

## 📝 总结

✅ **当前实现**:
- 完整的本地存储方案
- 自动保存历史记录
- 收藏和导出功能
- 多结果对比分析

✅ **集成状态**:
- 已集成到 `useSimulation.js`
- 可在所有组件中使用
- 存储容量: 约5-10MB (1000条记录)

✅ **下一步**:
- 在历史页面中展示记录
- 添加导出按钮到UI
- 实现对比功能界面

现在每次计算都会自动保存，您可以随时查看历史记录、对比不同场景，并导出结果！🎉
