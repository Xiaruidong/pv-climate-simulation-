# 🔄 参数映射关系表

## UI参数 → 计算参数映射

### 当前系统参数映射

| 前端UI参数 | 后端计算参数 | 数据类型 | 必需/可选 | 默认值 |
|------------|-------------|----------|-----------|--------|
| 反照率 | albedo | Float | 必需 | 0.35 |
| 🆕 覆盖率 | coverage_ratio | Float | 必需 | 1e-8 |
| (缺失) 光伏效率 | pv_efficiency | Float | 必需 | 0.23 |
| (缺失) CO2浓度 | co2_current | Float | 必需 | 420.0 |
| 温度 | initial_temp | Float | 必需 | 15.0 |
| (缺失) 陆地反照率 | albedo_land | Float | 可选 | 0.3 |
| (缺失) 海洋反照率 | albedo_ocean | Float | 可选 | 0.06 |

### 缺失的重要参数

当前UI中缺少这些核心计算参数：

1. **光伏效率 (pv_efficiency)**
   - 影响: CO2减排量
   - 范围: 0.15-0.30
   - 推荐值: 0.23 (单晶硅)

2. **CO2浓度 (co2_current)**
   - 影响: 温度基准值
   - 范围: 280-1000 ppm
   - 推荐值: 420 (当前水平)

## 🎨 建议的UI改进

### 在ParameterPanel中添加

```vue
<!-- 光伏系统参数 -->
<div class="param-section">
  <h3 class="param-section-title">⚡ 光伏系统参数</h3>
  
  <div class="param-group">
    <div class="param-label">光伏效率</div>
    <input v-model.number="params.pvEfficiency" 
           type="number" step="0.01" min="0.15" max="0.30" />
    <span class="input-unit">效率值</span>
    <div class="param-hint">影响发电量和CO2减排</div>
  </div>
  
  <div class="param-group">
    <div class="param-label">面板类型预设</div>
    <select v-model="params.panelType" class="tech-select">
      <option value="mono">单晶硅 (23%)</option>
      <option value="poly">多晶硅 (16%)</option>
      <option value="thin_film">薄膜 (12%)</option>
      <option value="perovskite">钙钛矿 (25%)</option>
    </select>
  </div>
</div>

<!-- 气候参数 -->
<div class="param-section">
  <h3 class="param-section-title">🌡 气候参数</h3>
  
  <div class="param-group">
    <div class="param-label">CO2浓度</div>
    <input v-model.number="params.co2Current" 
           type="number" step="10" min="280" max="1000" />
    <span class="input-unit">ppm</span>
    <div class="param-hint">影响基准温度</div>
  </div>
  
  <div class="param-group">
    <div class="param-label">气候情景</div>
    <select v-model="params.climateScenario" class="tech-select">
      <option value="current">当前水平 (420ppm)</option>
      <option value="pre_industrial">前工业化 (280ppm)</option>
      <option value="rcp26">RCP2.6 (450ppm)</option>
      <option value="rcp85">RCP8.5 (1000ppm)</option>
    </select>
  </div>
</div>
```

### 参数建议的JavaScript逻辑

```javascript
// 在 ParameterPanel.vue 的 script setup 中添加
const params = reactive({
  // 现有参数...
  coverageRatio: 1e-8,
  
  // 🆕 新增光伏参数
  pvEfficiency: 0.23,
  panelType: 'mono',
  
  // 🆕 新增气候参数
  co2Current: 420.0,
  climateScenario: 'current'
})

// 面板类型预设
const panelTypes = {
  mono: { efficiency: 0.23, name: '单晶硅' },
  poly: { efficiency: 0.16, name: '多晶硅' },
  thin_film: { efficiency: 0.12, name: '薄膜' },
  perovskite: { efficiency: 0.25, name: '钙钛矿' }
}

// 气候情景预设
const climateScenarios = {
  current: { co2: 420 },
  pre_industrial: { co2: 280 },
  rcp26: { co2: 450 },
  rcp85: { co2: 1000 }
}

// 监听面板类型变化
watch(() => params.panelType, (newType) => {
  params.pvEfficiency = panelTypes[newType].efficiency
}, { immediate: false })

// 监听气候情景变化
watch(() => params.climateScenario, (newScenario) => {
  params.co2Current = climateScenarios[newScenario].co2
})
```

## 🔧 参数验证矩阵

### 当前状态检查

| 参数 | UI中存在 | 传递到计算 | 计算中使用 | 状态 |
|------|---------|-----------|-----------|------|
| 反照率 | ✅ | ✅ | ✅ | 🟢 完整 |
| 覆盖率 | ✅ | ✅ | ✅ | 🟢 完整 |
| 光伏效率 | ❌ | ❌ | ❌ | 🔴 缺失 |
| CO2浓度 | ❌ | ❌ | ❌ | 🔴 缺失 |
| 初始温度 | ✅ (温度) | ✅ | ✅ | 🟢 完整 |
| 陆地反照率 | ❌ | ✅ (默认) | ✅ | 🟡 使用默认 |
| 海洋反照率 | ❌ | ✅ (默认) | ✅ | 🟡 使用默认 |

## 🎯 关键发现

### 问题1: 光伏效率缺失
**影响**: CO2减排计算不准确
**解决方案**: 添加光伏效率输入框
**优先级**: ⭐⭐⭐⭐⭐

### 问题2: CO2浓度缺失
**影响**: 温度基准值固定为420ppm，无法测试不同气候情景
**解决方案**: 添加CO2浓度选择器
**优先级**: ⭐⭐⭐⭐

### 问题3: 参数名称不一致
**影响**: 参数传递可能失败
**解决方案**: 统一使用驼峰式或下划线式
**优先级**: ⭐⭐⭐

## 🚀 推荐改进方案

### 短期修复
1. 在ParameterPanel中添加光伏效率输入
2. 添加CO2浓度选择器
3. 添加面板类型预设（自动设置效率）

### 长期优化
1. 设计参数分组UI（光伏/气候/地理）
2. 添加参数验证和警告
3. 实现参数预设和场景管理
4. 添加参数影响实时预览

## 📊 完整参数需求对比

### 计算必需参数 (3个)
- ✅ 反照率 (现有)
- ✅ 覆盖率 (已添加)
- ❌ 光伏效率 (缺失)
- ❌ CO2浓度 (缺失)

### 计算增强参数 (3个)
- ✅ 初始温度 (现有)
- ❌ 陆地反照率 (使用默认)
- ❌ 海洋反照率 (使用默认)

### 高级参数 (可选)
- ❌ 纬度/经度 (现有但未使用)
- ❌ 装机容量 (现有但不相关)
- ❌ 太阳辐照度 (现有但未使用)

## 💡 立即行动建议

1. **优先添加光伏效率**: 对CO2减排计算至关重要
2. **优先添加CO2浓度**: 对温度基准计算至关重要
3. **简化其他参数**: 装机容量等参数对当前计算模型无影响
4. **优化参数布局**: 按物理意义分组显示

这样可以确保用户能够完整控制所有影响计算结果的关键参数！
